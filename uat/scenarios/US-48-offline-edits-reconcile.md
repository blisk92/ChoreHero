# `US-48` — Offline edits flow in cleanly on reconnect

| Field | Value |
|-------|-------|
| Story ID | `US-48` |
| Title | Offline edits flow in cleanly on reconnect |
| Feature area | Sync & Offline |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.48 |
| Spec ref | `spec-v1-mvp.md` §User Stories 48 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/screens/kid-today.md`

## Preconditions

1. Parent edits a chore (e.g. point value) while the kid is offline.
2. Kid reconnects.

## Scenario

**Given** a parent edited a chore while the kid was offline

**When** the kid reconnects

**Then** the following expected outcomes are observed:

1. The kid's local cache reconciles without losing either side's intent.
2. Per-field last-write-wins resolves any conflict (US-49).
3. No clobbering of offline kid actions; no clobbering of the parent's edit.

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. UI updates on kid side without manual refresh.

## Accessibility (WCAG 2.1 AA)

1. Skip — covered by component a11y.

## Evidence to record

Capture under `evidence/US-48-offline-edits-reconcile/` and reference
from `templates/uat-report.md` §"Evidence index".

1. DB row state after reconciliation.
2. Screenshot of kid UI post-reconnect.

## References

- User-story source: `docs/scope-brief.md` §2.48
- Spec section: `spec-v1-mvp.md` §User Stories 48
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Sync & Offline cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
