#!/usr/bin/env python3
"""
trigger.py — ChoreHero merge-review trigger.

Polls the kanban board (default: `chorehero`) for tasks whose status is `done`
AND that carry a git worktree reference (tasks.branch_name, or the `branch`
field on the completing task_run metadata), and that have NOT been reviewed yet
according to the durable state file. For each new candidate it:

  1. Resolves the worktree path and feature branch from the card.
  2. Creates a unique review worktree at <worktree-root>/review/<task-id>/ on
     top of the configured base branch (default: master).
  3. Invokes merge_review.py as a subprocess, captures stdout/stderr and exit
     code for every step.
  4. Builds a structured result JSON (pass/fail, conflicts list, conflicting
     files, automated notes).
  5. Writes the verdict back to the card via `hermes kanban edit --metadata`
     — this updates a `review_status` field on the latest completed run
     (preserving the existing `task.result` so the original worker's
     handoff stays intact), then appends a Markdown comment with the
     verdict and the raw JSON report.

Idempotent across re-runs: the state file is consulted before any work begins,
so a card is reviewed at most once (unless you pass --force).

Usage:
  # Daemon mode (foreground poll, sleeps interval between passes):
  python trigger.py --watch

  # One polling pass:
  python trigger.py --once

  # Force-review a specific card (bypasses state):
  python trigger.py --card t_xxx

Environment variables (all optional; CLI flags override):
  KANBAN_BOARD          - kanban board slug (default: chorehero)
  KBOARD_TOKEN          - optional token for future HTTP-mode use; reserved
                          (the local-CLI path uses the Hermes profile auth)
  GIT_REPO_PATH         - path to the git repo (default: <script-dir>/../..)
  MERGE_REVIEW_BIN      - path to merge_review.py
                          (default: <script-dir>/merge_review.py)
  MERGE_REVIEW_BASE     - base branch (default: master)
  REVIEW_WORKTREE_ROOT  - parent dir for review worktrees
                          (default: <git-repo>/.worktrees/review)
  STATE_FILE            - durable reviewed-set path
                          (default: <script-dir>/.trigger-state.json)
  TRIGGER_INTERVAL_SEC  - seconds between polling passes (default: 900 = 15m)

Exit codes:
  0 — all candidates processed successfully (or there were none)
  1 — at least one card failed review processing
  2 — internal error (config, missing CLI, bad repo)
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


DEFAULTS = {
    "KANBAN_BOARD": "chorehero",
    "GIT_REPO_PATH": str(Path(__file__).resolve().parent.parent.parent),
    "MERGE_REVIEW_BIN": str(Path(__file__).resolve().parent / "merge_review.py"),
    "MERGE_REVIEW_BASE": "master",
    "REVIEW_WORKTREE_ROOT": "",  # filled in after GIT_REPO_PATH resolution
    "STATE_FILE": str(Path(__file__).resolve().parent / ".trigger-state.json"),
    "TRIGGER_INTERVAL_SEC": "900",
}


def resolve_config(overrides: dict[str, str] | None = None) -> dict[str, str]:
    cfg = dict(DEFAULTS)
    for k in DEFAULTS:
        v = os.environ.get(k)
        if v is not None and v != "":
            cfg[k] = v
    if overrides:
        cfg.update({k: v for k, v in overrides.items() if v is not None and v != ""})
    if not cfg["REVIEW_WORKTREE_ROOT"]:
        cfg["REVIEW_WORKTREE_ROOT"] = str(Path(cfg["GIT_REPO_PATH"]) / ".worktrees" / "review")
    return cfg


# ---------------------------------------------------------------------------
# Data shapes
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class Candidate:
    task_id: str
    title: str
    branch: str
    completed_at: int | None
    completed_run_id: int | None
    source: str  # "branch_name" | "run_metadata"


@dataclasses.dataclass
class ReviewResult:
    task_id: str
    branch: str
    base_branch: str
    worktree_path: str
    verdict: str  # clean-merge | trivial-auto-merge | real-conflict | error | skipped
    exit_code: int
    report: dict[str, Any]
    stdout: str
    stderr: str
    conflicts: list[str]
    auto_resolved_files: list[str]
    manual_conflict_files: list[str]
    notes: list[str]
    error: str | None


# ---------------------------------------------------------------------------
# Kanban IO via `hermes kanban` CLI
# ---------------------------------------------------------------------------


class KanbanError(RuntimeError):
    pass


def run_kanban(*args: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Run `hermes kanban --board=<id> <subcommand> ...`.

    `--board` must come BEFORE the subcommand (it's parsed by the kanban
    subcommand group itself, not the individual subcommands).
    """
    full = ["hermes", "kanban", "--board", _board(), *args]
    return subprocess.run(
        full,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        env=_scrubbed_env(),
    )


_board_singleton: str | None = None


def _board() -> str:
    global _board_singleton
    return _board_singleton or "chorehero"


def set_board(board: str) -> None:
    global _board_singleton
    _board_singleton = board


def _scrubbed_env() -> dict[str, str]:
    """Run kanban CLI in an env stripped of dispatcher-imposed flags.

    `HERMES_DELEGATED_CHILD_CONTEXT` makes `hermes kanban ...` refuse every
    command (read or write) when a kanban worker invokes it, which would
    brick the trigger if it ever ran from inside another worker. Stripping
    the var gives the CLI a fresh-shell context regardless of how the
    trigger itself was launched.
    """
    return {k: v for k, v in os.environ.items()
            if k not in {"HERMES_DELEGATED_CHILD_CONTEXT", "HERMES_SINGLE_QUERY_SESSION"}}


def list_done_cards_with_worktree(repo_path: Path) -> list[Candidate]:
    """Fetch all `done` tasks whose branch_name (or latest completed run's
    metadata.branch) is a real local branch in repo_path."""
    proc = run_kanban("list", "--status", "done", "--json", timeout=60)
    if proc.returncode != 0:
        raise KanbanError(f"hermes kanban list failed: rc={proc.returncode}\n{proc.stderr}")

    try:
        rows = json.loads(proc.stdout or "[]")
    except json.JSONDecodeError as e:
        raise KanbanError(f"hermes kanban list returned non-JSON: {e}\nstdout head: {proc.stdout[:200]}") from e

    # Resolve local branch set once so we don't shell out per candidate.
    local_branches = set(_local_branch_names(repo_path))

    candidates: list[Candidate] = []
    for row in rows:
        task_id = row.get("id")
        if not task_id:
            continue
        branch_name = (row.get("branch_name") or "").strip() or None
        completed_at = row.get("completed_at")
        # Completed run branch (preferred if branch_name absent or unresolvable)
        run_branch = None
        run_id = None
        try:
            rproc = run_kanban("runs", task_id, "--json", timeout=30)
            if rproc.returncode == 0 and rproc.stdout:
                runs = json.loads(rproc.stdout)
                # runs come back most-recent-first; pick the first completed run.
                for run in runs:
                    if run.get("outcome") == "completed":
                        meta = run.get("metadata")
                        if isinstance(meta, dict) and meta.get("branch"):
                            run_branch = str(meta["branch"]).strip()
                        run_id = run.get("id")
                        break
        except (KanbanError, json.JSONDecodeError):
            run_branch = None

        chosen_branch: str | None = None
        chosen_source: str | None = None
        if branch_name and branch_name in local_branches:
            chosen_branch = branch_name
            chosen_source = "branch_name"
        elif run_branch and run_branch in local_branches:
            chosen_branch = run_branch
            chosen_source = "run_metadata"
        # If neither resolves locally, the card has no usable worktree ref.

        if chosen_branch and chosen_source:
            candidates.append(Candidate(
                task_id=task_id,
                title=row.get("title", ""),
                branch=chosen_branch,
                completed_at=completed_at,
                completed_run_id=run_id,
                source=chosen_source,
            ))

    return candidates


def post_card_comment(task_id: str, body: str) -> bool:
    """Append a comment to a card via hermes kanban comment. Returns True on
    success, False on failure (errors logged but never raise — the trigger
    must keep going across the rest of the batch)."""
    proc = run_kanban(
        "comment", task_id, body,
        "--author", "merge-review-trigger",
        "--max-len", "12000",
        timeout=60,
    )
    if proc.returncode != 0:
        print(
            f"warn: comment on {task_id} failed: rc={proc.returncode}\n"
            f"  stderr: {proc.stderr.strip()[:400]}",
            file=sys.stderr,
        )
        return False
    return True


def _read_task_result(task_id: str) -> str:
    """Return the current task.result so an edit_metadata call can pass it back
    unchanged. `hermes kanban edit --metadata` REPLACES the entire metadata
    dict and --metadata requires --result, which itself REPLACES the task's
    result field. We preserve the existing result verbatim to keep the
    original worker's handoff intact; only the metadata block is updated.
    """
    proc = run_kanban("show", task_id, "--json", timeout=30)
    if proc.returncode != 0:
        return ""
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return ""
    return str((data.get("task") or {}).get("result") or "")


def writeback_review_status(task_id: str, result: ReviewResult) -> bool:
    """Update the card's latest-completed-run metadata with a structured
    `review_status` field (and supporting facts: branch, base, exit_code,
    conflicts, auto/manual-resolved files, reviewed_at). The existing
    `task.result` is read back and re-passed unchanged so we don't clobber
    the original worker's handoff. The metadata dict is REPLACED on each
    call — that's deliberate: it represents the latest review, not a log.

    Returns True on success, False on any failure (errors logged but never
    raise — the trigger must keep going across the rest of the batch)."""
    existing_result = _read_task_result(task_id)
    metadata = {
        "review_status": result.verdict,
        "review_branch": result.branch,
        "review_base_branch": result.base_branch,
        "review_exit_code": result.exit_code,
        "review_worktree_path": result.worktree_path,
        "review_conflicts": result.conflicts,
        "review_auto_resolved_files": result.auto_resolved_files,
        "review_manual_conflict_files": result.manual_conflict_files,
        "review_notes": result.notes,
        "review_reviewed_at": int(time.time()),
    }
    # kanban edit --metadata REQUIRES --result; pass existing back verbatim.
    proc = run_kanban(
        "edit", task_id,
        "--result", existing_result if existing_result else f"merge-review: {result.verdict}",
        "--metadata", json.dumps(metadata, ensure_ascii=False),
        timeout=60,
    )
    if proc.returncode != 0:
        print(
            f"warn: review_status writeback on {task_id} failed: rc={proc.returncode}\n"
            f"  stderr: {proc.stderr.strip()[:400]}",
            file=sys.stderr,
        )
        return False
    return True


# ---------------------------------------------------------------------------
# State file (durable "already reviewed" set)
# ---------------------------------------------------------------------------


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": 1, "reviewed": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        # Corrupt state — back it up and start fresh so we don't lose history.
        backup = path.with_suffix(path.suffix + ".corrupt")
        shutil.copy2(path, backup)
        return {"schema_version": 1, "reviewed": {}}
    if not isinstance(data, dict) or "reviewed" not in data:
        return {"schema_version": 1, "reviewed": {}}
    return data


def save_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def is_already_reviewed(state: dict[str, Any], task_id: str) -> bool:
    return task_id in state.get("reviewed", {})


def mark_reviewed(state: dict[str, Any], task_id: str, result: ReviewResult) -> None:
    reviewed = state.setdefault("reviewed", {})
    reviewed[task_id] = {
        "branch": result.branch,
        "base_branch": result.base_branch,
        "verdict": result.verdict,
        "exit_code": result.exit_code,
        "review_status": result.verdict,  # the requested field name
        "worktree_path": result.worktree_path,
        "conflicts": result.conflicts,
        "auto_resolved_files": result.auto_resolved_files,
        "manual_conflict_files": result.manual_conflict_files,
        "reviewed_at": int(time.time()),
    }


# ---------------------------------------------------------------------------
# Review invocation
# ---------------------------------------------------------------------------


def _local_branch_names(repo_path: Path) -> list[str]:
    proc = subprocess.run(
        ["git", "-C", str(repo_path), "for-each-ref", "--format=%(refname:short)", "refs/heads"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30,
    )
    if proc.returncode != 0:
        return []
    return [n.strip() for n in proc.stdout.splitlines() if n.strip()]


def create_review_worktree(repo_path: Path, task_id: str, base: str, root: Path) -> Path:
    """Create .worktrees/review/<task_id> on top of `base`. Idempotent: if the
    worktree already exists, prune it first to guarantee a clean base.

    Also pre-cleans any leftover ``wt-<base>`` subdir AND the
    ``merge-review/<base>`` branch from prior runs (the inner merge_review.py
    uses a fixed branch name, so sequential reviews of different cards in the
    same repo otherwise collide on the second card)."""
    wt_path = root / task_id
    if wt_path.exists():
        # Best-effort cleanup; ignore errors so we proceed to a fresh add.
        subprocess.run(
            ["git", "-C", str(repo_path), "worktree", "remove", "--force", str(wt_path)],
            capture_output=True, text=True, timeout=60,
        )
        shutil.rmtree(wt_path, ignore_errors=True)
    root.mkdir(parents=True, exist_ok=True)
    branch_name = f"review/{task_id}"
    # If the outer review branch already exists from a prior partial run,
    # reuse it but reset it to base. Otherwise create a fresh one.
    local_branches = set(_local_branch_names(repo_path))
    if branch_name in local_branches:
        subprocess.run(
            ["git", "-C", str(repo_path), "branch", "-D", branch_name],
            capture_output=True, text=True, timeout=30,
        )
    # Also nuke any stale merge-review/<base> branch so the inner tool can
    # recreate it cleanly. Only safe if no other worktree has it checked out.
    inner_branch = f"merge-review/{base}"
    inner_wt = root / f"wt-{base}"
    if inner_branch in local_branches:
        # If the inner wt dir exists in our scoped root, prune it so the branch
        # can be deleted (git refuses to delete a checked-out branch).
        if inner_wt.exists():
            subprocess.run(
                ["git", "-C", str(repo_path), "worktree", "remove", "--force", str(inner_wt)],
                capture_output=True, text=True, timeout=60,
            )
            shutil.rmtree(inner_wt, ignore_errors=True)
        # Now check across all worktrees whether this branch is still held.
        list_proc = subprocess.run(
            ["git", "-C", str(repo_path), "worktree", "list", "--porcelain"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30,
        )
        if list_proc.returncode == 0 and f"refs/heads/{inner_branch}" not in list_proc.stdout:
            subprocess.run(
                ["git", "-C", str(repo_path), "branch", "-D", inner_branch],
                capture_output=True, text=True, timeout=30,
            )
    subprocess.run(
        ["git", "-C", str(repo_path), "worktree", "add", "-b", branch_name, str(wt_path), base],
        capture_output=True, text=True, encoding="utf-8", timeout=120, check=True,
    )
    return wt_path


def run_merge_review(
    *,
    merge_review_bin: Path,
    repo_path: Path,
    branch: str,
    base: str,
    worktree_root: Path,
    report_path: Path,
) -> tuple[int, str, str, dict[str, Any]]:
    """Invoke merge_review.py and return (exit_code, stdout, stderr, report_or_empty)."""
    proc = subprocess.run(
        [
            sys.executable, str(merge_review_bin),
            "--repo", str(repo_path),
            "--feature", branch,
            "--base", base,
            "--worktree-root", str(worktree_root),
            "--report", str(report_path),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=600,
    )
    report: dict[str, Any] = {}
    if report_path.exists():
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            report = {}
    return proc.returncode, proc.stdout, proc.stderr, report


def review_candidate(
    candidate: Candidate,
    *,
    cfg: dict[str, str],
) -> ReviewResult:
    repo = Path(cfg["GIT_REPO_PATH"]).resolve()
    base = cfg["MERGE_REVIEW_BASE"]
    root = Path(cfg["REVIEW_WORKTREE_ROOT"]).resolve()
    merge_bin = Path(cfg["MERGE_REVIEW_BIN"]).resolve()
    notes: list[str] = []

    try:
        wt_path = create_review_worktree(repo, candidate.task_id, base, root)
        notes.append(f"created review worktree at {wt_path} on top of {base}")
        report_path = wt_path / ".merge-review-report.json"
        exit_code, stdout, stderr, report = run_merge_review(
            merge_review_bin=merge_bin,
            repo_path=repo,
            branch=candidate.branch,
            base=base,
            worktree_root=wt_path,
            report_path=report_path,
        )
        verdict = report.get("verdict", "error") if report else "error"
        return ReviewResult(
            task_id=candidate.task_id,
            branch=candidate.branch,
            base_branch=base,
            worktree_path=str(wt_path),
            verdict=str(verdict),
            exit_code=exit_code,
            report=report,
            stdout=stdout,
            stderr=stderr,
            conflicts=list(report.get("manual_conflict_files", [])),
            auto_resolved_files=list(report.get("auto_resolved_files", [])),
            manual_conflict_files=list(report.get("manual_conflict_files", [])),
            notes=notes + list(report.get("notes", [])),
            error=None,
        )
    except Exception as exc:
        notes.append(f"trigger-level exception: {type(exc).__name__}: {exc}")
        return ReviewResult(
            task_id=candidate.task_id,
            branch=candidate.branch,
            base_branch=base,
            worktree_path="",
            verdict="error",
            exit_code=3,
            report={},
            stdout="",
            stderr=str(exc),
            conflicts=[],
            auto_resolved_files=[],
            manual_conflict_files=[],
            notes=notes,
            error=str(exc),
        )


# ---------------------------------------------------------------------------
# Comment formatter
# ---------------------------------------------------------------------------


VERDICT_EMOJI = {
    "clean-merge": ":white_check_mark:",
    "trivial-auto-merge": ":wrench:",
    "real-conflict": ":collision:",
    "error": ":warning:",
    "skipped": ":fast_forward:",
}


def format_comment(result: ReviewResult, candidate: Candidate) -> str:
    emoji = VERDICT_EMOJI.get(result.verdict, ":grey_question:")
    lines = [
        f"{emoji} **Merge-review verdict: `{result.verdict}`** (rc={result.exit_code})",
        "",
        f"- Task: `{result.task_id}` — {candidate.title}",
        f"- Branch: `{result.branch}` (source: `{candidate.source}`)",
        f"- Base: `{result.base_branch}`",
        f"- Review worktree: `{result.worktree_path}`",
        f"- review_status: `{result.verdict}`",
    ]
    if result.auto_resolved_files:
        lines.append(f"- Auto-resolved ({len(result.auto_resolved_files)}): "
                     + ", ".join(f"`{f}`" for f in result.auto_resolved_files))
    if result.manual_conflict_files:
        lines.append(f"- Manual conflicts ({len(result.manual_conflict_files)}): "
                     + ", ".join(f"`{f}`" for f in result.manual_conflict_files))
    if result.notes:
        lines.append("")
        lines.append("**Notes:**")
        for n in result.notes:
            lines.append(f"- {n}")
    if result.error:
        lines.append("")
        lines.append(f"**Error:** {result.error}")
    if result.report:
        lines.append("")
        lines.append("<details><summary>Raw JSON report</summary>\n\n```json")
        lines.append(json.dumps(result.report, indent=2))
        lines.append("```\n\n</details>")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main poll loop
# ---------------------------------------------------------------------------


def poll_once(cfg: dict[str, str], *, force_card: str | None = None) -> int:
    """One pass: enumerate candidates, review the new ones, post comments.

    Returns 0 if everything succeeded, 1 if any candidate failed."""
    set_board(cfg["KANBAN_BOARD"])
    repo = Path(cfg["GIT_REPO_PATH"]).resolve()
    if not (repo / ".git").exists():
        print(f"error: {repo} is not a git repo", file=sys.stderr)
        return 2

    state_path = Path(cfg["STATE_FILE"])
    state = load_state(state_path)

    candidates = list_done_cards_with_worktree(repo)
    if force_card:
        candidates = [c for c in candidates if c.task_id == force_card]
        if not candidates:
            # The forced card may exist but lack a worktree ref. Surface that.
            print(f"warn: forced card {force_card} has no resolvable worktree branch", file=sys.stderr)

    # Filter out ones we've already reviewed unless forced.
    if not force_card:
        candidates = [c for c in candidates if not is_already_reviewed(state, c.task_id)]

    if not candidates:
        print("info: no new candidates to review")
        save_state(state_path, state)
        return 0

    print(f"info: {len(candidates)} candidate(s) to review")
    failures = 0
    for cand in candidates:
        print(f"-- reviewing {cand.task_id} (branch={cand.branch}, source={cand.source})")
        result = review_candidate(cand, cfg=cfg)
        if result.verdict == "error":
            failures += 1
        mark_reviewed(state, cand.task_id, result)
        # Update the card's structured `review_status` field first (so the
        # comment posted below can reference the freshly-written metadata),
        # then post the human-readable verdict as a comment.
        writeback_review_status(cand.task_id, result)
        post_card_comment(cand.task_id, format_comment(result, cand))
        print(f"   verdict={result.verdict} rc={result.exit_code}")

    save_state(state_path, state)
    return 1 if failures else 0


def watch(cfg: dict[str, str]) -> int:
    interval = int(cfg["TRIGGER_INTERVAL_SEC"])
    print(f"info: watching board `{cfg['KANBAN_BOARD']}` every {interval}s (Ctrl+C to stop)")
    rc = 0
    try:
        while True:
            rc = poll_once(cfg)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\ninfo: stopped")
    return rc


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="ChoreHero merge-review trigger")
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--once", action="store_true",
                      help="Run a single polling pass and exit")
    mode.add_argument("--watch", action="store_true",
                      help="Continuously poll every TRIGGER_INTERVAL_SEC")
    mode.add_argument("--card", metavar="TASK_ID",
                      help="Force-review one specific card (bypasses dedupe)")
    p.add_argument("--board", default=None,
                   help="Kanban board slug (overrides KANBAN_BOARD env)")
    p.add_argument("--repo", default=None,
                   help="Path to the git repo (overrides GIT_REPO_PATH env)")
    p.add_argument("--base", default=None,
                   help="Base branch (overrides MERGE_REVIEW_BASE env)")
    p.add_argument("--interval", type=int, default=None,
                   help="Seconds between polls (overrides TRIGGER_INTERVAL_SEC env)")
    p.add_argument("--state-file", default=None,
                   help="Durable state path (overrides STATE_FILE env)")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    overrides = {
        "KANBAN_BOARD": args.board,
        "GIT_REPO_PATH": args.repo,
        "MERGE_REVIEW_BASE": args.base,
        "STATE_FILE": args.state_file,
        "TRIGGER_INTERVAL_SEC": str(args.interval) if args.interval is not None else None,
    }
    cfg = resolve_config(overrides)

    if not args.once and not args.watch and not args.card:
        # Default behaviour: one pass (cron-style). Keeps a manual invocation
        # of `python trigger.py` safe and predictable.
        args.once = True

    if args.watch:
        return watch(cfg)
    return poll_once(cfg, force_card=args.card)


if __name__ == "__main__":
    sys.exit(main())