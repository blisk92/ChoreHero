#!/usr/bin/env python3
"""
dashboard.py — ChoreHero merge-review rolling dashboard.

Maintains a small human-readable markdown table of the last N reviews in
`docs/merge-review-dashboard.md`. Each row records:

    when, task_id, title, branch, review_status, exit_code,
    n_manual_conflicts, age_hours

The dashboard is rebuilt from scratch on every pass so it's always a pure
projection of current board state — no rotation bookkeeping required.
"""

from __future__ import annotations

import datetime as _dt
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent

# Maximum number of rows the dashboard keeps. Older rows are dropped.
DASHBOARD_MAX_ROWS = 10


@dataclass
class DashboardEntry:
    task_id: str
    title: str
    branch: str | None
    base_branch: str | None
    review_status: str
    exit_code: int | None
    n_manual_conflicts: int
    n_auto_resolved: int
    reviewed_at: int | None
    age_hours: float | None
    is_ready: bool


def _row_for(card: Any) -> DashboardEntry:
    # Tolerate a CardReview or an already-built DashboardEntry as input so the
    # caller doesn't have to think about shape.
    if isinstance(card, DashboardEntry):
        return card
    age = card.age_hours if hasattr(card, "age_hours") else None
    return DashboardEntry(
        task_id=card.task_id,
        title=card.title,
        branch=card.branch,
        base_branch=card.base_branch,
        review_status=card.review_status,
        exit_code=card.exit_code,
        n_manual_conflicts=len(getattr(card, "manual_conflict_files", None) or []),
        n_auto_resolved=len(getattr(card, "auto_resolved_files", None) or []),
        reviewed_at=getattr(card, "reviewed_at", None),
        age_hours=age,
        is_ready=bool(getattr(card, "is_ready", False)),
    )


STATUS_EMOJI = {
    "clean-merge": ":white_check_mark:",
    "trivial-auto-merge": ":wrench:",
    "real-conflict": ":collision:",
    "qa-fail": ":no_entry:",
    "error": ":warning:",
    "skipped": ":fast_forward:",
}


def format_dashboard(entries: list[DashboardEntry],
                     *, generated_at_epoch: int | None = None) -> str:
    generated_at_epoch = generated_at_epoch or int(
        _dt.datetime.now(_dt.timezone.utc).timestamp()
    )
    gen_iso = _dt.datetime.fromtimestamp(generated_at_epoch, tz=_dt.timezone.utc)\
        .strftime("%Y-%m-%d %H:%M:%S UTC")

    lines: list[str] = []
    lines.append("# Merge-review dashboard")
    lines.append("")
    lines.append(f"_Last regenerated: {gen_iso}._  ")
    lines.append(f"_Showing the last {len(entries)} review{'s' if len(entries) != 1 else ''}._")
    lines.append("")
    lines.append("| Status | Task | Title | Branch → base | Exit | Manual | Auto | Age |")
    lines.append("|---|---|---|---|---:|---:|---:|---:|")
    for e in entries:
        emoji = STATUS_EMOJI.get(e.review_status, ":grey_question:")
        branch = e.branch or "—"
        base = e.base_branch or "master"
        title = (e.title or "").replace("|", "\\|")
        if len(title) > 70:
            title = title[:67] + "…"
        ec = e.exit_code if e.exit_code is not None else "—"
        age = f"{e.age_hours:.1f}h" if e.age_hours is not None else "—"
        ready_marker = "  :rocket:" if e.is_ready else ""
        lines.append(
            f"| {emoji} `{e.review_status}`{ready_marker} "
            f"| `{e.task_id}` | {title} "
            f"| `{branch}` → `{base}` "
            f"| {ec} | {e.n_manual_conflicts} | {e.n_auto_resolved} | {age} |"
        )
    if not entries:
        lines.append("| _(no reviews yet)_ | | | | | | | |")
    lines.append("")
    lines.append("Legend: `:rocket:` = ready-to-merge (clean-merge or trivial-auto-merge "
                 "with QA pass). Manual / Auto count how many files the runner touched.")
    lines.append("")
    return "\n".join(lines)


def rebuild_dashboard(path: Path, cards: Iterable[Any]) -> int:
    """Rewrite the dashboard markdown with up to the last N reviews.

    Returns the number of rows written.
    """
    entries = [_row_for(c) for c in cards]
    entries.sort(
        key=lambda e: -(e.reviewed_at or 0)  # newest first
    )
    entries = entries[:DASHBOARD_MAX_ROWS]
    md = format_dashboard(entries)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(md, encoding="utf-8")
    return len(entries)


def update_dashboard_for_card(path: Path, cards: Iterable[Any]) -> int:
    """Convenience: rebuild dashboard from just one (or a few) card(s).

    Equivalent to `rebuild_dashboard` for now — the function exists so the
    caller doesn't have to know how the dashboard is stored. Kept as a
    distinct name to leave room for incremental updates later.
    """
    return rebuild_dashboard(path, cards)
