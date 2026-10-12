# `US-27` — Streak milestone notification (kid, in-app)

| Field | Value |
|-------|-------|
| Story ID | `US-27` |
| Title | Streak milestone notification (kid, in-app) |
| Feature area | Points & Streaks |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.27 |
| Spec ref | `spec-v1-mvp.md` §User Stories 27 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/components/celebratory-surface.md`
- `design/components/avatar.md`

## Preconditions

1. Recurring chore; kid completes the chore on day 7 (or 30) with no prior celebration at that milestone.

## Scenario

**Given** a kid hits a 7-day or 30-day milestone

**When** the streak reducer runs

**Then** the following expected outcomes are observed:

1. An in-app notification / celebratory surface appears for the kid.
2. The kid's avatar is the hero per CONTEXT.md mascot rules (US-54).
3. Celebratory phrase is one of the design-approved phrases; not theatrical.
4. A `Notification` row is written for the kid device.

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Surface uses `celebratory-surface.md`; large avatar; one phrase; brief animation (≤ 1s).

## Accessibility (WCAG 2.1 AA)

1. Surface is announced via aria-live; the phrase is the readable primary text (WCAG 1.4.1, 2.3.1).
2. No flashing content above safe thresholds (WCAG 2.3.1).

## Evidence to record

Capture under `evidence/US-27-streak-milestone-notification/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshot of celebratory surface.
2. DB row for `Notification`.

## References

- User-story source: `docs/scope-brief.md` §2.27
- Spec section: `spec-v1-mvp.md` §User Stories 27
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Points & Streaks cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
