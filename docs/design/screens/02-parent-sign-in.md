# Screen 02 — Parent Sign-in

> US 2 (sign-in by email + password) and US 2 (OAuth). Recovers an
> existing `Parent` session; redirects to `/dashboard`.

## User story

- US 2. Existing parent. Email + password or OAuth.

## Route

- `/sign-in` (parent SPA). Unauthenticated only.

## Layout

Identical structure to Screen 01 (sign-up), with field set shrunk
to email + password and the headline swapped.

```
┌──────────────────────────────────────────────────────────┐
│  ← Back              Brand                  Sign up →   │
├──────────────────────────────────────────────────────────┤
│ ┌────────────────────────┐ ┌───────────────────────────┐ │
│ │   Side illustration    │ │  H1: Welcome back         │ │
│ │                        │ │                           │ │
│ │                        │ │  • Email                  │ │
│ │                        │ │  • Password  [ Forgot? ] │ │
│ │                        │ │                           │ │
│ │                        │ │  [ Sign in ]              │ │
│ │                        │ │  or — divider —           │ │
│ │                        │ │  [ Continue with Google ]│
│ │                        │ │  [ Continue with Apple ] │
│ │                        │ │                           │ │
│ │                        │ │  Don't have an account?  │ │
│ │                        │ │  → Sign up                │ │
│ └────────────────────────┘ └───────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

## Copy

| Element       | Copy                                                              |
|---------------|-------------------------------------------------------------------|
| H1            | "Welcome back"                                                    |
| Email lbl     | "Email"                                                            |
| Password lbl  | "Password"                                                        |
| Forgot link   | "Forgot password?" → `/forgot-password`.                          |
| Submit        | "Sign in"                                                         |
| Sign up line  | "Don't have an account? Sign up"                                  |

## Components used

- Same as Screen 01 minus Full name + Confirm; plus
  `<Link variant="inline">` for Forgot + Sign up.

## Tab order

1. Back / Sign-up link (top)
2. Email
3. Password (toggle visibility)
4. Forgot link
5. Submit
6. Google
7. Apple
8. Sign-up link (bottom)

## States

| State                | How                                                           |
|----------------------|---------------------------------------------------------------|
| Default              | Empty fields; submit disabled.                                |
| Field invalid        | Border + helper text + `aria-invalid`.                        |
| Wrong credentials    | Form-level error above submit: "Email or password is wrong."   |
| Rate-limited         | Form-level error: "Too many tries. Wait a moment and try again." |
| Submitting           | Submit spinner + "Signing in…"; `aria-busy="true"`.           |
| Success              | Redirect to `/dashboard`.                                     |
| OAuth round-trip     | Same as sign-up.                                              |
| Account not found    | Same "Email or password is wrong." (do not leak which).       |

## Validation

| Field      | Rule                                                                |
|------------|---------------------------------------------------------------------|
| Email      | Required.                                                            |
| Password   | Required, ≥ 1 char (no client validation beyond emptiness).          |

## Accessibility

Same contract as Screen 01. The "Forgot password?" link is
positioned to the right of the password label on desktop and below
on mobile; its accessible name is identical.

## Composition rules

- A successful sign-in lands at `/dashboard` even if the user
  attempted to reach a deep link (e.g. `/dashboard/child`); the deep
  link is honored when the user is already signed in.
- Wrong-credentials error is identical for "no account" and "wrong
  password" to avoid leaking which.

## Fidelity rules (UAT)

- F-2.2: parent palette.
- F-3.1: touch targets.
- F-7.10: labels.

## Anti-patterns

- ❌ Different error copy for "wrong password" vs "no account"
     (account enumeration).
- ❌ Password manager suggestions blocked.
- ❌ OAuth button as primary visual.
