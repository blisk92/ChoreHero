# `US-14` — Mark a chore review-flagged

| Field | Value |
|-------|-------|
| Story ID | `US-14` |
| Title | Mark a chore review-flagged |
| Feature area | Chores & Pools |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.14 |
| Spec ref | `spec-v1-mvp.md` §User Stories 14 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/components/toggle.md`

## Preconditions

1. Creating or editing a chore.

## Scenario

**Given** a parent creating or editing a chore

**When** they set `review_flagged = true`

**Then** the following expected outcomes are observed:

1. The chore is marked `review_flagged = true`.
2. When the kid marks it complete (US-18), the server holds the points until parent approval (US-33 path for approval; the denied path returns the chore to pool per spec state machine).

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Toggle has visible explanation: "I'll approve before points are awarded."

## Accessibility (WCAG 2.1 AA)

1. Help text associated to the toggle via `aria-describedby` (WCAG 1.3.1, 3.3.2).

## Evidence to record

Capture under `evidence/US-14-review-flagged/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshot of editor with review flag on.
2. End-to-end: chore created → kid marks done → points NOT awarded yet → parent approves → points awarded.

## References

- User-story source: `docs/scope-brief.md` §2.14
- Spec section: `spec-v1-mvp.md` §User Stories 14
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Chores & Pools cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
