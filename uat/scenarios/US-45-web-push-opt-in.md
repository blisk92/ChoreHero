# `US-45` — Per-device web-push opt-in (parent only)

| Field | Value |
|-------|-------|
| Story ID | `US-45` |
| Title | Per-device web-push opt-in (parent only) |
| Feature area | Notifications |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.45 |
| Spec ref | `spec-v1-mvp.md` §User Stories 45 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/components/toggle.md`
- `design/components/lock-screen-notification.md`

## Preconditions

1. Parent signed in on a parent device.
2. Staging VAPID keys configured; OS-level push enabled.

## Scenario

**Given** a parent on a device

**When** they toggle "Allow push" in settings

**Then** the following expected outcomes are observed:

1. The device is subscribed to the parent's VAPID push endpoint.
2. Subsequent events 37-40 deliver a web-push ping to the lock screen.
3. Toggle is off by default.
4. Kid devices never subscribe (out of scope).

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Toggle uses `toggle.md`; default off; explanation mentions what pings they'll receive.

## Accessibility (WCAG 2.1 AA)

1. Toggle state announced; the explanation is programmatically associated via `aria-describedby` (WCAG 1.3.1, 3.3.2).

## Evidence to record

Capture under `evidence/US-45-web-push-opt-in/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshot of toggle off (default).
2. Screenshot of toggle on with subscription state.
3. Screenshot of lock-screen push on the parent device.
4. DB row for the subscription.

## References

- User-story source: `docs/scope-brief.md` §2.45
- Spec section: `spec-v1-mvp.md` §User Stories 45
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Notifications cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
