# Screen 11 — Parent redemption queue

> US 32 (parent sees pending requests). Lists all redemptions in the
> household across pending / approved / denied / reversed states,
> filterable.

## User story

- US 32, US 33 (approve), US 34 (deny + reason), US 35 (reverse).

## Route

- `/redemptions` (parent SPA).

## Layout

```
┌──────────────────────────────────────────────────────────────┐
│  TopNav                                                       │
├──────────┬───────────────────────────────────────────────────┤
│ SideNav  │  H1: Redemptions                  [+ Search ]     │
│          │  Tabs: [ Pending (badge) ] [ History ]            │
│          │                                                   │
│          │  Pending list (default):                           │
│          │  ┌─────────────────────────────────────────────┐  │
│          │  │ Avatar · Kid: Maya                          │  │
│          │  │ Reward: 30 min screens · 50 pts              │  │
│          │  │ Requested 2h ago · "Pleaseeeee"             │  │
│          │  │                              [Approve] [Deny]│  │
│          │  └─────────────────────────────────────────────┘  │
│          │  ...                                               │
│          │                                                   │
│          │  History tab: same layout, with rows that include   │
│          │  status chip (Approved/Denied/Reversed) + action.   │
│          │                                                   │
│          │  Empty state for either tab: quiet "All caught up."│
└──────────┴───────────────────────────────────────────────────┘
```

## Copy

| Element           | Copy                                                |
|-------------------|-----------------------------------------------------|
| H1                | "Redemptions"                                       |
| Tab Pending       | "Pending" with count badge                            |
| Tab History       | "History"                                            |
| Action labels     | "Approve", "Deny", "Reverse"                          |
| Deny confirm      | "Deny this request? You can add a reason."            |
| Deny modal title  | "Deny redemption"                                    |
| Deny reason helper | "Optional. The kid will see your reason."           |
| Approve success   | Toast "Approved. [Kid] has been notified."           |
| Deny success      | Toast "Denied. [Kid] has been notified."             |
| Reverse confirm   | "Reverse this approval? Points will be returned."     |
| Reverse success   | Toast "Reversed. Points returned to [Kid]."          |
| Empty Pending     | "All caught up."                                      |
| Empty History     | "No history yet."                                     |

## Tokens used

- Background: `--ch-surface-app-parent`.
- Card: `--ch-surface-card`, `--ch-radius-card`,
  `--ch-shadow-card-resting`.
- Status chip (history): success for Approved, danger for Denied,
  brand for Reversed.

## Components used

- `<Tabs variant="segmented">`.
- `<Card>` per redemption.
- `<Avatar size="md" variant="default">`.
- `<Chip variant="brand" | "success" | "danger">`.
- `<Button intent="approve">` and `<Button intent="deny">`.
- `<Modal variant="confirm">` for deny + reverse (Deny has a text
  area for reason).

## Hierarchy

- H1.
- H2 inside deny/reverse modals.

## Tab order

1. Tabs (Pending / History) – arrow keys cycle.
2. Search field (if present).
3. Each row's Approve/Deny/Reverse.
4. Modal action: Deny modal → Cancel / Confirm.

## States

| State             | How                                                |
|-------------------|----------------------------------------------------|
| Pending loading   | 3× skeleton row.                                    |
| Empty Pending     | Quiet empty state ("All caught up.").              |
| Pending full      | Card list with approve/deny actions.                |
| Deny modal        | Text area enabled only when deny intent.            |
| History filter    | Sub-tabs filter by status (default: All).           |
| After approve     | Row leaves Pending; appears in History as Approved. |
| After reverse     | Row stays in History; status → Reversed.            |

## Accessibility

- Each row a list item with kid name + reward + cost + action
  context.
- Approve / Deny / Reverse buttons have unique `aria-label`s that
  include kid + reward.
- The tab list uses proper ARIA.
- Pending count badge has `aria-label="3 pending redemptions"`.

## Composition rules

- Approve is the default visible action; Deny is a secondary action
  that opens a modal for an optional reason.
- Reverse is only available on Approved rows in History (and never
  on rows older than 30 days, per spec discretion — design rule:
  Reverse visible for 7 days after approval; after that, archived
  with no reverse).

## Fidelity rules (UAT)

- F-3.1: 44dp touch.
- F-7.x: a11y.

## Anti-patterns

- ❌ Bulk approve.
- ❌ Approve with an editable cost (the listed price is the
     approved price per spec).
