# Component: Nav (top bar, side rail, bottom bar)

> Three navigation patterns. Each app (parent SPA, kid SPA) uses
> exactly one.

## Anatomy by pattern

### A. Parent SPA — side rail (desktop / tablet, ≥ 768dp)

```
┌──────┬────────────────────────────────────────────┐
│ 🏠   │                                            │
│ Home │                                            │
│      │   (page content)                            │
│ 🧹   │                                            │
│Chores│                                            │
│      │                                            │
│ 🎁   │                                            │
│Reward│                                            │
│      │                                            │
│ 🔔   │                                            │
│Notif │                                            │
│      │                                            │
│ ⚙   │                                            │
│Setng │                                            │
└──────┴────────────────────────────────────────────┘
```

- Width: `--ch-space-nav-height-tall` (64dp) collapsed / 240dp
  expanded (hover/click to expand; user preference stored).
- Background: `--ch-color-brand-violet-800` (deep violet). Light
  text on dark.
- Active item: `--ch-color-brand-violet-600` background pill +
  `--ch-text-on-brand` text + `--ch-text-on-brand` icon.
- Inactive item: `--ch-text-on-brand` at 70% opacity. Hover →
  100% opacity + `--ch-color-brand-violet-700` background pill.
- Logo at top: ChoreHero emblem 32dp (small). The emblem never
  competes with a kid avatar anywhere it appears.
- Bottom of rail: parent account avatar + dropdown ("Sign out",
  "Settings").

### B. Parent SPA — bottom bar (mobile, < 768dp)

```
┌──────────────────────────────────────┐
│   🏠    🧹    🎁    🔔    ⚙        │
│  Home  Chores Reward Notif Settings │
└──────────────────────────────────────┘
```

- Height: `--ch-space-nav-height-compact` (48dp visual; 56dp hit
  area via padding).
- Background: `--ch-surface-card`, top hairline border.
- 5 items evenly distributed.
- Active item: `--ch-color-brand-violet-600` icon + label. Inactive:
  `--ch-text-tertiary`.
- Notification badge: top-right corner of icon, 16dp circle,
  `--ch-color-danger-600` background, `--ch-text-on-danger` count.
  Visible when unread > 0.

### C. Kid SPA — bottom bar (always)

```
┌──────────────────────────────────────┐
│   📋    ⭐    🎁    🔔            │
│  Today  Points Redeem Notif        │
└──────────────────────────────────────┘
```

- Height: 64dp (visual + hit). Larger because the kid user.
- Background: `--ch-color-brand-violet-700`, hairline top border
  `--ch-color-brand-violet-600`.
- 4 items, evenly distributed.
- Active item: pill background `--ch-color-accent-sunshine-500`
  spanning the icon + label, icon + label in `--ch-text-on-accent`.
- Inactive item: icon + label in `--ch-text-on-brand` at 80%
  opacity. Hover → 100% opacity + `--ch-color-brand-violet-600`
  background pill.
- Notification badge: top-right of icon, 16dp, `--ch-color-accent-sunshine-500`
  background, `--ch-text-on-accent` count.

## Active route detection

- Use Vue Router's matched route to set `aria-current="page"` on
  the active nav item.
- Visual indicator of active state must pair: pill background +
  icon color + label color. Never rely on icon color alone.

## Items

Parent SPA items: Home (dashboard), Chores, Rewards, Notifications,
Settings.

Kid SPA items: Today (chores), Points (balance + history detail),
Redeem (catalog), Notifications.

(Names: "Home" / "Today" / "Points" / "Notifications" / "Settings" —
plain, no clever names. "Rewards" not "Treasure Chest".)

## Accessibility

- `<nav>` element with `aria-label="Primary"` (parent) / `aria-label="Kid navigation"` (kid).
- Each item is an `<a>` (real anchor to the route).
- Active item has `aria-current="page"`.
- Bottom bar items have hit area ≥ 56dp on kid SPA.
- Side rail items have hit area 48dp vertical.
- Icon + label both render; never icon-only in nav (kid SPA
  especially).
- Keyboard: `Tab` moves through items; `Enter` / `Space` activates.

## Copy guidance

- Item labels are short nouns (parent: "Chores", "Rewards",
  "Settings"; kid: "Today", "Points", "Redeem").
- All items have text labels — no icon-only nav items.
- The parent SPA may abbreviate to icons only when collapsed (side
  rail narrow mode), but expanded mode and mobile bottom bar always
  show labels.

## Fidelity rules (UAT checklist)

- [ ] Nav is wrapped in `<nav>` with `aria-label`.
- [ ] Active item has `aria-current="page"`.
- [ ] Active item shows pill background + icon + label color change
      (three signals, not one).
- [ ] Bottom bar height ≥ 56dp on kid SPA, ≥ 48dp on parent SPA.
- [ ] All items have text labels, not icon-only.
- [ ] Notification badge uses an icon + count, never count alone
      (decorative value, but the icon anchors the location).
- [ ] Side rail uses `--ch-color-brand-violet-800` background, NOT
      `--ch-color-brand-violet-700` (the deeper tone is reserved
      for the side rail to set the parent surface apart).
- [ ] Kid bottom bar uses `--ch-color-brand-violet-700` background
      with `--ch-color-accent-sunshine-500` active pill.
- [ ] Logo / emblem is 32dp on the rail, smaller than any avatar
      on the same screen (US 54).

## Anti-patterns

- ❌ Icon-only nav items (kid SPA fails at icon recognition).
- ❌ A bottom bar with > 5 items (target size shrinks below safe).
- ❌ A nav item highlighted only by icon color (color-blind failure).
- ❌ A side rail that uses `--ch-color-brand-violet-700` (same as
  kid nav) — parent and kid should be visually distinct.
- ❌ A nav with "More..." overflow on kid SPA — kids do not
  understand overflow menus.