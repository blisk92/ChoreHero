# Screen 19 — Kid points detail

> US 21 (kid sees running balance), US 23 (parent sees kid balance,
> parent dashboard has its own card). This screen is the kid's
> dedicated balance view: running total with last 5 ledger entries.

## User story

- US 21 (parent dashboard partially covers too).

## Route

- `/points` (kid SPA, bottom nav).

## Layout

```
┌──────────────────────────────────────────────────────────────┐
│  ← Your points                            Avatar · Maya       │
├──────────────────────────────────────────────────────────────┤
│  Balance hero (taller than /today):                          │
│   H1: 245                                                    │
│   "Points" caption                                           │
│                                                              │
│   Streak chip: 🔥 5-day streak (current longest)            │
│                                                              │
│  Recent activity (last 5 ledger entries):                    │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  ✓ "Make bed"  · +5 pts · Today 8:14 AM              │    │
│  │  ✓ "Feed dog" · +5 pts · Yesterday                   │    │
│  │  ⤴ "30 min screens" · -50 pts · Monday              │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  Helper: "Last 7 days shown. Ask a grown-up for more."       │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│  BottomNav                                                   │
└──────────────────────────────────────────────────────────────┘
```

## Copy

| Element     | Copy                                                       |
|-------------|------------------------------------------------------------|
| Title       | "Your points"                                              |
| Caption     | "Points"                                                   |
| Streak chip | "🔥 [N]-day streak"                                        |
| Activity    | Icons: ✓ earned, ⤴ spent.                                  |
| Activity line | "[chore/reward] · [+N|-N] pts · [relative date/time]"    |
| Helper      | "Last 7 days shown. Ask a grown-up for more."              |

## Tokens used

- Background: `--ch-surface-app-kid`.
- Balance hero: same as /today, but at full height.
- Activity row: `--ch-surface-card`, compact padding
  `--ch-space-card-padding-compact`.

## Components used

- `<TopBar variant="kid-compact">`.
- `<BalanceHero variant="tall">`.
- `<StreakChip>`.
- `<ActivityRow>` per ledger entry.
- `<BottomNav variant="kid">`.

## Hierarchy

- H1.
- H2 for "Recent activity".

## Tab order

1. Top bar.
2. (Activity rows not focusable; they're display-only.)
3. Bottom nav.

## States

| State        | How                                                |
|--------------|----------------------------------------------------|
| Loading      | 3× skeleton activity rows + skeleton hero.           |
| Empty        | "No activity yet."                                  |
| Loaded       | Hero + activity rows.                                |
| Reduced motion | Streak chip static.                              |

## Accessibility

- H1 announces the points number via `aria-label="245 points"` (the
  rendered "245" is non-readable without it; aria-live updates).
- Activity rows have unique `aria-label`s ("Make bed, plus 5 points,
  today at 8:14 AM").
- Touch targets: balance zone is not interactive; activity rows not
  focusable.
- Streak chip not focusable; it informs.

## Composition rules

- The kid cannot delete history.
- The "ask a grown-up for more" copy is the bridge to the parent
  SPA: the kid cannot get more history directly.

## Fidelity rules (UAT)

- F-3.4: single column.
- F-2.5: balance numbers may be Fraunces only on celebration;
  here it's Inter.
- F-9.x: balance updates optimistically and reflects in
  aria-live.

## Anti-patterns

- ❌ An interactive filter or sort (kids cannot change history
     view).
- ❌ A "ledger export" button.
