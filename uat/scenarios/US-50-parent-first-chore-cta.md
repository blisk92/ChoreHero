# `US-50` — Parent first chore CTA

| Field | Value |
|-------|-------|
| Story ID | `US-50` |
| Title | Parent first chore CTA |
| Feature area | Empty States & Onboarding Nudges |
| Priority | Standard |
| Scope brief ref | `docs/scope-brief.md` §2.50 |
| Spec ref | `spec-v1-mvp.md` §User Stories 50 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/components/cta-card.md`
- `design/components/nudge-banner.md`

## Preconditions

1. Parent signed in; zero chores exist in the household.

## Scenario

**Given** a parent with zero chores

**When** they open the dashboard

**Then** the following expected outcomes are observed:

1. Primary CTA reads "Add your first chore" with secondary copy describing chore kinds.
2. Nudge banner stays until ≥1 chore exists in either pool.
3. Once a chore exists, the CTA/banner is replaced by the normal dashboard skeleton.

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. CTA card uses `cta-card.md`; parent-side quiet palette.
2. Banner uses `nudge-banner.md`; dismissible but auto-hides once a chore exists.

## Accessibility (WCAG 2.1 AA)

1. CTA has accessible name including "Add your first chore".
2. Banner uses polite aria-live on dismissal/auto-hide (WCAG 4.1.3).

## Evidence to record

Capture under `evidence/US-50-parent-first-chore-cta/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshot of dashboard with empty state.
2. Screenshot after adding the first chore (banner gone).

## References

- User-story source: `docs/scope-brief.md` §2.50
- Spec section: `spec-v1-mvp.md` §User Stories 50
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Empty States & Onboarding Nudges cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
