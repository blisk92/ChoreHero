# `US-29` — Edit or remove a reward

| Field | Value |
|-------|-------|
| Story ID | `US-29` |
| Title | Edit or remove a reward |
| Feature area | Rewards & Redemption |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.29 |
| Spec ref | `spec-v1-mvp.md` §User Stories 29 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/screens/reward-editor.md`
- `design/components/confirmation-dialog.md`

## Preconditions

1. At least one reward exists (US-28).

## Scenario

**Given** a parent viewing a reward

**When** they edit a field and save, OR tap Remove and confirm

**Then** the following expected outcomes are observed:

1. Edit: change persists; kid sees updated catalog on next sync.
2. Remove: reward disappears from the kid catalog on next sync; no in-flight redemption created.

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Remove requires `confirmation-dialog.md`.
2. Catalog update is eventual; UI does not require a manual refresh on the kid side.

## Accessibility (WCAG 2.1 AA)

1. Edit fields labelled; remove confirmation traps focus (WCAG 2.4.3).

## Evidence to record

Capture under `evidence/US-29-edit-remove-reward/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshots of edit form and confirm-remove dialog.
2. Network `.har` for edit/remove calls.
3. DB row diff.

## References

- User-story source: `docs/scope-brief.md` §2.29
- Spec section: `spec-v1-mvp.md` §User Stories 29
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Rewards & Redemption cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
