# `US-53` — Kid first-link welcome

| Field | Value |
|-------|-------|
| Story ID | `US-53` |
| Title | Kid first-link welcome |
| Feature area | Empty States & Onboarding Nudges |
| Priority | Standard |
| Scope brief ref | `docs/scope-brief.md` §2.53 |
| Spec ref | `spec-v1-mvp.md` §User Stories 53 (= US-9) |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/screens/kid-welcome.md`

## Preconditions

1. Kid device freshly linked; zero chores.

## Scenario

**Given** a kid on first link before any chore exists

**When** they open the kiosk

**Then** the following expected outcomes are observed:

1. Welcome screen renders with kid's name and avatar (US-9).
2. Once a chore lands, auto-transitions to the empty-state / pool (US-52).

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Inherits US-9.

## Accessibility (WCAG 2.1 AA)

1. Inherits US-9.

## Evidence to record

Capture under `evidence/US-53-kid-first-link-welcome/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Inherits US-9 evidence.

## References

- User-story source: `docs/scope-brief.md` §2.53
- Spec section: `spec-v1-mvp.md` §User Stories 53 (= US-9)
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Empty States & Onboarding Nudges cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
