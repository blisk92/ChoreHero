# `US-4` — Create a child profile with name + avatar

| Field | Value |
|-------|-------|
| Story ID | `US-4` |
| Title | Create a child profile with name + avatar |
| Feature area | Onboarding & Identity |
| Priority | Critical |
| Scope brief ref | `docs/scope-brief.md` §2.4 |
| Spec ref | `spec-v1-mvp.md` §User Stories 4 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/components/avatar-picker.md`
- `design/components/modal.md`
- `design/tokens/colors.json`

## Preconditions

1. Parent signed in (US-1).
2. Test child name and chosen avatar ID are recorded in the runbook §3.

## Scenario

**Given** a signed-in parent on the parent dashboard or settings

**When** they open "Add child", enter a name, and pick an avatar

**Then** the following expected outcomes are observed:

1. A `Child` row exists in the parent's household with the submitted name and `avatar_id`.
2. The chosen avatar is rendered in the kid SPA on the next device link (verified by US-5 / US-9).
3. The parent dashboard now lists one child in the household section.
4. No avatar upload path is exposed (v1 is pre-shipped SVG set per scope-brief §7 Q1 default).

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Avatar picker is a modal (`modal.md`) on `surface/elevated`; tile grid renders the pre-shipped SVG set.
2. Selected avatar is visually highlighted with the parent's primary accent (`action/primary-selected`).

## Accessibility (WCAG 2.1 AA)

1. Each avatar tile has an accessible name (e.g. "robot", "fox") (WCAG 4.1.2).
2. Tile grid reachable via arrow keys; selection announced via aria-live or focus (WCAG 1.3.1, 4.1.3).
3. Modal traps focus while open (WCAG 2.4.3).
4. Avatar swatches are not the sole carrier of identity — name is also shown (WCAG 1.4.1).

## Evidence to record

Capture under `evidence/US-4-create-child-profile/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshot of empty avatar picker.
2. Screenshot with avatar selected.
3. Screenshot of completed dashboard with child card.
4. Network `.har` for `POST /api/children`.
5. DB row for `Child`.

## References

- User-story source: `docs/scope-brief.md` §2.4
- Spec section: `spec-v1-mvp.md` §User Stories 4
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Onboarding & Identity cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
