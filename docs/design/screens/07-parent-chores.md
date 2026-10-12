# Screen 07 — Parent chores

> US 10, US 11, US 12, US 13, US 14. The parent chore library.
> Manage every chore in the household: see them grouped by pool,
> add a new chore, edit, delete. Review-flagged and deadline fields
> are inline toggles.

## User story

- US 10, US 11, US 12, US 13, US 14.

## Route

- `/chores` (parent SPA, default chores page).

## Layout

```
┌──────────────────────────────────────────────────────────────┐
│  TopNav                                                       │
├──────────┬───────────────────────────────────────────────────┤
│ SideNav  │  H1: Chores                       [+ Add chore] │
│          │  Tabs: [ Recurring ] [ One-off ]                  │
│          │  Helper: "Add a chore your kid can claim."        │
│          │                                                   │
│          │  List:                                             │
│          │  ┌─────────────────────────────────────────────┐  │
│          │  │ Make bed · 5 pts · review flagged          │  │
│          │  │ Claimed by Maya 2h ago · 3-day streak        │  │
│          │  │ [ Edit ] [ Delete ]                          │  │
│          │  └─────────────────────────────────────────────┘  │
│          │  ...                                               │
│          │                                                   │
│          │  Pagination / "Load more"                          │
│          │                                                   │
│          │  (Empty state CTA when zero chores — see US 50.)  │
└──────────┴───────────────────────────────────────────────────┘
```

Tabs are the two pools. On desktop, tabs sit under H1; on mobile,
they collapse into a sticky segmented control below the top nav.

## Copy

| Element        | Copy                                                  |
|----------------|-------------------------------------------------------|
| H1             | "Chores"                                              |
| Tab Recurring  | "Recurring"                                            |
| Tab One-off    | "One-off"                                              |
| Helper         | "These are chores your kid can claim from the pool."  |
| Add chore btn  | "Add chore"                                            |
| Empty headline | "No [Recurring | One-off] chores yet."                |
| Empty body     | "Add a chore to get started."                          |

## Token references per row

- Card rest: `--ch-surface-card`, `--ch-radius-card`,
  `--ch-shadow-card-resting`.
- Hover: `--ch-shadow-card-hover` (slight lift).
- Review-flagged indicator: chip `variant="warning"`.
- Deadline indicator: chip `variant="warning"` with due label.
- Streak chip: chip `variant="sunshine"` (kid-side use, but allowed
  here as a parent-facing streak tracker — palette stays neutral).

## Components used

- `<Tabs variant="segmented">`.
- `<Card>` per row.
- `<Chip variant="warning">` for review-flagged / deadline.
- `<Chip variant="sunshine">` for streak (🔥 + count).
- `<Button variant="primary">` for Add chore.
- `<Button variant="ghost">` Edit / Delete.
- `<ConfirmModal>` for Delete.
- `<EmptyState variant="parent">` empty per tab.
- `<Modal>` Screen 08 (chore editor).

## Hierarchy

- H1.
- H2 inside the editor modal.

## Tab order

1. Side nav / bottom nav.
2. Top nav.
3. Add chore.
4. Tabs (Recurring, One-off) — `aria-selected` on the active tab.
5. Each chore row's Edit / Delete actions.
6. Load more / pagination.

## States

| State            | How                                                |
|------------------|----------------------------------------------------|
| Loading          | 3× skeleton card.                                   |
| Empty (no chores)| Empty state CTA "Add your first chore."            |
| Empty (recurring only) | Tabs: Recurring state has its own empty card. |
| Loaded           | List of cards.                                     |
| Add modal open   | Modal focuses the Name field.                      |
| Delete confirm   | Modal traps focus.                                  |
| Delete success   | Row removed; toast "Chore deleted."                 |

## Accessibility

- Tab list uses `role="tablist"` with arrow-key navigation.
- Each row's streak chip has `aria-label="Current streak, 5 days"`.
- Review-flagged chip: `aria-label="Requires your approval"`.
- Delete confirm modal: standard pattern.
- Empty state replaces the list when count = 0.

## Composition rules

- A chore that is currently claimed (status = claimed) is shown but
  cannot be edited in v1 (US 12). The Edit button is disabled; a
  tooltip / `aria-disabled="true"` explains "Editing is disabled
  while claimed."
- Sorting: pool → claimable first, then by point value desc.
- Bulk actions are out of scope for v1.

## Fidelity rules (UAT)

- F-3.3: layout breakpoints.
- F-7.x: a11y (focus trap on editor modal).

## Anti-patterns

- ❌ A "select all + delete" affordance.
- ❌ Edit on a claimed chore (blocked per US 12).
