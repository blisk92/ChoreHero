# `US-25` — Streak resets on a missed day

| Field | Value |
|-------|-------|
| Story ID | `US-25` |
| Title | Streak resets on a missed day |
| Feature area | Points & Streaks |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.25 |
| Spec ref | `spec-v1-mvp.md` §User Stories 25 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/components/streak-pill.md`

## Preconditions

1. Recurring chore with `Streak.last_completed_on < D-1`.
2. Force staging clock per runbook §9.

## Scenario

**Given** a recurring chore with a stale streak

**When** day D arrives without completion and then the child completes it

**Then** the following expected outcomes are observed:

1. `Streak.current_length` resets to 1 (fresh streak).
2. `Streak.last_completed_on = D`.
3. Longest length is preserved.

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Streak pill shows `1` post-completion.

## Accessibility (WCAG 2.1 AA)

1. Skip — inherited from US-20.

## Evidence to record

Capture under `evidence/US-25-streak-reset/` and reference
from `templates/uat-report.md` §"Evidence index".

1. DB row for `Streak`.
2. Screenshot of streak pill.

## References

- User-story source: `docs/scope-brief.md` §2.25
- Spec section: `spec-v1-mvp.md` §User Stories 25
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Points & Streaks cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
