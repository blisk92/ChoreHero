#!/usr/bin/env python3
"""
stale_watcher.py — ChoreHero merge-review 24h-stale escalation.

A merge-review verdict that lands in `real-conflict`, `qa-fail`, or `error`
must be acted on inside a day, otherwise the backlog grows. This module:

  * Reads each card's review metadata (review_status + reviewed_at).
  * If review_status is in STUCK_VERDICTS AND (now - reviewed_at) >
    threshold_hours, posts the orchestrator's escalation comment (with the
    conflict report attached inline) and reassigns the card to a human
    reviewer so it surfaces in their queue.
  * Honors a per-card marker (`<!-- orchestrator:stale-escalation -->`) so a
    card is never double-escalated by repeated runs.
"""

from __future__ import annotations

import datetime as _dt
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable

# Imported lazily by the orchestrator; this module is also importable
# standalone for testing.
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from constants import (  # noqa: E402
    STUCK_VERDICTS,
    ESCALATION_COMMENT_MARKER,
)


@dataclass
class StaleConfig:
    threshold_hours: float = 24.0
    human_assignee: str = "human-reviewer"


def _now_epoch() -> int:
    return int(_dt.datetime.now(_dt.timezone.utc).timestamp())


def is_stale(card: Any, *, cfg: StaleConfig, now_epoch: int | None = None) -> bool:
    """Return True iff the card is stuck and past the stale threshold."""
    if not getattr(card, "is_stuck", False):
        return False
    if getattr(card, "escalated", False):
        return False
    if card.reviewed_at is None:
        return False
    now_epoch = now_epoch if now_epoch is not None else _now_epoch()
    age = now_epoch - int(card.reviewed_at)
    return age >= cfg.threshold_hours * 3600.0


def escalate_stale_cards(
    cards: Iterable[Any],
    *,
    client: Any,
    cfg: StaleConfig,
    comment_factory: Callable[[Any, float], str],
    now_epoch: int | None = None,
) -> dict[str, int]:
    """Walk the cards, post escalation comments + reassign where stale.

    `comment_factory` is the orchestrator's `format_escalation_comment`,
    injected so this module stays free of markdown formatting logic.
    """
    counters = {"posted": 0, "reassigned": 0, "skipped_fresh": 0,
                "skipped_already": 0, "errors": 0}
    now_epoch = now_epoch if now_epoch is not None else _now_epoch()

    for card in cards:
        if not getattr(card, "is_stuck", False):
            counters["skipped_fresh"] += 1
            continue
        if getattr(card, "escalated", False):
            counters["skipped_already"] += 1
            continue
        if card.reviewed_at is None:
            counters["skipped_fresh"] += 1
            continue

        age_seconds = now_epoch - int(card.reviewed_at)
        if age_seconds < cfg.threshold_hours * 3600.0:
            counters["skipped_fresh"] += 1
            continue

        hours_stale = age_seconds / 3600.0

        # 1) build the comment + conflict-report payload (serialize qa_verdict
        # so it survives even if the card body later changes).
        conflict_report = {
            "task_id": card.task_id,
            "branch": card.branch,
            "base_branch": card.base_branch,
            "review_status": card.review_status,
            "exit_code": card.exit_code,
            "manual_conflict_files": card.manual_conflict_files,
            "auto_resolved_files": card.auto_resolved_files,
            "qa_verdict": card.qa_verdict,
            "notes": list(card.notes),
            "error": card.error,
            "reviewed_at": card.reviewed_at,
            "stale_hours": round(hours_stale, 2),
        }
        body = comment_factory(card, hours_stale)
        # Append the JSON payload inline at the end of the comment so a human
        # can copy it without re-running the review.
        body = (
            body
            + "\n\n---\n\n<details><summary>Conflict report JSON</summary>\n\n"
            + "```json\n"
            + json.dumps(conflict_report, indent=2)
            + "\n```\n\n</details>\n"
        )

        # 2) post the comment + reassign
        try:
            ok = client.comment(card.task_id, body)
        except Exception as exc:  # noqa: BLE001 — errors counted
            print(f"warn: stale comment {card.task_id} failed: {exc}", file=sys.stderr)
            counters["errors"] += 1
            continue

        if not ok:
            counters["errors"] += 1
            print(f"warn: stale comment {card.task_id} returned non-zero", file=sys.stderr)
            continue
        counters["posted"] += 1

        try:
            client.assign(card.task_id, cfg.human_assignee)
            counters["reassigned"] += 1
        except Exception as exc:  # noqa: BLE001 — assignment is best-effort
            print(f"warn: reassign {card.task_id} -> {cfg.human_assignee} failed: {exc}",
                  file=sys.stderr)

        # Mark the in-memory card so a second pass in the same `run_once`
        # doesn't double-post.
        card.escalated = True
        print(f"   stale: escalated {card.task_id} "
              f"({hours_stale:.1f}h, status={card.review_status})")

    return counters
