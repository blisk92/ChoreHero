# `US-37` — Parent ping: review-flagged completion

| Field | Value |
|-------|-------|
| Story ID | `US-37` |
| Title | Parent ping: review-flagged completion |
| Feature area | Notifications |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.37 |
| Spec ref | `spec-v1-mvp.md` §User Stories 37 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/components/notification-list.md`
- `design/components/notification-toast.md`

## Preconditions

1. Review-flagged chore; kid marks it complete (US-18).

## Scenario

**Given** a review-flagged chore is marked done

**When** the completion commits server-side

**Then** the following expected outcomes are observed:

1. Parent's in-app notification list gains a "Review pending" entry with the chore name.
2. If parent opted into web push on this device (US-45), a web-push notification is delivered.

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Notification uses parent-side quiet palette; affordance to jump to the pending review.

## Accessibility (WCAG 2.1 AA)

1. Notification announced via aria-live; actionable with a single activation (WCAG 4.1.3, 2.1.1).

## Evidence to record

Capture under `evidence/US-37-parent-ping-review-pending/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshot of parent notification list.
2. (If push opt-in) screenshot of lock-screen push on the parent device.
3. DB row for `Notification`.

## References

- User-story source: `docs/scope-brief.md` §2.37
- Spec section: `spec-v1-mvp.md` §User Stories 37
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Notifications cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
