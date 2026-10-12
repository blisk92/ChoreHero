# `US-20` — See streak count on a recurring chore

| Field | Value |
|-------|-------|
| Story ID | `US-20` |
| Title | See streak count on a recurring chore |
| Feature area | Chores & Pools |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.20 |
| Spec ref | `spec-v1-mvp.md` §User Stories 20 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/components/chore-card.md`
- `design/components/streak-pill.md`

## Preconditions

1. At least one recurring chore with a non-zero `Streak.current_length` (run for several days or seed via admin).

## Scenario

**Given** a kid viewing a recurring chore

**When** they view it in Available Extras or My Active

**Then** the following expected outcomes are observed:

1. Current streak is shown inline on the card (e.g. "🔥 3").
2. Streak value is read from the `Streak` projection, not recomputed on the client (per scope brief).

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Streak pill uses `streak-pill.md`; kid-side accent; clearly secondary to the chore name.

## Accessibility (WCAG 2.1 AA)

1. Streak value is announced textually (e.g. "3-day streak"), not via emoji-only (WCAG 1.1.1, 1.4.1).

## Evidence to record

Capture under `evidence/US-20-streak-inline/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshot of recurring chore with streak.
2. Network `.har` for chore fetch.
3. DB row for `Streak` matching displayed value.

## References

- User-story source: `docs/scope-brief.md` §2.20
- Spec section: `spec-v1-mvp.md` §User Stories 20
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Chores & Pools cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
