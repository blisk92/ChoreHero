# ChoreHero v1 — Scope Brief

> Single source of truth for the v1 product shape. Downstream workers
> (frontend designer, frontend dev, backend dev, UAT) should each be able
> to pick their lane from this document without re-reading `spec-v1-mvp.md`,
> `CONTEXT.md`, or the ADR end-to-end.
>
> Synthesis date: 2026-10-11. Inputs read in full: `IDEA.md`, `CONTEXT.md`,
> `docs/adr/0001-kid-identity-is-the-device.md`, `spec-v1-mvp.md`.

---

## 1. Problem Statement

Parents want their child to do chores without nagging; children want
recognition and small rewards for what they do. Today's loop is verbal,
forgettable, and asymmetric — the parent carries 100% of the friction and
the child has no incentive stronger than avoiding a frown. ChoreHero v1
replaces the daily nag with a one-parent / one-child system in which the
parent writes down what they want done, the child picks what they want to
do first, points accrue as a visible running balance, streaks reward
consistency, and a parent-approved reward catalog gives the child a real
thing to spend points on. Two device shapes (parent SPA, kid SPA) share a
single Express + MariaDB backend and a WebSocket fan-out that surfaces
kid activity to the parent in near-real time. The kid device is the kid's
identity (ADR-0001), so there is no child account, no PIN, and no
cross-device sign-in for the child in v1. The product is validated for
exactly one parent + one child per household; v2 widens the household
without re-architecting the data model.

---

## 2. User Stories (Given/When/Then)

Numbered to match the order in `spec-v1-mvp.md` so the spec, this brief,
and the UAT scenarios stay in lock-step. Every story is a v1 must-have
unless marked otherwise.

### Onboarding & Identity

1. **Sign up by email + password**
   *Given* a new visitor on the marketing page, *when* they submit
   email + password on the sign-up form, *then* a `Parent` row is
   created, a `Household` is provisioned for them, and they land in
   the parent dashboard signed in.
2. **Sign in faster with OAuth**
   *Given* a parent on the sign-in screen, *when* they tap "Continue
   with Google" (or Apple) and complete the OAuth round-trip, *then*
   a session is established for an existing `Parent` matched by OAuth
   subject, or a new `Parent` + `Household` is created on first use.
3. **Automatic household creation**
   *Given* a freshly signed-up parent, *when* the sign-up call returns
   2xx, *then* a `Household` exists and is the FK anchor for every
   subsequent row.
4. **Create a child profile**
   *Given* a signed-in parent, *when* they create a child with a name
   and pick an avatar, *then* a `Child` row is created in the parent's
   household and the chosen avatar is the kid's identity in the app.
5. **Generate a household code + QR**
   *Given* a parent in settings, *when* they tap "Link a kid device"
   for the first time, *then* a `HouseholdCode` row is created (lazy),
   a 6-character alphanumeric code (no 0/O, 1/I/L) is shown alongside
   a QR encoding the same code.
6. **Permanent code until regenerated**
   *Given* an existing household code, *when* a new kid device is
   linked weeks later, *then* the same code still works without the
   parent re-running setup.
7. **Regenerate the household code**
   *Given* a parent in settings, *when* they tap "Regenerate code",
   *then* the previous code stops being accepted at the link endpoint
   and a new code is shown.
8. **List and revoke kid devices**
   *Given* a parent in settings, *when* they open "Kid devices",
   *then* every registered `KidDevice` is listed with a friendly name
   and `last_seen_at`, and they can revoke a device (sets
   `revoked_at`, invalidates the device token).
9. **Kid welcome on first launch**
   *Given* a freshly linked kid device with zero chores, *when* the
   kid opens the kiosk, *then* a welcome screen shows
   "Welcome, [name]!" with the chosen avatar. *Then*, the moment any
   chore lands in either pool, the screen auto-transitions to the
   regular "No chores yet" empty state (or the live pool).

### Chores & Pools

10. **Create a chore**
    *Given* a parent on the chores page, *when* they create a chore
    with name, point value, optional `review_flagged`, and optional
    `due_at`, *then* a `Chore` row is created in the correct pool
    (recurring vs one-off decided by the parent).
11. **Choose recurring vs one-off**
    *Given* a parent creating a chore, *when* they toggle
    recurring/one-off, *then* the chore's `kind` field is set
    accordingly, which controls the lifecycle on resolve.
12. **Edit / delete a pooled chore**
    *Given* a parent, *when* they edit or delete a chore that is in
    a pool, *then* the change is persisted and visible to the kid on
    the next sync tick; claimed chores are not editable in v1.
13. **Deadline on a one-off chore**
    *Given* a parent creating a one-off chore, *when* they set a
    `due_at`, *then* the chore's deadline-expiry path is active and
    a missed deadline will mark it `expired` and notify the parent.
14. **Mark a chore review-flagged**
    *Given* a parent editing or creating a chore, *when* they set
    `review_flagged = true`, *then* kid-completion routes through
    parent approval before any points are awarded.
15. **Kid sees "Available Extras"**
    *Given* a kid on the kiosk, *when* they open "Today", *then*
    every claimable chore across both pools is listed under
    "Available Extras".
16. **Claim a chore with one tap**
    *Given* a kid viewing Available Extras, *when* they tap a chore,
    *then* the chore's `status` becomes `claimed`, the
    `claimed_by_child_id` and `claimed_at` are set, and the chore
    moves into the kid's "My Active" section.
17. **See "My Active"**
    *Given* a kid with one or more claimed chores, *when* they open
    "Today", *then* those chores are listed under "My Active" and do
    not also appear in Available Extras.
18. **Mark a chore done**
    *Given* a kid with a claimed chore, *when* they tap "Done", *then*
    a `Chore.status = completed` transition fires: non-review-flagged
    chores immediately append a positive `PointsLedger` entry;
    review-flagged chores hold the points until parent approval.
19. **Skip a claimed chore**
    *Given* a kid with a claimed chore, *when* they tap "Skip", *then*
    the chore's lifecycle is:
    - recurring → back to pool, no points
    - one-off with deadline → `expired`, parent notified, no points
    - one-off without deadline → back to pool, no points
20. **See streak count on a recurring chore**
    *Given* a kid, *when* they view a recurring chore, *then* the
    current streak is surfaced inline (read from the `Streak`
    projection, not recomputed on the client).

### Points & Streaks

21. **Kid sees running balance**
    *Given* a kid on the kiosk, *when* they open the home screen,
    *then* the balance is `SUM(PointsLedger.delta) WHERE child_id = ?`
    and is shown prominently.
22. **Instant balance update on non-review-flagged completion**
    *Given* a kid completes a non-review-flagged chore, *when* the
    local mutation commits, *then* the balance updates within the
    same frame (no waiting on the network round-trip).
23. **Parent sees kid's balance**
    *Given* a parent on the dashboard, *when* the dashboard loads,
    *then* the kid's current balance is visible.
24. **Streak increments on consecutive-day completion**
    *Given* a recurring chore with `Streak.last_completed_on = D-1`,
    *when* the child completes it on day `D`, *then*
    `Streak.current_length` increments and `last_completed_on = D`.
25. **Streak resets on a missed day**
    *Given* a recurring chore with `Streak.last_completed_on < D-1`,
    *when* day `D` arrives without a completion, *then* the next
    completion resets `current_length` to 1 (a fresh streak starts).
26. **Parent sees per-chore streaks**
    *Given* a parent, *when* they open the chore detail, *then* the
    current and longest streak are visible.
27. **Streak milestone notification**
    *Given* a kid who hits a 7-day or 30-day milestone, *when* the
    streak reducer runs, *then* an in-app notification fires with a
    celebratory phrase and the kid's avatar.

### Rewards & Redemption

28. **Create a reward**
    *Given* a parent on the rewards page, *when* they create a reward
    with name, point cost, and optional `stock_remaining`, *then* a
    `Reward` row exists and the reward is visible to the kid in the
    catalog.
29. **Edit / remove rewards**
    *Given* a parent, *when* they edit or remove a reward, *then*
    the change persists; kids see the updated catalog on the next
    sync.
30. **Kid browses the catalog**
    *Given* a kid on the kiosk, *when* they open Redeem, *then* they
    see every reward with its name, description, and point cost.
31. **Kid requests a redemption**
    *Given* a kid, *when* they tap a reward, *then* a `Redemption`
    row is created with `status: pending` and a parent notification
    is enqueued.
32. **Parent sees pending requests**
    *Given* a parent, *when* they open the dashboard, *then* pending
    redemptions are listed with the kid's name, the reward, and the
    cost.
33. **Parent approves**
    *Given* a parent on a pending redemption, *when* they tap
    Approve, *then* `status: approved`, a negative `PointsLedger`
    entry is appended, the kid is notified, and (if `stock_remaining`
    is set) the stock is decremented.
34. **Parent denies with optional reason**
    *Given* a parent on a pending redemption, *when* they tap Deny
    and optionally type a reason, *then* `status: denied` with
    `denial_reason` captured, no points are moved, and the kid is
    notified.
35. **Parent reverses an approved redemption**
    *Given* a previously approved redemption, *when* the parent taps
    Reverse, *then* a positive `PointsLedger` entry offsets the
    original debit, `status: reversed`, and the kid is notified.
36. **Stock-limited reward refuses overflow**
    *Given* a reward with `stock_remaining = 0`, *when* the kid taps
    it, *then* the request is refused client-side and the reward is
    visibly out of stock; no `Redemption` row is created.

### Notifications

37. **Parent ping: review-flagged completion**
    *Given* a review-flagged chore is marked done, *when* the
    completion is committed server-side, *then* the parent's in-app
    notification list gains a "Review pending" entry.
38. **Parent ping: deadline expired**
    *Given* a deadline one-off chore passes `due_at` without
    completion, *when* the expiry pass runs, *then* the parent gets
    an in-app notification.
39. **Parent ping: redemption requested**
    *Given* a kid requests a redemption, *when* the request commits,
    *then* the parent gets an in-app notification.
40. **Parent ping: recurring pool empty**
    *Given* the recurring pool's claimable count drops to 0, *when*
    that state change is observed, *then* the parent is notified
    (in-app).
41. **Kid ping: new chore in pool**
    *Given* a parent adds a chore, *when* the chore is committed,
    *then* the kid device's in-app notification list gains an entry.
42. **Kid ping: streak milestone**
    *See story 27.* (Dedicated slot so the notification story list
    reads end-to-end.)
43. **Kid ping: points awarded after parent approval**
    *Given* a parent approves a review-flagged completion, *when* the
    approval commits, *then* the kid is notified of the balance
    increase.
44. **Kid ping: redemption approved or denied**
    *Given* a redemption resolves, *when* the parent acts, *then* the
    kid is notified of the outcome.
45. **Per-device web-push opt-in (parent only)**
    *Given* a parent on a device, *when* they toggle "Allow push" in
    settings, *then* the device is subscribed to the parent's VAPID
    push endpoint and receives a web-push ping for the four parent
    events (37-40). Default off. Kid devices never receive push.

### Sync & Offline

46. **Kid works offline**
    *Given* a kid device with no network, *when* the kid claims or
    completes a chore, *then* the mutation is persisted in the Dexie
    outbox, the UI updates optimistically, and the request replays
    on reconnect with the original `updated_at` and a stable
    operation ID for idempotency.
47. **Parent sees near-real-time activity**
    *Given* both devices online, *when* the kid takes an action,
    *then* the parent's dashboard reflects the change within a few
    seconds via the WebSocket fan-out.
48. **Offline edits flow in cleanly on reconnect**
    *Given* a parent who edited a chore while the kid was offline,
    *when* the kid reconnects, *then* the kid's local cache
    reconciles without losing either side's intent.
49. **Per-field last-write-wins**
    *Given* the parent and kid both edited different fields of the
    same chore, *when* both edits arrive, *then* each field is
    applied independently with its own `updated_at` and the union
    persists without one side clobbering the other.

### Empty States & Onboarding Nudges

50. **Parent first chore CTA**
    *Given* a parent with zero chores, *when* they open the
    dashboard, *then* the primary CTA reads "Add your first chore"
    with secondary copy describing chore kinds; the nudge banner
    stays until ≥1 chore exists.
51. **Parent first reward CTA**
    *Given* a parent with zero rewards, *when* they open the rewards
    page, *then* the primary CTA reads "Add your first reward" with
    example suggestions ("30 min screen time", "Pick dinner"). No
    auto-seeded rewards.
52. **Kid no-chores empty state**
    *Given* a kid with no chores in either pool, *when* they open
    the kiosk, *then* they see "No chores yet. Ask a parent to add
    some." with a small illustration.
53. **Kid first-link welcome**
    *See story 9.* (Dedicated slot for empty-state coverage.)

### Visual Identity

54. **Avatar in celebratory moments**
    *Given* a kid who hits a milestone or gets a redemption
    approved, *when* the celebratory surface renders, *then* the
    kid's chosen avatar is the hero; the ChoreHero emblem never
    competes.
55. **Parent-side quiet palette**
    *Given* a parent surface, *when* it renders, *then* the same
    palette (deep violet + sunshine yellow) is used but with more
    white space and quieter accents — the parent's phone should not
    feel like a toddler's toy.

---

## 3. Constraints & Tech Stack (locked unless explicitly relaxed)

### Hard constraints from the source material

- **One parent, one child per household in v1.** Multi-parent and
  multi-child are explicitly out of scope (`spec-v1-mvp.md` §"Out of
  Scope"). The data model is forward-compatible (no schema change
  required to widen later).
- **Kid identity = kid device (ADR-0001).** No kid account, no PIN,
  no cross-device sign-in. Each `KidDevice` holds a device-scoped
  session and can be revoked from the parent side.
- **Household code charset is 6 alphanumeric, no 0/O/1/I/L.**
- **Rewards are parent-catalogued only.** Kids cannot propose new
  rewards or change point costs in v1. Approval price = listed price.
  No counter-offers.
- **Streak milestones are hardcoded** (every 7 days for v1; 30-day
  variant mentioned in spec). Not configurable per chore in v1.
- **English only. No i18n.**
- **PWA only.** No Capacitor, no React Native shell.
- **Web push is parent-only and opt-in per device.** Kid devices
  get in-app notifications only.
- **One MariaDB, one schema.** No document store, no Redis, no
  secondary cache. v2 may add a read replica.

### Tech stack (per `spec-v1-mvp.md` §"Tech stack summary")

- Frontend: **Vue 3 + Vite + vite-plugin-pwa** (Workbox underneath).
  Two SPAs, two bundles, two route trees (parent SPA and kid SPA).
- Backend: **Node.js + Express + Prisma** against MariaDB.
- Local store on both devices: **Dexie.js** (IndexedDB) holding the
  offline mutation outbox.
- Auth: **email + password (bcrypt)**, optional **Google / Apple
  OAuth via Passport.js** strategies.
- Real-time: **WebSocket** using the `ws` library. The REST API
  publishes kid-activity webhooks into the WS layer; parent sessions
  fan out. No kid-to-kid, no parent-to-parent.
- Push: **web-push library + VAPID keys**, opt-in per parent device.
- Hosting: **Docker Compose** — `nginx` (TLS + static assets),
  `node` (API + WS), `mariadb` (state). One compose file. Volume for
  DB persistence.
- Test seam: **Playwright** end-to-end with two browser contexts
  (parent + kid) is the primary smoke / demo / regression net.
  Secondary: API contract tests against a test MariaDB, state-machine
  unit tests, Prisma migration smoke test.

### Conflict-resolution policy

- **Per-field last-write-wins.** Each updatable column carries its
  own `updated_at`. Dexie replay sends only the changed fields with
  their original captured `updated_at`; the server applies
  if-and-only-if `received.updated_at > stored.updated_at` for that
  field. No CRDT, no vector clocks.
- **Service worker strategies per resource type.** App shell
  precached (cache-first, immutable). API GETs use network-first
  with cache fallback. Mutation requests go through Dexie first,
  never through the SW.
- **WS reconnect strategy.** When the parent's WS is closed
  (background, network drop), the next dashboard open resumes via a
  single GET, and a fresh WS handshake is attempted in parallel.

---

## 4. Assets Already Produced

These are present in the project at the start of v1 work and are
authoritative for downstream lanes:

- `IDEA.md` — one-paragraph product seed ("gamify chores for kids").
- `CONTEXT.md` — glossary, tone, voice, and visual identity anchors
  (deep violet + sunshine yellow palette, mascot rules, error
  copy).
- `docs/adr/0001-kid-identity-is-the-device.md` — the locked decision
  that the kid device is the kid's identity. Read this before
  designing or building anything in the kid SPA.
- `spec-v1-mvp.md` — full product spec including the Prisma schema
  sketch, chore state machine, implementation decisions, and out-of-
  scope list. This brief is a distillation; the spec is the
  reference of last resort.

No code, no design files, no tests, and no Docker artefacts exist
yet. All four downstream lanes start from scratch in their own
worktrees.

---

## 5. Dependency Map — who owns which story

The downstream lanes are: **designer** (visual + interaction
design), **frontend dev** (both SPAs), **backend dev** (Express +
Prisma + WS), **UAT** (acceptance scenarios + fidelity checks).
The map below is which lane produces what per story. Stories that
need two lanes list both with their primary deliverable.

### Backend only (API + DB + WS, no UI)

- US 1, 2, 3, 6, 7 — auth, household provisioning, code
  persistence, code regeneration.
- US 10, 11, 13, 14 — chore creation / mutation endpoints and
  schema (the UI part is also needed but the API is the load-
  bearing piece; frontend dev wires the form once the endpoint
  exists).
- US 16, 18, 19 — claim / complete / skip endpoints and the chore
  state-machine reducer.
- US 21, 22, 23 — `PointsLedger` write path on completion + ledger
  read on dashboard. Frontend reads the value but the reducer and
  projection are server-side.
- US 24, 25, 26 — streak reducer + `Streak` projection.
- US 27, 37-45 — notification generation in the server's mutation
  handlers; the parent ping fan-out and the per-household event
  channel.
- US 28, 29, 31, 33, 34, 35, 36 — reward CRUD, redemption
  lifecycle, stock decrement, reversal flow.
- US 47, 48, 49 — WS layer, reconnect strategy, per-field
  last-write-wins merge logic.
- US 4 (API half), US 5 (code generation + QR endpoint), US 8
  (device list + revoke endpoint) — the API surface; the UI is a
  thin call.

### Frontend only (parent SPA, kid SPA, service worker)

- US 9, 52, 53 — kid kiosk empty / welcome states, copy and
  illustration placement.
- US 15, 17, 20, 30 — kid kiosk list rendering (Available Extras,
  My Active, streak inline, Redeem catalog).
- US 45 (parent toggle) — the opt-in toggle UI; backend supplies
  the VAPID public key + subscription endpoint.
- US 50, 51, 55 — empty states and parent-side visual restraint.
- US 54 — avatar placement in celebratory surfaces (designer-led
  with frontend implementing the placement).
- US 46, 48 (client half) — Dexie outbox, optimistic UI, SW
  caching strategy for the GETs and app shell.

### Designer (tokens + components + annotated wireframes + a11y)

The designer produces the package the frontend dev implements
against. The designer owns the *visual* and *interaction* layer;
every screen listed below needs an annotated wireframe plus the
shared component spec (button, input, card, nav, modal, table,
form fields, all states).

- US 1, 2 — sign-up / sign-in screens (parent).
- US 3 — first-load dashboard empty state visual.
- US 4 — child profile creation modal.
- US 5 — "Link a kid device" screen with QR + code.
- US 8 — kid devices list with revoke.
- US 9, 52, 53 — kid kiosk first launch + empty states.
- US 10-14 — chore editor (create / edit) for parent.
- US 15, 17, 20 — kid "Today" / "Available Extras" / "My Active".
- US 23, 26 — parent dashboard cards (balance, per-chore streaks).
- US 27, 42 — streak milestone celebratory surface.
- US 28, 29 — reward catalog editor for parent.
- US 30, 31 — kid Redeem catalog and request flow.
- US 32, 33, 34, 35 — parent redemption queue + approval modal +
  reversal flow.
- US 36 — out-of-stock state for the kid Redeem catalog.
- US 37-44 — in-app notification toasts / list views (parent and
  kid variants).
- US 45 — push opt-in toggle.
- US 50, 51 — first chore / first reward CTAs.
- US 54, 55 — mascot / palette restraint across the two surfaces.

The fidelity rules the UAT engineer will use later must be
declared by the designer in the design package (e.g. "Chore card
uses `surface.card` with `radius.lg` and `shadow.1`; streak
milestone modal is `surface.hero` with avatar 96dp").

### UAT (acceptance scenarios + fidelity verification)

UAT runs *after* implementation and is the last lane; it depends
on the designer's fidelity rules and on the backend / frontend
being deployed to staging. UAT does not design or build. UAT
consumes:

- Every story in §2 of this brief (one scenario per story).
- The designer's fidelity rules + component spec for visual
  verification.
- The deployed staging URL provided by the devops engineer.

### Cross-lane coordination

- US 5 (Link a kid device) is a coordination point: the designer
  decides the QR layout, the backend dev produces the QR
  payload + endpoint, the frontend dev renders it. Tag the
  `HouseholdCode.code_hash` storage decision in any backend
  story.
- US 27 / US 42 / US 54 (streak milestone notification +
  celebratory surface) is a coordination point between the
  backend (notification trigger + payload), the designer
  (celebratory surface spec), and the frontend dev (render
  surface + show avatar).
- US 45 (web push) spans backend (VAPID + subscription endpoint
  + push send), frontend (opt-in toggle + service worker push
  handler), and designer (toggle visual + lock-screen copy
  guidance).
- US 46-49 (offline + sync) span backend (merge + WS), frontend
  (Dexie outbox + SW), and the Playwright e2e test that proves
  it end-to-end.

---

## 6. Out of Scope (do not design for, do not build)

Carried verbatim from `spec-v1-mvp.md` so no downstream worker
"while-we're-at-it"s their way into a v2 feature:

- Second parent account, second child profile.
- Chore templates / starter library.
- Sibling leaderboards, family-vs-family challenges.
- Kid account with cross-device sign-in or email.
- Kid-proposed rewards or kid-proposed point costs.
- Chore categories, age tiers, difficulty tiers (Easy/Med/Hard).
- Photo / video proof for chores.
- Multi-day deadlines, idle-chore nudges, chore reminders.
- Configurable streak milestones.
- In-app chat.
- COPPA / GDPR / data export.
- Native mobile wrappers (Capacitor, React Native).
- Analytics beyond balance + pending queue.
- Marketing / A/B / paywall.
- Internationalisation.
- Push notifications to kid devices.

---

## 7. Ambiguities & Open Questions for the Requester

These are decisions that the spec leaves open. They are listed in
roughly the order they would block a downstream lane. The
designer and backend dev can make defensible defaults and
proceed; flagging here so the requester can correct course
before the UAT pass forces a rewrite.

1. **Avatar set** — pre-shipped SVG set (~12 hand-drawn-in-style
   characters, *recommended*), parent photo upload, or both? A
   photo-upload path adds trust + storage + moderation work that
   v1 doesn't need; the SVG set keeps the visual identity tight.
   *Default if no answer: pre-shipped SVG set.*
2. **Streak milestone list** — `every 7 days` only, or also
   14/30/100? The spec calls out 7 and 30. *Default if no answer:
   {7, 30}.*
3. **WebSocket auth at handshake** — JWT in query param
   (*recommended* for v1; kid device isn't a hostile actor since
   the parent registered it) vs. short-lived ticket-exchange
   flow. *Default if no answer: JWT in query param.*
4. **Backup / restore on parent reinstall** — accepting
   "re-link kid devices after reinstall" (*recommended*) vs.
   per-household recovery code the parent saves offline. *Default
   if no answer: no recovery code in v1.*
5. **Parent dashboard with no kid activity yet** — quiet "No
   activity yet" section + nudges (*recommended*) vs. illustrative
   preview state. *Default if no answer: quiet empty section.*
6. **Stock-decrement on approval** — decrement at request time vs.
   approval time? Spec implies approval time (story 36 talks about
   refusing at zero; that means the request still goes through if
   stock drops between request and approval, but redemptions at
   zero are refused). Confirm. *Default if no answer: refuse at
   request time when stock = 0; otherwise decrement at approval.*
7. **Review-flagged denial semantics** — chore returns to pool
   (per the spec's state machine), or marked skipped, or
   archived? Spec says "parent denial → chore returns to pool,
   no points awarded". Confirm this is the desired UX (kid
   sees the same chore re-appear in Available Extras). *Default
   if no answer: returns to pool.*
8. **OAuth providers in v1** — Google only, Apple only, or both?
   Apple requires Apple Developer Program enrolment for the
   private key + service ID. *Default if no answer: Google only
   for v1; Apple is a v1.1 add.*
9. **Web-push icon + lock-screen copy** — the spec calls this out
   but doesn't specify. Designer will need this for the
   opt-in flow + UAT will verify it. *Default if no answer: app
   icon + kid's first name + reward/chore name in the title.*
10. **What happens to a chore the parent deletes while the kid has
    it claimed?** — Spec says "claimed chores are not editable
    in v1" but doesn't say what happens on delete. The kid will
    see the chore vanish from My Active on the next sync.
    Confirm. *Default if no answer: chore disappears on next
    sync, no points awarded, no notification.*

---

## 8. Glossary (quick reference for the lanes)

Definitions live in full in `CONTEXT.md`. The minimum a downstream
worker needs in their head:

- **Household** = unit of data isolation. One family, one install
  universe. v1 = 1 parent + 1 child.
- **Kid Device** = the kid's identity. Holds a device-scoped
  session. Revocable by the parent.
- **Pool** = container of claimable chores. Two pools: **Recurring
  Pool** (chore re-enters after resolve) and **One-off Pool**
  (chore is removed from circulation on resolve).
- **Claim** = kid's act of pulling a chore into "My Active".
  Implemented as a state on the chore (`status: claimed`), not a
  separate table.
- **Review-flagged chore** = parent approval gates the points
  award, regardless of how the kid marks the chore.
- **Redemption** = kid's request to spend points on a catalog
  reward. Always parent-approved. Reversible.
- **Streak** = denormalised projection, not derived. The reducer
  updates it; UIs read it.
- **Points Ledger** = append-only log. Current balance = `SUM(delta)`
  per child. Append-only makes reversal and audit trivial.
