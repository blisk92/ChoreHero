# `US-46` — Kid works offline (Dexie outbox)

| Field | Value |
|-------|-------|
| Story ID | `US-46` |
| Title | Kid works offline (Dexie outbox) |
| Feature area | Sync & Offline |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.46 |
| Spec ref | `spec-v1-mvp.md` §User Stories 46 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/screens/kid-today.md`

## Preconditions

1. Kid device linked; kid SPA loaded at least once so the SW + Dexie store are primed.

## Scenario

**Given** a kid device with no network

**When** the kid claims or completes a chore

**Then** the following expected outcomes are observed:

1. The mutation is persisted in the Dexie outbox.
2. The UI updates optimistically (US-22 applies).
3. On reconnect, the mutation replays with the original `updated_at` and a stable operation ID for idempotency.
4. The SW does NOT intercept mutation requests (per scope brief §3; mutations go through Dexie first).

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Subtle offline indicator (banner or icon) signals the kid is in offline mode.

## Accessibility (WCAG 2.1 AA)

1. Offline indicator announced via aria-live (WCAG 4.1.3).

## Evidence to record

Capture under `evidence/US-46-kid-offline/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Dexie / IndexedDB dump before and after the offline mutation.
2. Screenshot of UI update while offline.
3. Screenshot of the offline indicator.
4. Network `.har` showing no outbound request until reconnect.
5. DB rows applied on reconnect with original `updated_at`.

## References

- User-story source: `docs/scope-brief.md` §2.46
- Spec section: `spec-v1-mvp.md` §User Stories 46
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Sync & Offline cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
