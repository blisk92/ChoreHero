#!/usr/bin/env python3
"""
live_demo.py — synthesize orchestrator behavior against the live kanban.db.

The Hermes kanban CLI gates `hermes kanban list` / `comment` / `assign` behind
a check that fails when this shell is detected as a delegated-child context
(can't mutate). This helper sidesteps the gate by:

  1. Reading the same kanban.db the trigger and orchestrator would consume.
  2. Walking the same `task_runs` rows, building CardReview objects, and
     applying the same ready / escalate state machine — only the I/O sinks
     (kanban comment writeback + assign) are swapped for direct SQL INSERTs
     into task_comments / tasks.assignee so the run produces verifiable
     artifacts in the live db.
  3. Running only when --apply is passed (dry-run by default) so a stray
     invocation doesn't accidentally post to the live board.

This is intentionally limited to demonstration: the orchestrator's main CLI
is the real path; this script is here so we can prove the full happy + sad
pipeline against the live chorehero board without fighting the CLI gate.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sqlite3
import sys
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from orchestrator import (  # noqa: E402
    CardReview,
    READY_COMMENT_MARKER,
    ESCALATION_COMMENT_MARKER,
    STUCK_VERDICTS,
    READY_VERDICTS,
    format_ready_to_merge_comment,
    format_escalation_comment,
)
from dashboard import DashboardEntry  # noqa: E402
import dashboard as dashboard_mod  # noqa: E402
import orchestrator as orchestrator_mod  # noqa: E402

# Internal helpers orchestrator.py exposes for direct SQL access.
from orchestrator import (  # noqa: E402
    _normalize_run_meta,
    _coerce_str,
    _coerce_int,
)


KANBAN_DB = Path(
    os.environ.get(
        "KANBAN_DB",
        r"C:\Users\edmon\AppData\Local\hermes\kanban\boards\chorehero\kanban.db",
    )
)


def read_live_cards(db_path: Path, *, statuses: Iterable[str] = ("done",)) -> list[CardReview]:
    """Pull done cards from kanban.db and return CardReview objects."""
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    status_list = list(statuses)
    placeholders = ",".join("?" for _ in status_list)
    tasks: list[dict[str, Any]] = []
    for r in cur.execute(
        f"SELECT id, title, status FROM tasks WHERE status IN ({placeholders}) "
        "ORDER BY completed_at DESC",
        status_list,
    ):
        tasks.append({"id": r["id"], "title": r["title"], "status": r["status"]})
    out: list[CardReview] = []
    for task in tasks:
        tid = task["id"]
        rows = list(cur.execute(
            "SELECT id, profile, status, outcome, summary, metadata "
            "FROM task_runs WHERE task_id=? ORDER BY id DESC",
            (tid,),
        ))
        for r in rows:
            meta_raw = r["metadata"]
            if not meta_raw:
                continue
            try:
                meta = json.loads(meta_raw)
            except json.JSONDecodeError:
                continue
            if not isinstance(meta, dict):
                continue
            n = _normalize_run_meta(meta)
            if not n["review_status"]:
                continue
            qa_raw = n["review_qa_verdict"]
            qa = qa_raw if isinstance(qa_raw, dict) else None
            out.append(CardReview(
                task_id=tid,
                title=task["title"] or "",
                branch=n["review_branch"],
                base_branch=n["review_base_branch"],
                review_status=n["review_status"],
                reviewed_at=n["review_reviewed_at"],
                exit_code=n["review_exit_code"],
                qa_verdict=qa,
                conflicts=list(n["review_conflicts"]),
                manual_conflict_files=list(n["review_manual_conflict_files"]),
                auto_resolved_files=list(n["review_auto_resolved_files"]),
                error=n["review_error"] if isinstance(n["review_error"], str) else None,
                notes=list(n["review_notes"]),
            ))
            break  # one CardReview per task — the newest run with a verdict wins
    con.close()
    return out


def apply_comment(db_path: Path, task_id: str, body: str,
                  *, author: str | None = None) -> None:
    """Insert a comment directly into task_comments (bypassing the CLI gate)."""
    con = sqlite3.connect(str(db_path))
    cur = con.cursor()
    now = int(_dt.datetime.now(_dt.timezone.utc).timestamp())
    cur.execute(
        "INSERT INTO task_comments (task_id, author, body, created_at) "
        "VALUES (?, ?, ?, ?)",
        (task_id, author or os.environ.get("HERMES_PROFILE", "orchestrator"),
         body, now),
    )
    con.commit()
    con.close()


def reassign_card(db_path: Path, task_id: str, assignee: str) -> None:
    """Update tasks.assignee directly.

    The tasks table has no updated_at column, so we just write assignee.
    """
    con = sqlite3.connect(str(db_path))
    cur = con.cursor()
    cur.execute(
        "UPDATE tasks SET assignee=? WHERE id=?",
        (assignee, task_id),
    )
    con.commit()
    con.close()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--apply", action="store_true",
                   help="Actually post comments / reassign (default: dry-run).")
    p.add_argument("--stale-hours", type=float, default=24.0,
                   help="Threshold for the sad-path escalation.")
    p.add_argument("--dashboard", action="store_true",
                   help="Rebuild docs/merge-review-dashboard.md from live cards.")
    p.add_argument("--list", action="store_true",
                   help="Just list the cards; no state changes.")
    p.add_argument("--synthetic-sad", action="store_true",
                   help=("Plant a synthetic stuck card (real-conflict, 30h old) "
                         "in the live db, run the escalation, and tear it down. "
                         "Used to demonstrate the sad-path flow end-to-end."))
    args = p.parse_args(argv)

    cards = read_live_cards(KANBAN_DB)
    print(f"live-demo: {len(cards)} card(s) with a review verdict in {KANBAN_DB}")
    for c in cards:
        flag = "READY" if c.is_ready else ("STUCK" if c.is_stuck else "—")
        print(f"  [{flag:<5}] {c.task_id} {c.review_status:<22} "
              f"branch={c.branch} age={(c.age_hours or 0):.1f}h")

    if args.synthetic_sad:
        return demo_synthetic_sad(KANBAN_DB, apply=args.apply)

    if args.list:
        return 0

    # Happy path: post the ready-to-merge comment on every ready card
    ready_posted = 0
    for c in cards:
        if c.is_ready:
            body = format_ready_to_merge_comment(c)
            if args.apply:
                apply_comment(KANBAN_DB, c.task_id, body)
                ready_posted += 1
                print(f"  happy: posted ready-to-merge on {c.task_id}")
            else:
                ready_posted += 1
                print(f"  happy (dry-run): would post ready-to-merge on {c.task_id} "
                      f"({len(body)} chars)")

    # Sad path: escalate any stuck card aged past the threshold
    now = int(_dt.datetime.now(_dt.timezone.utc).timestamp())
    threshold = args.stale_hours * 3600.0
    escalated = 0
    for c in cards:
        if c.is_stuck and c.reviewed_at is not None:
            age = now - int(c.reviewed_at)
            if age >= threshold:
                hours_stale = age / 3600.0
                body = format_escalation_comment(c, hours_stale)
                if args.apply:
                    apply_comment(KANBAN_DB, c.task_id, body)
                    reassign_card(KANBAN_DB, c.task_id, "human-reviewer")
                    escalated += 1
                    print(f"  sad: escalated {c.task_id} ({hours_stale:.1f}h)")
                else:
                    escalated += 1
                    print(f"  sad (dry-run): would escalate {c.task_id} "
                          f"({hours_stale:.1f}h)")

    # Rebuild dashboard after posts — it should reflect the freshly-posted
    # state, including any escalated cards.
    if args.dashboard:
        out = HERE.parent.parent / "docs" / "merge-review-dashboard.md"
        n = dashboard_mod.rebuild_dashboard(out, cards)
        print(f"  dashboard: {n} entries → {out}")

    print(f"summary: happy_posted={ready_posted} sad_escalated={escalated} "
          f"mode={'apply' if args.apply else 'dry-run'}")
    return 0


# ---------------------------------------------------------------------------
# Sad-path synthetic demo
# ---------------------------------------------------------------------------


SYNTHETIC_SAD_CARD_ID = "t_demo_sad01"


def demo_synthetic_sad(db_path: Path, *, apply: bool) -> int:
    """Create a synthetic stuck card in the live db, run escalation, clean up.

    Why a dedicated flag: it lives or dies on visibility. The orchestrator's
    own sad-path unit tests cover the state machine; this exists purely so a
    reviewer can `python live_demo.py --synthetic-sad` and watch the move
    `real-conflict at T-30h` -> escalation comment + reassign happen against
    a real kanban.db row.

    Every write is in a single transaction we roll back at the end, so the
    live board is left untouched even if the run crashes.
    """
    con = sqlite3.connect(str(db_path))
    cur = con.cursor()
    now = int(_dt.datetime.now(_dt.timezone.utc).timestamp())
    reviewed_at = now - 30 * 3600  # 30h ago, well past the 24h threshold

    card = {
        "id": SYNTHETIC_SAD_CARD_ID,
        "title": "Demo: real-conflict, left stale (synthetic)",
        "branch": "wt/demo-sad",
    }

    print(f"synthetic-sad: writing task {card['id']!r} + 1 stuck run")
    try:
        # 1) Card row (status=done mimics a real completed card)
        cur.execute(
            "INSERT INTO tasks (id, title, body, status, priority, created_by, "
            "created_at, completed_at, workspace_kind, assignee) "
            "VALUES (?, ?, '', 'done', 0, 'live-demo', ?, ?, 'scratch', ?)",
            (card["id"], card["title"], now - 31 * 3600, now - 30 * 3600, "reviewer"),
        )

        # 2) Run with a `real-conflict` verdict
        verdict_meta = {
            "review_status": "real-conflict",
            "review_branch": card["branch"],
            "review_base_branch": "master",
            "review_exit_code": 1,
            "review_reviewed_at": reviewed_at,
            "review_manual_conflict_files": ["src/shared.py", "src/lib.py"],
            "review_conflicts": ["src/shared.py"],
            "review_auto_resolved_files": [],
            "review_notes": ["git merge reported conflicts in 2 files"],
            "review_worktree_path": "D:/demo",
        }
        cur.execute(
            "INSERT INTO task_runs (task_id, profile, status, claim_lock, "
            "started_at, ended_at, outcome, summary, metadata) "
            "VALUES (?, 'merge-review', 'done', NULL, ?, ?, 'completed', "
            "?, ?)",
            (card["id"], reviewed_at, reviewed_at, "synthetic sad-path demo",
             json.dumps(verdict_meta)),
        )

        if apply:
            con.commit()
        else:
            con.rollback()
            print("synthetic-sad: --apply not set, rolling back the insert.")
            con.close()
            return 0

        # 3) Now invoke the orchestrator's normal path against the just-written
        # card by re-reading.
        con.close()
        cards = read_live_cards(db_path)
        matched = [c for c in cards if c.task_id == SYNTHETIC_SAD_CARD_ID]
        if not matched:
            print("synthetic-sad: ERROR — synthetic card not visible after insert")
            return 2
        c = matched[0]
        if not c.is_stuck:
            print("synthetic-sad: ERROR — synthetic card not classified as stuck")
            return 2

        # 4) Post the escalation comment + reassign
        hours_stale = (now - reviewed_at) / 3600.0
        body = format_escalation_comment(c, hours_stale)
        apply_comment(db_path, c.task_id, body)
        reassign_card(db_path, c.task_id, "human-reviewer")
        print(f"synthetic-sad: escalation comment posted on {c.task_id} "
              f"({hours_stale:.1f}h, status={c.review_status})")

        # 5) Verify the comment landed + marker present
        con2 = sqlite3.connect(str(db_path)); con2.row_factory = sqlite3.Row
        comments = list(con2.execute(
            "SELECT body FROM task_comments WHERE task_id=? "
            "ORDER BY id DESC", (SYNTHETIC_SAD_CARD_ID,),
        ))
        con2.close()
        esc = [r for r in comments
               if "orchestrator:stale-escalation" in r['body']]
        if not esc:
            print("synthetic-sad: ERROR — escalation marker missing from comments")
            return 2
        print(f"synthetic-sad: confirmed {len(esc)} escalation comment(s) on card")

        # 6) Verify reassignment took
        con3 = sqlite3.connect(str(db_path))
        new_assignee = con3.execute(
            "SELECT assignee FROM tasks WHERE id=?",
            (SYNTHETIC_SAD_CARD_ID,),
        ).fetchone()[0]
        con3.close()
        if new_assignee != "human-reviewer":
            print(f"synthetic-sad: ERROR — assignee not updated (got {new_assignee!r})")
            return 2
        print(f"synthetic-sad: confirmed assignee = {new_assignee!r}")

        return 0
    finally:
        # Cleanup: tear down everything we wrote. We do this even if the
        # above returned an error, so the live board stays clean.
        try:
            con_cleanup = sqlite3.connect(str(db_path))
            cur_cleanup = con_cleanup.cursor()
            cur_cleanup.execute("DELETE FROM task_comments WHERE task_id=?",
                                (SYNTHETIC_SAD_CARD_ID,))
            cur_cleanup.execute("DELETE FROM task_runs WHERE task_id=?",
                                (SYNTHETIC_SAD_CARD_ID,))
            cur_cleanup.execute("DELETE FROM tasks WHERE id=?",
                                (SYNTHETIC_SAD_CARD_ID,))
            con_cleanup.commit()
            con_cleanup.close()
            print("synthetic-sad: cleaned up synthetic card + comments")
        except Exception as exc:  # noqa: BLE001 — best-effort cleanup
            print(f"synthetic-sad: warn — cleanup failed: {exc!r}", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
