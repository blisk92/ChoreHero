# Screen 09 — Parent rewards

> US 28, US 29, US 51. Manage the reward catalog: add, edit,
> remove.

## User story

- US 28, US 29, US 51.

## Route

- `/rewards` (parent SPA).

## Layout

Same shell as Screen 07. List of cards, one per reward, plus
add / edit / remove actions.

```
┌──────────────────────────────────────────────────────────────┐
│  TopNav                                                       │
├──────────┬───────────────────────────────────────────────────┤
│ SideNav  │  H1: Rewards                       [+ Add reward] │
│          │  Helper: "Choose rewards your kid can redeem..."   │
│          │                                                   │
│          │  Grid (2-up at ≥ 768dp, 3-up at ≥ 1024dp):         │
│          │  ┌──────────────────┐ ┌──────────────────┐         │
│          │  │ 30 min screens   │ │ Pick dinner      │         │
│          │  │ Cost: 50 pts     │ │ Cost: 80 pts     │         │
│          │  │ No stock limit   │ │ Stock: 3 left    │         │
│          │  │ [ Edit ] [ × ]   │ │ [ Edit ] [ × ]   │         │
│          │  └──────────────────┘ └──────────────────┘         │
│          │  ...                                               │
│          │                                                   │
│          │  Empty state CTA: "Add your first reward."        │
└──────────┴───────────────────────────────────────────────────┘
```

## Copy

| Element       | Copy                                                |
|---------------|-----------------------------------------------------|
| H1            | "Rewards"                                            |
| Helper        | "Choose rewards your kid can spend points on."      |
| Add btn       | "Add reward"                                         |
| Card cost     | "[N] pts"                                            |
| Stock helper  | "Stock: [N] left" or "No stock limit"               |
| Empty H       | "No rewards yet."                                    |
| Empty body    | "Add your first reward."                             |
| Empty eg line | "Examples: 30 min screen time, pick dinner, choose the movie." |

## Tokens used

- Cards: `--ch-surface-card`, `--ch-radius-card`,
  `--ch-shadow-card-resting`. Hover: `--ch-shadow-card-hover`.
- Cost chip: `variant="brand"`.
- Stock-out chip: `variant="warning"`.

## Components used

- `<Card>`.
- `<Chip>` for cost & stock.
- `<Button>` Edit, Delete.
- `<Modal>` Screen 10 (reward editor).
- `<EmptyState variant="parent">`.

## Hierarchy

- H1.
- H2 inside the editor modal.

## Tab order

1. Add reward.
2. Each card's actions in turn.

## States

| State              | How                                             |
|--------------------|-------------------------------------------------|
| Loading            | 3× skeleton card.                                |
| Empty              | EmptyState.                                      |
| Edit modal open    | Same as Screen 08 (modal pattern).              |
| Delete confirm     | Standard.                                        |
| Delete success     | Row removed; toast "Reward deleted."            |

## Accessibility

- Each card is a list item with its own accessible name
  (reward name + cost).
- Edit/Delete buttons have unique `aria-label`s per row.

## Composition rules

- A reward with stock_remaining = 0 stays visible to the parent,
  but the kid catalog marks it out of stock (Screen 17 + US 36).
- Deletion is confirm-modal-driven; the modal names the reward.

## Fidelity rules (UAT)

- F-3.5: card grid breakpoints.
- F-3.1: touch targets.
- F-7.x: a11y.

## Anti-patterns

- ❌ Stock remaining > 100 (cap reasonable).
- ❌ A reward without a positive cost.
