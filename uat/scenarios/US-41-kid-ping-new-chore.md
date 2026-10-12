# `US-41` — Kid ping: new chore in pool

| Field | Value |
|-------|-------|
| Story ID | `US-41` |
| Title | Kid ping: new chore in pool |
| Feature area | Notifications |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.41 |
| Spec ref | `spec-v1-mvp.md` §User Stories 41 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/components/kid-notification-toast.md`

## Preconditions

1. Parent creates a chore (US-10); kid SPA is in-app (open or backgrounded).

## Scenario

**Given** a parent adds a chore

**When** the chore is committed

**Then** the following expected outcomes are observed:

1. Kid device's in-app notification list gains an entry.
2. If the kid SPA is open and the chore is in a visible pool, the UI updates without manual refresh (eventually-consistent on next sync tick).
3. Kid devices NEVER receive a web-push (out of scope per CONTEXT.md).

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Toast uses kid-side accent; the chore name + point value is on the surface.

## Accessibility (WCAG 2.1 AA)

1. Toast announced via aria-live; not the only signal (list also updates) (WCAG 1.4.1, 4.1.3).

## Evidence to record

Capture under `evidence/US-41-kid-ping-new-chore/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshot of kid SPA toast.
2. DB row for `Notification`.

## References

- User-story source: `docs/scope-brief.md` §2.41
- Spec section: `spec-v1-mvp.md` §User Stories 41
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Notifications cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
