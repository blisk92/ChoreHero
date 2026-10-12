# Screen 01 — Parent Sign-up

> US 1. Email + password registration. Creates a `Parent` row and a
> `Household` row, then redirects to `/dashboard`.

## User story

- US 1 (parent sign-up by email + password).
- US 3 (automatic household creation) happens server-side; the UI
  just confirms it after sign-up.

## Route

- `/sign-up` (parent SPA).
- Unauthenticated only; signed-in users are redirected to
  `/dashboard`.

## Layout

```
┌──────────────────────────────────────────────────────────┐
│  ← Back              Brand                    Sign in → │
├──────────────────────────────────────────────────────────┤
│ ┌────────────────────────┐ ┌───────────────────────────┐ │
│ │   Side illustration    │ │  H1: Create your account  │ │
│ │   (parent + tablet +   │ │                           │ │
│ │    chores list)        │ │  Subhead                  │ │
│ │                        │ │  Fields:                  │ │
│ │   Static. Decorative.  │ │   • Full name             │ │
│ │                        │ │   • Email                 │ │
│ │                        │ │   • Password              │ │
│ │                        │ │   • Confirm password      │ │
│ │                        │ │                           │ │
│ │                        │ │  [ Create account ]       │ │
│ │                        │ │  or — divider —           │ │
│ │                        │ │  [ Continue with Google ]│
│ │                        │ │  [ Continue with Apple ] │
│ │                        │ │                           │ │
│ │                        │ │  By creating… (tiny T&C) │
│ └────────────────────────┘ └───────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

- Two columns ≥ 1024dp; single column below (illustration stacks on
  top, hidden on < 480dp).
- Page padding: `--ch-space-screen-padding-x`, top
  `--ch-space-screen-padding-y`.
- Form max-width 480dp.

## Copy

| Element        | Copy                                                              |
|----------------|-------------------------------------------------------------------|
| H1             | "Create your account"                                            |
| Subhead        | "It's free for one parent and one kid."                          |
| Full name lbl  | "Your name" (required)                                            |
| Email lbl      | "Email" (required)                                                |
| Password lbl   | "Password" (required) + helper "At least 8 characters."           |
| Confirm lbl    | "Type the password again"                                         |
| Submit btn     | "Create account"                                                   |
| Divider        | "or" (small, centered)                                            |
| Google btn     | "Continue with Google"                                            |
| Apple btn      | "Continue with Apple"                                             |
| T&C footer     | "By creating an account, you agree to our Terms and Privacy Policy." |
| Sign-in link   | "Already have an account? Sign in"                                |

## Tokens used

- Background: `--ch-surface-app-parent`.
- Card (form container on < 1024dp): `--ch-surface-card`,
  `--ch-radius-card`, `--ch-shadow-card-resting`.
- Primary CTA: `--ch-color-brand-violet-700`, no sunshine.
- OAuth buttons: `--ch-surface-card`, 1px border, secondary-style.
- Input: per `components/input.md`.

## Components used

- `<TopNav variant="parent-marketing">` (compact).
- `<Input variant="default">` × 4.
- `<Button variant="primary" size="lg">` × 1.
- `<OAuthButton variant="google" | "apple">` × up to 2.
- `<FormError>` inline + `<FormHelper>` under fields.
- `<Link>` for "Sign in".

## Hierarchy

- H1: "Create your account".
- No H2 needed (single form).

## Tab order

1. Back link
2. Sign-in link (top-right)
3. Full name
4. Email
5. Password (toggle visibility)
6. Confirm password (toggle visibility)
7. Submit button
8. Google button
9. Apple button (if present)
10. Terms link
11. Privacy link

Submit is reached before OAuth because the visual hierarchy is
"primary then alternatives".

## States

| State              | How                                                                |
|--------------------|--------------------------------------------------------------------|
| Default            | Empty fields; submit disabled until all valid.                     |
| Field focus        | Border → `--ch-border-focus`; focus ring visible.                  |
| Field invalid      | Border `--ch-border-danger`, helper text in danger, `aria-invalid="true"`. |
| Field valid        | Optional check icon (subtle; only after blur).                     |
| Passwords mismatch | Confirm field shows "Passwords don't match." (live, polite).        |
| Submitting         | Submit shows spinner + "Creating your account…"; `aria-busy="true"`. |
| Network failure    | Inline error banner above submit: "Something went wrong. Try again?" |
| Success            | Auto-redirect to `/dashboard` after 200ms grace; toast "Account created." |
| OAuth round-trip   | Redirect happens in the same tab; loading spinner overlay on the whole form. |
| OAuth cancelled    | Returns to form with no error state; OAuth buttons recover focus.  |
| Existing account   | Email field shows "An account already uses this email. Sign in instead." |

## Validation rules

| Field      | Rule                                                                |
|------------|---------------------------------------------------------------------|
| Full name  | Non-empty, ≤ 60 chars.                                              |
| Email      | RFC 5322 + lowercase normalization. Server is the source of truth.  |
| Password   | ≥ 8 chars; ≥ 1 letter and 1 number. (Looser on client; server enforces.) |
| Confirm    | Equal to Password.                                                  |

## Accessibility

- Each field has a `<label>` (visible). Placeholder absent on label fields.
- Required fields marked with `*` + `aria-required="true"`.
- Password show/hide toggle uses `aria-pressed`.
- Errors use `aria-invalid` + `aria-describedby` pointing at the error
  text.
- Form has `<form aria-describedby="form-help">` where `form-help`
  carries the T&C line.
- Submit error uses `role="alert"` so it is announced.
- OAuth buttons render with the brand mark on the left (default
  neutral fill; the Google/Apple glyph is the only brand color in the
  row).
- Reduced motion: the redirect transition is a 200ms fade only.
- Forced colors: each OAuth button keeps a 1px border in `ButtonText`
  so it remains distinct.

## Empty / loading / error

- Loading the page itself is rare (it's a static shell on the PWA);
  show a skeleton card while CSS assets load if needed.
- Network errors use the universal error component: card, red border,
  retry button.

## Composition rules

- The back link sends to `/` (marketing).
- The sign-in link sends to `/sign-in`.
- The OAuth section is below the form, separated by an "or"
  divider. Visually, OAuth is the alternative path, not the primary.
- No password-strength meter in v1; the helper text is enough.

## Fidelity rules (UAT)

- F-2.2: parent-side palette only.
- F-3.1: 44dp touch targets.
- F-4.5: no exclamation marks.
- F-7.10: visible labels.
- F-8.x: voice rules apply.

## Anti-patterns

- ❌ Placeholder-as-label ("Email address" inside the field).
- ❌ OAuth button above the form (creates ambiguity about the
     primary path).
- ❌ A modal-style pop-up on failure (the error is inline).
- ❌ Auto-sign-in after OAuth without explicit confirmation.
