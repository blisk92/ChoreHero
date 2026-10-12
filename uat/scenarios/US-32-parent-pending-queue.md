# `US-32` — Parent sees pending requests on dashboard

| Field | Value |
|-------|-------|
| Story ID | `US-32` |
| Title | Parent sees pending requests on dashboard |
| Feature area | Rewards & Redemption |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.32 |
| Spec ref | `spec-v1-mvp.md` §User Stories 32 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/screens/parent-dashboard.md`
- `design/components/pending-item.md`

## Preconditions

1. At least one pending redemption (US-31).

## Scenario

**Given** a parent on the dashboard

**When** the dashboard loads

**Then** the following expected outcomes are observed:

1. Pending redemptions are listed with kid name, reward name, and cost.
2. Each row has Approve and Deny controls.

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. List uses `pending-item.md`; parent-side quiet palette.

## Accessibility (WCAG 2.1 AA)

1. List semantic structure preserved (WCAG 1.3.1).
2. Approve/Deny buttons have accessible names with reward context.

## Evidence to record

Capture under `evidence/US-32-parent-pending-queue/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshot of dashboard with pending queue.
2. Network `.har` for `GET /api/redemptions?status=pending`.

## References

- User-story source: `docs/scope-brief.md` §2.32
- Spec section: `spec-v1-mvp.md` §User Stories 32
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Rewards & Redemption cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
