# `US-3` — Automatic household creation on signup

| Field | Value |
|-------|-------|
| Story ID | `US-3` |
| Title | Automatic household creation on signup |
| Feature area | Onboarding & Identity |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.3 |
| Spec ref | `spec-v1-mvp.md` §User Stories 3 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/tokens/spacing.json`
- `design/screens/parent-dashboard.md`

## Preconditions

1. Fresh staging DB (no orphan `Household` rows).
2. Sign-up flow (US-1) completed for the test parent.

## Scenario

**Given** a freshly signed-up parent

**When** the sign-up API call returns 2xx

**Then** the following expected outcomes are observed:

1. A `Household` row exists with the parent's `household_id` foreign key.
2. No user-visible configuration step is required before the parent can add a chore.
3. Subsequent parent API calls (e.g. chore create) succeed without first selecting a household.

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. No empty-state config card is shown — the parent lands on the standard dashboard skeleton.

## Accessibility (WCAG 2.1 AA)

1. Skip — covered by US-1 sign-up a11y.

## Evidence to record

Capture under `evidence/US-3-auto-household-create/` and reference
from `templates/uat-report.md` §"Evidence index".

1. DB dump: `Household` and `Parent` rows present; foreign keys set.
2. Screenshot of parent dashboard immediately post-signup.

## References

- User-story source: `docs/scope-brief.md` §2.3
- Spec section: `spec-v1-mvp.md` §User Stories 3
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Onboarding & Identity cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
