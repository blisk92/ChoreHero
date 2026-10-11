#!/usr/bin/env python3
"""
build_fixtures.py — generate three throwaway fixture git repos for the
merge-review runner:

  clean-merge          — feature only adds a new file (no conflicts)
  trivial-auto-merge   — base adds A, feature adds B (pure add/add)
  real-conflict        — both branches modify the same line of the same file

Each fixture is a self-contained git repo. master is the base, feature is the
branch the runner will try to merge.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        check=check,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def init_repo(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    git(root, "init", "-q", "--initial-branch=master")
    git(root, "config", "user.email", "merge-review@example.com")
    git(root, "config", "user.name", "merge-review")
    git(root, "config", "commit.gpgsign", "false")


def commit(root: Path, msg: str) -> None:
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", msg)


def build_clean_merge(root: Path) -> None:
    init_repo(root)
    (root / "README.md").write_text("# clean-merge fixture\n", encoding="utf-8")
    commit(root, "initial commit")
    git(root, "checkout", "-q", "-b", "feature/add-greeting")
    (root / "greeting.txt").write_text("hello from feature branch\n", encoding="utf-8")
    commit(root, "feature: add greeting file")


def build_trivial_auto_merge(root: Path) -> None:
    """Trivial delete/modify conflict.

    Base file has a legacy block. feature branch deletes the legacy block.
    master branch modifies a comment in the legacy block. Git reports a
    conflict because the modify hunk references lines that were deleted.
    The runner can safely resolve by preferring the modification (the
    delete is itself a "take theirs" choice that the runner applies).
    """
    init_repo(root)
    (root / "config.py").write_text(
        "DEBUG = False\n"
        "# legacy block\n"
        "LEGACY_FLAG = True\n"
        "OTHER = 1\n",
        encoding="utf-8",
    )
    commit(root, "initial commit")
    git(root, "checkout", "-q", "-b", "feature/remove-legacy")
    (root / "config.py").write_text(
        "DEBUG = False\n"
        "OTHER = 1\n",
        encoding="utf-8",
    )
    commit(root, "feature: remove legacy block")
    git(root, "checkout", "-q", "master")
    (root / "config.py").write_text(
        "DEBUG = False\n"
        "# legacy block\n"
        "LEGACY_FLAG = True  # updated comment\n"
        "OTHER = 1\n",
        encoding="utf-8",
    )
    commit(root, "master: update comment in legacy block")


def build_real_conflict(root: Path) -> None:
    init_repo(root)
    (root / "shared.txt").write_text(
        "line one\nline two\nline three\nline four\n", encoding="utf-8"
    )
    commit(root, "initial commit")
    git(root, "checkout", "-q", "-b", "feature/edit-line-three")
    (root / "shared.txt").write_text(
        "line one\nline two\nfeature version of line three\nline four\n",
        encoding="utf-8",
    )
    commit(root, "feature: edit line three")
    git(root, "checkout", "-q", "master")
    (root / "shared.txt").write_text(
        "line one\nline two\nmaster version of line three\nline four\n",
        encoding="utf-8",
    )
    commit(root, "master: edit line three")


FIXTURES = {
    "clean-merge": build_clean_merge,
    "trivial-auto-merge": build_trivial_auto_merge,
    "real-conflict": build_real_conflict,
}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--out", default=None,
                    help="Output root (default: a new tmp dir).")
    args = ap.parse_args(argv)

    out_root = Path(args.out) if args.out else Path(tempfile.mkdtemp(prefix="chorehero-fixtures-"))
    out_root.mkdir(parents=True, exist_ok=True)

    for name, builder in FIXTURES.items():
        builder(out_root / name)
        print(f"built {out_root / name}", file=sys.stderr)

    print(str(out_root))
    return 0


if __name__ == "__main__":
    sys.exit(main())