# `US-13` — Deadline on a one-off chore

| Field | Value |
|-------|-------|
| Story ID | `US-13` |
| Title | Deadline on a one-off chore |
| Feature area | Chores & Pools |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.13 |
| Spec ref | `spec-v1-mvp.md` §User Stories 13 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/components/date-picker.md`

## Preconditions

1. Creating or editing a one-off chore.

## Scenario

**Given** a parent creating or editing a one-off chore

**When** they set a `due_at` timestamp

**Then** the following expected outcomes are observed:

1. The chore's deadline-expiry path is active.
2. If the kid does not complete it by `due_at`, the server-side expiry pass transitions the chore to `status: expired` and enqueues a parent notification (US-38).
3. Validation: cannot set `due_at` on a recurring chore (US-11).

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Date picker uses `date-picker.md`; default value unset; reasonable future-only restriction.

## Accessibility (WCAG 2.1 AA)

1. Date picker is keyboard-operable and announces selected value (WCAG 1.3.1, 2.1.1).
2. Error state for past dates is announced.

## Evidence to record

Capture under `evidence/US-13-deadline-oneoff/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshot of editor with `due_at` set.
2. DB row showing `due_at`.
3. (Time-dependent) screenshot after expiry pass — force fixed staging time per runbook §9.

## References

- User-story source: `docs/scope-brief.md` §2.13
- Spec section: `spec-v1-mvp.md` §User Stories 13
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Chores & Pools cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
