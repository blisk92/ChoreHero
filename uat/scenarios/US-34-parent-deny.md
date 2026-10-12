# `US-34` — Parent denies with optional reason

| Field | Value |
|-------|-------|
| Story ID | `US-34` |
| Title | Parent denies with optional reason |
| Feature area | Rewards & Redemption |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.34 |
| Spec ref | `spec-v1-mvp.md` §User Stories 34 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/components/deny-dialog.md`

## Preconditions

1. Pending redemption exists.

## Scenario

**Given** a parent on a pending redemption row

**When** they tap Deny and optionally enter a reason

**Then** the following expected outcomes are observed:

1. `Redemption.status = denied` with `denial_reason` captured if provided.
2. No points moved.
3. The kid is notified (US-44).

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Deny opens a dialog with an optional textarea; reason optional per spec.

## Accessibility (WCAG 2.1 AA)

1. Dialog traps focus; textarea has associated label (WCAG 1.3.1, 2.4.3).
2. Submit button label clarifies "Deny without reason" vs "Deny with reason".

## Evidence to record

Capture under `evidence/US-34-parent-deny/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshot of deny dialog.
2. DB row for `Redemption` with status and reason.

## References

- User-story source: `docs/scope-brief.md` §2.34
- Spec section: `spec-v1-mvp.md` §User Stories 34
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Rewards & Redemption cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
