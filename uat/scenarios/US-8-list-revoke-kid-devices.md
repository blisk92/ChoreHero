# `US-8` — List and revoke kid devices

| Field | Value |
|-------|-------|
| Story ID | `US-8` |
| Title | List and revoke kid devices |
| Feature area | Onboarding & Identity |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.8 |
| Spec ref | `spec-v1-mvp.md` §User Stories 8 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/components/list-item.md`
- `design/components/confirmation-dialog.md`

## Preconditions

1. At least one `KidDevice` linked to the household (from US-5).

## Scenario

**Given** a parent in settings → "Kid devices"

**When** they open the device list

**Then** the following expected outcomes are observed:

1. Every registered `KidDevice` is listed with friendly name, `last_seen_at`, and a revoke control.
2. Tapping revoke sets `revoked_at`, invalidates the device token, and the device is removed from the active list (or marked revoked).
3. Subsequent kid-device API calls with the revoked token return 401.

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. List uses `list-item.md`; each row has friendly name, relative timestamp ("last seen 3 min ago"), and a destructive Revoke action.
2. Empty state copy: "No kid devices linked yet." with a CTA to US-5.

## Accessibility (WCAG 2.1 AA)

1. List is semantic `<ul>` / `<li>` or aria-equivalent (WCAG 1.3.1).
2. Each row's revoke button has an accessible name including the device's friendly name (WCAG 4.1.2).
3. Confirm-revoke dialog traps focus (WCAG 2.4.3).

## Evidence to record

Capture under `evidence/US-8-list-revoke-kid-devices/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshot of populated device list.
2. Screenshot of confirm-revoke dialog.
3. Network `.har` for revoke call.
4. Network `.har` showing a 401 from the kid SPA after revoke.

## References

- User-story source: `docs/scope-brief.md` §2.8
- Spec section: `spec-v1-mvp.md` §User Stories 8
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Onboarding & Identity cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
