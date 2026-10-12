# `US-54` — Avatar in celebratory moments

| Field | Value |
|-------|-------|
| Story ID | `US-54` |
| Title | Avatar in celebratory moments |
| Feature area | Visual Identity |
| Priority | Standard |
| Scope brief ref | `docs/scope-brief.md` §2.54 |
| Spec ref | `spec-v1-mvp.md` §User Stories 54 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/components/avatar.md`
- `design/components/celebratory-surface.md`

## Preconditions

1. A kid has hit a milestone (US-27) or had a redemption approved (US-33 → US-44).

## Scenario

**Given** a kid who hits a milestone or gets a redemption approved

**When** the celebratory surface renders

**Then** the following expected outcomes are observed:

1. The kid's chosen avatar is the hero.
2. The ChoreHero emblem does not compete with the kid's avatar.

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Avatar at hero size; emblem relegated to corner or absent per design spec.

## Accessibility (WCAG 2.1 AA)

1. Avatar is the primary readable content (name + celebratory phrase in text) (WCAG 1.4.1).

## Evidence to record

Capture under `evidence/US-54-avatar-celebratory/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshot of celebratory surface.

## References

- User-story source: `docs/scope-brief.md` §2.54
- Spec section: `spec-v1-mvp.md` §User Stories 54
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Visual Identity cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
