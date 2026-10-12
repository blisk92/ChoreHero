# Component: Table

> Parent SPA only. Used for: parent chores list (admin grid view),
> rewards list, kid devices list, notification log, points ledger
> (parent view of kid's balance), per-household activity audit.

The kid SPA does NOT use tables. Lists on the kid SPA are stacked
cards (see `card.md`).

## Anatomy

```
┌──────────────────────────────────────────────────────────────┐
│  ☐  Chore name       Kind       Points   Streak   Review  ⋮ │
├──────────────────────────────────────────────────────────────┤
│  ☐  Make bed         🔁 Daily   5        🔥 4     ⏳     ⋮ │
│  ☐  Take out trash   ⭐ One-off 10       —        —      ⋮ │
└──────────────────────────────────────────────────────────────┘
```

- Background: `--ch-surface-card`.
- Header row: `--ch-surface-skeleton` background;
  `--ch-text-label-sm` text, UPPERCASE, color `--ch-text-tertiary`.
- Body row: padding `--ch-space-card-padding-compact` (12dp)
  vertical, `--ch-space-4` horizontal.
- Row hover: `--ch-surface-skeleton` background.
- Border-bottom: 1px `--ch-border-default` between rows.
- Radius: outer 16dp; rows inside do not round.

## Columns (defaults)

Every table in v1 has these default columns by surface:

### Chores table (parent)

- Selection checkbox
- Chore name
- Kind (chip: "Recurring" / "One-off")
- Points
- Streak (when > 0; else "—")
- Review flag (chip: "Review" or "—")
- Due (when present; else "—")
- Actions (`⋮` menu: Edit / Delete)

### Rewards table (parent)

- Selection checkbox
- Reward name
- Cost (points)
- Stock (chip: "Unlimited" / "12 left" / "Out")
- Actions (`⋮` menu: Edit / Delete)

### Kid devices table (parent)

- Device name
- Linked on (date)
- Last seen (relative: "2 hours ago")
- Status (chip: "Active" / "Revoked")
- Actions (`Revoke` button)

### Notification log (parent)

- Type (icon: review / deadline / redemption / pool-empty)
- Subject (short string)
- When (relative time)
- Read state (filled circle for unread)
- No actions; click row to navigate.

### Points ledger (parent view)

- When (date + time)
- Chore or reward name
- Delta (`+5` green, `-50` red)
- Running balance

## Density

| Density | Vertical padding | Usage |
|---|---|---|
| `compact` (default for ledger, devices) | `--ch-space-card-padding-compact` (12dp) | Dense information; user is scanning. |
| `default` | `--ch-space-4` (16dp) | Chores, rewards (items per household is small). |

## Selection

- Header checkbox: tri-state (none / some / all). Indeterminate when
  0 < selected < total.
- Selected rows: `--ch-color-brand-violet-050` background.
- Bulk action bar appears above the table when ≥ 1 row selected:
  "N selected · [Delete] [Edit...]". Sticky on scroll.

## Sorting

- Default sort: by column the table was opened with
  (chores by created desc, devices by last_seen desc, ledger by
  when desc).
- Sortable columns get a sort indicator (▲/▼) on the header.
- Click header to sort; second click reverses.
- `aria-sort="ascending" | "descending" | "none"` on the header cell.

## Pagination / virtualization

- v1 household size is small (≤ ~50 chores, ≤ ~20 rewards, ≤ ~10
  devices, ≤ ~200 ledger rows / month). No pagination in v1.
- Tables render all rows. If row count > 100, the table body
  scrolls internally with a sticky header.

## Empty state

- Empty tables show a row that spans all columns with the matching
  empty-state copy + illustration + primary CTA:
  - Chores: "Add your first chore" + a flat illustration.
  - Rewards: "Add your first reward".
  - Devices: "No kid devices linked yet" + link flow.
  - Ledger: never empty (kid has ≥ 0 ledger entries on creation).
    Show "No activity yet" with a quiet illustration.

## Row actions

- Per-row: `⋮` icon button (`sm` size) opens a popover menu with
  Edit / Delete.
- Popover anchored right; closes on outside click or `Escape`.
- Destructive actions in the popover use `--ch-color-danger-600`
  for the label.
- Bulk action bar uses the same intent button grid for visible
  destructive actions.

## States

| State | Notes |
|---|---|
| Default | Header + body rows. |
| Hover (row) | `--ch-surface-skeleton`. |
| Selected | `--ch-color-brand-violet-050`. |
| Focused | Row receives focus via `<tr tabindex="0">` when row is clickable; otherwise the action button receives focus. |
| Loading (skeleton) | 5 placeholder rows with shimmer. `--ch-color-surface-skeleton`. |
| Empty | Single full-width empty-state row. |

## Accessibility

- `<table>` with `<thead>` / `<tbody>` / `<tfoot>` as appropriate.
- `<th scope="col">` on header cells.
- Sortable `<th>` has `aria-sort` and a real `<button>` inside the
  cell that triggers sort (so screen readers announce the sort
  action).
- Clickable row: `<tr>` with a single primary `<a>` or `<button>`
  inside the row that is the entire row's interactive surface
  (the rest of the row is non-interactive cells). Alternative: the
  row itself is not clickable; the action button is.
- Selection checkbox inside each row has `aria-label` including
  the chore / reward name.
- Focus ring on the action button, not on the row.
- The bulk action bar announces "N selected" via `aria-live="polite"`
  on the count element.

## Copy guidance

- Column headers: sentence case, no abbreviations ("Streak",
  not "Str."). Use icons in headers only when paired with text
  (e.g. "📅 Created").
- Row values render as plain data ("5 points", not "5p").
- Empty-state copy follows the parent's `CONTEXT.md` rule:
  primary CTA + descriptive sub-copy.

## Fidelity rules (UAT checklist)

- [ ] Real `<table>` / `<thead>` / `<tbody>` / `<th scope>` (no
      div-soup).
- [ ] Sortable column header has `aria-sort` and a `<button>` inside.
- [ ] Selected rows show `--ch-color-brand-violet-050` background.
- [ ] Bulk action bar appears at ≥ 1 selected, sticky on scroll.
- [ ] Empty state row spans all columns and contains the
      matching empty-state CTA + illustration.
- [ ] Row hover state on pointer devices only (no hover on
      touch devices via `@media (hover: hover)`).
- [ ] Kid devices table renders "Active" / "Revoked" chips with
      semantic colors.
- [ ] Ledger table renders delta + (positive, green) /
      − (negative, red) — colored but always paired with the sign.

## Anti-patterns

- ❌ A `<div>` grid pretending to be a table (screen readers can't
  infer column structure).
- ❌ Sort indicator as the only signal that a column is sortable
  (no visible change on the header itself).
- ❌ An "empty state" row that just shows "No data" with no CTA.
- ❌ Tables on the kid SPA.
- ❌ Color-only signaling for status (always pair color + label).