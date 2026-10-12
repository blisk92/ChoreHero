# ChoreHero v1 — UAT Report

> One file per run. Save alongside the evidence folder and attach
> to the task at sign-off.

## Header

| Field | Value |
|-------|-------|
| Report ID | `UAT-<YYYY>-<NNN>` (increment per run) |
| Date run started | `<ISO date>` |
| Date run ended | `<ISO date>` |
| UAT engineer | `<name>` |
| Staging URL (parent SPA) | `<url>` |
| Staging URL (kid SPA) | `<url>` |
| Staging API base | `<url>` |
| Staging build / image tag | `<tag or SHA>` |
| Design package SHA / commit | `<designer package commit>` |
| Spec / scope brief commit | `<docs/scope-brief.md commit>` |

## Pre-flight check

- [ ] All scenarios in `uat/scenarios/` are present and readable.
- [ ] Staging URL reachable; parent + kid SPAs load.
- [ ] Test parent, child, kid device, household code, chore and reward
      fixtures seeded per `runbook.md` §4.
- [ ] Design package paths cited by scenarios all resolve.

If any pre-flight item fails, **do not start**; record the failure in
§"Blockers" and surface to the orchestrator.

## Results table

One row per scenario. Critical-path rows marked `*`.

| # | Scenario | Result | Tag | Notes |
|---|----------|--------|-----|-------|
| \* US-1  | Sign up by email + password | `PASS / FAIL / BLOCKED / N/A` | `TAG-?` |  |
| US-2  | Sign in faster with OAuth | | |  |
| US-3  | Automatic household creation | | |  |
| \* US-4  | Create a child profile | | |  |
| \* US-5  | Generate household code + QR | | |  |
| US-6  | Permanent code until regenerated | | |  |
| US-7  | Regenerate household code | | |  |
| US-8  | List and revoke kid devices | | |  |
| US-9  | Kid welcome on first launch | | |  |
| \* US-10 | Create a chore | | |  |
| US-11 | Choose recurring vs one-off | | |  |
| US-12 | Edit / delete a pooled chore | | |  |
| US-13 | Deadline on a one-off chore | | |  |
| US-14 | Mark a chore review-flagged | | |  |
| US-15 | Kid sees "Available Extras" | | |  |
| \* US-16 | Claim a chore with one tap | | |  |
| US-17 | See "My Active" | | |  |
| \* US-18 | Mark a chore done | | |  |
| US-19 | Skip a claimed chore | | |  |
| US-20 | See streak count on a recurring chore | | |  |
| \* US-21 | Kid sees running balance | | |  |
| US-22 | Instant balance update on non-review completion | | |  |
| \* US-23 | Parent sees kid's balance | | |  |
| US-24 | Streak increments on consecutive-day completion | | |  |
| US-25 | Streak resets on a missed day | | |  |
| US-26 | Parent sees per-chore streaks | | |  |
| US-27 | Streak milestone notification | | |  |
| \* US-28 | Create a reward | | |  |
| US-29 | Edit / remove rewards | | |  |
| US-30 | Kid browses the catalog | | |  |
| \* US-31 | Kid requests a redemption | | |  |
| US-32 | Parent sees pending requests | | |  |
| \* US-33 | Parent approves | | |  |
| US-34 | Parent denies with optional reason | | |  |
| US-35 | Parent reverses an approved redemption | | |  |
| US-36 | Stock-limited reward refuses overflow | | |  |
| US-37 | Parent ping: review-flagged completion | | |  |
| US-38 | Parent ping: deadline expired | | |  |
| US-39 | Parent ping: redemption requested | | |  |
| US-40 | Parent ping: recurring pool empty | | |  |
| US-41 | Kid ping: new chore in pool | | |  |
| US-42 | Kid ping: streak milestone | | |  |
| US-43 | Kid ping: points awarded after parent approval | | |  |
| US-44 | Kid ping: redemption approved or denied | | |  |
| US-45 | Per-device web-push opt-in (parent only) | | |  |
| US-46 | Kid works offline | | |  |
| US-47 | Parent sees near-real-time activity | | |  |
| US-48 | Offline edits flow in cleanly on reconnect | | |  |
| US-49 | Per-field last-write-wins | | |  |
| US-50 | Parent first chore CTA | | |  |
| US-51 | Parent first reward CTA | | |  |
| US-52 | Kid no-chores empty state | | |  |
| US-53 | Kid first-link welcome | | |  |
| US-54 | Avatar in celebratory moments | | |  |
| US-55 | Parent-side quiet palette | | |  |

## Critical-path result

(`runbook.md` §7 — must re-run on the final staging build.)

| Scenario | Mid-suite result | Final-build result | Notes |
|----------|------------------|--------------------|-------|
| US-1  | | |  |
| US-4  | | |  |
| US-5  | | |  |
| US-10 | | |  |
| US-16 | | |  |
| US-18 | | |  |
| US-21 | | |  |
| US-23 | | |  |
| US-28 | | |  |
| US-31 | | |  |
| US-33 | | |  |

## Tag summary

| Tag | Count | Scenarios affected |
|-----|-------|---------------------|
| TAG-1 Critical defect |  |  |
| TAG-2 Fidelity defect |  |  |
| TAG-3 Copy defect |  |  |
| TAG-4 Accessibility defect |  |  |
| TAG-5 Cosmetic / informational |  |  |

For each TAG-1 / TAG-2 / TAG-3 / TAG-4, list the Then outcome that
fired, the screenshot evidence path, and the routing target (which
lane is asked to fix).

## Blockers

Any scenario in `BLOCKED` and the reason. Each blocker names a target
resolver (designer / backend-dev / frontend-dev / orchestrator).

| Scenario | Block reason | Target resolver | Target resolved by |
|----------|--------------|------------------|---------------------|
|  |  |  |  |

## Evidence index

Link the engineer-local evidence folder or attach each
scenario's evidence file. One path per scenario is fine; one folder
index is also acceptable.

```
evidence/
├── US-01-signup/
│   ├── US-01-step-1.png
│   ├── US-01-step-2.png
│   ├── network.har
│   └── console.log
├── US-02-oauth/
...
```

## Verdict

**READY TO SHIP** or **NOT READY**.

One paragraph rationale citing the totals, the critical-path result,
and any unresolved blockers.

## Sign-off

```
UAT engineer: <name>
Date:         <ISO date>
Signature:    <e-signature or digital equivalent>
```

Once signed, attach this report to the task card and surface to the
orchestrator.