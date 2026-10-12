# `US-5` — Generate household code + QR from "Link a kid device"

| Field | Value |
|-------|-------|
| Story ID | `US-5` |
| Title | Generate household code + QR from "Link a kid device" |
| Feature area | Onboarding & Identity |
| Priority | Critical |
| Scope brief ref | `docs/scope-brief.md` §2.5 |
| Spec ref | `spec-v1-mvp.md` §User Stories 5 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/screens/link-kid-device.md`
- `design/components/qr-tile.md`

## Preconditions

1. Parent signed in, child profile created (US-4).
2. Test kid device available with the kid SPA loaded.

## Scenario

**Given** a parent in settings with no `HouseholdCode` row yet

**When** they tap "Link a kid device" for the first time

**Then** the following expected outcomes are observed:

1. A `HouseholdCode` row is created (lazy) with a hashed code.
2. A 6-character alphanumeric plaintext code is shown to the parent: charset excludes 0/O, 1/I/L (per CONTEXT.md & spec schema).
3. A QR code encodes the same 6-character string; scanning the QR on the kid SPA enters the code automatically.
4. Manual code entry on the kid SPA accepts the code and completes the link handshake.
5. The kid SPA lands on the welcome screen (US-9).

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. QR + code render side-by-side using `qr-tile.md`; sufficient contrast between QR and background for scanner reliability.
2. Code is rendered in a monospace token so ambiguous characters are unambiguous.

## Accessibility (WCAG 2.1 AA)

1. Plaintext code has an accessible name and copyable announcement (WCAG 4.1.2).
2. Manual entry input has an associated label and supports paste (WCAG 1.3.1, 2.1.1).
3. QR alone is not the sole channel — manual entry is an equivalent path (WCAG 1.1.1 / non-text content).

## Evidence to record

Capture under `evidence/US-5-household-code-qr/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshot of QR + code visible.
2. Screenshot of kid SPA after QR scan or manual entry.
3. Network `.har` for code-generation endpoint and link handshake.
4. DB row for `HouseholdCode` (note: only hash stored, never plaintext).

## References

- User-story source: `docs/scope-brief.md` §2.5
- Spec section: `spec-v1-mvp.md` §User Stories 5
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Onboarding & Identity cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
