# ChoreHero v1 — Spec

> Synthesised from `IDEA.md` and the `grill-with-docs` session that produced `CONTEXT.md` and `docs/adr/0001-kid-identity-is-the-device.md`. Vocabulary throughout follows `CONTEXT.md`; the device-as-identity rule is locked by ADR-0001.

## Problem Statement

Parents want their child to do chores without nagging. Children want recognition and small rewards for what they do, not a lecture. Today the loop looks like: parent reminds, child resists or forgets, parent reminds harder, child does it once, no one remembers by the next morning. There's no durable record, no earned reward, no celebration. The friction is high on the parent side (remembering, enforcing, rewarding consistently) and low-stakes on the child side (no incentive stronger than avoiding a parent's frown).

ChoreHero replaces the daily nag with a system where: the parent writes down what they want done, the child picks what they want to do first, points accrue as a visible running balance, streaks reward consistency, and a parent-approved reward catalog gives the child a real thing to spend points on — turning chores into a game the child actually wants to play.

## Solution

A PWA with two device shapes (parent and kid) for a single household. Parents sign up, build a chore pool and a reward catalog, and link a kid device by scanning a QR code. Children open the kid device, see their pool of available chores and their active claim, mark chores done to earn points, watch their streaks climb, and tap to request a reward redemption that the parent approves. Synchronisation works offline-first: the kid device never blocks on a network round-trip to claim or complete a chore; mutations queue locally and replay against the backend when the network returns. The parent sees the kid's activity update in-app within a few seconds when both devices are online.

In v1, a household contains exactly one parent and one child. The product is built and validated for that single shape; v2 widens it without rewriting v1's data model.

## User Stories

### Onboarding & Identity

1. As a parent, I want to sign up with an email and password, so that I have a stable identity across devices and re-installs.
2. As a parent, I want to sign in faster with Google or Apple, so that I don't have to remember yet another password.
3. As a parent, I want the app to create a household for me at signup, so that I don't have to configure anything before adding chores.
4. As a parent, I want to create a child profile with a name and an avatar, so that the kid device feels personal to my kid.
5. As a parent, I want to generate a QR code and a 6-character household code from a "Link a kid device" button, so that I can link a new device in seconds.
6. As a parent, I want the household code to stay permanent unless I regenerate it, so that re-linking a device weeks later doesn't require a fresh code.
7. As a parent, I want to regenerate the household code from settings, so that I can cut off a device that left the household unexpectedly.
8. As a parent, I want to see a list of every kid device linked to my household with a friendly name and last-seen timestamp, so that I can revoke a device that was lost or shared.
9. As a kid, I want my device to show "Welcome, [name]!" with my avatar on first launch, so that the app feels like it's mine.

### Chores & Pools

10. As a parent, I want to create a chore with a name, a point value, an optional review flag, and optionally a deadline, so that the chore matches the work I want done.
11. As a parent, I want to choose whether a chore is recurring (re-enters the pool after completion) or one-off (stays gone after one resolution), so that the chore's lifecycle matches the real-world rhythm.
12. As a parent, I want to edit or delete a chore that is in a pool, so that I can correct typos and remove chores that no longer apply.
13. As a parent, I want to set a deadline on a one-off chore, so that I get notified if my kid doesn't complete it in time.
14. As a parent, I want to mark a chore as review-flagged, so that I get a chance to verify before points are awarded.
15. As a kid, I want to see every claimable chore in my "Available Extras" section, so that I always know what's on offer.
16. As a kid, I want to claim a chore with one tap, so that I can start working on it immediately.
17. As a kid, I want to see my currently active chores in a separate "My Active" section, so that I don't claim the same chore twice by accident.
18. As a kid, I want to mark an active chore done, so that I earn its points.
19. As a kid, I want to skip an active chore I no longer want, so that it doesn't sit in my active list forever.
20. As a kid, I want to see the streak count for a recurring chore, so that I'm reminded of my consistency.

### Points & Streaks

21. As a kid, I want to see my current point balance prominently on the home screen, so that I always know what I've earned.
22. As a kid, I want my balance to update the moment I complete a non-review-flagged chore, so that the reward feels immediate.
23. As a parent, I want to see my child's running balance on my dashboard, so that I can answer "How many points do you have?" from memory later.
24. As a kid, I want a streak to climb on a recurring chore when I complete it on consecutive days, so that consistency feels rewarded.
25. As a kid, I want my streak to reset when I miss a day, so that the streak remains meaningful.
26. As a parent, I want to see my child's per-chore streaks, so that I can spot patterns (e.g. "they always skip Trash Duty").
27. As a kid, I want a milestone notification when I hit a streak like 7 or 30 days, so that the streak feels celebrated.

### Rewards & Redemption

28. As a parent, I want to create a reward with a name, a point cost, and an optional stock limit, so that I can shape what my child is working toward.
29. As a parent, I want to see a list of all my rewards, so that I can edit or remove them as life changes.
30. As a kid, I want to browse the reward catalog and see what each reward costs, so that I know what's within reach.
31. As a kid, I want to tap a reward to request redemption, so that the parent gets a chance to approve.
32. As a parent, I want to see pending redemption requests on my dashboard with the kid's name, the reward, and the cost, so that I can decide quickly.
33. As a parent, I want to approve a redemption with one tap, so that the kid's points are deducted and the kid is notified immediately.
34. As a parent, I want to deny a redemption with an optional reason, so that the kid understands and I have a record.
35. As a parent, I want to reverse a redemption I previously approved, so that I can recover points if the reward wasn't actually delivered.
36. As a parent, I want a reward with `stock_remaining: 3` to refuse redemptions once the stock runs out, so that I don't over-promise on a limited reward.

### Notifications

37. As a parent, I want a notification when my child completes a review-flagged chore, so that I know there's a decision waiting for me.
38. As a parent, I want a notification when a deadline chore expires, so that I know a chore went uncompleted.
39. As a parent, I want a notification when my child requests a redemption, so that I can act on it.
40. As a parent, I want a notification when a recurring pool is empty, so that I can add new chores before the kid gets bored.
41. As a kid, I want a notification when a new chore lands in my pool, so that I notice new opportunities.
42. As a kid, I want a celebratory notification when I hit a streak milestone, so that the streak feels special.
43. As a kid, I want to be notified when a point increase lands after parent approval, so that I notice the reward.
44. As a kid, I want to be notified when a redemption is approved or denied, so that I know the outcome.
45. As a parent, I want to opt in to web push on a per-device basis, so that I get lock-screen pings when the app is closed.

### Sync & Offline

46. As a kid, I want to claim and complete chores even when the kid device is offline, so that the app works in the basement or on a flaky cellular connection.
47. As a parent, I want my dashboard to reflect the kid's latest activity within a few seconds when both devices are online, so that the loop feels real-time.
48. As a parent, I want edits my kid made offline to flow in cleanly when their device reconnects, so that I don't have to retype anything.
49. As a parent, I want conflicting edits to a chore's point value to resolve predictably (last-write-wins per field), so that I never lose data without knowing.

### Empty States & Onboarding Nudges

50. As a parent with no chores yet, I want a clear "Add your first chore" CTA, so that I know exactly what to do next.
51. As a parent with no rewards yet, I want a clear "Add your first reward" CTA with example suggestions, so that I can set up a reward in under a minute.
52. As a kid with no chores in either pool, I want to see "No chores yet. Ask a parent to add some." with a small illustration, so that I'm not staring at a blank screen.
53. As a kid on first link before any chore exists, I want a welcome screen with my name and avatar, so that I have a friendly first impression.

### Visual Identity

54. As a kid, I want my chosen avatar to appear in celebratory moments (milestone, redemption approved), so that the app feels personal.
55. As a parent, I want a clean, adult-friendly parent-side surface, so that the app doesn't look like a toddler's toy on my phone.

## Implementation Decisions

### Modules (high-level)

- **Marketing / public pages.** Static SPA served by nginx. Contains the landing page with the tagline, a sign-in entry, and a sign-up entry. No data behind it except a "create household" call on sign-up success.
- **Parent SPA.** Vue 3 single-page app. The parent's main experience: dashboard, chore management, reward catalog, redemption approval queue, settings (kid devices, household code, account).
- **Kid SPA.** Vue 3 single-page app, kiosk-shaped. Today (Available Extras / My Active), Points, Streaks, Redeem. Barely any chrome, no parent-side nav.
- **Express API.** REST endpoints for parent CRUD, redemption lifecycle, kid claims/completes/skips, and a device-linking handshake. JWT-authenticated for parent endpoints; device-token-authenticated for kid endpoints.
- **WebSocket layer.** A `ws`-based channel per parent session for "kid device activity stream" pushes. The kid device POSTs to the REST API; the API publishes a webhook into the WS layer; the parent's open WebSocket fan-outs the event. No kid-to-kid, no parent-to-parent; only kid-activity-to-parent.
- **MariaDB schema managed by Prisma.** Migrations live alongside the API repo. See schema sketch below.
- **Offline mutation queue.** A Dexie.js store on both parent and kid devices, holding pending mutations with a per-field `updated_at` and a stable operation ID for idempotency on replay.

### Schema (Prisma sketch — decision-rich, not exact)

```
Household { id, name?, created_at }
Parent { id, household_id, email, password_hash, oauth_provider?, oauth_subject?, created_at }
Child { id, household_id, name, avatar_id, created_at }
KidDevice { id, child_id, household_id, device_token_hash, friendly_name,
            last_seen_at, installed_at, revoked_at? }
HouseholdCode { household_id (unique), code_hash, created_at }
Chore { id, household_id, name, point_value, review_flagged, kind: recurring|one_off,
        due_at?, status: pool|claimed|completed|skipped|expired,
        claimed_by_child_id?, claimed_at?, created_at, archived_at? }
Streak { chore_id, current_length, longest_length, last_completed_on }
Reward { id, household_id, name, point_cost, description?, stock_remaining? }
Redemption { id, household_id, child_id, reward_id, status: pending|approved|denied|reversed,
             requested_at, resolved_at?, denial_reason? }
PointsLedger { id, child_id, delta, source: chore|redemption|reversal, source_id, created_at }
Notification { id, recipient_kind: parent|kid_device, recipient_id, kind, payload_json, read_at, created_at }
```

Notes on the sketch:

- The chore state machine lives entirely in `Chore.status`. There's no separate "claim" table — a claim *is* a state on the chore with `claimed_by_child_id` and `claimed_at`.
- `Streak` is a denormalised projection, not a derived calculation, so the kid device and parent UI can read it without scanning history. The reducer updates it whenever a `Chore` resolves with `kind: recurring`.
- `PointsLedger` is an append-only log; the current balance is `SUM(delta)` filtered to child. This makes reward approval/decline/reversal trivial to audit and roll back.
- `HouseholdCode.code_hash` stores a hash, not the code itself. The plaintext 6-character code is only ever held by the generating parent device.

### Authoritative rules from `CONTEXT.md`

These crystallised terms bind every module that touches them:

- **Chore lifecycle:** recurring auto-resets to pool after complete or skip; one-off with deadline → `expired` on skip or non-completion by `due_at`; one-off without deadline → returns to pool on skip; parent notified on `expired`.
- **Review flag:** kid marks done → if review-flagged, parent approval gates the `PointsLedger` insert. Otherwise the ledger entry is appended immediately.
- **Kid identity:** identity at the kid layer is the `KidDevice`, not the child. ADR-0001.
- **Household code generation:** lazy, on first "Link a kid device" tap. Regenerable. QR + 6-char alphanumeric (no 0/O, 1/I/L).
- **Rewards:** parent-catalogued only in v1. Permanent by default; per-reward optional `stock_remaining`. Kid cannot propose rewards in v1.
- **Redemption:** parent approves at catalog price or denies (no counter). Approval → points deducted, kid notified. Reversal → points returned, kid notified.
- **Empty states:** see `CONTEXT.md` for the specific copy on each of the 5 surfaces (welcome variant, no-chores kid, 0-point kid, parent first chore, parent first reward).
- **Tone:** parent voice quietly functional; kid voice cheerful but not theatrical; tagline "Your chores. Your points. Your rewards."

### State machine (the only logic that was prototype-shaped enough to inline)

```
Chore.status transitions:

                ┌──── (kid taps claim) ◄──── child claims it
                │
   pool ────────┤
                │
                └──── (kid taps skip on a claimed chore that is recurring)
                              │
                              ▼
                          (back to pool)

Claimed state transitions:
   claimed → completed   (kid taps done; non-review-flagged: points now;
                          review-flagged: pending parent approval)
   claimed → skipped     (kid taps skip)
                          recurring: → pool
                          one-off, deadline: → expired
                          one-off, no deadline: → pool
   claimed → expired     (one-off, deadline; due_at passed without complete)

Completed state:
   completed (non-review-flagged): terminal for this resolution.
   completed (review-flagged): points awarded when parent approves.
                                 parent denial → chore returns to pool,
                                 no points awarded.
```

This is the only piece of logic that's tight enough to deserve pinning in the spec rather than scattering across modules.

### Tech stack summary

- Frontend: Vue 3 + Vite + vite-plugin-pwa (Workbox strategies underneath)
- Backend: Node.js + Express + Prisma (against MariaDB)
- Local store: Dexie.js over IndexedDB
- Auth: email + password (bcrypt), optional Google / Apple OAuth via Passport.js strategies
- Sync visibility: WebSocket (`ws` library) carrying per-household kid-activity events
- Push notifications: web-push library + VAPID keys, opt-in per parent device
- Hosting: self-hosted via Docker Compose — `nginx` (TLS + static assets), `node` (API + WS), `mariadb` (state). One Compose file. Volume for DB persistence.

### Architectural decisions

- **Two SPAs, one API.** The parent SPA and kid SPA share the API but have separate bundles, separate routes, and a different set of components. They are not branches in a single SPA; the kid experience is a kiosk and the parent's is a manager.
- **One MariaDB, one schema.** Households, parents, children, chores, rewards, redemptions, ledger, devices, codes, notifications. No document store, no cache layer beyond MariaDB itself. Scale by adding a `mariadb` read replica in v2 if needed.
- **Service worker strategies tuned per resource type.** App shell precached (cache-first, immutable). API GETs use network-first with cache fallback (so the kid UI feels instant offline but stays fresh online). Mutation requests go through Dexie first, never through the SW.
- **Per-field last-write-wins.** Each updatable column carries its own `updated_at`. The Dexie replay sends only the fields the local copy changed, with their original captured `updated_at` on the wire. The server applies if-and-only-if `received.updated_at > stored.updated_at` for that field. No CRDT, no vector clocks.
- **WebSockets for kid→parent visibility, polling fallback only for reconnects.** When the parent's WS is closed (background, network drop), the next dashboard open resumes via a single GET, and a fresh WS handshake is attempted in parallel.
- **Web push is opt-in per device, parent only.** Kid devices never receive a lock-screen push — in-app only.

## Testing Decisions

### Primary seam: Playwright end-to-end

The whole loop — parent signs up, creates child + chores + rewards, links a kid device, kid claims and completes, parent sees the activity, kid redeems, parent approves — is exercised by a single Playwright spec that drives two browser contexts (one parent, one kid). This is the demo, the smoke test, and the regression net.

### Secondary seams

- **API contract tests** against a test MariaDB. Exercise the offline-mutation replay path (claim → offline → complete → reconnect → server applies both), the deadline expiry pass, and the redemption approval/reversal flow end-to-end without a browser.
- **Chore state-machine unit tests** on the reducer. Cover the off-by-one corners the e2e won't hit cheaply: claim → skip → re-claim; review-flagged denial → chore returns to pool without points; recurring skip after claim; one-off with deadline → expired at `due_at`.
- **Prisma migration smoke test** in CI. Boot a fresh MariaDB, apply migrations, assert schema version. Cheap; catches accidentally destructive migrations.

### What makes a good test for ChoreHero

- Test the contract, not the implementation. A test that asserts "kid taps claim → chore status becomes `claimed` and appears in My Active" is good. A test that asserts "the Dexie store now has a record with `status: claimed`" is brittle to the local-store refactor.
- Don't mock the WS layer; use a real WS in tests with a parent context open. Mocking the WS hides real desync bugs.
- For time-dependent logic (streaks, deadlines), inject a clock rather than sleeping. Sleeps make CI slow and flaky.

### What we explicitly aren't building into the test suite

- Comprehensive UI screenshot diffs. The UI will iterate.
- Property-based / fuzz testing on the reducer. The state machine is small enough that exhaustive explicit cases cover it.

## Out of Scope

Explicitly not in v1. Anything in this list that creeps into a "while we're at it" should be deferred:

- **Second parent account.** v1 supports exactly one parent.
- **Second child in the household.** v1 supports exactly one child.
- **Chore templates / curated starter library.** Parents create chores from scratch.
- **Sibling leaderboards, family-vs-family challenges, rivalry mechanics.** Individual progress only.
- **Kid account with cross-device sign-in or email.** Kid identity remains the kid device (ADR-0001).
- **Kid-proposed rewards or kid-proposed point costs.** Pre-defined catalog only; parent approves at listed price or denies.
- **Chore categories, age-conditional chores, chore difficulty tiers (Easy/Medium/Hard).** Single point value per chore, set by the parent.
- **Real-time video / photo proof for chores.** No upload pipeline in v1; review-flagged means parent looks with their own eyes.
- **Multi-day deadlines (e.g. "by Friday"), reminders to do a claimed chore, idle-chore nudges.** Streaks are the only behavioural pressure.
- **Streak milestone config.** Hardcoded set of milestones (every 7 days) for v1; configurable in v2.
- **In-app chat between parent and child.** Out.
- **Data export / child-data privacy controls (COPPA / GDPR).** Should be addressed before any external launch; not blocking local-only v1 build.
- **Native mobile wrappers (Capacitor / React Native shells).** PWA only.
- **Analytics dashboards beyond "what's pending and what's my kid's current balance".** No reporting.
- **Marketing / onboarding A/B tests, conversion funnels, paywall experiments.** Single user, single install.
- **Internationalisation.** English only.
- **Push notifications to kid devices.** Parent devices only, opt-in.

## Further Notes

### Open questions worth picking up before implementation starts

1. **Avatar set.** Does the kid pick from a pre-shipped SVG set (cheapest, consistent style), or does the parent upload a photo (more personal, more trust work)? My recommendation for v1 is a pre-shipped SVG set of ~12 hand-drawn-in-style characters so the visual identity stays consistent and there's no upload pipeline to build.
2. **Streak milestones.** Hardcoded set (`every 7 days`) or configurable per chore? My recommendation is hardcoded for v1, configurable per chore in v2.
3. **WebSocket auth.** JWT in a query param on handshake (simple), or short-lived ticket-exchange flow (safer, mirrors what e.g. Figma does). My recommendation is the simple JWT-in-query-param for v1 — kid device isn't a hostile actor; it's a device the parent registered.
4. **Backup / restore.** If the parent wipes their phone and reinstalls, they reset their password (email+password auth handles that) and the household is back. Kid devices need to be re-linked (new device tokens). Is that acceptable or do we need a per-household "recovery code" the parent saves offline? My recommendation is to defer until at least one parent reports the pain.
5. **What shows up on the parent's dashboard when there is no kid activity yet?** Recommend: a quiet "No activity yet" section plus the nudges called out in empty-state stories above. Nothing clever.

### Implementation sequencing (suggestion, not a contract)

A vertical slice that proves the whole loop works end-to-end before any single feature gets polished:

1. Auth + household + child profile + kid device link (no chores, no points).
2. Parent creates one chore; kid sees it in the pool and claims it; kid marks done; ledger entry appears.
3. Parent creates one reward; kid redeems; parent approves; ledger debits.
4. Recurring-chore streak logic.
5. Deadline expiry + parent notification.
6. Review-flagged chore approval loop.
7. Web push opt-in flow.
8. Marketing page.

Everything else (multiple rewards, empty-state illustrations, streak milestone copy, etc.) lands after the loop is closed and demoable.

### Migration / forward-compatibility notes

- The data model assumes v2 will add a second `Parent` row per `Household` without schema change — `Household.id` is the foreign key anchor; `Parent.household_id` is already non-unique in spirit. The unique constraint on email at the global level should remain so a parent can't double-sign-up across households, but a household-scoped re-invite should work.
- A future second `Child` will require no schema change either; `KidDevice.child_id` is already the discriminator. The kid device kiosk stays one-child-per-device; a household with two kids uses two devices.
- A future migration to multi-tenant (many households in one install universe) does *not* require a data move — `Household` is already the unit of isolation. It is a UX move only (parent UI shows "switch household", household-scoped code becomes more obvious).

### What this spec doesn't fix

- Final screen-by-screen wireframes. Those land during the `implement` skill's TDD phase, not here.
- Final SQL DDL. The Prisma sketch above is decision-rich; the real migration is generated by `prisma migrate`.
- Library / package pins. Whatever's current at implementation time, with Vue 3 / Prisma / Socket.IO or `ws` / Dexie / vite-plugin-pwa as the families. ADR-worthy version pins come up if they intersect with the locked decisions.
