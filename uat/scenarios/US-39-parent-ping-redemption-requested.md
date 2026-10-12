# `US-39` — Parent ping: redemption requested

| Field | Value |
|-------|-------|
| Story ID | `US-39` |
| Title | Parent ping: redemption requested |
| Feature area | Notifications |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.39 |
| Spec ref | `spec-v1-mvp.md` §User Stories 39 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/components/notification-list.md`

## Preconditions

1. Kid requests a redemption (US-31).

## Scenario

**Given** a kid requests a redemption

**When** the request commits

**Then** the following expected outcomes are observed:

1. Parent's in-app notification list gains a "Redemption requested" entry.
2. If push opt-in, web-push fires.

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Skip — inherited from US-37.

## Accessibility (WCAG 2.1 AA)

1. Skip — inherited from US-37.

## Evidence to record

Capture under `evidence/US-39-parent-ping-redemption-requested/` and reference
from `templates/uat-report.md` §"Evidence index".

1. DB row for notification.
2. Screenshot of notification.

## References

- User-story source: `docs/scope-brief.md` §2.39
- Spec section: `spec-v1-mvp.md` §User Stories 39
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Notifications cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
