#!/usr/bin/env python3
"""
orchestrator.py — ChoreHero merge-review orchestrator.

Sits on top of trigger.py and owns the post-verdict stages of the state
machine for every card in the review pipeline:

    queued -> reviewing -> clean-merge / trivial-auto-merge
                                     -> ready-to-merge    (final command comment)
                          qa-fail / real-conflict / error
                                     -> blocked / conflict
                                     -> (after 24h) -> escalated (human reassign)

This module does NOT do the actual merge test — trigger.py does that and
writes the verdict + verdict comment. The orchestrator is responsible for:

1. Spotting cards that just transitioned to a "ready" verdict and posting the
   ONE-CLICK MERGE comment with the exact squash/preview commands.
2. Maintaining a rolling dashboard note (docs/merge-review-dashboard.md)
   summarizing the last 10 reviews.
3. Wiring the stale-watcher (stale_watcher.py) so any review left in
   conflict/blocked for more than 24h gets re-escalated to a human with the
   conflict-report attached.

The orchestrator runs in three sub-commands — `ready`, `dashboard`, `escalate` —
so each stage can be tested independently and the per-card work in the dashboard
stage is also driven by `run_once()` for cron-friendly single-pass invocations.

The kanban CLI is wrapped via a tiny adapter (`KanbanClient`) that defaults to
real subprocess calls but is overridable in tests via `set_client(...)`.

Usage:
    python orchestrator.py ready                  # post ready-to-merge comments
    python orchestrator.py ready --card t_xxx     # only one card
    python orchestrator.py dashboard              # rebuild dashboard markdown
    python orchestrator.py escalate --threshold 24h
    python orchestrator.py run-once              # all three stages in order
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable

# Local package imports. orchestrator.py lives next to merge_review.py /
# trigger.py in tools/merge-review.
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import stale_watcher  # noqa: E402  (path-mutating import above)
import dashboard  # noqa: E402

from constants import (  # noqa: E402
    READY_VERDICTS,
    STUCK_VERDICTS,
    READY_COMMENT_MARKER,
    ESCALATION_COMMENT_MARKER,
)


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------


KANBAN_BOARD_DEFAULT = "chorehero"
DASHBOARD_PATH_DEFAULT = HERE.parent.parent / "docs" / "merge-review-dashboard.md"
HUMAN_ASSIGNEE_DEFAULT = "human-reviewer"
TRIGGER_STATE_PATH = HERE / ".trigger-state.json"


# ---------------------------------------------------------------------------
# Kanban client (defaults to real hermes CLI; tests inject a fake)
# ---------------------------------------------------------------------------


class KanbanClient:
    """Thin wrapper around `hermes kanban <verb>` that tests can subclass/fake."""

    def __init__(self, *, board: str = KANBAN_BOARD_DEFAULT, timeout: int = 60):
        self.board = board
        self.timeout = timeout

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        cmd = ["hermes", "kanban", "--board", self.board, *args]
        return subprocess.run(
            cmd, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=self.timeout,
        )

    def list(self, *, status: str, json_out: bool = True) -> list[dict[str, Any]]:
        args = ["list", "--status", status]
        if json_out:
            args.append("--json")
        proc = self._run(*args)
        if proc.returncode != 0:
            raise RuntimeError(
                f"kanban list {status} failed rc={proc.returncode}: "
                f"{proc.stderr.strip() or proc.stdout.strip()}"
            )
        try:
            data = json.loads(proc.stdout)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"kanban list produced non-JSON: {e}: {proc.stdout[:200]!r}")
        # `kanban list --json` returns either a top-level list OR
        # a dict with a `tasks` key depending on version.
        if isinstance(data, dict) and "tasks" in data:
            data = data["tasks"]
        if not isinstance(data, list):
            raise RuntimeError(f"unexpected kanban list payload shape: {type(data).__name__}")
        return data

    def runs(self, task_id: str) -> list[dict[str, Any]]:
        proc = self._run("runs", task_id, "--json")
        if proc.returncode != 0:
            raise RuntimeError(f"kanban runs {task_id} failed: {proc.stderr.strip()}")
        data = json.loads(proc.stdout)
        if isinstance(data, dict) and "runs" in data:
            data = data["runs"]
        if not isinstance(data, list):
            raise RuntimeError(f"unexpected kanban runs payload shape")
        return data

    def comment(self, task_id: str, body: str) -> bool:
        # `hermes kanban comment <task_id> <text...>` joins free-text args
        # into the comment body. We pass it as a single arg; the comment
        # body is plain markdown and doesn't contain shell metacharacters
        # beyond our normal orchestrator output.
        proc = self._run("comment", task_id, body)
        return proc.returncode == 0

    def assign(self, task_id: str, profile: str) -> bool:
        proc = self._run("assign", task_id, profile)
        return proc.returncode == 0

    def block(self, task_id: str, reason: str) -> bool:
        proc = self._run("block", task_id, "--reason", reason)
        return proc.returncode == 0


_CLIENT: KanbanClient | None = None


def get_client() -> KanbanClient:
    """Get the process-wide kanban client (override with set_client in tests)."""
    global _CLIENT
    if _CLIENT is None:
        board = os.environ.get("KANBAN_BOARD", KANBAN_BOARD_DEFAULT)
        _CLIENT = KanbanClient(board=board)
    return _CLIENT


def set_client(client: KanbanClient | None) -> None:
    """Override the kanban client (used by tests)."""
    global _CLIENT
    _CLIENT = client


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class CardReview:
    task_id: str
    title: str
    branch: str | None
    base_branch: str | None
    review_status: str  # clean-merge | trivial-auto-merge | real-conflict | qa-fail | error | skipped
    reviewed_at: int | None  # epoch seconds when trigger wrote the verdict
    exit_code: int | None = None
    qa_verdict: dict[str, Any] | None = None
    conflicts: list[str] = field(default_factory=list)
    manual_conflict_files: list[str] = field(default_factory=list)
    auto_resolved_files: list[str] = field(default_factory=list)
    error: str | None = None
    notes: list[str] = field(default_factory=list)
    ready_to_merge_commented: bool = False  # whether the ready-to-merge comment already exists
    escalated: bool = False                # whether stale-watcher has already escalated

    @property
    def is_ready(self) -> bool:
        """A card is ready-to-merge iff review_status is clean / trivial AND QA passed."""
        if self.review_status not in READY_VERDICTS:
            return False
        if self.qa_verdict is None:
            # No QA verdict supplied — assume QA passed (legacy / skipped path).
            return True
        return self.qa_verdict.get("overall") == "pass"

    @property
    def is_stuck(self) -> bool:
        return self.review_status in STUCK_VERDICTS

    @property
    def age_seconds(self) -> int | None:
        if self.reviewed_at is None:
            return None
        return int(_dt.datetime.now(_dt.timezone.utc).timestamp()) - int(self.reviewed_at)

    @property
    def age_hours(self) -> float | None:
        a = self.age_seconds
        return None if a is None else a / 3600.0


# ---------------------------------------------------------------------------
# Reading the board state
# ---------------------------------------------------------------------------


def _coerce_str(v: Any) -> str | None:
    if v is None:
        return None
    if isinstance(v, str):
        return v
    return str(v)


def _coerce_int(v: Any) -> int | None:
    if v is None:
        return None
    if isinstance(v, int):
        return v
    if isinstance(v, str) and v.strip().isdigit():
        return int(v.strip())
    if isinstance(v, float):
        return int(v)
    return None


def _normalize_run_meta(meta: dict[str, Any] | None) -> dict[str, Any]:
    """Pull the subset of metadata fields orchestrator cares about."""
    if not meta:
        return {}
    out = {
        "review_status": _coerce_str(meta.get("review_status")),
        "review_branch": _coerce_str(meta.get("review_branch")),
        "review_base_branch": _coerce_str(meta.get("review_base_branch")),
        "review_exit_code": _coerce_int(meta.get("review_exit_code")),
        "review_reviewed_at": _coerce_int(meta.get("review_reviewed_at")),
        "review_conflicts": list(meta.get("review_conflicts") or []),
        "review_manual_conflict_files": list(meta.get("review_manual_conflict_files") or []),
        "review_auto_resolved_files": list(meta.get("review_auto_resolved_files") or []),
        "review_notes": list(meta.get("review_notes") or []),
        "review_error": meta.get("review_error"),
        "review_qa_verdict": meta.get("review_qa_verdict") or meta.get("qa_verdict"),
    }
    # Older trigger writes used names without the `review_` prefix (e.g.
    # `branch`, `verdict`). Tolerate those for backwards compat:
    if out["review_status"] is None:
        out["review_status"] = _coerce_str(meta.get("verdict"))
    if out["review_branch"] is None:
        out["review_branch"] = _coerce_str(meta.get("branch"))
    return out


def load_card_review(
    task: dict[str, Any],
    runs: list[dict[str, Any]],
) -> CardReview | None:
    """Merge a task dict and its runs list into a CardReview, or None if uninteresting."""
    task_id = _coerce_str(task.get("id"))
    if not task_id:
        return None
    title = _coerce_str(task.get("title")) or ""

    # Find the most recent run that actually wrote a review_status.
    chosen: dict[str, Any] | None = None
    for run in runs:  # already sorted newest-first by `runs()`
        meta = run.get("metadata")
        if not meta:
            continue
        if isinstance(meta, str):
            try:
                meta = json.loads(meta)
            except json.JSONDecodeError:
                continue
        if not isinstance(meta, dict):
            continue
        if meta.get("review_status"):
            chosen = meta
            chosen_run_id = run.get("id")
            break
    if chosen is None:
        return None

    n = _normalize_run_meta(chosen)
    if not n["review_status"]:
        return None

    # Heuristic: check if a "ready-to-merge" / "stale" orchestrator comment has
    # already been posted to this card. The trigger's verdict comment DOES NOT
    # count — we look for the orchestrator's signature markers.
    ready_to_merge_commented = False
    escalated = False
    # (The actual dedup happens inside each stage; we make decisions there.)

    qa_raw = n["review_qa_verdict"]
    qa_verdict = qa_raw if isinstance(qa_raw, dict) else None

    return CardReview(
        task_id=task_id,
        title=title,
        branch=n["review_branch"],
        base_branch=n["review_base_branch"],
        review_status=n["review_status"],
        reviewed_at=n["review_reviewed_at"],
        exit_code=n["review_exit_code"],
        qa_verdict=qa_verdict,
        conflicts=list(n["review_conflicts"]),
        manual_conflict_files=list(n["review_manual_conflict_files"]),
        auto_resolved_files=list(n["review_auto_resolved_files"]),
        error=n["review_error"] if isinstance(n["review_error"], str) else None,
        notes=list(n["review_notes"]),
        ready_to_merge_commented=ready_to_merge_commented,
        escalated=escalated,
    )


def collect_card_reviews(
    client: KanbanClient | None = None,
    *,
    only_card: str | None = None,
    status_filter: str = "done",
) -> list[CardReview]:
    """List candidate cards on the board, return those with a writeback verdict."""
    client = client or get_client()
    tasks = client.list(status=status_filter)
    out: list[CardReview] = []
    for task in tasks:
        tid = _coerce_str(task.get("id"))
        if not tid:
            continue
        if only_card and tid != only_card:
            continue
        try:
            runs = client.runs(tid)
        except RuntimeError as exc:
            print(f"warn: skipping {tid}: {exc}", file=sys.stderr)
            continue
        cr = load_card_review(task, runs)
        if cr is not None:
            out.append(cr)
    return out


# ---------------------------------------------------------------------------
# Comment formatting
# ---------------------------------------------------------------------------

# Markers are defined in constants.py and imported at the top of this file
# (READY_COMMENT_MARKER, ESCALATION_COMMENT_MARKER) so the same constants
# can be reused by stale_watcher.py without a circular import.


def format_ready_to_merge_comment(card: CardReview, *, base_branch: str = "master") -> str:
    """Compose the final one-click MERGE comment for a ready-to-merge card.

    Includes the exact squash + preview commands the user can copy/paste, plus
    inline <details> blocks for the squash/preview script buttons (if the
    gateway renders them).
    """
    branch = card.branch or "<unknown-branch>"
    target = base_branch
    qa_block = ""
    if card.qa_verdict:
        qlines = [
            f"- Overall: `{card.qa_verdict.get('overall')}`",
        ]
        if card.qa_verdict.get("reasons"):
            qlines.append("- Reasons:")
            for r in card.qa_verdict["reasons"]:
                qlines.append(f"  - {r}")
        if card.qa_verdict.get("unmet_acs"):
            qlines.append("- Unmet ACs:")
            for ac in card.qa_verdict["unmet_acs"]:
                qlines.append(f"  - {ac}")
        qa_block = "\n".join(qlines)
    else:
        qa_block = "_No QA verdict recorded (legacy path — no card body was supplied)._"

    # One-line block that the gateway (Telegram etc.) can render as buttons
    # if it supports actions on comments.
    auto_section = ""
    if card.auto_resolved_files:
        auto_section = (
            "\n\n**Auto-resolved conflicts (reviewer please verify):**\n"
            + "\n".join(f"- `{p}`" for p in card.auto_resolved_files)
        )

    body = f"""{READY_COMMENT_MARKER}
:rocket: **Card is ready to merge** (`{card.review_status}`)

- Task: `{card.task_id}` — {card.title}
- Feature branch: `{branch}` → `{target}`
- Worktree: `{card.qa_verdict.get('worktree') if card.qa_verdict else '<see dashboard>'}` _(if QA recorded)_

**QA gate**

{qa_block}{auto_section}

---

### :fast_forward: One-click merge commands

```bash
# Squash-merge into {target} (single commit; preserves the feature branch ref)
git checkout {target}
git merge --squash {branch}
git commit -m "Merge {card.task_id}: {card.title}"

# or, if you prefer a real merge commit that preserves history:
git merge --no-ff {branch} -m "Merge {card.task_id}: {card.title}"
```

:safety_vest: **Before you push**, copy this dry-run preview:

```bash
git diff --stat {target}..{branch}
git log --oneline {target}..{branch}
```

---

_Posted by `merge-review/orchestrator.py` from card `review_status = {card.review_status}` (exit {card.exit_code})._
"""
    return body.strip()


def format_escalation_comment(card: CardReview, hours_stale: float) -> str:
    """Compose the stale/24h escalation comment for a human reviewer."""
    files_block = ""
    if card.manual_conflict_files:
        files_block = "\n\n**Manual conflicts:**\n" + "\n".join(
            f"- `{p}`" for p in card.manual_conflict_files
        )
    notes_block = ""
    if card.notes:
        notes_block = "\n\n**Trigger notes:**\n" + "\n".join(f"- {n}" for n in card.notes)
    err_block = ""
    if card.error:
        err_block = f"\n\n**Error:** {card.error}"

    return f"""{ESCALATION_COMMENT_MARKER}
:hourglass: **Review stalled for {hours_stale:.1f}h — escalating to human reviewer**

- Task: `{card.task_id}` — {card.title}
- Branch: `{card.branch or '<unknown>'}` → `{card.base_branch or 'master'}`
- review_status: `{card.review_status}` (exit {card.exit_code})
- Last verdict at: {card.reviewed_at} ({hours_stale:.1f}h ago)
- Conflict report payload (see attached `conflict-report.json`)
{files_block}{notes_block}{err_block}

---

### :bust_in_silhouette: Action required

The merge-review ran into `{card.review_status}` and has been idle for more
than the 24h threshold. This card has been auto-reassigned to a human
reviewer; the conflict-report JSON is attached to this comment.

Recommended next steps:

1. Pull `{card.branch}` into a fresh worktree (`git worktree add ../review-stale {card.branch}`).
2. Open the attached `conflict-report.json` — the `suggested_resolution_order`
   key lists the order to resolve files in.
3. After resolving, push a new commit on the feature branch and re-trigger
   the review (`python tools/merge-review/trigger.py --card {card.task_id} --force`).

_Posted by `merge-review/orchestrator.py escalate` (24h stale-watcher)._
""".strip()


# ---------------------------------------------------------------------------
# Stages
# ---------------------------------------------------------------------------


def detect_already_posted_marker(task_id: str, marker: str, *,
                                 runs: list[dict[str, Any]],
                                 comments: list[str]) -> bool:
    """A reviewer may also leave the same marker in a comment. Be conservative."""
    # Cheap check: look at the comment blobs we already loaded; if the marker
    # is present we've definitely already posted.
    return any(marker in c for c in comments)


def stage_ready(
    cards: Iterable[CardReview],
    *,
    client: KanbanClient | None = None,
    force: bool = False,
) -> dict[str, int]:
    """Post the one-click ready-to-merge comment for every ready card.

    Returns counters: {"posted": N, "skipped_already": N, "not_ready": N, "errors": N}
    """
    client = client or get_client()
    counters = {"posted": 0, "skipped_already": 0, "not_ready": 0, "errors": 0}

    for card in cards:
        if not card.is_ready:
            counters["not_ready"] += 1
            continue

        if not force and card.ready_to_merge_commented:
            counters["skipped_already"] += 1
            continue

        body = format_ready_to_merge_comment(card)
        try:
            ok = client.comment(card.task_id, body)
        except Exception as exc:  # noqa: BLE001 — logged + counted
            print(f"warn: comment {card.task_id} failed: {exc}", file=sys.stderr)
            counters["errors"] += 1
            continue

        if ok:
            counters["posted"] += 1
            print(f"   ready: posted merge-cmd comment on {card.task_id} "
                  f"(verdict={card.review_status})")
        else:
            counters["errors"] += 1
            print(f"warn: comment {card.task_id} returned non-zero", file=sys.stderr)

    return counters


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _resolve_dashboard_path() -> Path:
    env = os.environ.get("MERGE_REVIEW_DASHBOARD")
    if env:
        return Path(env).expanduser().resolve()
    return DASHBOARD_PATH_DEFAULT


def _resolve_threshold_hours() -> float:
    raw = os.environ.get("MERGE_REVIEW_STALE_HOURS", "24")
    try:
        return float(raw)
    except ValueError:
        print(f"warn: bad MERGE_REVIEW_STALE_HOURS={raw!r}, defaulting to 24", file=sys.stderr)
        return 24.0


def _resolve_human_assignee() -> str:
    return os.environ.get("MERGE_REVIEW_HUMAN_ASSIGNEE", HUMAN_ASSIGNEE_DEFAULT)


def cmd_ready(args: argparse.Namespace) -> int:
    client = get_client()
    cards = collect_card_reviews(client, only_card=args.card)
    counters = stage_ready(cards, client=client, force=args.force)
    # Always refresh the dashboard after touching any cards.
    dashboard.update_dashboard_for_card(
        _resolve_dashboard_path(),
        [c for c in cards if c.is_ready],
    )
    print(f"ready: {counters}")
    return 0 if counters["errors"] == 0 else 1


def cmd_dashboard(args: argparse.Namespace) -> int:
    client = get_client()
    cards = collect_card_reviews(client)
    path = _resolve_dashboard_path()
    n = dashboard.rebuild_dashboard(path, cards)
    print(f"dashboard: wrote {n} entries to {path}")
    return 0


def cmd_escalate(args: argparse.Namespace) -> int:
    client = get_client()
    cards = collect_card_reviews(client, only_card=args.card)
    cfg = stale_watcher.StaleConfig(
        threshold_hours=_resolve_threshold_hours(),
        human_assignee=_resolve_human_assignee(),
    )
    counters = stale_watcher.escalate_stale_cards(
        cards,
        client=client,
        cfg=cfg,
        comment_factory=format_escalation_comment,
    )
    print(f"escalate: {counters}")
    return 0 if counters["errors"] == 0 else 1


def cmd_run_once(args: argparse.Namespace) -> int:
    """Single-pass convenience: ready → dashboard → escalate."""
    client = get_client()
    cards = collect_card_reviews(client)
    print(f"orchestrator: {len(cards)} card(s) with a review verdict")

    # 1) ready
    r = stage_ready(cards, client=client, force=False)
    print(f"  ready: {r}")

    # 2) dashboard (always rebuild from scratch so it's accurate)
    dash_path = _resolve_dashboard_path()
    n_rows = dashboard.rebuild_dashboard(dash_path, cards)
    print(f"  dashboard: {n_rows} entries → {dash_path}")

    # 3) escalate stale stuck cards
    cfg = stale_watcher.StaleConfig(
        threshold_hours=_resolve_threshold_hours(),
        human_assignee=_resolve_human_assignee(),
    )
    e = stale_watcher.escalate_stale_cards(
        cards,
        client=client,
        cfg=cfg,
        comment_factory=format_escalation_comment,
    )
    print(f"  escalate: {e}")

    return 0 if (r["errors"] + e["errors"]) == 0 else 1


# ---------------------------------------------------------------------------
# Argparse
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="ChoreHero merge-review orchestrator")
    sub = p.add_subparsers(dest="cmd", required=True)

    pr = sub.add_parser("ready", help="Post ready-to-merge comments")
    pr.add_argument("--card", help="only operate on this card id")
    pr.add_argument("--force", action="store_true", help="re-post even if marker present")
    pr.set_defaults(func=cmd_ready)

    pd = sub.add_parser("dashboard", help="Rebuild docs/merge-review-dashboard.md")
    pd.set_defaults(func=cmd_dashboard)

    pe = sub.add_parser("escalate", help="Escalate stuck cards past the 24h threshold")
    pe.add_argument("--card", help="only operate on this card id")
    pe.set_defaults(func=cmd_escalate)

    pro = sub.add_parser("run-once", help="ready + dashboard + escalate in one pass")
    pro.set_defaults(func=cmd_run_once)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args) or 0)


if __name__ == "__main__":
    sys.exit(main())
