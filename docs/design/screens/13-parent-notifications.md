# Screen 13 — Parent notifications

> US 37, 38, 39, 40, 45. Parent in-app notification list. Lives at
> `/notifications` and as an inline strip in the dashboard
> (see Screen 03).

## User story

- US 37, 38, 39, 40 (the parent ping feed).

## Route

- `/notifications` (parent SPA).

## Layout

```
┌──────────────────────────────────────────────────────────────┐
│  TopNav                                                       │
├──────────┬───────────────────────────────────────────────────┤
│ SideNav  │  H1: Updates                                         │
│          │  Tabs: [ Unread (badge) ] [ All ]                    │
│          │  Filters: [ Review pending ] [ Redemptions ]         │
│          │            [ Deadlines ] [ Pool empty ]             │
│          │                                                   │
│          │  List (newest first):                               │
│          │  ┌──────────────────────────────────────────────┐  │
│          │  │ Avatar/kid icon · Review pending             │  │
│          │  │ "Maya marked 'Make bed' done. Approve? →"     │  │
│          │  │ 2h ago · [ Review ] [ Mark read ]             │  │
│          │  └──────────────────────────────────────────────┘  │
│          │  ...                                                │
│          │  Empty: "All caught up."                             │
└──────────┴───────────────────────────────────────────────────┘
```

## Copy

| Element       | Copy                                                |
|---------------|-----------------------------------------------------|
| H1            | "Updates"                                           |
| Tabs          | "Unread" with count badge, "All"                    |
| Filter        | "Review pending", "Redemptions", "Deadlines", "Pool empty" |
| Review item   | "[Kid] marked '[chore]' done. Approve?" |
| Redemption item | "[Kid] wants [reward] for [N] pts."              |
| Deadline item | "Deadline missed: [chore] for [Kid] expired."       |
| Pool empty item | "Recurring pool is empty."                        |
| Actions       | "Review", "Mark read", "Open"                       |
| Empty         | "All caught up."                                    |

## Tokens used

- Card per item: `--ch-surface-card`, `--ch-radius-card`,
  `--ch-shadow-card-resting`.
- Unread indicator: 3px left border in `--ch-color-brand-violet-600`.
- Filter chips: `variant="brand"` when selected (filled).

## Components used

- `<Tabs>` (Unread/All).
- `<FilterRow>` (chip-based filters).
- `<Card>` per item.
- `<Button variant="ghost">` for actions.
- `<EmptyState>`.

## Hierarchy

- H1.
- (Item heading is the message; H3 inside the card.)

## Tab order

1. Tabs.
2. Filters.
3. Each item action.

## States

| State            | How                                                |
|------------------|----------------------------------------------------|
| Loading          | 3× skeleton row.                                    |
| Empty            | "All caught up."                                     |
| Loaded Unread    | Card list with unread left border.                  |
| Loaded All       | Same layout; all items regardless of read state.    |
| Mark read        | Item moves from Unread to All; toast "Marked read." |
| Open action      | Navigates to relevant surface (e.g. Review → pending reviews). |

## Accessibility

- The whole list is `role="log"` with `aria-live="polite"` so new
  notifications are announced.
- Read/unread state uses `aria-label` on the card; unread items
  carry an `aria-current="true"` for tab focus.
- Each card action has a unique label (kid + chore/reward name).

## Composition rules

- Marking an item as read never deletes it. The list persists for
  the parent's history.
- Filter chips are multi-select; selecting "Redemptions" +
  "Deadlines" shows the union.

## Fidelity rules (UAT)

- F-3.1: 44dp.
- F-7.x: a11y.
- F-12.1: in-app list, not a separate page (this IS the dedicated
      page for the verbose view; the dashboard also shows the
      inline strip).

## Anti-patterns

- ❌ Push-only delivery (in-app is canonical default per spec).
- ❌ Pagination that hides older than 30 days silently; load more
     keeps going back.
