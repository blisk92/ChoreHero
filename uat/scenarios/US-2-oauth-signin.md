# `US-2` — Sign in faster with OAuth (Google / Apple)

| Field | Value |
|-------|-------|
| Story ID | `US-2` |
| Title | Sign in faster with OAuth (Google / Apple) |
| Feature area | Onboarding & Identity |
| Priority | High |
| Scope brief ref | `docs/scope-brief.md` §2.2 |
| Spec ref | `spec-v1-mvp.md` §User Stories 2 |

## Designer artefacts to match

The UI fidelity checks below reference these files in the design
package (produced by the frontend-designer lane, task
`t_fba7600a`). The UAT engineer resolves the
`<from-design-package>` placeholders against these paths before
executing the scenario.

- `design/screens/sign-in.md`
- `design/components/button.md`

## Preconditions

1. Staging parent URL reachable.
2. Test Google (and Apple, if shipped in v1) OAuth account available; not previously bound to a different parent on this staging DB.
3. OAuth redirect URLs configured in the staging env.

## Scenario

**Given** a parent on the sign-in screen

**When** they tap "Continue with Google" (or Apple) and complete the OAuth round-trip

**Then** the following expected outcomes are observed:

1. API responds 2xx with a session token.
2. If this is the first use of the OAuth subject, a new `Parent` row + `Household` are created; otherwise the existing `Parent` is matched by `oauth_subject`.
3. The parent lands on the parent dashboard signed in.
4. `oauth_provider` and `oauth_subject` are populated on the `Parent` row.

## UI fidelity

Each item below is a binary pass/fail check against the design
package. Token values in `<from-design-package>` are resolved
against `design/tokens/*.json` and the matching component spec
in `design/components/*.md` before execution.

1. OAuth buttons sit below the email/password form, visually de-emphasised (`button.md` `variant=secondary`).
2. Buttons show the provider brand mark per each provider's current usage rules.

## Accessibility (WCAG 2.1 AA)

1. OAuth buttons have accessible names that include the provider name (WCAG 4.17.2 / 2.34).
2. Keyboard reachability and focus indicator visible (WCAG 2.1.1, 2.4.7).

## Evidence to record

Capture under `evidence/US-2-oauth-signin/` and reference
from `templates/uat-report.md` §"Evidence index".

1. Screenshot of sign-in screen with both auth paths visible.
2. Network `.har` capturing the OAuth redirect chain and the final `POST /api/auth/oauth` exchange.
3. DB row showing `oauth_provider` / `oauth_subject` populated.

## References

- User-story source: `docs/scope-brief.md` §2.2
- Spec section: `spec-v1-mvp.md` §User Stories 2
- Cross-lane coordination: see scope-brief §5 for stories
  spanning multiple lanes.
- Glossary terms: `CONTEXT.md` (Onboarding & Identity cluster).
- Runbook procedure: `uat/runbook.md` §5 (per-scenario
  procedure), §7 (critical path), §9 (failure modes).
