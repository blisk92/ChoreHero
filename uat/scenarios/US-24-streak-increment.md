# `US-24` — Streak increments on consecutive-day completion

| Field | Value |
|-------|-------|
| Story ID | `US-24` |
| Title | Streak increments on consecutive-day completion |
| Feature area | Points & Streaks |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.24 |
| Spec ref | `spec-v1-mvp.md` §User Stories 24 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/components/streak-pill.md`

## Preconditions

1. A recurring chore with `Streak.last_completed_on = D-1`.
2. Force staging clock per runbook §9.

## Scenario

**Given** a recurring chore with streak last completed yesterday

**When** the child completes the chore on day D

**Then** the following expected outcomes are observed:

1. `Streak.current_length` increments by 1.
2. `Streak.last_completed_on = D`.
3. Longest length updated if exceeded.

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Streak pill on kid + parent views reflects the new length (US-20, US-26).

## Accessibility (WCAG 2.1 AA)

1. Skip — inherited from US-20 / US-26.

## Evidence to record

Capture under `evidence/US-24-streak-increment/` and reference
from `templates/uat-report.md` §"Evidence index".

1. DB row for `Streak` before and after.
2. Screenshot of streak pill before and after.

## References

- User-story source: `docs/scope-brief.md` §2.24
- Spec section: `spec-v1-mvp.md` §User Stories 24
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Points & Streaks cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
