# Flow: parent review + approval

> US 14 (mark review-flagged). US 18 (kid marks review-flagged
> done; points await). US 37 (parent ping). US 38 (deadline
> expiry). The parent approves or denies a review-flagged
> completion, awarding or withholding points.

## Triggers

- A chore has `review_flagged = true`.
- The kid completes the chore; an in-app notification fires on the
  parent side.

## Visual sequence

```
Parent dashboard
  Pending reviews card surfaces "Maya marked 'Make bed' done."
    → Tap → /dashboard/pending/123
        → Single chore card with photo-less approval surface.
            → [ Approve ] → points awarded, kid notified, row archived.
            → [ Deny ]   → confirm modal; chore returns to pool per
                            default (open question 7).
            → [ Later ]  → dismisses; row stays.
```

## Steps in detail

### 1. Ping

- In-app notification on parent SPA (top-bar bell badge increments).
- Inline strip on the dashboard surfaces "1 new review".
- Toast top-right on parent SPA: "1 review waiting". Does not block.

### 2. Open the review

- Tap the row → opens the pending review modal (`/redemptions`
  layout with a single review-focused row).
- Approve / Deny buttons visible.

### 3. Approve

- Single tap on Approve.
- Server applies the positive `PointsLedger` entry.
- Toast success: "[Kid] has been notified."
- Row leaves Pending; appears in Dashboard "Recent activity".
- WS push: kid sees her balance increase via toast on kid SPA
  ("You earned 5 points!").
- Streak reducer runs; if it triggers a milestone, kid SPA shows
  celebration modal (Screen 18).

### 4. Deny

- Tap Deny → opens the deny modal (Screen 12 style with reason).
- The chore returns to the pool per spec (open question 7 default).
- Toast success: "Denied. [Kid] has been notified."
- WS push: kid sees denial toast ("[Grown-up] didn't approve. [reason]")
- The chore is back in Available Extras on kid SPA.

### 5. Streak + balance

- Approval increments streak if same-day; else resets per reducer.
- Balance updates optimistically on the parent dashboard and via WS
  on kid.

## Components touched

- Dashboard `PendingReviewsCard`.
- Review modal (variant of redemption row).
- `<Toast variant="success">`.
- WS hooks (kid + parent).
- Streak reducer (server-side; UI reads state).

## Tokens touched

- Approve button: `<Button intent="approve" size="lg">`.
- Deny button: `<Button intent="deny" size="lg">`.
- Toast variant success.

## Animation

- Toast standard.
- Balance number ticks.

## States

| State             | How                                                |
|-------------------|----------------------------------------------------|
| Pending loaded    | Row visible in Dashboard.                           |
| Pending empty     | "All caught up."                                    |
| Approve in flight | Spinner on the approve button.                      |
| Approve success   | Toast; row archived.                                |
| Deny modal open   | Standard focus trap.                                |
| Deny success      | Toast; chore returns to pool.                       |
| Streak milestone  | Kid SPA celebration modal.                          |

## Accessibility

- Parent: tab order matches visual order.
- Modal: focus trap.
- Toast: does not steal focus.
- Aria-live polite for balance update on parent side.
- Keyboard: Approve is `Enter`-activatable as the default action.

## Composition rules

- A deny reason longer than 0 chars is shown to the kid verbatim
  (warm-but-clear); the parent can leave it blank.
- The chore returns to the pool per spec; if the parent denies on
  a recurring chore, the kid can re-claim it later.

## Fidelity rules (UAT)

- F-9.10: review flow has confirm modal for deny.
- F-7.4: focus trap.
- F-12.3: toast success.

## Anti-patterns

- ❌ Allowing the parent to adjust point value on approval (price
     is locked per spec).
- ❌ A "deny + remove" button (deny returns to pool, not delete).
- ❌ Auto-dismiss of the review row without parent action.
