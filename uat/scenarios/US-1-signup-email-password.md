# `US-1` — Sign up by email + password

| Field | Value |
|-------|-------|
| Story ID | `US-1` |
| Title | Sign up by email + password |
| Feature area | Onboarding & Identity |
| Priority | Critical |
| Scope brief ref | `docs/scope-brief.md` §2.1 |
| Spec ref | `spec-v1-mvp.md` §User Stories 1 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/screens/sign-up.md`
- `design/components/form-field.md`
- `design/components/button.md`
- `design/tokens/colors.json`

## Preconditions

1. Staging parent URL is reachable (runbook §3).
2. Test parent email and password are fresh — not previously registered on this staging DB.
3. Marketing / landing page loads without console errors.

## Scenario

**Given** a new visitor on the marketing page with no active session

**When** they submit the sign-up form with email + password (twice) and tap "Create account"

**Then** the following expected outcomes are observed:

1. API responds 2xx with a session token within 2 s of submit.
2. A `Parent` row exists with the submitted email and a bcrypt password hash (never plaintext over the wire or at rest).
3. A `Household` row exists with the parent as its sole member.
4. The parent lands on the parent dashboard signed in; no intermediate interstitial asking them to log in again.
5. A success toast or in-app confirmation reads "Welcome — your household is ready." (or the design-package equivalent).

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. Email + password fields render using `form-field.md` with labels above inputs.
2. Primary CTA uses `button.md` `variant=primary`, palette token `action/cta` (sunshine yellow per CONTEXT.md).
3. Error states for invalid email / weak password render inline beneath the field, not as a modal.

## Accessibility (WCAG 2.1 AA)

1. Form fields have associated <label> elements (WCAG 1.3.1, 4.1.2).
2. Tab order: email → password → confirm password → submit (WCAG 2.4.3).
3. Submit button reachable via keyboard and operable via Enter / Space (WCAG 2.1.1).
4. Color contrast for primary CTA text on yellow background ≥ 4.5:1 (WCAG 1.4.3).

## Evidence to record

Capture under `evidence/US-1-signup-email-password/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshot of empty sign-up form (`US-01-step-1.png`).
2. Screenshot of filled form just before submit (`US-01-step-2.png`).
3. Screenshot of dashboard after redirect (`US-01-step-3.png`).
4. Network `.har` showing `POST /api/auth/signup` 2xx and the follow-up `GET /api/household` call.
5. DB row dump for `Parent` and `Household` (anonymised; no password).

## References

- User-story source: `docs/scope-brief.md` §2.1
- Spec section: `spec-v1-mvp.md` §User Stories 1
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Onboarding & Identity cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
