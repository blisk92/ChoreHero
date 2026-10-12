# ChoreHero v1 — UAT Scenario Index

> One row per user story in `docs/scope-brief.md` §2. Click any
> story id to jump to its executable scenario file.

| ID | Title | Feature area | Priority | Critical-path | File |
|----|-------|--------------|----------|---------------|------|
| `US-1` | Sign up by email + password | Onboarding & Identity | Critical | ★ | [`US-1-signup-email-password.md`](./US-1-signup-email-password.md) |
| `US-2` | Sign in faster with OAuth (Google / Apple) | Onboarding & Identity | High |  | [`US-2-oauth-signin.md`](./US-2-oauth-signin.md) |
| `US-3` | Automatic household creation on signup | Onboarding & Identity | High |  | [`US-3-auto-household-create.md`](./US-3-auto-household-create.md) |
| `US-4` | Create a child profile with name + avatar | Onboarding & Identity | Critical | ★ | [`US-4-create-child-profile.md`](./US-4-create-child-profile.md) |
| `US-5` | Generate household code + QR from "Link a kid device" | Onboarding & Identity | Critical | ★ | [`US-5-household-code-qr.md`](./US-5-household-code-qr.md) |
| `US-6` | Household code is permanent until regenerated | Onboarding & Identity | High |  | [`US-6-code-permanent.md`](./US-6-code-permanent.md) |
| `US-7` | Regenerate the household code | Onboarding & Identity | High |  | [`US-7-regenerate-code.md`](./US-7-regenerate-code.md) |
| `US-8` | List and revoke kid devices | Onboarding & Identity | High |  | [`US-8-list-revoke-kid-devices.md`](./US-8-list-revoke-kid-devices.md) |
| `US-9` | Kid welcome on first launch | Onboarding & Identity | High |  | [`US-9-kid-welcome-first-launch.md`](./US-9-kid-welcome-first-launch.md) |
| `US-10` | Create a chore | Chores & Pools | Critical | ★ | [`US-10-create-chore.md`](./US-10-create-chore.md) |
| `US-11` | Choose recurring vs one-off when creating | Chores & Pools | High |  | [`US-11-recurring-vs-oneoff.md`](./US-11-recurring-vs-oneoff.md) |
| `US-12` | Edit or delete a pooled chore | Chores & Pools | High |  | [`US-12-edit-delete-chore.md`](./US-12-edit-delete-chore.md) |
| `US-13` | Deadline on a one-off chore | Chores & Pools | High |  | [`US-13-deadline-oneoff.md`](./US-13-deadline-oneoff.md) |
| `US-14` | Mark a chore review-flagged | Chores & Pools | High |  | [`US-14-review-flagged.md`](./US-14-review-flagged.md) |
| `US-15` | Kid sees "Available Extras" | Chores & Pools | High |  | [`US-15-available-extras.md`](./US-15-available-extras.md) |
| `US-16` | Claim a chore with one tap | Chores & Pools | Critical | ★ | [`US-16-claim-chore-one-tap.md`](./US-16-claim-chore-one-tap.md) |
| `US-17` | See "My Active" claimed chores | Chores & Pools | High |  | [`US-17-my-active.md`](./US-17-my-active.md) |
| `US-18` | Mark a claimed chore done | Chores & Pools | Critical | ★ | [`US-18-mark-chore-done.md`](./US-18-mark-chore-done.md) |
| `US-19` | Skip a claimed chore | Chores & Pools | High |  | [`US-19-skip-chore.md`](./US-19-skip-chore.md) |
| `US-20` | See streak count on a recurring chore | Chores & Pools | High |  | [`US-20-streak-inline.md`](./US-20-streak-inline.md) |
| `US-21` | Kid sees running balance on home | Points & Streaks | Critical | ★ | [`US-21-kid-running-balance.md`](./US-21-kid-running-balance.md) |
| `US-22` | Instant balance update on non-review completion | Points & Streaks | Critical |  | [`US-22-instant-balance-update.md`](./US-22-instant-balance-update.md) |
| `US-23` | Parent sees kid's balance on dashboard | Points & Streaks | Critical | ★ | [`US-23-parent-sees-balance.md`](./US-23-parent-sees-balance.md) |
| `US-24` | Streak increments on consecutive-day completion | Points & Streaks | High |  | [`US-24-streak-increment.md`](./US-24-streak-increment.md) |
| `US-25` | Streak resets on a missed day | Points & Streaks | High |  | [`US-25-streak-reset.md`](./US-25-streak-reset.md) |
| `US-26` | Parent sees per-chore streaks | Points & Streaks | High |  | [`US-26-parent-streaks.md`](./US-26-parent-streaks.md) |
| `US-27` | Streak milestone notification (kid, in-app) | Points & Streaks | High |  | [`US-27-streak-milestone-notification.md`](./US-27-streak-milestone-notification.md) |
| `US-28` | Create a reward | Rewards & Redemption | Critical | ★ | [`US-28-create-reward.md`](./US-28-create-reward.md) |
| `US-29` | Edit or remove a reward | Rewards & Redemption | High |  | [`US-29-edit-remove-reward.md`](./US-29-edit-remove-reward.md) |
| `US-30` | Kid browses the reward catalog | Rewards & Redemption | High |  | [`US-30-browse-reward-catalog.md`](./US-30-browse-reward-catalog.md) |
| `US-31` | Kid requests a redemption | Rewards & Redemption | Critical | ★ | [`US-31-request-redemption.md`](./US-31-request-redemption.md) |
| `US-32` | Parent sees pending requests on dashboard | Rewards & Redemption | High |  | [`US-32-parent-pending-queue.md`](./US-32-parent-pending-queue.md) |
| `US-33` | Parent approves a pending redemption | Rewards & Redemption | Critical | ★ | [`US-33-parent-approve.md`](./US-33-parent-approve.md) |
| `US-34` | Parent denies with optional reason | Rewards & Redemption | High |  | [`US-34-parent-deny.md`](./US-34-parent-deny.md) |
| `US-35` | Parent reverses an approved redemption | Rewards & Redemption | High |  | [`US-35-parent-reverse.md`](./US-35-parent-reverse.md) |
| `US-36` | Stock-limited reward refuses overflow | Rewards & Redemption | High |  | [`US-36-stock-limited-overflow.md`](./US-36-stock-limited-overflow.md) |
| `US-37` | Parent ping: review-flagged completion | Notifications | High |  | [`US-37-parent-ping-review-pending.md`](./US-37-parent-ping-review-pending.md) |
| `US-38` | Parent ping: deadline expired | Notifications | High |  | [`US-38-parent-ping-deadline-expired.md`](./US-38-parent-ping-deadline-expired.md) |
| `US-39` | Parent ping: redemption requested | Notifications | High |  | [`US-39-parent-ping-redemption-requested.md`](./US-39-parent-ping-redemption-requested.md) |
| `US-40` | Parent ping: recurring pool empty | Notifications | High |  | [`US-40-parent-ping-pool-empty.md`](./US-40-parent-ping-pool-empty.md) |
| `US-41` | Kid ping: new chore in pool | Notifications | High |  | [`US-41-kid-ping-new-chore.md`](./US-41-kid-ping-new-chore.md) |
| `US-42` | Kid ping: streak milestone (celebratory) | Notifications | High |  | [`US-42-kid-ping-streak-milestone.md`](./US-42-kid-ping-streak-milestone.md) |
| `US-43` | Kid ping: points awarded after parent approval | Notifications | High |  | [`US-43-kid-ping-points-awarded.md`](./US-43-kid-ping-points-awarded.md) |
| `US-44` | Kid ping: redemption approved or denied | Notifications | High |  | [`US-44-kid-ping-redemption-resolved.md`](./US-44-kid-ping-redemption-resolved.md) |
| `US-45` | Per-device web-push opt-in (parent only) | Notifications | High |  | [`US-45-web-push-opt-in.md`](./US-45-web-push-opt-in.md) |
| `US-46` | Kid works offline (Dexie outbox) | Sync & Offline | High |  | [`US-46-kid-offline.md`](./US-46-kid-offline.md) |
| `US-47` | Parent sees near-real-time kid activity | Sync & Offline | High |  | [`US-47-parent-realtime-activity.md`](./US-47-parent-realtime-activity.md) |
| `US-48` | Offline edits flow in cleanly on reconnect | Sync & Offline | High |  | [`US-48-offline-edits-reconcile.md`](./US-48-offline-edits-reconcile.md) |
| `US-49` | Per-field last-write-wins on conflicts | Sync & Offline | High |  | [`US-49-last-write-wins-per-field.md`](./US-49-last-write-wins-per-field.md) |
| `US-50` | Parent first chore CTA | Empty States & Onboarding Nudges | Standard |  | [`US-50-parent-first-chore-cta.md`](./US-50-parent-first-chore-cta.md) |
| `US-51` | Parent first reward CTA | Empty States & Onboarding Nudges | Standard |  | [`US-51-parent-first-reward-cta.md`](./US-51-parent-first-reward-cta.md) |
| `US-52` | Kid no-chores empty state | Empty States & Onboarding Nudges | Standard |  | [`US-52-kid-no-chores-empty.md`](./US-52-kid-no-chores-empty.md) |
| `US-53` | Kid first-link welcome | Empty States & Onboarding Nudges | Standard |  | [`US-53-kid-first-link-welcome.md`](./US-53-kid-first-link-welcome.md) |
| `US-54` | Avatar in celebratory moments | Visual Identity | Standard |  | [`US-54-avatar-celebratory.md`](./US-54-avatar-celebratory.md) |
| `US-55` | Parent-side quiet palette | Visual Identity | Standard |  | [`US-55-parent-quiet-palette.md`](./US-55-parent-quiet-palette.md) |

**Critical path (★)** — re-run on the final staging build before
sign-off. A `FAIL` or `BLOCKED` on any of these blocks ship.
Matches `uat/runbook.md` §7 and the critical-path table in
`uat/templates/uat-report.md`.

## Totals by area

| Feature area | Count |
|--------------|-------|
| Onboarding & Identity | 9 |
| Chores & Pools | 11 |
| Points & Streaks | 7 |
| Rewards & Redemption | 9 |
| Notifications | 9 |
| Sync & Offline | 4 |
| Empty States & Onboarding Nudges | 4 |
| Visual Identity | 2 |

**Total scenarios:** 55

## Synthesis provenance

- Source of truth: `docs/scope-brief.md` §2 (55 Given/When/Then user stories).
- Cross-checked against: `spec-v1-mvp.md` §User Stories 1–55.
- Voice + palette anchors: `CONTEXT.md`.
- Locked architecture: `docs/adr/0001-kid-identity-is-the-device.md`.
- Designer fidelity rules: `design/tokens/*.json` + `design/components/*.md`
  (placeholder paths until `t_fba7600a` ships the package).
- Authoring run: programmatic via `uat/tools/generate_scenarios.py`
  (deterministic; safe to regenerate).
