# `US-22` — Instant balance update on non-review completion

| Field | Value |
|-------|-------|
| Story ID | `US-22` |
| Title | Instant balance update on non-review completion |
| Feature area | Points & Streaks |
| Priority | Critical |
| Scope brief ref | `docs/scope-brief.md` §2.22 |
| Spec ref | `spec-v1-mvp.md` §User Stories 22 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/components/balance-badge.md`

## Preconditions

1. Kid on home screen with at least one claimed non-review chore (US-16 + chore with `review_flagged = false`).

## Scenario

**Given** a kid completes a non-review-flagged chore

**When** the local mutation commits

**Then** the following expected outcomes are observed:

1. Balance updates within the same frame (no waiting on the network round-trip).
2. The optimistic value matches what the server eventually returns (no flicker / no rollback to lower value on success).

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Badge updates with a subtle animation (≤ 200 ms) — no theatrical scale.

## Accessibility (WCAG 2.1 AA)

1. Balance change announced via aria-live polite (WCAG 4.1.3).

## Evidence to record

Capture under `evidence/US-22-instant-balance-update/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Network-throttled recording showing the balance update precedes the API response.
2. Server ledger entry timestamp ≤ posted order.

## References

- User-story source: `docs/scope-brief.md` §2.22
- Spec section: `spec-v1-mvp.md` §User Stories 22
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Points & Streaks cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
