# `US-9` — Kid welcome on first launch

| Field | Value |
|-------|-------|
| Story ID | `US-9` |
| Title | Kid welcome on first launch |
| Feature area | Onboarding & Identity |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.9 |
| Spec ref | `spec-v1-mvp.md` §User Stories 9 + 53 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/screens/kid-welcome.md`
- `design/components/avatar.md`
- `design/tokens/colors.json`

## Preconditions

1. Kid device freshly linked (US-5), zero chores in either pool.

## Scenario

**Given** a freshly linked kid device with zero chores

**When** the kid opens the kiosk

**Then** the following expected outcomes are observed:

1. The welcome screen shows "Welcome, [name]!" with the chosen avatar hero.
2. No parent-side nav or chrome is visible (kiosk surface).
3. The moment any chore lands in either pool, the screen auto-transitions to the regular "No chores yet" empty state or the live pool — without a refresh.

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Avatar uses `avatar.md` at hero size (per design spec); the ChoreHero emblem does not compete (CONTEXT.md mascot rule).
2. Palette uses the kid-side accent treatment; parent-side quiet-palette is NOT applied here.

## Accessibility (WCAG 2.1 AA)

1. Avatar has an `alt`/aria-label with the kid's name (WCAG 1.1.1).
2. Greeting text is the primary heading; readable at 200% zoom (WCAG 1.4.4).
3. No flashing animation that exceeds safe thresholds (WCAG 2.3.1).

## Evidence to record

Capture under `evidence/US-9-kid-welcome-first-launch/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshot of welcome screen on a fresh kid device.
2. Screenshot taken moments after chore creation showing auto-transition to pool.

## References

- User-story source: `docs/scope-brief.md` §2.9
- Spec section: `spec-v1-mvp.md` §User Stories 9 + 53
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Onboarding & Identity cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
