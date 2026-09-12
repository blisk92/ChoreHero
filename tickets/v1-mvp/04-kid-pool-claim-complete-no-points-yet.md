# 04: Kid pool, claim, and complete (no points yet)

**What to build:** The first complete loop through every layer. Parent creates a chore (recurring or one-off, point value, review flag off). The chore appears in the kid device's "Available Extras" section within ~5s. Kid claims it (status flips to `claimed`) — it moves to "My Active". Kid marks it complete. Parent's dashboard reflects the completed chore within ~5s via a real WebSocket push (not polling). No points ledger, no rewards, no streak — the deliverable is the closure of the loop and nothing more.

This ticket is the **loop-closure tracer bullet** per the spec's implementation sequencing. Once it lands, every subsequent ticket is a feature deepening an already-working loop.

**Blocked by:** 03

**Status:** ready-for-agent

- [ ] Parent can create a chore with: name, point value (positive integer), review flag (boolean), kind (recurring | one-off). For one-off, `due_at` is accepted but **not required** in this ticket (deadline-driven `expired` transitions land in ticket 08).
- [ ] Created chore appears on the kid device's "Available Extras" section within ~5s without a parent-triggered refresh (real WebSocket push from the API to the parent is sufficient; the kid device pulls on focus until kid-side push lands in a later ticket).
- [ ] Kid can claim a chore with one tap. The chore's `Chore.status` flips `pool → claimed`; the kid device shows it in "My Active"; the chore disappears from "Available Extras" for any other claim attempts (one-claim-at-a-time).
- [ ] Kid can mark the claimed chore complete. Status flips `claimed → completed`. The chore disappears from "My Active".
- [ ] For a non-review-flagged chore, the parent sees "Billy completed [chore]" in their dashboard within ~5s via a real WebSocket event from the API. The WS connection carries a JWT-authenticated parent session; events are fanned out per household.
- [ ] WebSocket auth follows the spec recommendation: JWT in a query param on the handshake for v1.
- [ ] Playwright e2e covers the whole slice in two browser contexts: parent creates a chore → kid device shows it in Available Extras → kid claims → My Active shows it → kid completes → parent dashboard shows the completion event within 5s. **This is the demo for the loop.**
- [ ] Chore state-machine unit tests cover the **non-expiry** transitions of this ticket: `pool → claimed`, `claimed → completed`, `claimed → pool` (skip on recurring). The review-flagged and deadline-expiry transitions land in tickets 07 and 08 respectively and are NOT tested here.
- [ ] Per-field last-write-wins primitive from ticket 01 is exercised: if the parent edits the chore's point value while the kid has it claimed, the parent's edit applies because it carries a newer `updated_at` for that field and does not touch the status.
- [ ] Domain vocabulary: parent SPA calls this surface "Chores" and uses the term **Claim** / **Complete** in copy per `CONTEXT.md`.
