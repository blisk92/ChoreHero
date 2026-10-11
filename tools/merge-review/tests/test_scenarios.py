#!/usr/bin/env python3
"""
test_scenarios.py — run merge_review.py against the three fixture repos and
assert that each produces its documented verdict.

Usage:
  python test_scenarios.py              # builds fixtures in a tmp dir, then runs
  python test_scenarios.py --keep       # keep fixtures on disk for inspection
  python test_scenarios.py --fixtures <existing-root>
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUNNER = ROOT.parent / "merge_review.py"
BUILD = ROOT / "build_fixtures.py"


# (fixture-name, expected-verdict, expected-feature-branch, expected-base)
EXPECTED = [
    ("clean-merge",        "clean-merge",        "feature/add-greeting",    "master"),
    ("trivial-auto-merge", "trivial-auto-merge", "feature/remove-legacy",  "master"),
    ("real-conflict",      "real-conflict",      "feature/edit-line-three", "master"),
]


def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None,
                          capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def build_fixtures(out: Path) -> Path:
    proc = run([sys.executable, str(BUILD), "--out", str(out)])
    if proc.returncode != 0:
        raise RuntimeError(f"build_fixtures failed: {proc.stderr}")
    return out


def invoke_runner(repo: Path, feature: str, base: str, tmp_root: Path) -> tuple[int, dict]:
    report_path = tmp_root / f"{repo.name}-report.json"
    proc = run([
        sys.executable, str(RUNNER),
        "--repo", str(repo),
        "--feature", feature,
        "--base", base,
        "--worktree-root", str(tmp_root / repo.name),
        "--report", str(report_path),
    ])
    report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else {}
    return proc.returncode, report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--fixtures", default=None,
                    help="Path to existing fixture root (skips rebuild).")
    ap.add_argument("--keep", action="store_true",
                    help="Keep fixtures and worktrees after running.")
    args = ap.parse_args(argv)

    if args.fixtures:
        fx_root = Path(args.fixtures).resolve()
        if not fx_root.exists():
            print(f"error: fixtures root {fx_root} does not exist", file=sys.stderr)
            return 2
        cleanup_fixtures = False
    else:
        fx_root = build_fixtures(Path(tempfile.mkdtemp(prefix="chorehero-test-")))
        cleanup_fixtures = not args.keep

    worktree_root = Path(tempfile.mkdtemp(prefix="chorehero-test-wt-"))
    if not args.keep:
        # Schedule cleanup of worktrees at exit
        import atexit
        atexit.register(lambda: shutil.rmtree(worktree_root, ignore_errors=True))

    failures: list[str] = []
    for name, expected_verdict, feature, base in EXPECTED:
        repo = fx_root / name
        rc, report = invoke_runner(repo, feature, base, worktree_root)
        verdict = report.get("verdict", "<missing>")
        manual = report.get("manual_conflict_files", [])
        auto = report.get("auto_resolved_files", [])
        ok = (verdict == expected_verdict)
        marker = "PASS" if ok else "FAIL"
        print(f"[{marker}] {name}: rc={rc} verdict={verdict} "
              f"manual={manual} auto={auto}", file=sys.stderr)
        if not ok:
            failures.append(f"{name}: expected verdict {expected_verdict!r}, got {verdict!r}")
            print(json.dumps(report, indent=2), file=sys.stderr)

    # Specific assertions per scenario
    clean_repo = fx_root / "clean-merge"
    rc, clean_report = invoke_runner(clean_repo, "feature/add-greeting", "master", worktree_root)
    assert clean_report["verdict"] == "clean-merge", \
        f"clean-merge verdict: {clean_report['verdict']}"
    assert clean_report["manual_conflict_files"] == []
    assert clean_report["auto_resolved_files"] == []

    trivial_repo = fx_root / "trivial-auto-merge"
    rc, trivial_report = invoke_runner(trivial_repo, "feature/remove-legacy", "master",
                                       worktree_root)
    assert trivial_report["verdict"] == "trivial-auto-merge", \
        f"trivial-auto-merge verdict: {trivial_report['verdict']}"
    assert trivial_report["manual_conflict_files"] == []
    assert len(trivial_report["auto_resolved_files"]) >= 1

    real_repo = fx_root / "real-conflict"
    rc, real_report = invoke_runner(real_repo, "feature/edit-line-three", "master",
                                    worktree_root)
    assert real_report["verdict"] == "real-conflict", \
        f"real-conflict verdict: {real_report['verdict']}"
    assert len(real_report["manual_conflict_files"]) >= 1
    assert "shared.txt" in real_report["manual_conflict_files"]
    # Resolution order must be present (even if trivial for one-file conflicts)
    assert "suggested_resolution_order" in real_report

    if cleanup_fixtures:
        shutil.rmtree(fx_root, ignore_errors=True)

    if failures:
        print(f"\n{len(failures)} scenario(s) failed:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print("\nAll three scenarios produced the documented verdict.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())