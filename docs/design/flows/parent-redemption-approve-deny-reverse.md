# Flow: redemption approve / deny / reverse

> US 31 (kid requests). US 33 (approve). US 34 (deny + reason).
> US 35 (reverse approved). US 36 (out-of-stock refuses). The full
> redemption lifecycle on the parent side.

## Visual sequence

```
  /redeem on kid                  /redemptions on parent
  ┌────────────────┐              ┌──────────────────────────┐
  │ Reward · 50 pts │              │ Pending: Maya · 30 min    │
  │ [ Ask for it ]  │ → WS →       │ screens · 50 pts · 2h ago│
  └────────────────┘              │ [Approve] [Deny]          │
                                   └──────────────────────────┘
                                          │
                  ┌───────────────────────┴─────────────┐
                  ↓                                      ↓
            ┌──────────┐                          ┌────────────┐
            │ Approve  │                          │ Deny       │
            │ single   │                          │ modal:     │
            │ tap →    │                          │ reason     │
            │ success  │                          │ (optional) │
            │ toast    │                          │ → confirm  │
            └──────────┘                          └────────────┘
                  ↓                                      ↓
            kid notified:                         kid notified:
            "Grown-up said                         "Grown-up said
            yes to …"                              no to …"
            balance debited                        chore stays
            WS push                                (deny returns
                                                  chore to pool per
                                                  spec default —
                                                  applies to chores,
                                                  not redemptions)
                                                  
                  ↓ (later — same day or up to 7 days)
            ┌──────────────────────────┐
            │ Reverse (History tab)    │ → confirm modal
            │ consequence row shows    │ → points returned
            │ return + stock++         │ → kid notified
            └──────────────────────────┘
```

## Detailed steps

### 1. Kid requests redemption (`/redeem`)

- Kid taps "Ask for it" on a card (US 31).
- Out-of-stock tap → blocked client-side (US 36); card carries the
  chip "Out of stock".
- Insufficient balance → button disabled with chip "Need [N] more".
- On submit: optimistic UI shows "Waiting for a grown-up." chip;
  toast "Sent to a grown-up."

### 2. Parent sees pending (`/redemptions` → Pending tab)

- WS push: new row appears (US 32).
- Bell badge increments.
- Two actions visible: Approve, Deny.

### 3. Approve

- Single tap. No modal.
- Server: redemption `status → approved`, appends negative
  `PointsLedger` entry, decrements reward stock if set.
- WS push to kid: balance debited; toast.
- Toast on parent: "Approved. [Kid] has been notified."
- Row leaves Pending; appears in History as Approved with a Reverse
  button.

### 4. Deny

- Tap Deny → focus-trapped modal with optional reason (US 34).
- Cancel keeps row.
- Confirm (Deny) → status = denied, `denial_reason` stored.
- WS push to kid: "Grown-up said no to [reward]. [reason]"
- Toast on parent: "Denied. [Kid] has been notified."
- Row leaves Pending; appears in History as Denied (no further
  action).

### 5. Reverse (only on Approved, History tab)

- Tap Reverse → focus-trapped modal (Screen 12).
- Consequence row: "[Kid] gets [N] points back."
- Confirm → status = reversed, appends positive `PointsLedger`
  entry (offsetting the original debit), stock increments by 1.
- WS push to kid: balance updated; toast.
- Toast on parent: "Reversed. [Kid] got [N] points back."
- Row stays in History with status `reversed`.

## Components touched

- `<RedemptionRow>`.
- `<Modal variant="confirm">` for deny + reverse.
- `<Toast variant="success">`.
- WS hooks.

## Tokens touched

- Intent `approve` / `deny` / `reverse`.
- Standard surface tokens.

## Animation

- Row appears in History with `--ch-duration-base` enter fade.
- Toast is standard.

## States

| State              | How                                                |
|--------------------|----------------------------------------------------|
| Pending empty      | "All caught up."                                    |
| Pending loaded     | List with approve/deny.                              |
| Approve flight     | Spinner on Approve button.                           |
| Deny modal         | Focus trap; textarea + counter.                     |
| Reverse modal      | Focus trap; consequence row.                        |
| History filter     | Approved/Denied/Reversed sub-tabs.                   |
| Net for kid        | After WS push, balance card and history reflect.    |

## Accessibility

- Standard modal a11y.
- Approve/Deny/Reverse buttons have unique `aria-label`s including
  reward and kid.
- Aria-live polite on the parent's toast to announce the resolution.
- Kid side: aria-live announces balance + outcome.

## Composition rules

- Approve is the default visible action.
- Reverse is available for 7 days after approval (locked decision
  for v1; archived rows are not reversible).
- A new redemption request cannot edit cost; price is locked per
  spec (kid cannot propose counter-offers).

## Fidelity rules (UAT)

- F-9.9: deny requires confirmation modal.
- F-9.6: out-of-stock chip blocks.
- F-12.2: toast position surface-appropriate.

## Anti-patterns

- ❌ Approve in a modal (single-tap, not focus-trapped).
- ❌ Reverse after 7 days (archived).
- ❌ A bulk approve action.
