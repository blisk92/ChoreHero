# 05: Points ledger and balance

**What to build:** Completing a non-review-flagged chore awards points immediately and durably. A `PointsLedger` row is appended at completion time with the chore's point value, attributable to the child. The kid device's points badge reads `SUM(delta)` for the child (or whatever the equivalent in the chosen query layer is); the parent dashboard shows the same number for the child profile.

This is intentionally a thin slice — it deepens ticket 04 by giving completion a tangible numeric outcome. Review-flagged chores are still gated in this ticket (no points until approval lands in ticket 07).

**Blocked by:** 04

**Status:** ready-for-agent

- [ ] On `claimed → completed` for a non-review-flagged chore, the API appends a `PointsLedger` row with `delta = chore.point_value`, `source = "chore"`, `source_id = chore.id`, attributed to the child.
- [ ] The kid device's points badge derives from the ledger (running balance), not a denormalised column on `Child`. Balance updates without a manual refresh.
- [ ] Parent dashboard shows the child's current balance in the same numbers the kid sees.
- [ ] Review-flagged chores do NOT append a ledger entry in this ticket — the gated flow is ticket 07.
- [ ] API contract tests: ledger-append on completion, balance query, idempotency (replaying the same completion event doesn't double-credit).
- [ ] Playwright e2e extension: after the ticket 04 loop completes, the parent dashboard shows the kid's balance equal to the chore's point value, and the kid device shows the same number.
- [ ] Domain vocabulary: the kid-facing label is **Points** (singular), not "coins" or "tokens". Internal column names match the schema (e.g. `PointsLedger.delta` is signed integer).
