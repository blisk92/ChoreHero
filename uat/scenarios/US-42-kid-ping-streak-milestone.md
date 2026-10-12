# `US-42` — Kid ping: streak milestone (celebratory)

| Field | Value |
|-------|-------|
| Story ID | `US-42` |
| Title | Kid ping: streak milestone (celebratory) |
| Feature area | Notifications |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.42 |
| Spec ref | `spec-v1-mvp.md` §User Stories 42 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/components/celebratory-surface.md`

## Preconditions

1. Recurring chore; milestone (7-day or 30-day) reached (US-27).

## Scenario

**Given** a kid hits a milestone

**When** the streak reducer runs

**Then** the following expected outcomes are observed:

1. An in-app celebratory surface appears (US-27).
2. Avatar is the hero (US-54).
3. No web-push (kid devices never receive push).

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Inherits US-27 / US-54 surface styling.

## Accessibility (WCAG 2.1 AA)

1. Inherits US-27 a11y.

## Evidence to record

Capture under `evidence/US-42-kid-ping-streak-milestone/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshot of celebratory surface.
2. DB row for `Notification`.

## References

- User-story source: `docs/scope-brief.md` §2.42
- Spec section: `spec-v1-mvp.md` §User Stories 42
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Notifications cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
