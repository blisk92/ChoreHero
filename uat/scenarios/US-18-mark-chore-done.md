# `US-18` — Mark a claimed chore done

| Field | Value |
|-------|-------|
| Story ID | `US-18` |
| Title | Mark a claimed chore done |
| Feature area | Chores & Pools |
| Priority | Critical |
| Scope brief ref | `docs/scope-brief.md` §2.18 |
| Spec ref | `spec-v1-mvp.md` §User Stories 18 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/components/chore-card.md`
- `design/components/celebration-toast.md`

## Preconditions

1. At least one claimed chore (US-16).

## Scenario

**Given** a kid with a claimed chore in My Active

**When** they tap "Done"

**Then** the following expected outcomes are observed:

1. `Chore.status = completed`.
2. Non-review-flagged: a positive `PointsLedger` entry is appended immediately and the balance updates within the same frame (US-22).
3. Review-flagged: points held until parent approval (US-37 → US-43 path); chore status remains `completed` (pending review).
4. A celebratory affordance renders per the design spec (no over-the-top theatre; one phrase + avatar).

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Done action visibly responds within the same frame on non-review completion.
2. Review-flagged variant shows a quieter acknowledgement ("Sent for review").

## Accessibility (WCAG 2.1 AA)

1. Celebration does not rely on sound or animation alone; the balance change is announced to assistive tech (WCAG 1.4.1, 4.1.3).

## Evidence to record

Capture under `evidence/US-18-mark-chore-done/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshot before and after tap.
2. Network `.har` for complete mutation.
3. DB rows for chore status transition and (if non-review) ledger entry.

## References

- User-story source: `docs/scope-brief.md` §2.18
- Spec section: `spec-v1-mvp.md` §User Stories 18
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Chores & Pools cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
