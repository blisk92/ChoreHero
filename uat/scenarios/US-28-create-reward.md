# `US-28` — Create a reward

| Field | Value |
|-------|-------|
| Story ID | `US-28` |
| Title | Create a reward |
| Feature area | Rewards & Redemption |
| Priority | Critical |
| Scope brief ref | `docs/scope-brief.md` §2.28 |
| Spec ref | `spec-v1-mvp.md` §User Stories 28 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/screens/reward-editor.md`
- `design/components/form-field.md`

## Preconditions

1. Parent signed in (US-1).

## Scenario

**Given** a parent on the rewards page

**When** they create a reward with name, point cost, and optional `stock_remaining`

**Then** the following expected outcomes are observed:

1. A `Reward` row exists in the household.
2. The reward is visible to the kid in the catalog on the next sync (US-30).
3. Validation: name non-empty; cost ≥ 1; if `stock_remaining` set, must be ≥ 0.

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Editor uses `reward-editor.md`; stock field is optional and disabled unless the parent toggles "limited stock".

## Accessibility (WCAG 2.1 AA)

1. Stock toggle follows US-11 a11y.
2. Cost field has associated label and validation messaging.

## Evidence to record

Capture under `evidence/US-28-create-reward/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshot of reward editor.
2. DB row for `Reward`.
3. Screenshot of kid catalog showing the new reward.

## References

- User-story source: `docs/scope-brief.md` §2.28
- Spec section: `spec-v1-mvp.md` §User Stories 28
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Rewards & Redemption cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
