# `US-12` — Edit or delete a pooled chore

| Field | Value |
|-------|-------|
| Story ID | `US-12` |
| Title | Edit or delete a pooled chore |
| Feature area | Chores & Pools |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.12 |
| Spec ref | `spec-v1-mvp.md` §User Stories 12 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/screens/chore-editor.md`
- `design/components/confirmation-dialog.md`

## Preconditions

1. At least one chore exists in the pool (from US-10).
2. The chore is in `status: pool` — not claimed.

## Scenario

**Given** a parent viewing a pooled chore

**When** they edit a field and save, OR tap Delete and confirm

**Then** the following expected outcomes are observed:

1. Edit: change persists; kid sees updated values on the next sync tick.
2. Edit: `updated_at` per field advances; per-field last-write-wins applies (US-49).
3. Delete: chore row archived (or removed per implementation) and disappears from the kid pool on the next sync.
4. Edit a claimed chore is disabled in v1 (per scope-brief §2.12); the editor surfaces a disabled state with explanatory copy.

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Delete requires `confirmation-dialog.md`.
2. Edit form pre-populates current values.

## Accessibility (WCAG 2.1 AA)

1. Edit fields keep their labels and order from US-10.
2. Delete confirmation traps focus (WCAG 2.4.3).

## Evidence to record

Capture under `evidence/US-12-edit-delete-chore/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshots of edit form and confirm-delete dialog.
2. Network `.har` for `PATCH /api/chores/:id` and `DELETE /api/chores/:id`.
3. DB row diff for the chore.
4. Screenshot of kid SPA reflecting the change.

## References

- User-story source: `docs/scope-brief.md` §2.12
- Spec section: `spec-v1-mvp.md` §User Stories 12
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Chores & Pools cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
