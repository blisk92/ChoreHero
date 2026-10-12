# `US-36` — Stock-limited reward refuses overflow

| Field | Value |
|-------|-------|
| Story ID | `US-36` |
| Title | Stock-limited reward refuses overflow |
| Feature area | Rewards & Redemption |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.36 |
| Spec ref | `spec-v1-mvp.md` §User Stories 36 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/components/reward-card.md`

## Preconditions

1. Reward with `stock_remaining = 0` (seeded via runbook §4.4 or admin).

## Scenario

**Given** a kid viewing an out-of-stock reward

**When** they tap it

**Then** the following expected outcomes are observed:

1. The request is refused client-side (visible out-of-stock state).
2. No `Redemption` row is created.
3. No parent notification.
4. Server returns 4xx if a request slips through.

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Out-of-stock badge is shown on the card; tap does not initiate redemption.
2. Affordance is disabled (greyed) with a tooltip or label "Out of stock".

## Accessibility (WCAG 2.1 AA)

1. Disabled state conveyed by both visual styling and `aria-disabled` (WCAG 4.1.2).
2. Out-of-stock label is in the accessible name.

## Evidence to record

Capture under `evidence/US-36-stock-limited-overflow/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshot of out-of-stock reward card.
2. Network `.har` confirming no `POST /api/redemptions` for the reward.

## References

- User-story source: `docs/scope-brief.md` §2.36
- Spec section: `spec-v1-mvp.md` §User Stories 36
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Rewards & Redemption cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
