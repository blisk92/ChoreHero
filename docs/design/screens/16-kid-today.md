# Screen 16 — Kid Today

> US 15 (Available Extras), US 17 (My Active), US 20 (streak inline),
> US 21 (running balance). The kid's home. Big points badge,
> streaks summary chip, "My Active" then "Available Extras", empty
> states per section.

## User story

- US 15, US 17, US 20, US 21, US 22 (instant balance update),
> US 27/42 (streak milestone entry point — opens Screen 18).

## Route

- `/today` (kid SPA, default after welcome).

## Layout

```
┌──────────────────────────────────────────────────────────────┐
│  ← Today                              (Avatar · Maya 👋)     │
├──────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐    │
│  │  Your points: [   245   ]                            │    │
│  │  Streak chip: 🔥 5-day streak (visible when >0)      │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  My active (3)                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ [ chore name ] · [ N pts ] · streak inline (if rec) │    │
│  │            [   Done   ]   [   Skip   ]                │    │
│  └──────────────────────────────────────────────────────┘    │
│  ...                                                         │
│                                                              │
│  Available extras (N)                                        │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ [ chore name ] · [ N pts ]                            │    │
│  │            [   Claim it   ]                            │    │
│  └──────────────────────────────────────────────────────┘    │
│  ...                                                         │
│                                                              │
│  (Empty states when each section is empty — see Screen 22.) │
│                                                              │
│  Notification inline list (in-app, last 3).                  │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│  BottomNav: [ Today ] [ Points ] [ Streaks ] [ Redeem ]      │
└──────────────────────────────────────────────────────────────┘
```

## Copy

| Section / Element       | Copy                                                  |
|-------------------------|-------------------------------------------------------|
| Top bar                 | "Today" + kid avatar (no greeting chip by default; emoji wave appears after a milestone). |
| Balance title           | "Your points"                                          |
| Streak chip             | "🔥 5-day streak" (or longer days).                   |
| My active heading       | "My active" with count                                 |
| Available heading       | "Available extras" with count                          |
| Done btn                | "Done"                                                 |
| Skip btn                | "Skip"                                                 |
| Claim btn               | "Claim it"                                             |
| Streak inline           | "🔥 3-day"                                             |
| Empty My active         | "Nothing in progress."                                 |
| Empty Available extras  | "No chores yet. Ask a grown-up to add some." (Screen 22 covers this empty state per US 52.) |

## Tokens used

- Background: `--ch-surface-app-kid`.
- Balance card: `--ch-surface-card-hero` for the hero balance
  zone, with `--ch-radius-card-hero`, white text. Streak chip sits
  inside this card. Or alternative: balance card uses
  `--ch-color-brand-violet-600` background (sunshine fallback on the
  points number). The brand uses `--ch-color-brand-violet-600` for
  the card with white points number; sunshine is reserved for primary
  CTA. Decisions locked:

  - Balance card bg: `--ch-color-brand-violet-600`.
  - Balance number text: `--ch-color-neutral-paper-000`,
    `--ch-text-display-md` on the number.
  - Streak chip: `variant="sunshine"` (yellow pill, ink text) — the
    only place a sunshined chip is allowed in the kid SPA chrome.
- Chore rows: `--ch-surface-card`, `--ch-radius-card`,
  `--ch-shadow-card-resting`. Hover: `--ch-shadow-card-hover`.
- Primary CTAs in rows: `<Button variant="primary" size="xl">` for
  Claim (sunshine), Done (success green), Skip (ghost).

## Components used

- `<TopBar variant="kid-compact">`.
- `<BalanceHero>`.
- `<StreakChip>`.
- `<ChoreRow>` per row.
- `<BottomNav variant="kid">`.
- `<NotificationStrip variant="kid">`.
- `<EmptyState variant="kid">`.

## Hierarchy

- H1 (page title or balance title? — locked: balance title is
  H1; section headings are H2; no other h1).
- H2 for "My active", "Available extras".

## Tab order

1. Top bar (avatar tap → profile).
2. Done / Skip on each My active row (2 per row).
3. Claim on each Available row.
4. Notification strip items (icons).
5. Bottom nav (Today, Points, Streaks, Redeem).

## States

| State               | How                                                  |
|---------------------|------------------------------------------------------|
| Loading initial     | Skeleton per row (3 visible).                          |
| Empty both sections | Single empty state across whole body (US 52).         |
| Mid-action          | Tap "Done" → optimistic update; row flips to "Saving…"; toast "Nice work!" (celebrate variant) on success; row disappears. |
| Review-flagged done | Toast "Sent to a grown-up." (no celebrate). Points wait. |
| Skip                | Confirmation bottom sheet for review-flagged/one-off chores. |
| Streak milestone    | Celebration modal (Screen 18) appears once when entering a milestone. |
| Offline             | Top bar shows "Offline" pill (subtle); mutations queue. |

## Accessibility

- The Points number is in an `aria-live="polite"` region so updates
  are announced ("245 points"). Numbers rendered with tabular
  numerals.
- Chore rows: each row is `role="group"` with the chore title as the
  name. Actions inside have unique `aria-label`s.
- Buttons reach 56dp minimum; primary Claim/Done reach 64dp.
- Streak chip pulse does NOT fire on prefers-reduced-motion.
- Reduced motion: celebrate toast uses no slide.

## Composition rules

- "My active" precedes "Available extras" so the kid sees what
  they're doing before their options.
- Bottom-nav order: Today (selected), Points, Streaks, Redeem.
- Notifications appear as a slim row above the bottom nav (last 3
  in-app pings).
- Review-flagged Done shows "Sent to a grown-up." instead of "Nice
  work!" because the celebration is gated.

## Fidelity rules (UAT)

- F-9.5: "My active" above "Available extras".
- F-3.4: single column.
- F-2.3: kid CTA yellow.
- F-2.4: brand glow only here on the balance card's CTAs.

## Anti-patterns

- ❌ A two-column desktop layout (single column only).
- ❌ A celebratory avatar competing with the balance card.
- ❌ A "view all chores" link (the kid SPA is intentionally limited;
     the parent SPA is the library).
