# Screen 21 — Parent settings

> Hub for household-level settings + links to sub-screens (kid
> devices, push opt-in, sign-out).

## User story

- US 5, US 6, US 7 (household code sub-screen).
- US 8 (kid devices sub-screen).
- US 45 (push sub-screen).
- Sign-out is straightforward.

## Route

- `/settings` (parent SPA, side nav).

## Layout

```
┌──────────────────────────────────────────────────────────────┐
│  TopNav                                                       │
├──────────┬───────────────────────────────────────────────────┤
│ SideNav  │  H1: Settings                                      │
│          │  Helper: "Manage your household."                  │
│          │                                                   │
│          │  ┌──────────────────────────────────────────────┐  │
│          │  │ Household                                     │  │
│          │  │   • Children  → /settings/children           │  │
│          │  │   • Kid devices → /settings/kid-devices      │  │
│          │  │   • Household code → /settings/household-code│  │
│          │  └──────────────────────────────────────────────┘  │
│          │  ┌──────────────────────────────────────────────┐  │
│          │  │ Notifications                                │  │
│          │  │   • Push → /settings/notifications           │  │
│          │  └──────────────────────────────────────────────┘  │
│          │  ┌──────────────────────────────────────────────┐  │
│          │  │ Account                                      │  │
│          │  │   • Profile (name, email)                    │  │
│          │  │   • Sign out                                 │  │
│          │  └──────────────────────────────────────────────┘  │
└──────────┴───────────────────────────────────────────────────┘
```

## Copy

| Section           | Copy                                                |
|-------------------|-----------------------------------------------------|
| H1                | "Settings"                                          |
| Children          | "Children" + count                                 |
| Children sub      | "Add or edit child profiles"                       |
| Kid devices       | "Kid devices"                                       |
| Household code    | "Household code"                                    |
| Notifications     | "Notifications"                                      |
| Push              | "Push notifications"                                |
| Profile           | "Profile"                                            |
| Sign out          | "Sign out"                                          |

## Tokens used

- Section cards: `--ch-surface-card`, `--ch-radius-card`,
  `--ch-shadow-card-resting`.
- Each row inside the card: list-row variant with chevron.

## Components used

- `<TopNav>`.
- `<SideNav>`.
- `<ListRow>` × N.
- `<Modal variant="confirm">` for sign-out.

## Hierarchy

- H1.
- H2 for each section card.

## Tab order

1. Side nav.
2. Top nav.
3. Each row in section order (Household → Notifications →
   Account).

## States

| State              | How                                                |
|--------------------|----------------------------------------------------|
| Default            | Section list.                                       |
| Sign-out confirm   | Modal.                                               |
| Saved toast        | Toast appears at top-right.                          |

## Accessibility

- Each section is `<section>` with `aria-labelledby` to its H2.
- Rows are `<a>` (real link) for navigations.
- Sign-out confirm standard modal.

## Composition rules

- "Children" route shows the list of kids + the Add/Edit modal
  (Screen 04). Out of scope for v1 if there is only one kid; the
  row still works to edit that kid.
- The "Household code" route is essentially Screen 05 without the
  QR + devices list (the QR stays on the Link screen).

## Fidelity rules (UAT)

- F-3.3: side nav ≥ 1024dp.
- F-2.2: parent palette.
- F-7.x: a11y.

## Anti-patterns

- ❌ A "delete household" affordance (irreversible; not in v1).
- ❌ Nested modals on sign-out.
