# `US-55` — Parent-side quiet palette

| Field | Value |
|-------|-------|
| Story ID | `US-55` |
| Title | Parent-side quiet palette |
| Feature area | Visual Identity |
| Priority | Standard |
| Scope brief ref | `docs/scope-brief.md` §2.55 |
| Spec ref | `spec-v1-mvp.md` §User Stories 55 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/tokens/colors.json`
- `design/tokens/spacing.json`

## Preconditions

1. Parent SPA surfaces rendered.

## Scenario

**Given** a parent surface

**When** it renders

**Then** the following expected outcomes are observed:

1. Same palette (deep violet + sunshine yellow) is used but with more white space and quieter accents.
2. Parent's phone does not feel like a toddler's toy.

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Tokens: parent surfaces use `surface/parent-quiet` token; whitespace via `spacing/parent-roomy`.
2. Accent usage limited to primary actions; kid-side celebratory treatments are not present.

## Accessibility (WCAG 2.1 AA)

1. Color contrast unaffected by the quieter palette — all text-on-background meets WCAG 1.4.3.

## Evidence to record

Capture under `evidence/US-55-parent-quiet-palette/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshots of multiple parent surfaces (dashboard, chores, rewards, settings).
2. Resolved token values cited from `design/tokens/colors.json`.

## References

- User-story source: `docs/scope-brief.md` §2.55
- Spec section: `spec-v1-mvp.md` §User Stories 55
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Visual Identity cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
