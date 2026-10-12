# Screen 20 — Kid notifications

> US 41, US 43, US 44. The kid's in-app notification list.

## User story

- US 41 (new chore in pool), US 42 (streak milestone), US 43 (points
> after approval), US 44 (redemption approved or denied).

## Route

- `/notifications` (kid SPA).

> Note: bottom nav may include "Notifications" in place of
> "Streaks" depending on density; locked to "Streaks" per bottom
> nav decision. The kid accesses notifications via the bell in the
> top bar.

## Layout

```
┌──────────────────────────────────────────────────────────────┐
│  ← Updates                                Avatar · Maya       │
├──────────────────────────────────────────────────────────────┤
│  Tabs: [ Unread (badge) ] [ All ]                            │
│  Helper: "Updates from your chores and rewards."             │
│                                                              │
│  List:                                                      │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  ⭐ "New chore: 'Tidy bedroom' (10 pts)"             │    │
│  │  Just now · "Claim it?" → /today                      │    │
│  └──────────────────────────────────────────────────────┘    │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  ✓ "Reviewed. You earned 5 points!"                  │    │
│  │  2h ago                                              │    │
│  └──────────────────────────────────────────────────────┘    │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  🎉 "Grown-up said yes to 30 min screens."           │    │
│  │  Yesterday                                           │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  Empty: "You're all caught up!"                              │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│  BottomNav                                                   │
└──────────────────────────────────────────────────────────────┘
```

## Copy

| Element           | Copy                                                       |
|-------------------|------------------------------------------------------------|
| H1                | "Updates"                                                  |
| Tabs              | "Unread", "All"                                            |
| Items             | "[chore/reward headline]" with timestamp                   |
| New chore line    | "New chore: '[chore]' ([N] pts)"                            |
| Awarded line      | "Reviewed. You earned [N] points!"                          |
| Streak milestone  | "🔥 [N]-day streak on [chore]!" (occasional celebratory)   |
| Approved (redemption) | "Grown-up said yes to [reward]."                       |
| Denied (redemption)| "Grown-up said no to [reward]. [reason]"                 |
| Empty             | "You're all caught up!"                                    |

## Tokens used

- Card per row: `--ch-surface-card`, `--ch-radius-card`,
  `--ch-shadow-card-resting`.
- Unread indicator: 3px left border `violet-600`.

## Components used

- `<TopBar>`.
- `<Tabs variant="segmented">`.
- `<Card>` per item.
- `<EmptyState variant="kid">`.

## Hierarchy

- H1.
- H2 for empty state.

## Tab order

1. Tabs.
2. Card actions (mostly none — informational).

## States

| State           | How                                                |
|-----------------|----------------------------------------------------|
| Loading         | 3× skeleton row.                                    |
| Empty           | "All caught up."                                     |
| Loaded          | Card list.                                           |
| Item tap (where actionable) | "New chore" → /today with chore highlighted.  |

## Accessibility

- `role="log"` + `aria-live="polite"` for the list.
- Each item has descriptive label; emoji decoration is
  `aria-hidden="true"`.
- Tabs standard.

## Composition rules

- A streak milestone chip duplicates on Today for 24 hours.
- "Reviewed. You earned [N] points!" never appears for
  non-review-flagged completions (those go straight to the
  balance).

## Fidelity rules (UAT)

- F-12.1: in-app list inline within screen (here it's a
      dedicated screen because the list is verbose — context
      rule allows the full page when viewing history).
- F-7.x: a11y.

## Anti-patterns

- ❌ Push notifications to the kid device.
- ❌ A web push opt-in toggle on kid SPA.
