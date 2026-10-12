# Screen 22 — Empty-state catalogue

> Visual rules for empty states across the app. Defines each variant
> for use in any list view where the underlying count is zero. This
> is a reference page; the actual empty-state surfaces live in the
> relevant parent and kid screens. UAT uses this page to verify
> illustration + copy + CTA together.

## Variants

| Variant            | Where used                                  | Title                    | Body                                                                 | CTA                            | Illustration                                       |
|--------------------|---------------------------------------------|--------------------------|----------------------------------------------------------------------|--------------------------------|-----------------------------------------------------|
| `parent-chores`    | /dashboard first-load, /chores empty        | "No chores yet"          | "Add your first chore to get started."                              | "Add chore"                    | Open notebook                                       |
| `parent-rewards`   | /rewards empty                              | "No rewards yet"         | "Add your first reward. Examples: 30 min screen time, pick dinner." | "Add reward"                    | Wrapped gift box                                    |
| `parent-redemptions` | /redemptions Pending empty               | "All caught up"          | (none)                                                                | (none)                          | Smiling face icon                                    |
| `parent-notifications` | /notifications Unread/All empty         | "All caught up"          | (none)                                                                | (none)                          | Empty inbox icon                                     |
| `parent-devices`   | /settings/kid-devices empty                 | "No devices linked yet"  | "Link a kid device to get started."                                  | "Link a new device"             | Empty tablet icon                                    |
| `kid`              | /today, /redeem, /points empty              | "No chores yet." / "No rewards yet." | "Ask a grown-up to add some."                          | (none — kid SPA is read-only)  | Empty basket / folded towel                          |
| `kid-welcome`      | First launch                                 | "Welcome, [name]!"       | "Let's find you something to do."                                    | "Let's go"                      | Big waving hand                                      |
| `error`            | Anywhere                                      | "Something went wrong." | "Try again?"                                                         | "Try again"                     | Cloud with one raindrop                              |
| `offline`          | Any surface when WS down                     | "You're offline."        | "Changes will sync when you're back online."                          | "Try reconnecting"              | Plug with a small "x"                                |

## Common anatomy

- Container: vertical stack, centered, max-width 360dp parent /
  440dp kid.
- Vertical rhythm: illustration → 24dp → heading → 8dp → body → 24dp
  → CTA.
- Illustration size: 96dp parent, 128dp kid.

## Tokens used

- Heading: parent uses `--ch-text-title-md`; kid uses
  `--ch-text-title-lg`.
- Body: parent `--ch-text-body-md`; kid `--ch-text-body-lg`.
- CTA: parent `<Button variant="primary">`; kid never has a CTA
  here (read-only).

## Components used

- `<EmptyState>` (one component, multiple variants).
- `<Button>` (parent CTA only).

## Hierarchy

- H2 (the empty-state heading is rendered as an H2 so it slots into
  any page hierarchy).
- Sectioned context (the page that hosts the empty state has its
  own H1).

## Tab order

- The CTA (when present) is the only focusable element.

## States

| State            | How                                                 |
|------------------|-----------------------------------------------------|
| Default          | Variant baseline.                                    |
| Loading initial  | Skeletons for ≤ 1.2s before empty state.             |
| Retry (error)   | "Try again" CTA reloads.                              |
| Reduced motion   | Static; no illustration wiggle.                      |

## Accessibility

- Whole empty state is `role="region"` with `aria-labelledby` to the
  heading.
- Illustration is `aria-hidden="true"`.
- CTA inherits `<Button variant="primary">` a11y.

## Composition rules

- An empty state replaces a list when count = 0. The list itself is
  not rendered at the same time.
- Empty state CTA never duplicates a control already in the page
  chrome (e.g. inside a parent dashboard, the empty-state CTA
  shouldn't be a duplicate of the bottom-nav "Add chore" button).

## Fidelity rules (UAT)

- F-9.3: parent first chore empty until ≥1 chore.
- F-9.4: kid SPA no-chores empty + welcome first-launch.
- F-9.6: redemption catalog out-of-stock is not an empty state;
      it is the regular card with a chip (this catalog does NOT
      cover stock-out which is on Screen 17).
- F-10.2: ChoreHero emblem allowed in empty-state illustrations
      BUT not co-located with a kid avatar.

## Anti-patterns

- ❌ A bespoke illustration per screen (the variants listed in
     `components/empty-state.md` are the canonical set).
- ❌ A "no chores yet" empty state shown above the fold when the
     page already has a hero card (the hero is the answer until
     there's nothing to show).
- ❌ Two stacked empty states in the same screen (collapse to one).
