# `US-33` — Parent approves a pending redemption

| Field | Value |
|-------|-------|
| Story ID | `US-33` |
| Title | Parent approves a pending redemption |
| Feature area | Rewards & Redemption |
| Priority | Critical |
| Scope brief ref | `docs/scope-brief.md` §2.33 |
| Spec ref | `spec-v1-mvp.md` §User Stories 33 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/screens/parent-dashboard.md`
- `design/components/pending-item.md`

## Preconditions

1. Pending redemption exists (US-31).

## Scenario

**Given** a parent on a pending redemption row

**When** they tap Approve

**Then** the following expected outcomes are observed:

1. `Redemption.status = approved`.
2. A negative `PointsLedger` entry is appended (delta = -cost).
3. The kid is notified (US-44).
4. If `stock_remaining` is set, stock is decremented (or refused per scope-brief §7 Q6 default — refuse at request time when stock = 0, decrement at approval).

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Approve is a primary action; Deny is secondary in the row.

## Accessibility (WCAG 2.1 AA)

1. Action result announced (WCAG 4.1.3).
2. Focus moves to the next pending item or to the empty state.

## Evidence to record

Capture under `evidence/US-33-parent-approve/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshot of row before and after.
2. Network `.har` for approval call.
3. DB rows: `Redemption` (status), `PointsLedger` (delta), `Notification` (kid).

## References

- User-story source: `docs/scope-brief.md` §2.33
- Spec section: `spec-v1-mvp.md` §User Stories 33
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Rewards & Redemption cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
