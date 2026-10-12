# `US-6` — Household code is permanent until regenerated

| Field | Value |
|-------|-------|
| Story ID | `US-6` |
| Title | Household code is permanent until regenerated |
| Feature area | Onboarding & Identity |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.6 |
| Spec ref | `spec-v1-mvp.md` §User Stories 6 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/screens/link-kid-device.md`

## Preconditions

1. An existing `HouseholdCode` row exists from a prior run.
2. A new kid device is available to link.

## Scenario

**Given** a parent whose household already has a code

**When** a new kid device is linked (via QR or manual entry) without regenerating

**Then** the following expected outcomes are observed:

1. The previously-issued code is still valid and accepted by the link endpoint.
2. No `HouseholdCode` row is overwritten; the existing row continues to be the active one.
3. The new `KidDevice` row is created successfully.

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Settings → "Link a kid device" still shows the same QR + code as before.

## Accessibility (WCAG 2.1 AA)

1. Skip — same surface as US-5; a11y inherited.

## Evidence to record

Capture under `evidence/US-6-code-permanent/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Network `.har` for the link call on a "new" device using an old code.
2. DB row count: `HouseholdCode` count unchanged, `KidDevice` count incremented.

## References

- User-story source: `docs/scope-brief.md` §2.6
- Spec section: `spec-v1-mvp.md` §User Stories 6
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Onboarding & Identity cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
