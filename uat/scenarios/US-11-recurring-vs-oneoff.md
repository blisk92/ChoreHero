# `US-11` — Choose recurring vs one-off when creating

| Field | Value |
|-------|-------|
| Story ID | `US-11` |
| Title | Choose recurring vs one-off when creating |
| Feature area | Chores & Pools |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.11 |
| Spec ref | `spec-v1-mvp.md` §User Stories 11 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/screens/chore-editor.md`
- `design/components/toggle.md`

## Preconditions

1. Same as US-10.

## Scenario

**Given** a parent creating a chore

**When** they toggle recurring/one-off in the editor

**Then** the following expected outcomes are observed:

1. The chore's `kind` field is set to `recurring` or `one_off` accordingly.
2. Recurring: no `due_at` exposed / accepted.
3. One-off: `due_at` input becomes enabled.
4. Lifecycle on resolve behaves per CONTEXT.md glossary: recurring returns to pool; one-off is removed from circulation on resolve.

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Toggle uses `toggle.md`; both states labelled inline.
2. When switching to recurring, the `due_at` field collapses (animatable).

## Accessibility (WCAG 2.1 AA)

1. Toggle's on/off state is conveyed by both text label and visual position (WCAG 1.4.1).
2. Disabled `due_at` is announced as disabled to assistive tech (WCAG 4.1.2).

## Evidence to record

Capture under `evidence/US-11-recurring-vs-oneoff/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshots of editor in both toggle positions.
2. DB row showing `kind` field.

## References

- User-story source: `docs/scope-brief.md` §2.11
- Spec section: `spec-v1-mvp.md` §User Stories 11
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Chores & Pools cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
