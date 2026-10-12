# `US-44` — Kid ping: redemption approved or denied

| Field | Value |
|-------|-------|
| Story ID | `US-44` |
| Title | Kid ping: redemption approved or denied |
| Feature area | Notifications |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.44 |
| Spec ref | `spec-v1-mvp.md` §User Stories 44 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/components/kid-notification-toast.md`

## Preconditions

1. Redemption exists; parent acts (approve US-33 / deny US-34 / reverse US-35).

## Scenario

**Given** a redemption resolves

**When** the parent acts

**Then** the following expected outcomes are observed:

1. Kid receives an in-app notification with the outcome.
2. If approved, balance reflects the debit.
3. If denied, balance unchanged; optional reason shown.
4. If reversed, balance reflects the offset.
5. No web-push.

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Inherits US-41 toast styling.

## Accessibility (WCAG 2.1 AA)

1. Inherits US-41 a11y.

## Evidence to record

Capture under `evidence/US-44-kid-ping-redemption-resolved/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshots per outcome variant (approved / denied / reversed).
2. DB rows: notifications + ledger entries.

## References

- User-story source: `docs/scope-brief.md` §2.44
- Spec section: `spec-v1-mvp.md` §User Stories 44
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Notifications cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
