# `US-30` — Kid browses the reward catalog

| Field | Value |
|-------|-------|
| Story ID | `US-30` |
| Title | Kid browses the reward catalog |
| Feature area | Rewards & Redemption |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.30 |
| Spec ref | `spec-v1-mvp.md` §User Stories 30 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/screens/kid-redeem.md`
- `design/components/reward-card.md`

## Preconditions

1. At least one reward exists (US-28).

## Scenario

**Given** a kid on the kiosk

**When** they open Redeem

**Then** the following expected outcomes are observed:

1. Every reward is shown with name, description (if any), and point cost.
2. Out-of-stock rewards are visibly marked (US-36).

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Catalog uses `reward-card.md`; cost badge uses kid-side accent.

## Accessibility (WCAG 2.1 AA)

1. Each card has accessible name with reward name and cost (WCAG 4.1.2).
2. Out-of-stock state is conveyed by both visual badge and accessible name ("Out of stock") (WCAG 1.4.1).

## Evidence to record

Capture under `evidence/US-30-browse-reward-catalog/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshot of catalog with multiple rewards.
2. Screenshot of catalog with out-of-stock reward.

## References

- User-story source: `docs/scope-brief.md` §2.30
- Spec section: `spec-v1-mvp.md` §User Stories 30
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Rewards & Redemption cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
