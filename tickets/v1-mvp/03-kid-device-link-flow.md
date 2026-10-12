# 03: Kid device link flow

**What to build:** The end-to-end flow that turns a fresh browser context into a kid device registered to a specific child profile inside a household. The parent opens a "Link a kid device" screen that lazy-generates the household code (and its hash row) and displays both a QR code encoding the link payload and the 6-character alphanumeric code as fallback. A second browser context (the kid device) scans the QR — e2e submits the same payload via the API — and lands on the kid kiosk shell holding a device token. The parent sees the new device in settings with a friendly name (parent names it at link time) and a "last seen" timestamp, and can revoke the device which signs it out on next sync.

This ticket honors ADR-0001 by treating the `KidDevice` as the unit of kid identity — there is no kid login, no PIN, no cross-device kid session. Two devices linked to the same child produce two independent `KidDevice` rows; v2 siblings get the same model for free.

**Blocked by:** 02

**Status:** ready-for-agent

- [ ] First tap on "Link a kid device" generates a `HouseholdCode` row whose plaintext 6-character alphanumeric code (no `0/O/1/I/L`) is shown once alongside its QR-encoded payload, and whose hash is stored server-side. The plaintext code is never written to the DB — only the hash.
- [ ] Subsequent taps show the same code (not regenerated) until the parent taps "Regenerate" in settings, which rotates the code and immediately invalidates any pre-rotation link attempts.
- [ ] QR payload contains everything the kid device needs to register itself (link URL or compact token). Kid device scans → POSTs the payload → server validates the hash → creates a `KidDevice` row with a freshly issued `device_token_hash` → returns the device token in the response (held by the kid device, used for all kid-side API calls).
- [ ] Parent names the kid device at link time ("Billy's tablet", "iPad in kitchen"). The name is displayed in the settings list alongside `last_seen_at`.
- [ ] Revoking a kid device flips a row flag and forces the device to re-authenticate on next API call; the kid device lands back on the link screen.
- [ ] Playwright e2e exercises the full link: parent opens link screen → kid context scans → kid context lands on the empty kiosk welcome ("Welcome, [name]!" with the kid's avatar) → parent sees the new device in settings with a friendly name → revoke → kid context's next action signs it out.
- [ ] Kid device kiosk shell renders only the kid surfaces (per `CONTEXT.md`): Today, Points, Streaks, Redeem. No parent-side nav is reachable from the kid device.
- [ ] API contract tests: link-creation accept/happy path, link-creation reject when code is wrong, regenerate invalidates prior token, revoke invalidates active token.
