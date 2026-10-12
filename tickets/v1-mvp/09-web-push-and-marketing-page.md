# 09: Web push opt-in and marketing page

**What to build:** The last two surfaces, both thin: web push opt-in for the parent (using VAPID keys via the `web-push` library), and a static marketing landing page served by nginx. Final empty-state illustrations ship here, palette tokens are applied across both SPAs, and a final visual pass lands. This is the v1 release-candidate ticket — once it merges, v1 ships.

Web push is parent-only and opt-in per parent device, default off. Adding it here (rather than as part of ticket 08) lets the notifications ticket focus on the in-app surface that's always on.

**Blocked by:** 08

**Status:** ready-for-agent

- [ ] Parent SPA has a "Notifications" toggle in settings that opts the current parent device into web push. Default off.
- [ ] When opted in, the parent device registers a push subscription with the API (VAPID public key hand-shake). API stores the subscription per parent device.
- [ ] When a parent-ping event fires (the same set as ticket 08), if the parent is offline (parent SPA not in foreground), the push notification is delivered to opted-in devices only.
- [ ] Opt-out disables the subscription. Revoked kid device subscriptions don't get push (different table — kid devices only have in-app notifications per `CONTEXT.md`).
- [ ] VAPID keys are generated and stored as environment variables; rotation procedure is documented in the API's README.
- [ ] Marketing landing page lives at the root URL and renders the tagline ("Your chores. Your points. Your rewards.") plus a sign-up / sign-in entry.
- [ ] Empty-state illustrations ship on both SPAs per `CONTEXT.md` (kid no-chores illustration, welcome screen, parent first-chore CTA illustration, parent first-reward CTA).
- [ ] Palette tokens (deep violet primary, sunshine yellow accent) are defined once and applied across both SPAs; parent-side surfaces get the quieter-accent variant per `CONTEXT.md`.
- [ ] mascot: the kid's avatar appears in celebration surfaces (milestone, redemption approved) — verified by visual snapshot in the e2e flow run from ticket 07.
- [ ] E2E regression net: the full Playwright e2e from ticket 04 still passes against the new build, and a new Playwright e2e verifies the marketing page renders and the sign-up entry routes into the parent SPA.
- [ ] v1 changelog / release notes entry added.
