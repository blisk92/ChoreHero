# `US-21` — Kid sees running balance on home

| Field | Value |
|-------|-------|
| Story ID | `US-21` |
| Title | Kid sees running balance on home |
| Feature area | Points & Streaks |
| Priority | Critical |
| Scope brief ref | `docs/scope-brief.md` §2.21 |
| Spec ref | `spec-v1-mvp.md` §User Stories 21 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/screens/kid-home.md`
- `design/components/balance-badge.md`

## Preconditions

1. Kid device signed in (US-5).
2. At least one ledger entry (or seed balance of 0).

## Scenario

**Given** a kid on the kiosk home

**When** they open the home screen

**Then** the following expected outcomes are observed:

1. Balance shown = `SUM(PointsLedger.delta) WHERE child_id = ?`.
2. Balance is prominent (top of screen / hero area).
3. When balance is 0, badge shows `0` with no special copy (per CONTEXT.md).

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Badge uses `balance-badge.md`; large number; kid-side accent.

## Accessibility (WCAG 2.1 AA)

1. Badge has accessible name including the numeric value (WCAG 4.1.2).
2. Color contrast on the badge text ≥ 4.5:1.

## Evidence to record

Capture under `evidence/US-21-kid-running-balance/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshot of home screen with balance.
2. Network `.har` for balance fetch.
3. DB ledger sum compared to displayed value.

## References

- User-story source: `docs/scope-brief.md` §2.21
- Spec section: `spec-v1-mvp.md` §User Stories 21
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Points & Streaks cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
