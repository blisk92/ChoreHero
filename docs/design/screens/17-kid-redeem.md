# Screen 17 — Kid Redeem

> US 30, US 31, US 36. The catalog; "out of stock" handling.

## User story

- US 30 (browse), US 31 (request redemption), US 36 (out of stock
> refuses overflow).

## Route

- `/redeem` (kid SPA).

## Layout

```
┌──────────────────────────────────────────────────────────────┐
│  ← Redeem                                Avatar · Maya       │
├──────────────────────────────────────────────────────────────┤
│  Your points: 245                                           │
│  Helper: "Pick a reward. A grown-up will say yes or no."    │
│                                                              │
│  Catalog (1-column, full-width cards):                       │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  Reward name                                         │    │
│  │  Description (short)                                 │    │
│  │  Cost: 50 pts · "3 left" or "Out of stock"           │    │
│  │           [ Ask for it ]                              │    │
│  └──────────────────────────────────────────────────────┘    │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  Reward name                                         │    │
│  │  ...                                                  │    │
│  │           [ Ask for it ]                              │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  Empty state: "No rewards yet. Ask a grown-up to add some."  │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│  BottomNav                                                   │
└──────────────────────────────────────────────────────────────┘
```

## Copy

| Element           | Copy                                                  |
|-------------------|-------------------------------------------------------|
| Title             | "Redeem"                                              |
| Helper            | "Pick a reward. A grown-up will say yes or no."       |
| Cost line         | "[N] pts"                                              |
| Stock line        | "[N] left" or "Out of stock"                           |
| Out-of-stock chip | "Out of stock" (warning variant)                       |
| Ask for it btn    | "Ask for it"                                           |
| Tap blocked       | Toast "Out of stock. Try again later?" (warm-but-clear) |
| After request     | Toast "Sent to a grown-up." (success, polite)         |
| Empty H           | "No rewards yet."                                      |
| Empty body        | "Ask a grown-up to add some."                          |

## Tokens used

- Background: `--ch-surface-app-kid`.
- Cards: `--ch-surface-card`, `--ch-radius-card`,
  `--ch-shadow-card-resting`.
- Cost chip: `variant="brand"` (violet fill).
- Stock-out chip: `variant="warning"`.
- Out-of-stock card: opacity 0.7 + striped stock chip; the CTA is
  disabled.

## Components used

- `<Card>` per reward.
- `<Chip variant="brand">` for cost.
- `<Chip variant="warning">` for stock-out.
- `<Button intent="approve" size="xl">` for "Ask for it".
- `<EmptyState variant="kid">`.
- `<Toast>`.

## Hierarchy

- H1.
- H2 for empty state heading.

## Tab order

1. Top bar.
2. (Card body not focusable; text only.)
3. "Ask for it" on each card.
4. Bottom nav.

## States

| State             | How                                                |
|-------------------|----------------------------------------------------|
| Loading           | 3× skeleton card.                                    |
| Empty             | "No rewards yet." empty state.                       |
| Loaded            | Catalog.                                            |
| Out of stock tap  | "Ask for it" disabled; tapping does nothing; an explicit aria-disabled and visual chip. |
| Insufficient pts  | The card carries a chip "You need [N] more points" and the CTA disabled. |
| Request sent      | Toast + card state → "Waiting for a grown-up." (chip `variant="brand"`, no further taps). |
| Approved          | The card refreshes from WS; stock decrements; toast. |
| Denied            | Toast "[Grown-up] declined. [reason text]." with reason if provided. |

## Accessibility

- Each card has `role="group"` and the reward name is announced.
- Out-of-stock chip: `aria-label="Out of stock"`.
- Cost chip: `aria-label="Costs [N] points"`.
- "Ask for it" disabled state uses `aria-disabled="true"`.
- A live region announces "Sent to a grown-up" via toast.

## Composition rules

- The catalog is consumed via WS so updates from the parent flow in
  within seconds.
- A reward with stock_remaining = 0 is rendered visibly but not
  interactive. The kid sees what could be there next.
- Insufficient points: the chip is rendered when
  `balance < reward.cost`. Disabled state.

## Fidelity rules (UAT)

- F-9.6: out-of-stock chip when stock_remaining = 0.
- F-2.3: kid primary CTA yellow when balance sufficient.
- F-3.4: single column.

## Anti-patterns

- ❌ Showing a redeem count leaderboard (no sibling sharing).
- ❌ Edit or counter-offer flow (kid-cannot-propose is hard rule).
