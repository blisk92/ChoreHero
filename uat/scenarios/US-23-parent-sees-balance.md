# `US-23` — Parent sees kid's balance on dashboard

| Field | Value |
|-------|-------|
| Story ID | `US-23` |
| Title | Parent sees kid's balance on dashboard |
| Feature area | Points & Streaks |
| Priority | Critical |
| Scope brief ref | `docs/scope-brief.md` §2.23 |
| Spec ref | `spec-v1-mvp.md` §User Stories 23 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/screens/parent-dashboard.md`
- `design/components/balance-card.md`

## Preconditions

1. Parent signed in (US-1).
2. Child profile exists (US-4).
3. At least one ledger entry.

## Scenario

**Given** a parent on the dashboard

**When** the dashboard loads

**Then** the following expected outcomes are observed:

1. Kid's current balance is visible.
2. Balance equals the server-computed `SUM(PointsLedger.delta)` for the child.

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Balance card uses `balance-card.md`; parent-side quiet palette (US-55).

## Accessibility (WCAG 2.1 AA)

1. Card has accessible name including child name and balance value (WCAG 4.1.2).

## Evidence to record

Capture under `evidence/US-23-parent-sees-balance/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshot of parent dashboard.
2. DB ledger sum matches displayed value.

## References

- User-story source: `docs/scope-brief.md` §2.23
- Spec section: `spec-v1-mvp.md` §User Stories 23
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Points & Streaks cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
