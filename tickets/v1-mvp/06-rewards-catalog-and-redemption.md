# 06: Rewards catalog and redemption (approve / deny / reverse)

**What to build:** The rewards side of the loop. Parent adds a reward to the catalog (name, point cost, optional `stock_remaining`). Kid device surfaces a Redeem screen listing the catalog with each reward's cost. Kid taps a reward → server creates a `Redemption` row with `status = pending`. Parent dashboard shows pending redemptions with the kid's name, the reward, and the cost; parent taps Approve or Deny (with optional reason). Approval debits the `PointsLedger` (negative delta) and notifies the kid; denial notifies the kid without touching the ledger. Parent can reverse a previously approved redemption (one-tap safety valve), which adds an opposite-sign ledger entry and notifies the kid.

This closes the **redemption half of the loop**. Review-flagged chore approval lands in ticket 07 — both flows share the same "parent decides" shape and intentionally land in different tickets to keep each one demoable on its own.

**Blocked by:** 05

**Status:** ready-for-agent

- [ ] Parent can create a reward with name, point cost (positive integer), optional description, optional `stock_remaining` (positive integer).
- [ ] Catalog is permanent by default — rewards are visible until the parent deletes them. Deleting a reward does not retroactively affect completed redemptions (they remain in audit history).
- [ ] Kid device shows a Redeem screen listing every reward with cost. Disabled / greyed out if the kid's current balance is below the cost.
- [ ] Kid taps an affordable reward → server creates a `Redemption` row (`status: pending`, `requested_at = now`) → parent dashboard reflects the new pending request in-app within ~5s.
- [ ] Parent Approve → ledger entry `delta = -point_cost` → kid notified → reward's `stock_remaining` decremented if it was set.
- [ ] Parent Deny with optional reason → no ledger entry → kid notified with the reason if present.
- [ ] Approve requires the kid's balance to still cover the cost at click-time; if it doesn't (race), parent sees a clear "Not enough points" message and the redemption stays pending.
- [ ] A reward with `stock_remaining = 0` does not appear in the kid's redeem list (or appears disabled with a "Out of stock" hint).
- [ ] Parent can reverse a previously approved redemption from the redemption history view. Reversal appends a positive ledger entry equal to the cost, sets `status = reversed`, notifies the kid.
- [ ] Playwright e2e: parent adds a reward → kid requests redemption → parent approves → ledger debits → kid device reflects the lower balance. A second e2e covers the deny path. A third covers reversal.
- [ ] API contract tests: redemption-create happy-path, approve-debits-ledger, deny-no-ledger-effect, reverse-credits-ledger, out-of-stock rejection, insufficient-balance rejection.
- [ ] Domain vocabulary: kid surfaces call this **Redeem** and the pending state **Waiting for a parent** (per `CONTEXT.md`).
