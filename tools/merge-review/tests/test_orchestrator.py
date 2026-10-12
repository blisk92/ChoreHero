#!/usr/bin/env python3
"""
test_orchestrator.py — exercise the merge-review orchestrator end-to-end.

Two scenarios:

  HAPPY: a card whose review_status = clean-merge + QA pass → the orchestrator
         posts a one-click merge comment and the dashboard reflects it.

  SAD:   a card whose review_status = real-conflict AND the verdict is older
         than 24h → the orchestrator posts a stale-escalation comment and
         reassigns it to a human reviewer.

The orchestrator talks to kanban via a `KanbanClient` interface; tests inject
a fake that records every call and returns canned board state. The dashboard
markdown is written to a tmp file so the real `docs/` directory is untouched.
"""

from __future__ import annotations

import datetime as _dt
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
HERE = ROOT.parent
sys.path.insert(0, str(HERE))

# Import orchestrator under test
import orchestrator  # noqa: E402
from orchestrator import (  # noqa: E402
    CardReview,
    KanbanClient,
    READY_COMMENT_MARKER,
    ESCALATION_COMMENT_MARKER,
    STUCK_VERDICTS,
    collect_card_reviews,
    format_ready_to_merge_comment,
    format_escalation_comment,
    stage_ready,
)
import stale_watcher  # noqa: E402
from dashboard import (  # noqa: E402
    DashboardEntry,
    rebuild_dashboard,
    format_dashboard,
    DASHBOARD_MAX_ROWS,
)


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------


class FakeKanban(KanbanClient):
    """In-memory kanban fake that records every mutation.

    `seed(tasks)` and `seed_runs(task_id, runs_data)` let each test set the
    board state. Every comment/assign/reassign call appends to `self.calls`,
    so tests can assert on the exact side-effects without a real board.
    """

    def __init__(self):
        super().__init__(board="test")
        self._tasks: list[dict[str, Any]] = []
        self._runs: dict[str, list[dict[str, Any]]] = {}
        # (task_id, body) tuples for comment writes
        self.comments: list[tuple[str, str]] = []
        # (task_id, profile) tuples for assign writes
        self.assigns: list[tuple[str, str]] = []
        self.fail_comment = False  # toggle to simulate a kanban error

    def seed(self, tasks: list[dict[str, Any]]) -> None:
        self._tasks = list(tasks)

    def seed_runs(self, task_id: str, runs: list[dict[str, Any]]) -> None:
        self._runs[task_id] = list(runs)

    # --- KanbanClient surface ---

    def list(self, *, status: str, json_out: bool = True) -> list[dict[str, Any]]:
        return [t for t in self._tasks if t.get("status") == status]

    def runs(self, task_id: str) -> list[dict[str, Any]]:
        return list(self._runs.get(task_id, []))

    def comment(self, task_id: str, body: str) -> bool:
        if self.fail_comment:
            return False
        self.comments.append((task_id, body))
        return True

    def assign(self, task_id: str, profile: str) -> bool:
        self.assigns.append((task_id, profile))
        return True

    def block(self, task_id: str, reason: str) -> bool:
        return True


def _now_epoch() -> int:
    return int(_dt.datetime.now(_dt.timezone.utc).timestamp())


def _run_with_meta(task_id: str, run_id: int, meta: dict[str, Any],
                   *, profile: str = "devops-engineer",
                   status: str = "done",
                   outcome: str = "completed") -> dict[str, Any]:
    """Build a fake `task_runs` row with the metadata shape orchestrator reads."""
    return {
        "id": run_id,
        "task_id": task_id,
        "profile": profile,
        "status": status,
        "outcome": outcome,
        "started_at": 0,
        "ended_at": 0,
        "summary": "",
        "metadata": json.dumps(meta),
        "metadata_json": meta,  # convenience for tests that don't json-roundtrip
    }


# ---------------------------------------------------------------------------
# HAPPY path
# ---------------------------------------------------------------------------


class HappyPathTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fake = FakeKanban()
        orchestrator.set_client(self.fake)
        self.tmpdir = tempfile.mkdtemp(prefix="mr-orch-happy-")
        self.addCleanup(self._cleanup)

    def _cleanup(self) -> None:
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _happy_card(self) -> tuple[dict[str, Any], CardReview]:
        reviewed_at = _now_epoch() - 600  # 10 minutes ago — fresh
        card = {
            "id": "t_happy01",
            "title": "Happy-path: clean merge with passing QA",
            "status": "done",
        }
        run = _run_with_meta(
            "t_happy01", 1,
            {
                "review_status": "clean-merge",
                "review_branch": "feature/happy-path",
                "review_base_branch": "master",
                "review_exit_code": 0,
                "review_reviewed_at": reviewed_at,
                "review_conflicts": [],
                "review_manual_conflict_files": [],
                "review_auto_resolved_files": [],
                "review_notes": [],
                "review_qa_verdict": {
                    "overall": "pass",
                    "tests": {"passed": True, "ran": 12},
                    "coverage_delta": {"passed": True, "pct": 0.5},
                    "lint_delta": {"passed": True, "new_findings": 0},
                    "acs": {"total": 3, "met": 3, "unmet": []},
                    "reasons": [],
                    "unmet_acs": [],
                },
            },
        )
        self.fake.seed([card])
        self.fake.seed_runs("t_happy01", [run])

        cr = CardReview(
            task_id="t_happy01",
            title=card["title"],
            branch="feature/happy-path",
            base_branch="master",
            review_status="clean-merge",
            reviewed_at=reviewed_at,
            exit_code=0,
            qa_verdict={
                "overall": "pass",
                "tests": {"passed": True, "ran": 12},
                "acs": {"total": 3, "met": 3, "unmet": []},
                "reasons": [],
                "unmet_acs": [],
            },
            conflicts=[],
            manual_conflict_files=[],
            auto_resolved_files=[],
            notes=[],
            error=None,
        )
        return card, cr

    def test_is_ready_property(self) -> None:
        _, cr = self._happy_card()
        self.assertTrue(cr.is_ready)

    def test_collect_card_reviews_finds_clean_card(self) -> None:
        card, _ = self._happy_card()
        crs = collect_card_reviews(self.fake)
        self.assertEqual(len(crs), 1)
        self.assertEqual(crs[0].task_id, "t_happy01")
        self.assertEqual(crs[0].review_status, "clean-merge")

    def test_stage_ready_posts_merge_command_comment(self) -> None:
        _, cr = self._happy_card()
        counters = stage_ready([cr], client=self.fake)
        self.assertEqual(counters["posted"], 1)
        self.assertEqual(counters["not_ready"], 0)
        self.assertEqual(counters["errors"], 0)
        # Side-effect: one comment was posted on this task
        self.assertEqual(len(self.fake.comments), 1)
        tid, body = self.fake.comments[0]
        self.assertEqual(tid, "t_happy01")
        self.assertIn(READY_COMMENT_MARKER, body)
        self.assertIn("git merge --squash feature/happy-path", body)
        self.assertIn("git merge --no-ff feature/happy-path", body)
        self.assertIn("ready to merge", body.lower())

    def test_stage_ready_idempotent(self) -> None:
        # Pre-mark the card so the orchestrator would skip it if not present
        _, cr = self._happy_card()
        cr.ready_to_merge_commented = False
        # First post
        c1 = stage_ready([cr], client=self.fake)
        self.assertEqual(c1["posted"], 1)
        # Second post: orchestrator re-reads cards, but for this in-memory
        # path we flip the flag it would have flipped if it re-read from the
        # board; force=False plus marker presence is what guards it.
        # Simulate the marker seen by re-loading from the fake's state by
        # setting the dedup flag the orchestrator would have set on the
        # freshly collected card. Since we just call stage_ready again on
        # the same in-memory object, and we don't auto-set the flag, we
        # rely on the per-card `ready_to_merge_commented` flag.
        # → Force the flag to mimic a re-read:
        cr.ready_to_merge_commented = True
        c2 = stage_ready([cr], client=self.fake)
        self.assertEqual(c2["posted"], 0)
        self.assertEqual(c2["skipped_already"], 1)
        # Still only one comment in total
        self.assertEqual(len(self.fake.comments), 1)

    def test_dashboard_renders_clean_card(self) -> None:
        card, cr = self._happy_card()
        dash = Path(self.tmpdir) / "dash.md"
        n = rebuild_dashboard(dash, [cr])
        self.assertEqual(n, 1)
        text = dash.read_text(encoding="utf-8")
        self.assertIn("Merge-review dashboard", text)
        self.assertIn("`clean-merge`", text)
        self.assertIn("t_happy01", text)
        self.assertIn("feature/happy-path", text)
        self.assertIn(":rocket:", text)
        self.assertIn("ready-to-merge", text.lower())

    def test_qa_fail_card_does_not_post_ready_comment(self) -> None:
        # A clean-merge verdict with a FAILING QA gate is NOT ready-to-merge.
        reviewed_at = _now_epoch() - 60
        card = {
            "id": "t_qafail",
            "title": "Tests pass but an AC is unmet",
            "status": "done",
        }
        run = _run_with_meta(
            "t_qafail", 2,
            {
                "review_status": "qa-fail",
                "review_branch": "feature/qafail",
                "review_base_branch": "master",
                "review_exit_code": 1,
                "review_reviewed_at": reviewed_at,
                "review_qa_verdict": {
                    "overall": "fail",
                    "tests": {"passed": True, "ran": 12},
                    "acs": {"total": 2, "met": 1, "unmet": ["AC2"]},
                    "reasons": ["AC2 unmet"],
                    "unmet_acs": ["AC2 unmet"],
                },
            },
        )
        self.fake.seed([card])
        self.fake.seed_runs("t_qafail", [run])
        crs = collect_card_reviews(self.fake)
        cr = crs[0]
        self.assertFalse(cr.is_ready)
        counters = stage_ready([cr], client=self.fake)
        self.assertEqual(counters["posted"], 0)
        self.assertEqual(counters["not_ready"], 1)
        self.assertEqual(self.fake.comments, [])  # no comment posted

    def test_real_conflict_card_is_stuck(self) -> None:
        # A real-conflict verdict → stuck, not ready.
        reviewed_at = _now_epoch() - 60
        card = {
            "id": "t_conflict",
            "title": "Real conflict",
            "status": "done",
        }
        run = _run_with_meta(
            "t_conflict", 3,
            {
                "review_status": "real-conflict",
                "review_branch": "feature/conflict",
                "review_base_branch": "master",
                "review_exit_code": 1,
                "review_reviewed_at": reviewed_at,
                "review_manual_conflict_files": ["shared.py"],
                "review_conflicts": ["shared.py"],
            },
        )
        self.fake.seed([card])
        self.fake.seed_runs("t_conflict", [run])
        crs = collect_card_reviews(self.fake)
        cr = crs[0]
        self.assertTrue(cr.is_stuck)
        self.assertIn(cr.review_status, STUCK_VERDICTS)
        self.assertFalse(cr.is_ready)


# ---------------------------------------------------------------------------
# SAD path: stuck card aged > 24h
# ---------------------------------------------------------------------------


class SadPathTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fake = FakeKanban()
        orchestrator.set_client(self.fake)
        self.tmpdir = tempfile.mkdtemp(prefix="mr-orch-sad-")
        self.addCleanup(self._cleanup)

    def _cleanup(self) -> None:
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _stuck_card(self, *, hours_stale: float) -> tuple[dict[str, Any], CardReview]:
        reviewed_at = _now_epoch() - int(hours_stale * 3600)
        card = {
            "id": "t_stuck01",
            "title": "Sad-path: real conflict left for a day",
            "status": "done",
        }
        run = _run_with_meta(
            "t_stuck01", 10,
            {
                "review_status": "real-conflict",
                "review_branch": "feature/conflict",
                "review_base_branch": "master",
                "review_exit_code": 1,
                "review_reviewed_at": reviewed_at,
                "review_manual_conflict_files": ["src/shared.py", "src/lib/helpers.py"],
                "review_conflicts": ["src/shared.py"],
                "review_notes": ["git merge reported 2 conflicts"],
            },
        )
        self.fake.seed([card])
        self.fake.seed_runs("t_stuck01", [run])
        cr = CardReview(
            task_id="t_stuck01",
            title=card["title"],
            branch="feature/conflict",
            base_branch="master",
            review_status="real-conflict",
            reviewed_at=reviewed_at,
            exit_code=1,
            qa_verdict=None,
            conflicts=["src/shared.py"],
            manual_conflict_files=["src/shared.py", "src/lib/helpers.py"],
            auto_resolved_files=[],
            notes=["git merge reported 2 conflicts"],
            error=None,
        )
        return card, cr

    def test_fresh_stuck_card_is_NOT_escalated(self) -> None:
        # 5h old < 24h threshold → no escalation
        from stale_watcher import StaleConfig, escalate_stale_cards, is_stale
        cfg = StaleConfig(threshold_hours=24.0, human_assignee="human-reviewer")
        _, cr = self._stuck_card(hours_stale=5.0)
        self.assertFalse(is_stale(cr, cfg=cfg))
        counters = escalate_stale_cards(
            [cr], client=self.fake, cfg=cfg,
            comment_factory=format_escalation_comment,
        )
        self.assertEqual(counters["posted"], 0)
        self.assertEqual(counters["reassigned"], 0)
        self.assertEqual(counters["skipped_fresh"], 1)
        self.assertEqual(self.fake.comments, [])

    def test_aged_stuck_card_IS_escalated_with_comment_and_reassign(self) -> None:
        from stale_watcher import StaleConfig, escalate_stale_cards, is_stale
        cfg = StaleConfig(threshold_hours=24.0, human_assignee="human-reviewer")
        _, cr = self._stuck_card(hours_stale=30.0)  # well past threshold
        self.assertTrue(is_stale(cr, cfg=cfg))
        counters = escalate_stale_cards(
            [cr], client=self.fake, cfg=cfg,
            comment_factory=format_escalation_comment,
        )
        self.assertEqual(counters["posted"], 1)
        self.assertEqual(counters["reassigned"], 1)
        self.assertEqual(counters["errors"], 0)

        # Comment landed on the right card with the right markers
        self.assertEqual(len(self.fake.comments), 1)
        tid, body = self.fake.comments[0]
        self.assertEqual(tid, "t_stuck01")
        self.assertIn(ESCALATION_COMMENT_MARKER, body)
        self.assertIn("Action required", body)
        self.assertIn("`src/shared.py`", body)
        self.assertIn("conflict-report JSON", body)
        # The conflict report payload includes the manual-conflict list and
        # the stale_hours timestamp.
        self.assertIn("manual_conflict_files", body)
        self.assertIn("stale_hours", body)

        # Reassignment was recorded
        self.assertEqual(self.fake.assigns, [("t_stuck01", "human-reviewer")])

    def test_already_escalated_flag_prevents_double_post(self) -> None:
        from stale_watcher import StaleConfig, escalate_stale_cards
        cfg = StaleConfig(threshold_hours=24.0)
        _, cr = self._stuck_card(hours_stale=48.0)
        # Pass the card through once
        c1 = escalate_stale_cards(
            [cr], client=self.fake, cfg=cfg,
            comment_factory=format_escalation_comment,
        )
        self.assertEqual(c1["posted"], 1)
        # In-memory object now has escalated=True; calling again is a no-op.
        # Use a *fresh* copy of the same data but with escalated=False to
        # confirm the marker-flag would normally guard against repeats.
        self.assertTrue(cr.escalated)
        c2 = escalate_stale_cards(
            [cr], client=self.fake, cfg=cfg,
            comment_factory=format_escalation_comment,
        )
        self.assertEqual(c2["posted"], 0)
        self.assertEqual(c2["skipped_already"], 1)
        # Still exactly one comment in the fake
        self.assertEqual(len(self.fake.comments), 1)

    def test_threshold_is_per_stale_config(self) -> None:
        # A 22h-old conflict with a 12h threshold should escalate.
        from stale_watcher import StaleConfig, escalate_stale_cards
        cfg = StaleConfig(threshold_hours=12.0)
        _, cr = self._stuck_card(hours_stale=22.0)
        counters = escalate_stale_cards(
            [cr], client=self.fake, cfg=cfg,
            comment_factory=format_escalation_comment,
        )
        self.assertEqual(counters["posted"], 1)


# ---------------------------------------------------------------------------
# End-to-end via run-once on both kinds of cards
# ---------------------------------------------------------------------------


class EndToEndRunOnceTests(unittest.TestCase):
    """Drive `run_once` with one happy + one sad card at the same time."""

    def setUp(self) -> None:
        self.fake = FakeKanban()
        orchestrator.set_client(self.fake)
        # Override dashboard path so the real docs/ directory isn't touched.
        self.dash_dir = tempfile.mkdtemp(prefix="mr-orch-e2e-")
        self.dash_path = Path(self.dash_dir) / "merge-review-dashboard.md"
        os.environ["MERGE_REVIEW_DASHBOARD"] = str(self.dash_path)
        self.addCleanup(self._cleanup)

    def _cleanup(self) -> None:
        import shutil
        shutil.rmtree(self.dash_dir, ignore_errors=True)
        os.environ.pop("MERGE_REVIEW_DASHBOARD", None)

    def test_run_once_handles_both_cards(self) -> None:
        now = _now_epoch()

        # Card A — happy: clean-merge + QA pass, 10 min old
        card_a = {
            "id": "t_e2e_a",
            "title": "Happy card",
            "status": "done",
        }
        run_a = _run_with_meta(
            "t_e2e_a", 100,
            {
                "review_status": "clean-merge",
                "review_branch": "feature/happy",
                "review_base_branch": "master",
                "review_exit_code": 0,
                "review_reviewed_at": now - 600,
                "review_qa_verdict": {
                    "overall": "pass",
                    "acs": {"total": 1, "met": 1, "unmet": []},
                    "reasons": [],
                    "unmet_acs": [],
                },
            },
        )

        # Card B — sad: real-conflict, 30h old
        card_b = {
            "id": "t_e2e_b",
            "title": "Sad card",
            "status": "done",
        }
        run_b = _run_with_meta(
            "t_e2e_b", 101,
            {
                "review_status": "real-conflict",
                "review_branch": "feature/sad",
                "review_base_branch": "master",
                "review_exit_code": 1,
                "review_reviewed_at": now - 30 * 3600,
                "review_manual_conflict_files": ["x.py"],
                "review_conflicts": ["x.py"],
            },
        )

        # Card C — fresh stuck, should NOT escalate (under threshold)
        card_c = {
            "id": "t_e2e_c",
            "title": "Stuck but fresh",
            "status": "done",
        }
        run_c = _run_with_meta(
            "t_e2e_c", 102,
            {
                "review_status": "qa-fail",
                "review_branch": "feature/fresh-stuck",
                "review_base_branch": "master",
                "review_exit_code": 1,
                "review_reviewed_at": now - 60,
                "review_qa_verdict": {
                    "overall": "fail",
                    "acs": {"total": 1, "met": 0, "unmet": ["AC1"]},
                    "reasons": ["AC1 unmet"],
                    "unmet_acs": ["AC1 unmet"],
                },
            },
        )

        self.fake.seed([card_a, card_b, card_c])
        self.fake.seed_runs("t_e2e_a", [run_a])
        self.fake.seed_runs("t_e2e_b", [run_b])
        self.fake.seed_runs("t_e2e_c", [run_c])

        rc = orchestrator.cmd_run_once(argparse.Namespace())
        self.assertEqual(rc, 0)

        # Two comments total: one ready-to-merge on A, one escalation on B.
        # C is fresh so no escalation.
        task_ids_commented = {tid for (tid, _) in self.fake.comments}
        self.assertIn("t_e2e_a", task_ids_commented)
        self.assertIn("t_e2e_b", task_ids_commented)
        self.assertNotIn("t_e2e_c", task_ids_commented)

        # The ready-to-merge comment went to A, the escalation to B.
        a_comments = [b for (tid, b) in self.fake.comments if tid == "t_e2e_a"]
        b_comments = [b for (tid, b) in self.fake.comments if tid == "t_e2e_b"]
        self.assertTrue(any(READY_COMMENT_MARKER in c for c in a_comments))
        self.assertTrue(any(ESCALATION_COMMENT_MARKER in c for c in b_comments))

        # B was reassigned to a human
        self.assertIn(("t_e2e_b", "human-reviewer"), self.fake.assigns)

        # The dashboard was written and mentions both A and B but not C
        self.assertTrue(self.dash_path.exists())
        dash_text = self.dash_path.read_text(encoding="utf-8")
        self.assertIn("t_e2e_a", dash_text)
        self.assertIn("t_e2e_b", dash_text)


# Need to import argparse here because cmd_run_once expects a Namespace
import argparse  # noqa: E402


# ---------------------------------------------------------------------------
# Dashboard unit tests
# ---------------------------------------------------------------------------


class DashboardFormatTests(unittest.TestCase):
    def test_empty_dashboard(self) -> None:
        md = format_dashboard([])
        self.assertIn("Merge-review dashboard", md)
        self.assertIn("no reviews yet", md.lower())

    def test_caps_rows_at_max(self) -> None:
        # Create 15 fake entries (newest first)
        entries = []
        for i in range(15):
            entries.append(DashboardEntry(
                task_id=f"t_x{i:02d}",
                title=f"Title {i}",
                branch=f"feature/b{i}",
                base_branch="master",
                review_status="clean-merge",
                exit_code=0,
                n_manual_conflicts=0,
                n_auto_resolved=0,
                reviewed_at=1_000_000_000 + i,
                age_hours=1.0,
                is_ready=True,
            ))
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "d.md"
            n = rebuild_dashboard(path, entries)
            self.assertEqual(n, DASHBOARD_MAX_ROWS)
            text = path.read_text(encoding="utf-8")
            # Newest (t_x14) is in the output, the 15th oldest (t_x00) is NOT
            self.assertIn("t_x14", text)
            self.assertNotIn("t_x00", text)
            # t_x09 — the 10th-newest — IS in the output (slice keeps last 10)
            self.assertIn("t_x05", text)
            # t_x04 — 11th-newest — must be dropped to honor the cap
            self.assertNotIn("t_x04", text)
            # Sanity: the table has exactly DASHBOARD_MAX_ROWS data rows
            data_rows = [line for line in text.splitlines()
                         if line.startswith("| ") and "`t_x" in line]
            self.assertEqual(len(data_rows), DASHBOARD_MAX_ROWS)

    def test_status_emoji_map(self) -> None:
        e = DashboardEntry(
            task_id="t_e", title="t", branch="b", base_branch="master",
            review_status="real-conflict", exit_code=1,
            n_manual_conflicts=2, n_auto_resolved=0,
            reviewed_at=_now_epoch(), age_hours=2.0, is_ready=False,
        )
        md = format_dashboard([e])
        # real-conflict is the collision emoji, not a ready-to-merge rocket
        self.assertIn(":collision:", md)
        # Negative check: the entry itself doesn't carry the ready-mark
        # (the legend mentions `:rocket:` in a separate line, so use a
        # substring check scoped to the data row).
        data_row_line = next(
            line for line in md.splitlines()
            if line.startswith("| :collision:")
        )
        self.assertNotIn(":rocket:", data_row_line)


if __name__ == "__main__":
    unittest.main(verbosity=2)
