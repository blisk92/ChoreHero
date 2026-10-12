# Screen 03 — Parent dashboard

> The parent's home. Shows the kid's balance, streak summary, pending
> redemptions, pending reviews, first chore/reward CTA when those
> lists are empty, and a notification strip.

## User stories

- US 3 (first-load dashboard empty state).
- US 23 (parent sees kid's balance).
- US 26 (parent sees per-chore streaks).
- US 32 (parent sees pending requests).
- US 50 (parent first chore CTA).
- US 37-40 (notification tray content).

## Route

- `/dashboard` (parent SPA, default for signed-in parents).

## Layout (desktop, ≥ 1024dp)

```
┌──────────────────────────────────────────────────────────────────────┐
│  TopNav  (brand, search, profile)                       ☀/🌙  bell    │
├──────────┬───────────────────────────────────────────────────────────┤
│ Side Nav │  H1: Hi, [name].                                            │
│          │  Subhead: "[Kid] has earned 245 points this month."         │
│ • Chores │ ┌──────────────────────────────────────────────────────┐  │
│ • Rewards│ │  Balance card (large, hero): kid avatar + balance     │  │
│ • Devices│ │  + "Streak: 5 days" chip                            │  │
│ • Settings│ └──────────────────────────────────────────────────────┘  │
│          │ ┌──────────────────────────────────────────────────────┐  │
│          │ │  Pending redemptions (count badge in heading)         │  │
│          │ │   • row: avatar · reward · cost · approve · deny       │  │
│          │ │   • up to 3, "View all →" links to /redemptions       │  │
│          │ └──────────────────────────────────────────────────────┘  │
│          │ ┌──────────────────────────────────────────────────────┐  │
│          │ │  Pending reviews (review-flagged chores waiting)     │  │
│          │ │   • row: chore name · kid · claimed_at · review CTA │  │
│          │ └──────────────────────────────────────────────────────┘  │
│          │ ┌──────────────────────────────────────────────────────┐  │
│          │ │  Streak summary (top 3 streaks)                       │  │
│          │ │   tile tile tile                                       │  │
│          │ └──────────────────────────────────────────────────────┘  │
│          │ ┌──────────────────────────────────────────────────────┐  │
│          │ │  Notification strip (in-app notifications, last 3)    │  │
│          │ └──────────────────────────────────────────────────────┘  │
└──────────┴───────────────────────────────────────────────────────────┘
```

Side nav width: `--ch-space-nav-height-tall` (64dp label / icon).
Top nav height: `--ch-space-9` (48dp).

## Layout (mobile, < 768dp)

```
┌───────────────────────────────┐
│ ☰  ChoreHero        🔔 avatar │
├───────────────────────────────┤
│ H1: Hi, [name].               │
│                               │
│ [ Balance card (hero) ]       │
│   avatar · 245 points         │
│   Streak: 5 days              │
│                               │
│ [ Pending redemptions   → ]   │
│ [ Pending reviews       → ]   │
│                               │
│ [ Streak summary tiles ]      │
│                               │
│ [ Notification strip ]        │
│                               │
│ Quick links:                  │
│  • Add chore                  │
│  • Add reward                 │
├───────────────────────────────┤
│ BottomNav: Chores · Rewards · │
│            Devices · Settings │
└───────────────────────────────┘
```

Side nav becomes bottom nav on mobile. Below 1024dp, side nav is
hidden; the bottom-nav rail replaces it.

## Copy

| Section            | Heading                                                |
|--------------------|--------------------------------------------------------|
| Dashboard heading  | "Hi, [name]."                                          |
| Subhead (no chores)| "Add a chore and pick rewards to get started."        |
| Subhead (with activity) | "[Kid] earned [N] points this month."             |
| Balance card label | "Points"                                               |
| Redemptions heading | "Pending requests"                                    |
| Reviews heading    | "Waiting for your review"                              |
| Streak heading     | "Streaks"                                              |
| Streaks empty      | "No streaks yet."                                      |
| Notification strip | "[count] new updates" or "All caught up"              |

## Tokens used

- Background: `--ch-surface-app-parent`.
- Side rail + top nav: `--ch-surface-card`.
- Balance card (hero, parent side): `--ch-color-brand-violet-100` (subtle tint, parent palette restraint).
- Streak tiles: `--ch-surface-card`, `--ch-radius-card`,
  `--ch-shadow-card-resting`.
- Notification strip: `--ch-color-info-600` 100 tint background,
  with chevron-row items.
- Bottom nav background: `--ch-surface-card`, top border
  `--ch-border-default`.
- Active bottom-nav item: 2px violet underline; `aria-current="page"`.

## Components used

- `<TopNav variant="parent-app">`.
- `<SideNav variant="parent">` (desktop).
- `<BottomNav variant="parent">` (mobile).
- `<BalanceCard variant="hero">`.
- `<StreakSummary>`.
- `<RedemptionRow>` × up to 3 (compact rows).
- `<ReviewRow>` × up to 3.
- `<NotificationStrip>`.
- `<EmptyState variant="parent">` for first-load (when no chores).

## Hierarchy

- H1: "Hi, [name]." (1 per screen).
- H2: "Pending requests", "Waiting for your review", "Streaks",
  "Notifications".
- H3: streak tile labels, individual row headings inside sections.

## Tab order

1. Skip link.
2. Top nav: brand → search → profile → theme toggle → bell.
3. Side nav items (desktop) OR top nav continues.
4. Dashboard heading (not focusable; skipped).
5. Subhead (not focusable).
6. Balance card actions (if any).
7. Pending redemptions: each row's approve / deny / reverse button.
8. Pending reviews: each row's review CTA.
9. Streak tiles: each tile (link to chore detail).
10. Notification strip items.
11. Bottom nav items (mobile).

## States

| State                | How                                                                |
|----------------------|--------------------------------------------------------------------|
| First-load (no chores, no rewards, no kid) | Whole body shows EmptyState variant "parent" with "Add your first chore" CTA. |
| First-load (no rewards only) | Subhead card nudges "Set up rewards kids can spend points on." |
| Loading              | Skeletons for each card (5 visible).                              |
| Error                | Error banner top: "Couldn't load dashboard. Retry."                |
| WebSocket reconnecting | A subtle pill under top nav: "Reconnecting…" (no blocking).      |
| WebSocket live       | Pill hidden.                                                       |
| Notifications unread | Bell shows badge count (>0).                                       |
| Pending review due   | Stripe highlight on the review row with `aria-current="true"`.    |

## Accessibility

- H1 + heading hierarchy respected.
- Skip link to `#main`.
- Each pending row is a list item; the actions are real buttons with
  unique `aria-label`s (e.g. "Approve [reward] for [kid]").
- Balance card: the number is announced via `aria-live="polite"` when
  it changes; visual + audible update.
- WebSocket status pill is `role="status"` and updates via
  `aria-live="polite"`.
- Bottom nav icons + labels (kid-friendly but not themed): each
  item shows icon + label below; `aria-current="page"` for the
  active item.
- Streak tiles are buttons that navigate to chore detail.
- Touch targets respect parent min (44dp).
- Color is never the only signal: the streak chip carries text
  ("5-day") + fire icon + the violet chip background.

## Composition rules

- The dashboard is the canonical "live" surface. Pending review
  items + pending redemption items are always above the fold on
  desktop.
- The balance card never competes with a celebratory avatar; this
  is the parent's view, not the kid's.
- "All caught up" hides the notification strip; a single bell icon
  in top nav remains.

## Fidelity rules (UAT)

- F-9.3: first-load shows the empty state CTA until ≥1 chore exists.
- F-2.2: parent palette.
- F-3.3: side nav ≥ 1024dp; bottom nav below.
- F-7.x: a11y.

## Anti-patterns

- ❌ A celebratory avatar hero on the parent dashboard (US 55
     restraint).
- ❌ A "view all" link that becomes "view fewer" — single direction.
- ❌ Auto-scrolling to the first pending row when the user lands
     (let the user orient).
