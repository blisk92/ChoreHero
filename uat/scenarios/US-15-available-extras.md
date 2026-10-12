# `US-15` — Kid sees "Available Extras"

| Field | Value |
|-------|-------|
| Story ID | `US-15` |
| Title | Kid sees "Available Extras" |
| Feature area | Chores & Pools |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.15 |
| Spec ref | `spec-v1-mvp.md` §User Stories 15 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/screens/kid-today.md`
- `design/components/chore-card.md`

## Preconditions

1. At least one chore in pool (US-10).
2. Kid device signed in (US-5).

## Scenario

**Given** a kid on the kiosk on the Today screen

**When** they open Today

**Then** the following expected outcomes are observed:

1. Every claimable chore (status: pool) across both pools is listed under "Available Extras".
2. Each card shows chore name, point value, recurring/one-off indicator, and (for one-off) a deadline.
3. Claimed chores do NOT also appear here (US-17).

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Section header "Available Extras" using the kid-side accent.
2. Chore cards use `chore-card.md` with point token shown prominently.

## Accessibility (WCAG 2.1 AA)

1. Cards are buttons with accessible names including chore name and point value (WCAG 4.1.2).
2. Section headings use semantic heading levels (WCAG 1.3.1).

## Evidence to record

Capture under `evidence/US-15-available-extras/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshot of Today screen with populated Available Extras.
2. Network `.har` for `GET /api/chores` (or equivalent).

## References

- User-story source: `docs/scope-brief.md` §2.15
- Spec section: `spec-v1-mvp.md` §User Stories 15
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Chores & Pools cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
