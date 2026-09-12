# 07: Recurring streak and review-flagged approval

**What to build:** Two deepens of the existing loop that share the same parent-decides shape:
1. **Streak** — a denormalised projection on each recurring chore that increments on each completion-day and resets when a calendar day passes without one. Surfaces on the kid device home screen (with the kid's avatar in celebratory moments, per `CONTEXT.md` mascot rule) and on the parent view.
2. **Review-flagged chore approval** — when a kid completes a review-flagged chore, no points are awarded yet. Parent sees a pending approval in their dashboard with the kid's name, the chore, and the cost; parent Approves (ledger appended, chore fully resolved) or Denies (chore returns to `pool`, no ledger entry, kid notified).

These two land in the same ticket because they share the parent's "approve / deny" decision UI on the parent dashboard — building them together amortises that surface. Out of scope: per-reward proposal flow (already specified as out for v1), streak milestone notifications (ticket 08), deadline expiry (ticket 08).

**Blocked by:** 06

**Status:** ready-for-agent

- [ ] `Streak` row exists per recurring chore with `current_length`, `longest_length`, `last_completed_on`.
- [ ] On `claimed → completed` for a recurring chore, the streak projection is updated using an injected clock: if `today - last_completed_on` is exactly 1 calendar day, increment; if greater, reset to 1; if same day, leave unchanged (idempotent completion).
- [ ] Kid device home shows the streak count under each recurring chore ("🔥 5-day streak on Make bed").
- [ ] Parent dashboard shows the same streak counts.
- [ ] On `claimed → completed` for a review-flagged chore, the chore transitions to a `pending_review` state (or equivalent — implementation detail, but the contract is: no ledger entry until parent approves).
- [ ] Parent dashboard surfaces a pending review list with Approve / Deny per item. Approve → ledger entry appended → chore stays in `completed` for this resolution. Deny → chore returns to `pool` → no ledger entry → kid notified.
- [ ] Unit tests on the chore state machine cover the corners e2e can't easily drive: claim → skip (recurring: → pool, streak untouched), claim → complete (recurring: streak advances), claim → skip → re-claim (recurring: pool remains), review-flagged denied → pool with no ledger entry, deadline skip (lands in ticket 08 — placeholder here so the test list stays complete).
- [ ] Per `CONTEXT.md`: kid voice remains cheerful-but-not-theatrical; celebratory moments get one phrase each (e.g. "5-day streak — nice work!").
- [ ] Per ADR-0001: nothing here requires an additional kid identity surface — streaks, reviews, and approvals all route through existing parent SPA and kid SPA surfaces.
