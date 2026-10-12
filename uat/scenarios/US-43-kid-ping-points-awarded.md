# `US-43` — Kid ping: points awarded after parent approval

| Field | Value |
|-------|-------|
| Story ID | `US-43` |
| Title | Kid ping: points awarded after parent approval |
| Feature area | Notifications |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.43 |
| Spec ref | `spec-v1-mvp.md` §User Stories 43 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/components/kid-notification-toast.md`

## Preconditions

1. Review-flagged completion approved (US-37 → US-33-style approval for chore completion).

## Scenario

**Given** a parent approves a review-flagged completion

**When** the approval commits

**Then** the following expected outcomes are observed:

1. Kid receives an in-app notification announcing the points increase.
2. Kid's balance updates accordingly.
3. No web-push.

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Inherits US-41 toast styling.

## Accessibility (WCAG 2.1 AA)

1. Inherits US-41 a11y.

## Evidence to record

Capture under `evidence/US-43-kid-ping-points-awarded/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshot of kid SPA toast and updated balance.
2. DB rows: notification + ledger.

## References

- User-story source: `docs/scope-brief.md` §2.43
- Spec section: `spec-v1-mvp.md` §User Stories 43
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Notifications cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
