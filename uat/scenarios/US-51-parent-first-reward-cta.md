# `US-51` — Parent first reward CTA

| Field | Value |
|-------|-------|
| Story ID | `US-51` |
| Title | Parent first reward CTA |
| Feature area | Empty States & Onboarding Nudges |
| Priority | Standard |
| Scope brief ref | `docs/scope-brief.md` §2.51 |
| Spec ref | `spec-v1-mvp.md` §User Stories 51 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/components/cta-card.md`

## Preconditions

1. Parent signed in; zero rewards exist.

## Scenario

**Given** a parent with zero rewards

**When** they open the rewards page

**Then** the following expected outcomes are observed:

1. Primary CTA reads "Add your first reward" with example suggestions ("30 min screen time", "Pick dinner").
2. No auto-seeded rewards.

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. CTA card uses `cta-card.md`; parent-side quiet palette.

## Accessibility (WCAG 2.1 AA)

1. CTA has accessible name including "Add your first reward".

## Evidence to record

Capture under `evidence/US-51-parent-first-reward-cta/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshot of rewards page empty state.

## References

- User-story source: `docs/scope-brief.md` §2.51
- Spec section: `spec-v1-mvp.md` §User Stories 51
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Empty States & Onboarding Nudges cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
