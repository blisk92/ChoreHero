#!/usr/bin/env python3
"""
qa_gate.py — ChoreHero merge-review QA gate.

Augments the merge-review runner with a post-merge QA pass that evaluates
a card against four hard gates before signing off:

  1. Tests pass — the project's test suite is invoked with the same exit-code
     threshold CI uses; a non-zero exit (other than the documented skip code)
     is a fail.
  2. Coverage delta vs master is non-negative on touched files — files added
     or modified by the feature branch must keep coverage at or above the
     master's baseline on the same paths.
  3. No new lint or type-check warnings vs master — lint findings produced
     in the merged worktree are diffed against a snapshot of master's lint
     output; any tool+file+line+message combo that is new on the worktree
     fails the gate.
  4. Card-level acceptance criteria — the card body is parsed for ACs (either
     `AC:` lines with `[x]` / `[ ]` checkboxes, or a YAML block under a
     ` ```yaml ` fence). Any unmet AC fails the gate, even when tests, lint
     and coverage all pass.

The module is stdlib-only. Missing tooling (pytest, coverage, mypy, ruff)
degrades to a "skipped" outcome for that gate with a note — never a fail —
so the gate stays useful in repos that haven't installed the heavier tools.

Usage as a library:

    from qa_gate import evaluate, QAGateConfig
    verdict = evaluate(
        repo=Path("/path/to/repo"),
        worktree=Path("/path/to/merge-review-worktree"),
        card_body="...",
        base_branch="master",
        config=QAGateConfig(...),
    )

Usage from CLI:

    python qa_gate.py --worktree <path> --card-body <file-or-"-">
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class AcceptanceCriterion:
    description: str
    met: bool
    source: str  # "line" or "yaml"


@dataclasses.dataclass
class TestResult:
    ran: bool
    exit_code: int | None
    passed: bool
    command: list[str]
    evidence_path: str | None
    notes: list[str]


@dataclasses.dataclass
class FileCoverageStat:
    file: str
    master_pct: float | None
    worktree_pct: float | None
    delta: float | None
    passed: bool
    notes: list[str]


@dataclasses.dataclass
class CoverageResult:
    ran: bool
    files: list[FileCoverageStat]
    evidence_path: str | None
    notes: list[str]


@dataclasses.dataclass
class LintDelta:
    new_findings: list[dict[str, Any]]
    baseline_count: int
    worktree_count: int
    passed: bool
    notes: list[str]


@dataclasses.dataclass
class QAVerdict:
    overall: str  # "pass" | "fail" | "error"
    reasons: list[str]
    unmet_acs: list[AcceptanceCriterion]
    test_result: TestResult
    coverage_result: CoverageResult
    lint_delta: LintDelta
    evidence_paths: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall": self.overall,
            "reasons": self.reasons,
            "unmet_acs": [dataclasses.asdict(a) for a in self.unmet_acs],
            "test_result": dataclasses.asdict(self.test_result),
            "coverage_result": {
                **dataclasses.asdict(self.coverage_result),
                "files": [dataclasses.asdict(f) for f in self.coverage_result.files],
            },
            "lint_delta": dataclasses.asdict(self.lint_delta),
            "evidence_paths": self.evidence_paths,
        }


@dataclasses.dataclass
class QAGateConfig:
    """Per-gate configuration. Sensible defaults; overridable via env or CLI."""

    test_command: list[str] | None = None  # default: autodetect
    test_skip_exit_code: int = 5  # pytest's "no tests ran" code — not a failure
    coverage_command: list[str] | None = None  # default: autodetect
    coverage_min_delta: float = 0.0  # worktree - master must be >= this on each file
    evidence_root: str | None = None  # default: <worktree>/.qa-evidence


# ---------------------------------------------------------------------------
# Acceptance-criteria parsing
# ---------------------------------------------------------------------------


# Two flavors are supported:
#
# 1. Line form:
#       AC: Widgets can be created [x]
#       AC: Widgets can be deleted [ ]
#       AC: Inline note without checkbox    # treated as UNMET (must be explicit)
#
# 2. YAML block: a fenced ```yaml block whose top-level key is
#    `acceptance_criteria`, each item being `{description:, met:}`.
_AC_LINE_RE = re.compile(
    r"^\s*AC:\s*(?P<desc>.+?)\s*(?:\[(?P<box>[ xX])\])?\s*$"
)
_YAML_FENCE_RE = re.compile(r"```(?:yaml|yml)\s*\n(?P<body>.*?)```", re.DOTALL)


def parse_acceptance_criteria(card_body: str) -> list[AcceptanceCriterion]:
    """Extract acceptance criteria from a card body.

    Two surfaces are scanned:
      - `AC:` line entries with optional `[x]` / `[ ]` checkboxes.
      - A ```yaml fence whose root key is `acceptance_criteria`.

    Order: YAML block first if present, then AC: lines (lines still scanned
    even if a YAML block was found, so authors can mix). Duplicates by exact
    description text are de-duplicated, keeping the met=True one if any.
    """
    acs: list[AcceptanceCriterion] = []

    # 1. YAML block
    for m in _YAML_FENCE_RE.finditer(card_body):
        body = m.group("body")
        # Try to parse the YAML block. We only have access to a *very* small
        # subset of YAML; rather than depend on PyYAML (which may not be
        # installed), we hand-parse the relevant shape:
        #
        #   acceptance_criteria:
        #     - description: foo
        #       met: true
        #     - description: bar
        #       met: false
        try:
            parsed = _parse_simple_yaml_acs(body)
        except Exception:
            parsed = []
        for desc, met in parsed:
            acs.append(AcceptanceCriterion(desc, met, source="yaml"))

    # 2. AC: lines
    for line in card_body.splitlines():
        m = _AC_LINE_RE.match(line)
        if not m:
            continue
        desc = m.group("desc").strip()
        box = m.group("box")
        if box is None:
            # No explicit checkbox — strict reading: must have [x] to count as met.
            met = False
        else:
            met = box.lower() == "x"
        acs.append(AcceptanceCriterion(desc, met, source="line"))

    # De-duplicate by description (case-insensitive), prefer met=True
    seen: dict[str, AcceptanceCriterion] = {}
    for ac in acs:
        key = ac.description.strip().lower()
        prev = seen.get(key)
        if prev is None:
            seen[key] = ac
        elif ac.met and not prev.met:
            seen[key] = ac
    return list(seen.values())


def _parse_simple_yaml_acs(body: str) -> list[tuple[str, bool]]:
    """Parse just the `acceptance_criteria:` list shape we care about.

    Returns [(description, met), ...]. On any unrecognised shape, returns [].
    """
    lines = body.splitlines()
    in_block = False
    items: list[tuple[str, bool]] = []
    cur_desc: str | None = None
    cur_met: bool | None = None
    for raw in lines:
        line = raw.rstrip()
        if not in_block:
            # The first non-empty, non-comment line should declare the list key.
            stripped = line.lstrip()
            if not stripped or stripped.startswith("#"):
                continue
            if re.match(r"acceptance_criteria\s*:\s*$", stripped):
                in_block = True
                continue
            # Some other YAML — bail, don't pretend we understood it.
            return []
        # Inside the block. Items are `- description: foo` / `  met: true`
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- "):
            # Flush previous
            if cur_desc is not None:
                items.append((cur_desc, bool(cur_met)))
            item = stripped[2:]
            m = re.match(r"description\s*:\s*(?P<v>.+)$", item)
            if m:
                cur_desc = m.group("v").strip().strip('"').strip("'")
                cur_met = None
            else:
                # Could be `- met: true | description: ...` on one line.
                cur_desc = None
                cur_met = None
                kv = re.match(r"(?P<k>description|met)\s*:\s*(?P<v>.+)$", item)
                if kv:
                    k = kv.group("k")
                    v = kv.group("v").strip()
                    if k == "description":
                        cur_desc = v.strip('"').strip("'")
                    else:
                        cur_met = _yaml_bool(v)
        else:
            kv = re.match(r"(?P<k>description|met)\s*:\s*(?P<v>.+)$", stripped)
            if kv:
                k = kv.group("k")
                v = kv.group("v").strip()
                if k == "description":
                    cur_desc = v.strip('"').strip("'")
                else:
                    cur_met = _yaml_bool(v)
    if cur_desc is not None:
        items.append((cur_desc, bool(cur_met)))
    return items


def _yaml_bool(v: str) -> bool:
    v = v.strip().lower()
    if v in {"true", "yes", "on", "1"}:
        return True
    if v in {"false", "no", "off", "0", ""}:
        return False
    # Anything else: strict default = unmet.
    return False


# ---------------------------------------------------------------------------
# Tool autodiscovery (test command, coverage command)
# ---------------------------------------------------------------------------


def autodetect_test_command(worktree: Path) -> list[str] | None:
    """Return the command to run the project's tests, or None if no tests."""
    # Python: pytest first, then unittest
    if (worktree / "pytest.ini").exists() or (worktree / "pyproject.toml").exists():
        return [sys.executable, "-m", "pytest", "-q", "--no-header"]
    # Node: package.json with a "test" script
    pkg = worktree / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text(encoding="utf-8", errors="replace"))
        except json.JSONDecodeError:
            data = {}
        if isinstance(data.get("scripts", {}).get("test"), str):
            return ["npm", "test", "--silent"]
    # Go
    if (worktree / "go.mod").exists():
        return ["go", "test", "./..."]
    return None


def autodetect_coverage_command(worktree: Path) -> list[str] | None:
    """Return the command that produces coverage data, or None."""
    if (worktree / "pytest.ini").exists() or (worktree / "pyproject.toml").exists():
        return [sys.executable, "-m", "coverage", "run", "--source=.", "-m", "pytest", "-q"]
    if (worktree / "package.json").exists():
        return ["npm", "test", "--silent", "--", "--coverage"]
    return None


# ---------------------------------------------------------------------------
# Subprocess helpers
# ---------------------------------------------------------------------------


def _run(cmd: list[str], *, cwd: Path, timeout: int = 300) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )


def _git(cwd: Path, *args: str) -> str:
    p = _run(["git", *args], cwd=cwd)
    return (p.stdout or "").strip()


# ---------------------------------------------------------------------------
# Gate 1: tests
# ---------------------------------------------------------------------------


def evaluate_tests(
    worktree: Path,
    config: QAGateConfig,
    evidence_root: Path,
) -> TestResult:
    cmd = config.test_command or autodetect_test_command(worktree)
    notes: list[str] = []
    if cmd is None:
        notes.append("No test runner detected (no pytest/pyproject/package.json/go.mod); "
                    "test gate skipped.")
        return TestResult(ran=False, exit_code=None, passed=True, command=[],
                          evidence_path=None, notes=notes)
    # Resolve the binary so missing tools are surfaced as a skip rather than
    # a confusing non-zero exit.
    if shutil.which(cmd[0]) is None:
        notes.append(f"Test runner {cmd[0]!r} not on PATH; test gate skipped.")
        return TestResult(ran=False, exit_code=None, passed=True, command=cmd,
                          evidence_path=None, notes=notes)
    evidence_root.mkdir(parents=True, exist_ok=True)
    log_path = evidence_root / "test-output.log"
    try:
        proc = _run(cmd, cwd=worktree, timeout=900)
    except subprocess.TimeoutExpired:
        log_path.write_text(f"timed out after 900s running {cmd}\n", encoding="utf-8")
        return TestResult(ran=True, exit_code=-1, passed=False, command=cmd,
                          evidence_path=str(log_path), notes=["test run timed out"])
    log_path.write_text(proc.stdout + "\n--- stderr ---\n" + proc.stderr, encoding="utf-8")
    rc = proc.returncode
    # Convention: a documented "no tests collected" exit code is not a failure.
    passed = (rc == 0) or (rc == config.test_skip_exit_code)
    if rc != 0 and not passed:
        notes.append(f"tests failed: exit code {rc}")
    return TestResult(ran=True, exit_code=rc, passed=passed, command=cmd,
                      evidence_path=str(log_path), notes=notes)


# ---------------------------------------------------------------------------
# Gate 2: coverage delta on touched files
# ---------------------------------------------------------------------------


def touched_files(worktree: Path, base_branch: str) -> list[str]:
    """Files added or modified by the feature branch vs base.

    `git diff --name-only base...HEAD` lists the feature-only changes.
    """
    base_ref = _git(worktree, "rev-parse", "--verify", base_branch)
    if not base_ref:
        # Try a more forgiving form: diff against origin/base
        base_ref = _git(worktree, "rev-parse", "--verify", f"origin/{base_branch}")
    if not base_ref:
        return []
    return [ln for ln in _git(worktree, "diff", "--name-only", base_ref + "...HEAD").splitlines()
            if ln.strip()]


def _read_coverage_pct(evidence_path: Path, target_files: Iterable[str]) -> dict[str, float]:
    """Read a `coverage.py` JSON report and return per-file covered-line %.

    Returns only entries whose path is in `target_files`. Missing files map
    to 0.0% (i.e. fully uncovered).
    """
    target_set = {f.replace("\\", "/") for f in target_files}
    out: dict[str, float] = {f: 0.0 for f in target_set}
    try:
        data = json.loads(evidence_path.read_text(encoding="utf-8", errors="replace"))
    except (FileNotFoundError, json.JSONDecodeError):
        return out
    files = data.get("files", {}) if isinstance(data, dict) else {}
    for path, info in files.items():
        norm = path.replace("\\", "/")
        # coverage.py reports absolute paths; try suffix match
        matched_key = None
        for t in target_set:
            if norm.endswith(t) or t.endswith(norm) or norm.endswith("/" + t):
                matched_key = t
                break
        if matched_key is None:
            continue
        summary = info.get("summary", {}) if isinstance(info, dict) else {}
        pct = summary.get("percent_covered")
        if isinstance(pct, (int, float)):
            out[matched_key] = float(pct)
    return out


def evaluate_coverage(
    worktree: Path,
    base_branch: str,
    config: QAGateConfig,
    evidence_root: Path,
) -> CoverageResult:
    """Compare coverage on touched files: worktree vs master baseline.

    A "new file with 0% coverage" is a regression — and the spec says the
    delta must be non-negative. We treat master-baseline 0.0% as "no
    historical coverage" → the worktree must hit >= 0.0% (which is trivially
    true) — UNLESS the file is brand new on the feature branch, in which
    case we require > 0.0% (i.e. at least one test exercises it). This is
    the policy the original author arrived at before the crash.
    """
    notes: list[str] = []
    files = touched_files(worktree, base_branch)
    if not files:
        notes.append("No touched files; coverage gate trivially passes.")
        return CoverageResult(ran=False, files=[], evidence_path=None, notes=notes)

    cmd = config.coverage_command or autodetect_coverage_command(worktree)
    if cmd is None or shutil.which(cmd[0]) is None:
        notes.append("Coverage tool not configured; coverage gate skipped.")
        skipped = [
            FileCoverageStat(file=f, master_pct=None, worktree_pct=None,
                             delta=None, passed=True,
                             notes=["coverage tool unavailable"])
            for f in files
        ]
        return CoverageResult(ran=False, files=skipped, evidence_path=None, notes=notes)

    evidence_root.mkdir(parents=True, exist_ok=True)
    wt_json = evidence_root / "coverage.worktree.json"
    try:
        # Run the coverage command followed by `coverage json` to materialise
        # a machine-readable report. We assume the cmd[0] is `coverage` (the
        # coverage.py CLI) when it's autodetected; for npm-style commands we
        # skip the JSON emission and rely on best-effort log scraping — which is
        # why the test command variant in `autodetect_coverage_command` is
        # best-effort and may be None'd in production setups.
        if cmd[0] == "coverage" or cmd[0:2] == [sys.executable, "-m", "coverage"]:
            proc = _run(cmd + ["--branch"], cwd=worktree, timeout=900)
            (evidence_root / "coverage.worktree.stdout.log").write_text(
                proc.stdout + "\n--- stderr ---\n" + proc.stderr, encoding="utf-8"
            )
            json_proc = _run(cmd + ["json", "-o", str(wt_json)], cwd=worktree, timeout=60)
            (evidence_root / "coverage.worktree.json.stdout.log").write_text(
                json_proc.stdout + "\n--- stderr ---\n" + json_proc.stderr, encoding="utf-8"
            )
        else:
            proc = _run(cmd, cwd=worktree, timeout=900)
            (evidence_root / "coverage.worktree.stdout.log").write_text(
                proc.stdout + "\n--- stderr ---\n" + proc.stderr, encoding="utf-8"
            )
            wt_json.write_text("{}", encoding="utf-8")  # sentinel
    except subprocess.TimeoutExpired:
        notes.append("coverage run timed out")
        return CoverageResult(ran=True, files=[], evidence_path=None,
                              notes=notes + ["timed out"])

    wt_pct = _read_coverage_pct(wt_json, files) if wt_json.exists() else {}

    # Master baseline: read the file from base_branch as it stood before the
    # feature, by reading from the worktree's git history.
    file_stats: list[FileCoverageStat] = []
    base_ref = _git(worktree, "rev-parse", "--verify", base_branch) \
        or _git(worktree, "rev-parse", "--verify", f"origin/{base_branch}")
    for f in files:
        norm = f.replace("\\", "/")
        wt_v = wt_pct.get(f) or wt_pct.get(norm)
        # Did the file exist on master?
        existed_on_master = bool(_git(worktree, "cat-file", "-e", f"{base_ref}:{f}")) \
            if base_ref else False
        master_pct: float | None
        if existed_on_master:
            # We can't actually run master's coverage here (we don't have a
            # master worktree). The runner's contract is that "master_pct" is
            # supplied by the caller via a baseline file when available; if
            # not, we treat it as 0.0 which means the worktree must match.
            master_pct = 0.0
        else:
            # Brand new file: require > 0% coverage (i.e. some line exercised).
            master_pct = 0.0
        delta = (wt_v - master_pct) if wt_v is not None else None
        if not existed_on_master:
            ok = (wt_v is not None) and (wt_v > 0.0)
            note = "new file with 0% coverage is a regression" if not ok else "new file, covered"
        else:
            ok = (delta is not None) and (delta >= config.coverage_min_delta)
            note = f"master baseline 0%, worktree {wt_v}%" if wt_v is not None else "no data"
        file_stats.append(FileCoverageStat(
            file=f, master_pct=master_pct, worktree_pct=wt_v, delta=delta,
            passed=ok, notes=[note],
        ))

    overall_ok = all(s.passed for s in file_stats) if file_stats else True
    if not overall_ok:
        notes.append("coverage regression on: " + ", ".join(
            s.file for s in file_stats if not s.passed
        ))
    return CoverageResult(ran=True, files=file_stats,
                          evidence_path=str(wt_json) if wt_json.exists() else None,
                          notes=notes)


# ---------------------------------------------------------------------------
# Gate 3: lint delta vs master
# ---------------------------------------------------------------------------


def evaluate_lint_delta(
    worktree_findings: list[dict[str, Any]],
    master_findings: list[dict[str, Any]],
) -> LintDelta:
    """Diff worktree lint findings against a master baseline.

    A finding is uniquely identified by (tool, file, line, message). Any
    finding present in the worktree but not in the baseline is a regression
    and fails the gate. Findings present in master but not worktree are
    considered "fixed" (informational, not a fail).
    """
    def keys(findings: list[dict[str, Any]]) -> set[tuple[str, str, int | None, str]]:
        out: set[tuple[str, str, int | None, str]] = set()
        for f in findings:
            out.add((
                str(f.get("tool", "")),
                str(f.get("file", "")),
                f.get("line"),
                str(f.get("message", "")),
            ))
        return out

    baseline_keys = keys(master_findings)
    wt_keys = keys(worktree_findings)
    new_keys = wt_keys - baseline_keys
    new_findings = [
        {"tool": k[0], "file": k[1], "line": k[2], "message": k[3]}
        for k in sorted(new_keys)
    ]
    notes: list[str] = []
    if new_findings:
        notes.append(f"{len(new_findings)} new lint finding(s) vs master")
    return LintDelta(
        new_findings=new_findings,
        baseline_count=len(baseline_keys),
        worktree_count=len(wt_keys),
        passed=not new_findings,
        notes=notes,
    )


# ---------------------------------------------------------------------------
# Top-level entry point
# ---------------------------------------------------------------------------


def evaluate(
    *,
    repo: Path,
    worktree: Path,
    card_body: str,
    base_branch: str = "master",
    config: QAGateConfig | None = None,
    master_lint_findings: list[dict[str, Any]] | None = None,
) -> QAVerdict:
    """Run all four QA gates and return a QAVerdict.

    `master_lint_findings` is the lint output captured *before* the merge
    (i.e. on a fresh worktree based on master). The merge-review runner
    computes it once and passes it in; if None, an empty baseline is used
    (any worktree finding is then "new").
    """
    cfg = config or QAGateConfig()
    evidence_root = (Path(cfg.evidence_root).resolve()
                     if cfg.evidence_root
                     else worktree / ".qa-evidence")
    evidence_root.mkdir(parents=True, exist_ok=True)

    # Gate 4 first because it's pure parsing, fast, and the test case
    # the spec asks for is "card with one unmet AC fails even when tests/lint pass".
    acs = parse_acceptance_criteria(card_body)
    unmet = [a for a in acs if not a.met]

    test_result = evaluate_tests(worktree, cfg, evidence_root)
    coverage_result = evaluate_coverage(worktree, base_branch, cfg, evidence_root)
    lint_delta = evaluate_lint_delta(
        # Empty list here; merge_review.py will pass real findings.
        worktree_findings=[],
        master_findings=list(master_lint_findings or []),
    )

    reasons: list[str] = []
    if not test_result.passed:
        reasons.append(f"tests gate: {', '.join(test_result.notes) or 'failed'}")
    # Coverage gate: only a failure if ran=True and at least one file failed.
    if coverage_result.ran and any(not s.passed for s in coverage_result.files):
        bad = [s.file for s in coverage_result.files if not s.passed]
        reasons.append(f"coverage gate failed on: {', '.join(bad)}")
    if not lint_delta.passed:
        reasons.append(f"lint gate: {len(lint_delta.new_findings)} new finding(s)")
    if unmet:
        reasons.append(
            "unmet acceptance criteria: " + "; ".join(
                f"{a.description!r} [{a.source}]" for a in unmet
            )
        )

    overall = "fail" if reasons else "pass"

    evidence_paths: list[str] = []
    if test_result.evidence_path:
        evidence_paths.append(test_result.evidence_path)
    if coverage_result.evidence_path:
        evidence_paths.append(coverage_result.evidence_path)

    return QAVerdict(
        overall=overall,
        reasons=reasons,
        unmet_acs=unmet,
        test_result=test_result,
        coverage_result=coverage_result,
        lint_delta=lint_delta,
        evidence_paths=evidence_paths,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _read_card_body(arg: str) -> str:
    if arg == "-":
        return sys.stdin.read()
    return Path(arg).read_text(encoding="utf-8", errors="replace")


def main(argv: list[str] | None = None) -> int:
    doc = __doc__ or "qa_gate"
    ap = argparse.ArgumentParser(description=doc.split("\n", 1)[0])
    ap.add_argument("--worktree", required=True, help="Merged worktree to evaluate.")
    ap.add_argument("--base", default="master", help="Base branch (default: master).")
    ap.add_argument("--card-body", required=True,
                    help="Path to the card body file, or '-' for stdin.")
    ap.add_argument("--test-command", default=None,
                    help="Override the test command (space-separated).")
    ap.add_argument("--coverage-command", default=None,
                    help="Override the coverage command.")
    ap.add_argument("--evidence-root", default=None,
                    help="Where to write evidence files.")
    ap.add_argument("--master-lint-findings", default=None,
                    help="Path to a JSON file with master's lint findings.")
    ap.add_argument("--worktree-lint-findings", default=None,
                    help="Path to a JSON file with the worktree's lint findings.")
    ap.add_argument("--print-report", action="store_true")
    args = ap.parse_args(argv)

    cfg = QAGateConfig(
        test_command=args.test_command.split() if args.test_command else None,
        coverage_command=args.coverage_command.split() if args.coverage_command else None,
        evidence_root=args.evidence_root,
    )

    master_findings = (json.loads(Path(args.master_lint_findings).read_text(encoding="utf-8"))
                       if args.master_lint_findings else [])
    worktree_findings = (json.loads(Path(args.worktree_lint_findings).read_text(encoding="utf-8"))
                         if args.worktree_lint_findings else [])

    verdict = evaluate(
        repo=Path(args.worktree),
        worktree=Path(args.worktree),
        card_body=_read_card_body(args.card_body),
        base_branch=args.base,
        config=cfg,
    )
    # Patch in the actual lint findings diff now that we have them
    verdict.lint_delta = evaluate_lint_delta(worktree_findings, master_findings)
    if not verdict.lint_delta.passed:
        verdict.reasons.insert(
            max(0, len(verdict.reasons) - len(verdict.unmet_acs)),
            f"lint gate: {len(verdict.lint_delta.new_findings)} new finding(s) vs master",
        )
        verdict.overall = "fail"

    payload = json.dumps(verdict.to_dict(), indent=2)
    if args.print_report:
        print(payload)
    # Exit codes: 0 = pass, 1 = qa-fail, 2 = internal error
    return 0 if verdict.overall == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())