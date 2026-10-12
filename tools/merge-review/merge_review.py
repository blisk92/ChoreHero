#!/usr/bin/env python3
"""
merge_review.py — ChoreHero merge-review conflict detection & resolution runner.

For a given feature branch, this tool:
  1. Creates a temporary worktree based on the base branch (default: master).
  2. Attempts `git merge --no-commit --no-ff <feature>`.
  3. If the merge succeeds:
       - Runs `git diff --check` to surface whitespace issues.
       - Auto-discovers and runs project linters (eslint, ruff, golangci-lint,
         biome, check-jsonschema) based on repo config files.
       - Marks the verdict "clean-merge" and writes the lint output.
  5. If the merge fails:
       - Parses each conflicted file's blocks.
       - Classifies each as one of: trivial-add-add, trivial-delete-modify, real.
       - Auto-resolves only trivially-safe cases.
       - Leaves a "manual-conflict" flag for everything else, with a suggested
         resolution order derived from git log blame / merge-base topology.
       - Aborts the in-progress merge and writes a structured conflict report.

Usage:
  python merge_review.py --repo <path> --feature <branch> [--base master]
                         [--worktree-root <path>] [--keep-worktree] [--report <path>]

Exit codes:
  0 — clean merge
  1 — real conflicts (manual resolution required)
  2 — trivial conflicts auto-resolved (reviewer should still verify)
  3 — internal error (worktree cleanup, git invocation, etc.)
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
import tempfile
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# QA gate integration helpers
# ---------------------------------------------------------------------------


def _load_card_body(worktree: Path) -> str:
    """Locate the card body text for the QA gate.

    Resolution order:
      1. `$CHOREHERO_CARD_BODY` env var (raw text).
      2. `<worktree>/.card-body` — a sidecar file the orchestrator drops in.
      3. `<worktree>/.chorehero/card-body.md` — convention.

    Raises FileNotFoundError if none of these exist; callers treat that as
    "no card body supplied → QA gate skipped" (legacy behaviour).
    """
    env = os.environ.get("CHOREHERO_CARD_BODY")
    if env is not None:
        return env
    sidecar = worktree / ".card-body"
    if sidecar.exists():
        return sidecar.read_text(encoding="utf-8", errors="replace")
    named = worktree / ".chorehero" / "card-body.md"
    if named.exists():
        return named.read_text(encoding="utf-8", errors="replace")
    raise FileNotFoundError("no card body supplied for QA gate")


def _run_qa_gate(
    *,
    repo: Path,
    worktree: Path,
    base: str,
    lint_findings: list[dict[str, Any]],
    card_body: str,
) -> dict[str, Any]:
    """Invoke the QA gate against a merged worktree.

    Captures a master-baseline lint snapshot from a fresh worktree based on
    `base`, then evaluates tests, coverage, lint-delta, and card ACs. Returns
    the gate's verdict as a serialisable dict (the `to_dict()` of QAVerdict).

    Any internal exception is logged into `notes` and a minimal `{"overall":
    "error", "reasons": [...]}` payload is returned so the merge review can
    still emit a verdict instead of crashing.
    """
    import importlib

    try:
        qa_module = importlib.import_module("qa_gate")
    except ImportError:
        # qa_gate.py sits alongside this script; load it directly.
        import importlib.util as _ilu
        spec = _ilu.spec_from_file_location("qa_gate", str(Path(__file__).parent / "qa_gate.py"))
        if spec is None or spec.loader is None:
            return {"overall": "error", "reasons": ["qa_gate module not importable"]}
        qa_module = _ilu.module_from_spec(spec)
        spec.loader.exec_module(qa_module)

    notes: list[str] = []
    master_lint: list[dict[str, Any]] = []
    master_wt: Path | None = None
    master_root: Path | None = None
    try:
        # Build a tiny worktree on master to get its baseline lint findings.
        # Use a single tmpdir so make_worktree() and remove_worktree() agree
        # on the path layout (Path(root) / f"wt-{base}").
        master_root = Path(tempfile.mkdtemp(prefix="chorehero-qa-master-"))
        master_wt = make_worktree(repo, base, master_root)
        baseline_linters = discover_linters(repo)
        for binary, cfg, _hint in baseline_linters:
            for finding in run_linter(binary, master_wt, repo, cfg):
                master_lint.append(dataclasses.asdict(finding))
    except Exception as exc:
        notes.append(f"master baseline lint capture failed: {exc}")
    finally:
        if master_wt is not None:
            remove_worktree(repo, master_wt)

    try:
        verdict = qa_module.evaluate(
            repo=repo,
            worktree=worktree,
            card_body=card_body,
            base_branch=base,
            master_lint_findings=master_lint,
        )
        # Replace the lint-delta computed by qa_gate with the real diff
        # (qa_gate.evaluate() doesn't see the live lint findings by design;
        # we computed them above).
        verdict.lint_delta = qa_module.evaluate_lint_delta(lint_findings, master_lint)
        if not verdict.lint_delta.passed:
            verdict.reasons.append(
                f"lint gate: {len(verdict.lint_delta.new_findings)} new finding(s) vs master"
            )
            verdict.overall = "fail"
        payload = verdict.to_dict()
        if notes:
            payload.setdefault("notes", []).extend(notes)
        return payload
    except Exception as exc:
        return {"overall": "error", "reasons": [f"qa_gate raised: {exc}"], "notes": notes}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class ConflictBlock:
    file: str
    hunk_index: int
    ours_label: str
    theirs_label: str
    ours_lines: list[str]
    theirs_lines: list[str]
    classification: str  # "trivial-add-add" | "trivial-delete-modify" | "real"
    rationale: str


@dataclasses.dataclass
class FileConflict:
    file: str
    blocks: list[ConflictBlock]
    classification: str  # "auto-resolvable" | "manual-conflict"
    auto_resolved: bool


@dataclasses.dataclass
class LintFinding:
    tool: str
    file: str
    line: int | None
    severity: str
    message: str


@dataclasses.dataclass
class Report:
    verdict: str  # "clean-merge" | "trivial-auto-merge" | "real-conflict" | "qa-fail" | "error"
    feature_branch: str
    base_branch: str
    repo: str
    merge_base: str
    whitespace_warnings: list[str]
    lint_findings: list[LintFinding]
    linters_run: list[str]
    file_conflicts: list[FileConflict]
    auto_resolved_files: list[str]
    manual_conflict_files: list[str]
    suggested_resolution_order: list[str]
    notes: list[str]
    worktree_path: str | None
    qa_verdict: dict[str, Any] | None = None  # populated by run_qa_gate after clean merge

    def to_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict,
            "feature_branch": self.feature_branch,
            "base_branch": self.base_branch,
            "repo": self.repo,
            "merge_base": self.merge_base,
            "whitespace_warnings": self.whitespace_warnings,
            "lint_findings": [dataclasses.asdict(f) for f in self.lint_findings],
            "linters_run": self.linters_run,
            "file_conflicts": [
                {
                    "file": fc.file,
                    "classification": fc.classification,
                    "auto_resolved": fc.auto_resolved,
                    "blocks": [dataclasses.asdict(b) for b in fc.blocks],
                }
                for fc in self.file_conflicts
            ],
            "auto_resolved_files": self.auto_resolved_files,
            "manual_conflict_files": self.manual_conflict_files,
            "suggested_resolution_order": self.suggested_resolution_order,
            "notes": self.notes,
            "worktree_path": self.worktree_path,
            "qa_verdict": self.qa_verdict,
        }


# ---------------------------------------------------------------------------
# Subprocess helpers
# ---------------------------------------------------------------------------


def run(
    args: list[str],
    *,
    cwd: Path | None = None,
    check: bool = False,
    capture: bool = True,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    """Run a subprocess, raising CalledProcessError if check=True and rc != 0."""
    return subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        check=check,
        capture_output=capture,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )


def git(cwd: Path, *args: str, check: bool = False) -> subprocess.CompletedProcess:
    return run(["git", *args], cwd=cwd, check=check)


def git_out(cwd: Path, *args: str) -> str:
    return git(cwd, *args, check=False).stdout.strip()


# ---------------------------------------------------------------------------
# Worktree management
# ---------------------------------------------------------------------------


def make_worktree(repo: Path, base: str, root: Path | None = None) -> Path:
    """Create a fresh worktree based on `base`. Returns the worktree path."""
    if root is None:
        root = Path(tempfile.mkdtemp(prefix="chorehero-merge-review-"))
    else:
        root.mkdir(parents=True, exist_ok=True)
    wt_path = root / f"wt-{base}"
    if wt_path.exists():
        shutil.rmtree(wt_path, ignore_errors=True)
    p = git(repo, "worktree", "add", "-b", f"merge-review/{base}", str(wt_path), base, check=True)
    return wt_path


def remove_worktree(repo: Path, wt: Path) -> None:
    """Best-effort worktree removal."""
    try:
        git(repo, "worktree", "remove", "--force", str(wt), check=False)
    except Exception:
        pass
    try:
        git(repo, "worktree", "prune", check=False)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Linter autodiscovery
# ---------------------------------------------------------------------------


LINTER_DISCOVERY: list[tuple[str, list[str], str]] = [
    # (binary, config-file-patterns, install-hint)
    ("eslint",  ["eslint.config.js", ".eslintrc", ".eslintrc.js",
                 ".eslintrc.json", ".eslintrc.cjs", ".eslintrc.yaml"],
     "npm install --save-dev eslint"),
    ("ruff",    ["ruff.toml", ".ruff.toml", "pyproject.toml"],
     "pip install ruff"),
    ("golangci-lint", [".golangci.yml", ".golangci.yaml",
                       ".golangci.toml", ".golangci.json"],
     "go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest"),
    ("biome",   ["biome.json", "biome.jsonc"],
     "npm install --save-dev @biomejs/biome"),
    ("check-jsonschema", [], "pip install check-jsonschema"),
]


def discover_linters(repo: Path) -> list[tuple[str, str, list[str]]]:
    """Return [(binary, config-file, install-hint), ...] for available linters."""
    found: list[tuple[str, str, list[str]]] = []
    for binary, patterns, hint in LINTER_DISCOVERY:
        if shutil.which(binary) is None:
            continue
        matched_config = ""
        for pat in patterns:
            if (repo / pat).exists():
                matched_config = pat
                break
        # biome and check-jsonschema don't strictly need a config file to be useful
        if matched_config or binary in {"biome", "check-jsonschema"}:
            found.append((binary, matched_config, [hint]))
        elif patterns:
            # binary present but no recognized config in this repo — skip silently
            pass
    return found


def run_linter(binary: str, worktree: Path, repo: Path, config: str) -> list[LintFinding]:
    """Run a linter and parse its output into LintFinding entries."""
    findings: list[LintFinding] = []
    try:
        if binary == "eslint":
            cmd = ["eslint", "--format=json", "--no-error-on-unmatched-pattern", "."]
        elif binary == "ruff":
            cmd = ["ruff", "check", "--output-format=json", "."]
        elif binary == "golangci-lint":
            cmd = ["golangci-lint", "run", "--out-format=json", "./..."]
        elif binary == "biome":
            cmd = ["biome", "lint", "--reporter=json"]
        elif binary == "check-jsonschema":
            cmd = ["check-jsonschema", "--schemafile", config] if config else []
        else:
            return findings
        if not cmd:
            return findings
        proc = run(cmd, cwd=worktree, check=False)
        if not proc.stdout.strip():
            return findings
        try:
            data = json.loads(proc.stdout)
        except json.JSONDecodeError:
            findings.append(LintFinding(binary, "<tool-output>", None, "info",
                                        f"Could not parse JSON output (rc={proc.returncode})"))
            return findings
        findings.extend(parse_linter_json(binary, data, worktree, repo))
    except FileNotFoundError:
        pass
    except Exception as exc:
        findings.append(LintFinding(binary, "<runner>", None, "info", f"linter failed: {exc}"))
    return findings


def parse_linter_json(
    binary: str,
    data: Any,
    worktree: Path,
    repo: Path,
) -> list[LintFinding]:
    findings: list[LintFinding] = []
    if binary == "eslint":
        for entry in data:
            for msg in entry.get("messages", []):
                findings.append(LintFinding(
                    "eslint",
                    msg.get("file") or "<unknown>",
                    msg.get("line"),
                    {"1": "warning", "2": "error"}.get(str(msg.get("severity", 2)), "info"),
                    msg.get("message", ""),
                ))
    elif binary == "ruff":
        for entry in data:
            findings.append(LintFinding(
                "ruff",
                entry.get("filename") or entry.get("file") or "<unknown>",
                entry.get("location", {}).get("row"),
                entry.get("level", "warning"),
                f"{entry.get('code', '')}: {entry.get('message', '')}".strip(": "),
            ))
    elif binary == "golangci-lint":
        # golangci-lint JSON: { "Issues": [ { "Pos": {"Filename": ..., "Line": ...},
        # "Severity": "...", "Text": "..." } ] }
        for issue in data.get("Issues", []):
            pos = issue.get("Pos", {})
            findings.append(LintFinding(
                "golangci-lint",
                pos.get("Filename", "<unknown>"),
                pos.get("Line"),
                issue.get("Severity", "warning"),
                issue.get("Text", ""),
            ))
    elif binary == "biome":
        # biome JSON: { "diagnostics": [ { "location": {"path": ..., "line": ...},
        # "severity": "...", "description": "..." } ] }
        for diag in data.get("diagnostics", []):
            loc = diag.get("location", {})
            findings.append(LintFinding(
                "biome",
                loc.get("path", {}).get("file") or "<unknown>",
                (loc.get("span") or [None])[0] or loc.get("line"),
                diag.get("severity", "warning"),
                diag.get("description", ""),
            ))
    return findings


# ---------------------------------------------------------------------------
# Conflict classification
# ---------------------------------------------------------------------------


CONFLICT_MARKER = re.compile(
    r"^<<<<<<< (.*?)$"
    r"\n(.*?)"                           # ours body (lazy, dotall below)
    r"^=======$\n"
    r"(.*?)"
    r"^>>>>>>> (.*?)$",
    re.MULTILINE | re.DOTALL,
)


def parse_conflicted_file(path: Path) -> list[ConflictBlock]:
    """Parse conflict markers from a file. Returns one entry per hunk."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return []
    blocks: list[ConflictBlock] = []
    for idx, m in enumerate(CONFLICT_MARKER.finditer(text), start=1):
        ours_label, ours_body, theirs_body, theirs_label = m.groups()
        blocks.append(ConflictBlock(
            file=str(path),
            hunk_index=idx,
            ours_label=ours_label.strip(),
            theirs_label=theirs_label.strip(),
            ours_lines=ours_body.splitlines(),
            theirs_lines=theirs_body.splitlines(),
            classification="real",        # filled in by classify_block
            rationale="",
        ))
    return blocks


def classify_block(block: ConflictBlock, both_added: bool, ours_deleted: bool,
                   theirs_deleted: bool) -> ConflictBlock:
    """Mutates the block in-place and returns it."""
    ours_empty = len(block.ours_lines) == 0
    theirs_empty = len(block.theirs_lines) == 0

    # Trivial case 1: pure add/add where at least one side adds and the other is empty
    # (the file existed on both sides, only one side modified this region).
    if both_added and (ours_empty or theirs_empty):
        block.classification = "trivial-add-add"
        block.rationale = "Pure add/add with one side empty; take the non-empty side."
        return block
    if both_added and not ours_empty and not theirs_empty:
        # Both sides genuinely added content in the same place — that's a real conflict.
        block.classification = "real"
        block.rationale = "Both sides added content at the same location."
        return block

    # Trivial case 2: delete/modify — one side deleted, the other modified only.
    if ours_deleted and not theirs_deleted:
        block.classification = "trivial-delete-modify"
        block.rationale = "Ours deleted the surrounding region; theirs only modified."
        return block
    if theirs_deleted and not ours_deleted:
        block.classification = "trivial-delete-modify"
        block.rationale = "Theirs deleted the surrounding region; ours only modified."
        return block

    # Trivial case 3: ours-empty / theirs-empty on a modify/modify — pure additions
    # of new lines on one side.
    if ours_empty and not theirs_empty:
        block.classification = "trivial-add-add"
        block.rationale = "Ours empty; take theirs."
        return block
    if theirs_empty and not ours_empty:
        block.classification = "trivial-add-add"
        block.rationale = "Theirs empty; take ours."
        return block

    # Trivial case 4: one side identical to common ancestor — git usually does this
    # automatically, but if it shows up in markers we treat it as real (manual review).
    block.classification = "real"
    block.rationale = "Both sides modified the same region; manual review required."
    return block


def auto_resolve_block(block: ConflictBlock) -> str:
    """Apply auto-resolution. Returns the chosen label and the resolved text."""
    # trivial-add-add where one side is empty → take the non-empty side
    if block.classification == "trivial-add-add":
        if not block.ours_lines and block.theirs_lines:
            return "\n".join(block.theirs_lines)
        if not block.theirs_lines and block.ours_lines:
            return "\n".join(block.ours_lines)
    # trivial-delete-modify → prefer the modification (modify beats delete)
    if block.classification == "trivial-delete-modify":
        if block.ours_lines:
            return "\n".join(block.ours_lines)
        if block.theirs_lines:
            return "\n".join(block.theirs_lines)
    # Should not be called for "real" blocks.
    return ""


def apply_auto_resolution(path: Path, blocks: list[ConflictBlock]) -> bool:
    """Replace conflict markers with auto-resolved content. Returns True if all
    blocks in this file were trivial."""
    text = path.read_text(encoding="utf-8", errors="replace")
    any_real = any(b.classification == "real" for b in blocks)
    if any_real:
        return False
    # Walk markers left-to-right and replace each in turn
    pieces = []
    cursor = 0
    for m in CONFLICT_MARKER.finditer(text):
        pieces.append(text[cursor:m.start()])
        ours_label, ours_body, theirs_body, theirs_label = m.groups()
        # Use a synthetic block to dispatch
        synth = ConflictBlock(
            file=str(path), hunk_index=1,
            ours_label=ours_label, theirs_label=theirs_label,
            ours_lines=ours_body.splitlines(),
            theirs_lines=theirs_body.splitlines(),
            classification="", rationale="",
        )
        # Re-classify on the fly — auto_resolve_block picks the right side.
        if len(ours_body) == 0 and len(theirs_body) > 0:
            resolved = theirs_body
        elif len(theirs_body) == 0 and len(ours_body) > 0:
            resolved = ours_body
        else:
            # Both non-empty — try delete/modify semantics: pick ours first
            resolved = ours_body
        pieces.append(resolved)
        cursor = m.end()
    pieces.append(text[cursor:])
    path.write_text("\n".join(pieces) if pieces else "", encoding="utf-8")
    return True


def git_path_conflict_type(repo: Path, target_file: str) -> dict[str, bool]:
    """Inspect `git diff` against the merge base for `target_file` to classify
    the kind of edit each side made."""
    merge_base = git_out(repo, "merge-base", "HEAD", "MERGE_HEAD")
    both_added = False
    ours_deleted = False
    theirs_deleted = False
    if merge_base:
        # File mode / type changes
        ours_status = git_out(repo, "diff", "--name-status", merge_base, "--", target_file)
        theirs_status = git_out(repo, "diff", "--name-status", merge_base + "..MERGE_HEAD",
                                "--", target_file)
        # Treat any 'A' status as add; 'D' as delete
        both_added = ("A" in (ours_status or "").split("\t")[0:1]
                      and "A" in (theirs_status or "").split("\t")[0:1])
        ours_deleted = ours_status.startswith("D")
        theirs_deleted = theirs_status.startswith("D")
    return {
        "both_added": both_added,
        "ours_deleted": ours_deleted,
        "theirs_deleted": theirs_deleted,
    }


# ---------------------------------------------------------------------------
# Merge orchestration
# ---------------------------------------------------------------------------


def attempt_merge(worktree: Path, feature: str) -> tuple[bool, str, list[str]]:
    """Run `git merge --no-commit --no-ff <feature>`. Returns (success, msg,
    conflicted_files). Aborts the merge on failure (caller can re-attempt)."""
    proc = git(worktree, "merge", "--no-commit", "--no-ff", feature, check=False)
    conflicted = git_out(worktree, "diff", "--name-only", "--diff-filter=U").splitlines()
    return proc.returncode == 0, (proc.stdout + proc.stderr).strip(), conflicted


def abort_merge(worktree: Path) -> None:
    git(worktree, "merge", "--abort", check=False)


def diff_check(worktree: Path) -> list[str]:
    """Return `git diff --check` warnings (one per line)."""
    out = git_out(worktree, "diff", "--check")
    return [ln for ln in out.splitlines() if ln.strip()]


# ---------------------------------------------------------------------------
# Suggested resolution order
# ---------------------------------------------------------------------------


def resolution_order(repo: Path, conflicted_files: list[str], feature: str,
                     base: str) -> list[str]:
    """Suggest an order based on: simpler files first, then by recency of last
    change in each branch (older = resolve first so newer decisions stand)."""
    def score(path: str) -> tuple[int, int]:
        # Sort key (extra_lower_priority, recency_inverse)
        depth = path.count("/")
        ours_log = git_out(repo, "log", "-1", "--format=%ct", "HEAD", "--", path)
        theirs_log = git_out(repo, "log", "-1", "--format=%ct", feature, "--", path)
        ts = max(int(ours_log or 0), int(theirs_log or 0))
        return (depth, -ts)
    return sorted(conflicted_files, key=score)


# ---------------------------------------------------------------------------
# Top-level review
# ---------------------------------------------------------------------------


def review(
    repo: Path,
    feature: str,
    base: str = "master",
    worktree_root: Path | None = None,
    keep_worktree: bool = False,
) -> Report:
    notes: list[str] = []
    wt: Path | None = None
    worktree_root_resolved: Path | None = worktree_root
    try:
        # Fresh worktree based on base branch
        if worktree_root_resolved is None:
            worktree_root_resolved = Path(tempfile.mkdtemp(prefix="chorehero-merge-review-"))
        wt = make_worktree(repo, base, worktree_root_resolved)

        # Compute merge base for reporting & suggestions
        merge_base = git_out(repo, "merge-base", base, feature)
        if not merge_base:
            notes.append(f"No merge-base between {base} and {feature}; branches may be unrelated.")

        # Attempt merge
        ok, msg, conflicted = attempt_merge(wt, feature)
        if not ok and not conflicted:
            # Something went wrong that wasn't a conflict (e.g. unrelated histories
            # when --no-ff is forced). Treat as error.
            abort_merge(wt)
            return Report(
                verdict="error", feature_branch=feature, base_branch=base, repo=str(repo),
                merge_base=merge_base, whitespace_warnings=[], lint_findings=[],
                linters_run=[], file_conflicts=[], auto_resolved_files=[],
                manual_conflict_files=[], suggested_resolution_order=[],
                notes=[f"Merge did not produce conflicts and did not succeed: {msg}"],
                worktree_path=str(wt) if keep_worktree else None,
            )

        if ok:
            # Clean merge — surface whitespace + run linters
            ws = diff_check(wt)
            linters = discover_linters(repo)
            lint_findings: list[LintFinding] = []
            linters_run: list[str] = []
            for binary, cfg, _hint in linters:
                linters_run.append(binary)
                lint_findings.extend(run_linter(binary, wt, repo, cfg))
            # Commit the merge so subsequent worktrees start from a clean tree
            git(wt, "commit", "--no-edit", "-q", check=False)
            # QA gate pass: evaluate tests, coverage, lint-delta, and card ACs
            # against this merged worktree. The card body is read from a
            # sidecar file (`<worktree>/.card-body` or via CHOREHERO_CARD_BODY`
            # env var); when absent, the QA gate is skipped (legacy callers).
            qa_payload: dict[str, Any] | None = None
            qa_verdict_label = "clean-merge"
            try:
                card_body = _load_card_body(wt)
            except FileNotFoundError:
                card_body = ""
            if card_body:
                qa_payload = _run_qa_gate(
                    repo=repo, worktree=wt, base=base,
                    lint_findings=[lf.__dict__ for lf in lint_findings],
                    card_body=card_body,
                )
                if qa_payload and qa_payload.get("overall") == "fail":
                    qa_verdict_label = "qa-fail"
                    notes.append(
                        "QA gate failed: " + "; ".join(qa_payload.get("reasons", []))
                    )
            return Report(
                verdict=qa_verdict_label,
                feature_branch=feature, base_branch=base, repo=str(repo),
                merge_base=merge_base, whitespace_warnings=ws,
                lint_findings=lint_findings, linters_run=linters_run,
                file_conflicts=[], auto_resolved_files=[],
                manual_conflict_files=[], suggested_resolution_order=[],
                notes=notes + [f"Clean merge produced commit on top of {base}."],
                worktree_path=str(wt) if keep_worktree else None,
                qa_verdict=qa_payload,
            )

        # Conflict path
        file_conflicts: list[FileConflict] = []
        auto_resolved: list[str] = []
        manual_conflict: list[str] = []

        for f in conflicted:
            wt_file = wt / f
            types = git_path_conflict_type(wt, f)
            blocks = parse_conflicted_file(wt_file)
            for b in blocks:
                classify_block(b, types["both_added"], types["ours_deleted"],
                               types["theirs_deleted"])
            # Attempt auto-resolution
            fully_trivial = all(b.classification != "real" for b in blocks) and blocks
            if fully_trivial:
                apply_auto_resolution(wt_file, blocks)
                # Stage the auto-resolved file
                git(wt, "add", "--", f, check=False)
                auto_resolved.append(f)
                file_conflicts.append(FileConflict(
                    file=f, blocks=blocks,
                    classification="auto-resolvable", auto_resolved=True,
                ))
            else:
                manual_conflict.append(f)
                file_conflicts.append(FileConflict(
                    file=f, blocks=blocks,
                    classification="manual-conflict", auto_resolved=False,
                ))

        # If everything was auto-resolved, finalize the merge commit; otherwise abort.
        if not manual_conflict:
            git(wt, "commit", "--no-edit", "-q", check=False)
            verdict = "trivial-auto-merge"
            notes.append("All conflicts auto-resolved; merge commit created.")
        else:
            abort_merge(wt)
            verdict = "real-conflict"
            notes.append("Manual conflicts present; merge aborted, worktree reverted to "
                         f"clean {base} state.")

        order = resolution_order(repo, manual_conflict or auto_resolved, feature, base)

        return Report(
            verdict=verdict,
            feature_branch=feature, base_branch=base, repo=str(repo),
            merge_base=merge_base, whitespace_warnings=[],
            lint_findings=[], linters_run=[],
            file_conflicts=file_conflicts,
            auto_resolved_files=auto_resolved,
            manual_conflict_files=manual_conflict,
            suggested_resolution_order=order,
            notes=notes,
            worktree_path=str(wt) if keep_worktree else None,
        )
    finally:
        if wt is not None and not keep_worktree:
            remove_worktree(repo, wt)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--repo", required=True, help="Path to the git repo to review.")
    ap.add_argument("--feature", required=True, help="Feature branch to merge.")
    ap.add_argument("--base", default="master", help="Base branch (default: master).")
    ap.add_argument("--worktree-root", default=None,
                    help="Where to create the temp worktree (default: tempdir).")
    ap.add_argument("--keep-worktree", action="store_true",
                    help="Keep the temp worktree after review (for debugging).")
    ap.add_argument("--report", default=None,
                    help="Write the JSON report to this path.")
    ap.add_argument("--print-report", action="store_true",
                    help="Print the JSON report to stdout.")
    ap.add_argument("--card-body-file", default=None,
                    help="Path to the card body to feed the QA gate. "
                         "Equivalent to writing <worktree>/.card-body before review.")
    args = ap.parse_args(argv)

    repo = Path(args.repo).resolve()
    if not (repo / ".git").exists():
        print(f"error: {repo} is not a git repo", file=sys.stderr)
        return 3

    try:
        if args.card_body_file:
            # Surface the card body to the QA gate via env var so it doesn't
            # have to be written into a tempdir beforehand.
            cb = Path(args.card_body_file).read_text(encoding="utf-8", errors="replace")
            os.environ["CHOREHERO_CARD_BODY"] = cb
        r_obj = review(
            repo=repo,
            feature=args.feature,
            base=args.base,
            worktree_root=Path(args.worktree_root).resolve() if args.worktree_root else None,
            keep_worktree=args.keep_worktree,
        )
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3

    payload = json.dumps(r_obj.to_dict(), indent=2)
    if args.report:
        Path(args.report).write_text(payload, encoding="utf-8")
    if args.print_report or not args.report:
        print(payload)

    if r_obj.verdict == "clean-merge":
        return 0
    if r_obj.verdict == "trivial-auto-merge":
        return 2
    if r_obj.verdict == "real-conflict":
        return 1
    if r_obj.verdict == "qa-fail":
        # QA gate flagged an issue after a clean merge — same exit code as
        # real-conflict (the agent must look at it before shipping).
        return 1
    return 3


if __name__ == "__main__":
    sys.exit(main())