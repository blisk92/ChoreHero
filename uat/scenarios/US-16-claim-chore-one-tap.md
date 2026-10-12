# `US-16` — Claim a chore with one tap

| Field | Value |
|-------|-------|
| Story ID | `US-16` |
| Title | Claim a chore with one tap |
| Feature area | Chores & Pools |
| Priority | Critical |
| Scope brief ref | `docs/scope-brief.md` §2.16 |
| Spec ref | `spec-v1-mvp.md` §User Stories 16 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/components/chore-card.md`
- `design/components/button.md`

## Preconditions

1. Available Extras has at least one chore (US-15).

## Scenario

**Given** a kid viewing Available Extras

**When** they tap a chore

**Then** the following expected outcomes are observed:

1. Chore `status` becomes `claimed`; `claimed_by_child_id` and `claimed_at` are set.
2. The chore moves into the kid's "My Active" section (US-17).
3. Optimistic UI: card moves out of Available Extras immediately (US-46 path).
4. No second device prompt; one tap suffices.

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Tapping the card (not a separate "Claim" button) initiates the claim per spec.

## Accessibility (WCAG 2.1 AA)

1. Tap target ≥ 44x44 CSS px (WCAG 2.5.5).
2. Action result announced via aria-live (WCAG 4.1.3).

## Evidence to record

Capture under `evidence/US-16-claim-chore-one-tap/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshot of Available Extras before tap.
2. Screenshot after tap showing chore in My Active.
3. Network `.har` for the claim mutation.
4. DB row showing `status: claimed`.

## References

- User-story source: `docs/scope-brief.md` §2.16
- Spec section: `spec-v1-mvp.md` §User Stories 16
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Chores & Pools cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
