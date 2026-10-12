# `US-47` — Parent sees near-real-time kid activity

| Field | Value |
|-------|-------|
| Story ID | `US-47` |
| Title | Parent sees near-real-time kid activity |
| Feature area | Sync & Offline |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.47 |
| Spec ref | `spec-v1-mvp.md` §User Stories 47 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/screens/parent-dashboard.md`

## Preconditions

1. Both parent and kid devices online; parent SPA open.

## Scenario

**Given** both devices online

**When** the kid takes an action (claim, complete, redeem)

**Then** the following expected outcomes are observed:

1. Parent's dashboard reflects the change within a few seconds via WebSocket fan-out.
2. No manual refresh required.
3. Reconnect path: when the WS is closed and reopened, the parent sees a single GET resume plus a fresh WS handshake.

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Updated state visible on the relevant dashboard card / pending queue.

## Accessibility (WCAG 2.1 AA)

1. Skip — covered by per-component a11y (US-22, US-23, US-32).

## Evidence to record

Capture under `evidence/US-47-parent-realtime-activity/` and reference
from `templates/uat-report.md` §"Evidence index".

1. WebSocket trace showing the event pushed to the parent.
2. Screenshot before and after the kid action.

## References

- User-story source: `docs/scope-brief.md` §2.47
- Spec section: `spec-v1-mvp.md` §User Stories 47
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Sync & Offline cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
