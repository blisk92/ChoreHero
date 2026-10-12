# `US-38` — Parent ping: deadline expired

| Field | Value |
|-------|-------|
| Story ID | `US-38` |
| Title | Parent ping: deadline expired |
| Feature area | Notifications |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.38 |
| Spec ref | `spec-v1-mvp.md` §User Stories 38 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/components/notification-list.md`

## Preconditions

1. Deadline one-off chore exists; force staging clock past `due_at` per runbook §9.

## Scenario

**Given** a deadline one-off chore passes `due_at` without completion

**When** the expiry pass runs

**Then** the following expected outcomes are observed:

1. Chore transitions to `status: expired`.
2. Parent's in-app notification list gains an entry.
3. If push opt-in, web-push fires.

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Skip — inherited from US-37.

## Accessibility (WCAG 2.1 AA)

1. Skip — inherited from US-37.

## Evidence to record

Capture under `evidence/US-38-parent-ping-deadline-expired/` and reference
from `templates/uat-report.md` §"Evidence index".

1. DB row for chore (status) and notification.
2. Screenshot of notification.

## References

- User-story source: `docs/scope-brief.md` §2.38
- Spec section: `spec-v1-mvp.md` §User Stories 38
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Notifications cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
