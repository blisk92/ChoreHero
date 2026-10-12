# ChoreHero v1 — UAT Runbook

> How to execute the scenario suite against staging and record
> pass/fail evidence.

## 1. Audience & timing

This runbook is written for the **UAT engineer** picking up the
package after the design and implementation lanes ship. Run it
**after**:

1. The frontend-designer has published `design/` and signed off on
   visual fidelity (their card `t_fba7600a`).
2. The backend-dev and frontend-dev have deployed the staging
   environment and signed off (their card `t_4cbbbdbe`).
3. The staging URL has been provided to the UAT engineer via a
   comment on this card (`t_b241ef1`).

Do not start execution if any of those is missing — file a
`BLOCKED` on the suite in `templates/uat-report.md` instead.

## 2. Pre-flight checklist

Before running the first scenario:

- [ ] **Staging URL** recorded in §"Reference table: Staging
      environment" below.
- [ ] **Test parent account** provisioned (email + password). One
      parent = one household per staging environment; do not reuse an
      existing account unless the runbook explicitly calls for it.
- [ ] **Test kid device** available (a real tablet, phone, or
      browser context registered to the test parent via the
      household code generated under §4 below). One kid device per
      staging environment.
- [ ] **Browser devtools** accessible on both the parent and kid
      sessions (network tab, console, application/service worker
      panel, IndexedDB inspector).
- [ ] **Design package** cloned alongside the staging repo. Every
      scenario §"UI fidelity" block cites paths under `design/`; the
      engineer resolves `<from-design-package>` placeholders against
      the actual files before running.
- [ ] **Recording tools** ready: screenshot capture (with viewport
      size noted), short video for the critical path, and a copy of
      `templates/evidence-log.md` opened per scenario.
- [ ] **Clock** synced (date matters for streak and expiry tests —
      US-24, US-25, US-27, US-38).
- [ ] **Notification log** documented (the engineer's own inbox is
      off so push tests aren't masked by personal email / SMS noise).
- [ ] All scenarios in `scenarios/` readable. If a scenario file is
      missing or malformed, file a blocker in the report; do not
      improvise.

## 3. Reference table: Staging environment

| Field | Value |
|-------|-------|
| Staging URL (parent SPA) | `<fill at run time>` |
| Staging URL (kid SPA / kiosk) | `<fill at run time>` |
| Staging API base | `<fill at run time>` |
| WebSocket endpoint | `<fill at run time>` |
| Test parent email | `<fill at run time>` |
| Test parent password | `<fill at run time>` |
| Test child name | `<fill at run time>` |
| Test child avatar | `<fill at run time>` |
| Household code (generated under §4) | `<fill at run time>` |
| Staging build SHA / image tag | `<fill at run time>` |
| Date the run started | `<fill at run time>` |
| UAT engineer running the suite | `<fill at run time>` |

## 4. Test data setup (run once per staging environment)

Some of this can be automated, but for v1 every step is documented
so the engineer can rebuild state from scratch if the database is
reset.

### 4.1 Bootstrap parent + household

1. Open the parent SPA at the staging URL.
2. Sign up with the test parent email and password (US-1).
3. Confirm the test parent lands in the parent dashboard (US-3).

### 4.2 Bootstrap child profile

4. Create a child profile with the test child name and avatar
   (US-4). Record the chosen avatar value.

### 4.3 Bootstrap household code + kid device

5. Navigate to Settings → "Link a kid device" (US-5). Capture the
   generated code and QR.
6. Open the kid SPA on the test kid device, scan the QR (or enter
   the 6-character code manually per US-5 charset rule: no 0/O,
   1/I/L). Capture the device's friendly name as it registers.
7. Confirm the kid SPA lands on the welcome screen (US-9, US-52).
   Record `last_seen_at` for the device in the parent "Kid devices"
   view (US-8).

### 4.4 Bootstrap chores and rewards

For repeatable runs, seed a small fixed set that exercises both
pools, deadlines, review-flagging, and stock-limited rewards:

8. Create **3 chores** (US-10 / US-11 / US-13 / US-14):
   - One recurring, no deadline, no review flag ("Make bed", 10
     points).
   - One recurring, no deadline, review flag ("Tidy room", 15
     points).
   - One one-off with `due_at` set to **24 hours from now** ("Clean
     garage", 25 points).
9. Create **2 rewards** (US-28):
   - One without `stock_remaining` ("30 min screen time", 50
     points).
   - One with `stock_remaining = 1` ("Pick dinner", 75 points) —
     this exercises US-36.

Record every chore / reward ID so the evidence log can quote them.

### 4.5 Document open tags

Any TAG-1 / TAG-2 / TAG-3 hit during execution is logged in the
report's §"Tag summary" with a one-line resolution. See
§"Tagging" below.

## 5. Execution procedure (per scenario)

For each scenario file `scenarios/US-<NN>-<slug>.md`:

1. **Read the scenario end-to-end** before touching staging. Note
   the priority tag (Critical / High / Standard), the preconditions,
   and the evidence the engineer is expected to capture.
2. **Resolve design references.** Every §"UI fidelity" line cites
   a design artefact (e.g. `design/tokens/colors.json`,
   `design/components/chore-card.md`). Open that artefact, copy the
   expected token values (hex, spacing scale step, radius, font size)
   into the engineer-local copy of the scenario file under §"Resolved
   values", and use those values as the pass/fail reference. Do not
   edit the canonical scenario file in `scenarios/` — keep the
   engineer-local copy under the engineer's own scratch folder.
3. **Reset state if needed.** Some scenarios need a clean state
   (e.g. US-36 stock-limited, US-9 first-launch welcome). Use the
   staging admin endpoint or re-seed the database per §4; do not try
   to reuse stale state across scenarios.
4. **Execute step-by-step.** Perform each Given / When step and
   check each Then outcome, in order. Each numbered "Then" outcome
   is a binary pass/fail; record the result inline in
   `templates/evidence-log.md`.
5. **Capture evidence.**
   - **Screenshot** every UI assertion (named
     `US-<NN>-step-<n>.png` in the engineer's evidence folder).
   - **Network trace** for every API / WebSocket assertion (saved
     as `.har` or screenshot of the network tab filtered to the
     staging domain).
   - **Console log** saved as plain text per scenario.
   - **Dexie / IndexedDB dump** for any scenario that exercises the
     offline outbox (US-46, US-48, US-49).
6. **Mark the scenario result** in `templates/uat-report.md` §"Results
   table":
   - `PASS` — every Then outcome passed.
   - `FAIL` — any Then outcome failed. The failure column cites the
     Then item number and a one-line symptom.
   - `BLOCKED` — cannot execute because of missing data, missing
     build, or an upstream defect. The blocker column cites the
     reason and a target resolver.
   - `N/A` — explicitly outside the v1 scope (rare; requires UAT
     lead sign-off before marking).

## 6. Tagging

When an issue is found, the UAT engineer tags it so downstream
lanes can route fixes:

- **TAG-1** — **Critical visual / behaviour defect.** Blocks ship.
  Example: balance doesn't update on chore completion (US-22).
- **TAG-2** — **Fidelity defect.** Component / token doesn't match
  the design package. Blocks ship unless waived by UAT lead with a
  written reason.
- **TAG-3** — **Copy defect.** String on screen doesn't match the
  scenario's expected string. Blocks ship if on a critical-path
  scenario.
- **TAG-4** — **Accessibility defect.** WCAG 2.1 AA check fails
  (contrast, focus order, keyboard, aria). Blocks ship unless
  waived.
- **TAG-5** — **Cosmetic / informational.** Noted in the report
  appendix but does not block ship.

Every tag must reference the scenario number and the Then item it
fired against.

## 7. Critical path

These scenarios are run twice — once mid-suite for early signal and
once on the **final** staging build before sign-off. A `FAIL` or
`BLOCKED` on any of these blocks ship:

| Scenario | Reason |
|----------|--------|
| US-1  Sign up by email + password | Entry point |
| US-4  Create a child profile | Required for any kid activity |
| US-5  Generate household code + QR | Required for kid device link |
| US-10 Create a chore | Core parent flow |
| US-16 Claim a chore | Core kid flow |
| US-18 Mark a chore done | Core kid flow + points path |
| US-21 Kid sees running balance | Most visible kid UI |
| US-23 Parent sees kid's balance | Most visible parent UI |
| US-28 Create a reward | Core parent flow |
| US-31 Kid requests a redemption | Core kid → parent loop |
| US-33 Parent approves | Core parent action on kid request |

## 8. Sign-off procedure

1. Fill `templates/uat-report.md` end-to-end, including:
   - Total scenarios run, total PASS / FAIL / BLOCKED / N/A.
   - Tag summary (count per TAG-1..5).
   - Critical-path result table.
   - Ship / no-ship verdict with a one-paragraph rationale.
   - Sign-off line (UAT engineer name + date).
2. Save evidence under `evidence/` and link the path in the
   report's §"Evidence index".
3. Attach the report to the task (`kanban_attach` or the local
   handoff path the orchestrator expects) before marking
   `kanban_complete`.

## 9. Failure modes & how to recover

| Symptom | Likely cause | Recovery |
|---------|--------------|----------|
| Scenario references a `design/` path that doesn't exist | Designer package not yet merged | `BLOCKED` the suite; route to designer via `kanban_comment` on `t_fba7600a` |
| Staging returns 5xx on every API | Build not deployed or DB not migrated | `BLOCKED`; verify with backend-dev before re-running |
| Staging returns correct API responses but UI is blank / broken | Frontend bundle didn't deploy or PWA SW is stale | Clear SW + cache from the test browser; if still broken, `TAG-1` and route to frontend-dev |
| Push notification never arrives on the parent device | OS-level push disabled or staging VAPID keys missing | Verify push is enabled at the OS level first; if still missing, file `BLOCKED` with symptom |
| Dexie outbox is empty after a kid offline action | SW intercepted the mutation instead of routing it through Dexie | Per scope brief §3, mutations must never go through the SW. `TAG-1`. |
| Time-dependent scenarios (US-24, US-25, US-27, US-38) flake | Clock drift between host and DB | Force a fixed staging time and re-run; if DB can't fix time, mark `BLOCKED` |

## 10. Reference materials the engineer must have open

- `docs/scope-brief.md` — source of truth for the user stories.
- `spec-v1-mvp.md` — full product spec.
- `CONTEXT.md` — glossary, voice, palette anchors.
- `docs/adr/0001-kid-identity-is-the-device.md` — locked decision on
  kid identity.
- The design package at `design/` (produced by `t_fba7600a`).
- This runbook.
- `templates/uat-report.md` and `templates/evidence-log.md`.