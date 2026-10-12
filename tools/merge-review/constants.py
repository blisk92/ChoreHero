#!/usr/bin/env python3
"""
constants.py — shared constants for the merge-review orchestrator suite.

Kept dependency-free so modules like orchestrator.py and stale_watcher.py can
import from it without triggering a circular import.
"""

from __future__ import annotations

# Verdict values produced by trigger.py / merge_review.py
READY_VERDICTS = frozenset({"clean-merge", "trivial-auto-merge"})
STUCK_VERDICTS = frozenset({"real-conflict", "qa-fail", "error"})

# Inline HTML markers so the orchestrator can tell which comments it posted
# vs. which were posted by trigger.py or by humans.
READY_COMMENT_MARKER = "<!-- orchestrator:ready-to-merge -->"
ESCALATION_COMMENT_MARKER = "<!-- orchestrator:stale-escalation -->"
