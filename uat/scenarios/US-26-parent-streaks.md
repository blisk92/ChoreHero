# `US-26` — Parent sees per-chore streaks

| Field | Value |
|-------|-------|
| Story ID | `US-26` |
| Title | Parent sees per-chore streaks |
| Feature area | Points & Streaks |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.26 |
| Spec ref | `spec-v1-mvp.md` §User Stories 26 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/screens/chore-detail.md`
- `design/components/streak-pill.md`

## Preconditions

1. At least one recurring chore with non-zero streak (US-24).

## Scenario

**Given** a parent viewing a chore detail

**When** they open it

**Then** the following expected outcomes are observed:

1. Current streak length is visible.
2. Longest streak length is visible.
3. Last completed date is visible.

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Detail screen uses `chore-detail.md`; streak block uses `streak-pill.md` (parent variant).

## Accessibility (WCAG 2.1 AA)

1. Numeric values announced in plain language ("current 5-day streak, longest 12") (WCAG 1.1.1).

## Evidence to record

Capture under `evidence/US-26-parent-streaks/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshot of chore detail.
2. DB row for `Streak`.

## References

- User-story source: `docs/scope-brief.md` §2.26
- Spec section: `spec-v1-mvp.md` §User Stories 26
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Points & Streaks cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
