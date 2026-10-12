# `US-10` — Create a chore

| Field | Value |
|-------|-------|
| Story ID | `US-10` |
| Title | Create a chore |
| Feature area | Chores & Pools |
| Priority | Critical |
| Scope brief ref | `docs/scope-brief.md` §2.10 |
| Spec ref | `spec-v1-mvp.md` §User Stories 10 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/screens/chore-editor.md`
- `design/components/form-field.md`
- `design/components/button.md`

## Preconditions

1. Parent signed in (US-1).
2. Child profile exists (US-4).

## Scenario

**Given** a parent on the chores page

**When** they create a chore with name, point value, optional `review_flagged`, and optional `due_at`

**Then** the following expected outcomes are observed:

1. A `Chore` row is created in the correct pool (recurring vs one-off, decided by the parent — see US-11).
2. The chore is visible to the kid on the next sync tick.
3. Validation: name non-empty; point value > 0; `due_at` only meaningful for one-off chores (see US-13).

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Editor uses `form-field.md` for name + value, toggle switch for `review_flagged` and recurring/one-off, date picker for `due_at` (disabled unless one-off).
2. Submit CTA is disabled until required fields are valid.

## Accessibility (WCAG 2.1 AA)

1. All form fields labelled (WCAG 1.3.1).
2. Toggle switches announce on/off state via aria (WCAG 4.1.2).
3. Validation errors are programmatically associated to fields and announced (WCAG 1.3.1, 3.3.1).

## Evidence to record

Capture under `evidence/US-10-create-chore/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshot of editor pre-fill.
2. Screenshot of validation error.
3. Screenshot of kid SPA showing the new chore in the pool.
4. Network `.har` for `POST /api/chores`.
5. DB row for `Chore`.

## References

- User-story source: `docs/scope-brief.md` §2.10
- Spec section: `spec-v1-mvp.md` §User Stories 10
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Chores & Pools cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
