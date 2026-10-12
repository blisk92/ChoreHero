# `US-17` — See "My Active" claimed chores

| Field | Value |
|-------|-------|
| Story ID | `US-17` |
| Title | See "My Active" claimed chores |
| Feature area | Chores & Pools |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.17 |
| Spec ref | `spec-v1-mvp.md` §User Stories 17 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/screens/kid-today.md`
- `design/components/chore-card.md`

## Preconditions

1. At least one claimed chore (US-16).

## Scenario

**Given** a kid with one or more claimed chores

**When** they open Today

**Then** the following expected outcomes are observed:

1. Claimed chores appear under "My Active".
2. Claimed chores do NOT also appear in Available Extras.
3. Each card shows Done and Skip affordances.

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. "My Active" section uses kid-side accent with subtle elevation difference from Available Extras.

## Accessibility (WCAG 2.1 AA)

1. Cards maintain accessible names; Done and Skip buttons have descriptive accessible names (WCAG 4.1.2).

## Evidence to record

Capture under `evidence/US-17-my-active/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshot of Today with both sections populated.
2. Screenshot showing a claimed chore absent from Available Extras.

## References

- User-story source: `docs/scope-brief.md` §2.17
- Spec section: `spec-v1-mvp.md` §User Stories 17
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Chores & Pools cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
