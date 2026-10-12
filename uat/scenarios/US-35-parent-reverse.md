# `US-35` — Parent reverses an approved redemption

| Field | Value |
|-------|-------|
| Story ID | `US-35` |
| Title | Parent reverses an approved redemption |
| Feature area | Rewards & Redemption |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.35 |
| Spec ref | `spec-v1-mvp.md` §User Stories 35 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/screens/parent-dashboard.md`
- `design/components/confirmation-dialog.md`

## Preconditions

1. An approved `Redemption` exists.

## Scenario

**Given** a previously approved redemption

**When** the parent taps Reverse and confirms

**Then** the following expected outcomes are observed:

1. A positive `PointsLedger` entry offsets the original debit.
2. `Redemption.status = reversed`.
3. The kid is notified (US-44).

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Reverse requires a confirmation dialog (destructive).

## Accessibility (WCAG 2.1 AA)

1. Confirmation traps focus and is announced.

## Evidence to record

Capture under `evidence/US-35-parent-reverse/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshot of confirmation dialog.
2. DB rows: `Redemption` (status), `PointsLedger` (positive delta), `Notification`.

## References

- User-story source: `docs/scope-brief.md` §2.35
- Spec section: `spec-v1-mvp.md` §User Stories 35
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Rewards & Redemption cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
