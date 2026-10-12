# `US-19` — Skip a claimed chore

| Field | Value |
|-------|-------|
| Story ID | `US-19` |
| Title | Skip a claimed chore |
| Feature area | Chores & Pools |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.19 |
| Spec ref | `spec-v1-mvp.md` §User Stories 19 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/components/chore-card.md`

## Preconditions

1. A claimed chore exists.

## Scenario

**Given** a kid with a claimed chore

**When** they tap "Skip"

**Then** the following expected outcomes are observed:

1. Recurring → chore returns to pool; no ledger entry; no parent ping.
2. One-off with deadline → chore status becomes `expired`; parent is notified (US-38).
3. One-off without deadline → chore returns to pool; no ledger entry; no parent ping.

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Skip is a secondary affordance (less prominent than Done).
2. For deadline one-offs, the post-skip state shows a quiet "This chore expired" affordance on the kid side.

## Accessibility (WCAG 2.1 AA)

1. Skip action announces the outcome variant that will happen (e.g. "Skip — chore will return to pool") (WCAG 4.1.3).

## Evidence to record

Capture under `evidence/US-19-skip-chore/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Three scenarios × screenshots: recurring skip, deadline one-off skip (parent ping), at-will one-off skip.
2. DB row transitions per kind.

## References

- User-story source: `docs/scope-brief.md` §2.19
- Spec section: `spec-v1-mvp.md` §User Stories 19
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Chores & Pools cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
