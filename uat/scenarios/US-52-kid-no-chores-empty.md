# `US-52` — Kid no-chores empty state

| Field | Value |
|-------|-------|
| Story ID | `US-52` |
| Title | Kid no-chores empty state |
| Feature area | Empty States & Onboarding Nudges |
| Priority | Standard |
| Scope brief ref | `docs/scope-brief.md` §2.52 |
| Spec ref | `spec-v1-mvp.md` §User Stories 52 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/components/empty-state.md`
- `design/components/illustration.md`

## Preconditions

1. Kid device linked; zero chores in either pool.

## Scenario

**Given** a kid with no chores in either pool

**When** they open the kiosk

**Then** the following expected outcomes are observed:

1. Copy: "No chores yet. Ask a parent to add some."
2. A small illustration is rendered.
3. When the first chore lands, the state auto-transitions to the regular pool.

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Empty state uses `empty-state.md` + `illustration.md`.
2. Illustration follows CONTEXT.md style (hand-drawn accents).

## Accessibility (WCAG 2.1 AA)

1. Illustration has `alt` text describing intent, not just visual content (WCAG 1.1.1).
2. Page remains fully readable without the illustration (WCAG 1.4.1).

## Evidence to record

Capture under `evidence/US-52-kid-no-chores-empty/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshot of empty state.
2. Screenshot after first chore arrives (auto-transition).

## References

- User-story source: `docs/scope-brief.md` §2.52
- Spec section: `spec-v1-mvp.md` §User Stories 52
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Empty States & Onboarding Nudges cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
