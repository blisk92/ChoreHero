# `US-7` — Regenerate the household code

| Field | Value |
|-------|-------|
| Story ID | `US-7` |
| Title | Regenerate the household code |
| Feature area | Onboarding & Identity |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.7 |
| Spec ref | `spec-v1-mvp.md` §User Stories 7 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/screens/link-kid-device.md`
- `design/components/confirmation-dialog.md`

## Preconditions

1. Existing `HouseholdCode` row.
2. At least one currently-linked kid device that will become orphan after regeneration.

## Scenario

**Given** a parent in settings with an active household code

**When** they tap "Regenerate code" and confirm the destructive action

**Then** the following expected outcomes are observed:

1. The previous code's hash is replaced (or a new row takes over per implementation).
2. Attempting to link a new device with the *old* code returns 4xx.
3. A new 6-character code (matching the no-0/O/1/I/L charset) is shown with a fresh QR.
4. Existing linked devices are not automatically logged out in v1 (per spec out-of-scope notes); the parent is informed in copy that previously-linked devices will need to re-link.

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Regenerate requires a confirmation dialog (`confirmation-dialog.md`) — destructive intent.
2. After regenerate, the UI shows the new code + QR; old code is not visible anywhere.

## Accessibility (WCAG 2.1 AA)

1. Confirmation dialog traps focus and is announced (WCAG 2.4.3, 4.1.3).
2. Destructive action uses both colour and iconography to convey severity (WCAG 1.4.1).

## Evidence to record

Capture under `evidence/US-7-regenerate-code/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshot of regenerate confirmation dialog.
2. Screenshot of new code + QR.
3. Network `.har` showing the regenerate call + a failed link call with the old code.
4. DB row diff for `HouseholdCode`.

## References

- User-story source: `docs/scope-brief.md` §2.7
- Spec section: `spec-v1-mvp.md` §User Stories 7
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Onboarding & Identity cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
