# `US-31` — Kid requests a redemption

| Field | Value |
|-------|-------|
| Story ID | `US-31` |
| Title | Kid requests a redemption |
| Feature area | Rewards & Redemption |
| Priority | Critical |
| Scope brief ref | `docs/scope-brief.md` §2.31 |
| Spec ref | `spec-v1-mvp.md` §User Stories 31 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/screens/kid-redeem.md`
- `design/components/reward-card.md`

## Preconditions

1. Reward catalog has a reward the kid can afford.
2. Kid has a non-zero balance.

## Scenario

**Given** a kid on the Redeem screen

**When** they tap a reward

**Then** the following expected outcomes are observed:

1. A `Redemption` row is created with `status: pending`.
2. A parent notification is enqueued (US-39).
3. No points are deducted at this stage.
4. Optimistic local state shows the request as pending on the kid side.

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Tap target is the reward card.
2. Confirmation affordance: design may include a confirm step before request commits.

## Accessibility (WCAG 2.1 AA)

1. Tap target ≥ 44x44 CSS px (WCAG 2.5.5).
2. Result announced via aria-live (WCAG 4.1.3).

## Evidence to record

Capture under `evidence/US-31-request-redemption/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshot before and after tap.
2. Network `.har` for `POST /api/redemptions`.
3. DB rows: `Redemption` and `Notification`.

## References

- User-story source: `docs/scope-brief.md` §2.31
- Spec section: `spec-v1-mvp.md` §User Stories 31
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Rewards & Redemption cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
