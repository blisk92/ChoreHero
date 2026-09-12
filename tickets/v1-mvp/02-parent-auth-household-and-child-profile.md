# 02: Parent auth, household, and child profile

**What to build:** The end-to-end sign-up, sign-in, household-creation, and child-profile-creation flow. A new parent signs up with email + password, lands on a dashboard that creates a household for them at first login, and can create exactly one child profile (name + an avatar picked from a pre-shipped SVG set of ~12 illustrations). The parent session is JWT-based, persists across reloads, and works across multiple parent devices. OAuth (Google, Apple) is wired as a faster sign-in path on the login screen.

This is the first vertical slice. It cuts through the API (auth + household + child rows), the parent SPA (sign-up / sign-in screens + onboarding step), and Playwright (one e2e test that walks a parent through sign-up → dashboard → child creation).

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] Parent can sign up with email + password; passwords are stored as bcrypt hashes, never plaintext. The password rule is documented in code (a single line in the auth module).
- [ ] Parent can sign in with email + password and receive a JWT that authenticates subsequent API calls.
- [ ] Parent can sign in faster with Google and Apple; both flows resolve to a single `Parent` row keyed by `oauth_provider + oauth_subject`, falling back to linking an existing email match.
- [ ] First successful sign-in creates a `Household` for the parent if one doesn't exist.
- [ ] Parent can create exactly one child profile with a name and an avatar picked from a fixed SVG set (~12 illustrations, flat vector with hand-drawn accents per `CONTEXT.md`).
- [ ] Parent dashboard renders empty-state copy per `CONTEXT.md` ("Add your first chore" / "Add your first reward" big primary CTAs). The "Add your first chore" nudge banner stays visible until ≥1 chore exists in either pool (verified by re-running e2e after ticket 04 lands).
- [ ] Playwright e2e covers the full parent onboarding: sign up → first dashboard render → create child profile → reload and confirm child row is still present (no JWT session loss).
- [ ] A parent who tries to sign in from a second device gets a parallel valid session (per `CONTEXT.md`).
- [ ] API contract test: `POST /api/auth/signup`, `POST /api/auth/signin`, `POST /api/households/{id}/children` — happy path + duplicate-email failure + duplicate-child attempt rejected.
- [ ] Domain vocabulary aligns with `CONTEXT.md`: the SPA refers to users as Parents, the child row is a `Child` profile, and the household is the unit of isolation.
