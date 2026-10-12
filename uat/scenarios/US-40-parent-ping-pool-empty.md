# `US-40` — Parent ping: recurring pool empty

| Field | Value |
|-------|-------|
| Story ID | `US-40` |
| Title | Parent ping: recurring pool empty |
| Feature area | Notifications |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.40 |
| Spec ref | `spec-v1-mvp.md` §User Stories 40 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/components/notification-list.md`

## Preconditions

1. Recurring pool had claimable chores; the last one was claimed / completed (no recurrings left).

## Scenario

**Given** the recurring pool's claimable count drops to 0

**When** that state change is observed

**Then** the following expected outcomes are observed:

1. Parent's in-app notification list gains an entry.
2. If push opt-in, web-push fires.
3. Notification fires once per empty transition (not on every poll).

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Skip — inherited from US-37.

## Accessibility (WCAG 2.1 AA)

1. Skip — inherited from US-37.

## Evidence to record

Capture under `evidence/US-40-parent-ping-pool-empty/` and reference
from `templates/uat-report.md` §"Evidence index".

1. DB row for notification.
2. Screenshot of notification.

## References

- User-story source: `docs/scope-brief.md` §2.40
- Spec section: `spec-v1-mvp.md` §User Stories 40
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Notifications cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
