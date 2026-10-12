# `US-49` — Per-field last-write-wins on conflicts

| Field | Value |
|-------|-------|
| Story ID | `US-49` |
| Title | Per-field last-write-wins on conflicts |
| Feature area | Sync & Offline |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.49 |
| Spec ref | `spec-v1-mvp.md` §User Stories 49 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

_No design artefact — backend-only behaviour._

## Preconditions

1. Same chore edited on both parent and kid sides on different fields while disconnected.

## Scenario

**Given** the parent and kid both edited different fields of the same chore

**When** both edits arrive at the server

**Then** the following expected outcomes are observed:

1. Each field is applied independently with its own `updated_at`.
2. The union persists; neither side clobbers the other.
3. The server applies if-and-only-if `received.updated_at > stored.updated_at` for that field (per spec §"Architectural decisions").

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. No UI; backend behaviour.

## Accessibility (WCAG 2.1 AA)

1. N/A — backend logic.

## Evidence to record

Capture under `evidence/US-49-last-write-wins-per-field/` and reference
from `templates/uat-report.md` §"Evidence index".

1. DB row showing per-field `updated_at` after both writes applied.
2. Server logs capturing the per-field apply / skip decisions.

## References

- User-story source: `docs/scope-brief.md` §2.49
- Spec section: `spec-v1-mvp.md` §User Stories 49
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Sync & Offline cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
