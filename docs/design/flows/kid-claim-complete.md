# Flow: kid claim → complete → balance

> The single most important kid-side interaction. US 16, US 18,
> US 21, US 22, US 46 (offline variant). Visual + interaction rules
> for the optimistic update, the celebrate toast, and the
> reconcile-on-reconnect path.

## Triggers

| Step                | Trigger                                          |
|---------------------|--------------------------------------------------|
| 1. Tap chore        | Kid taps a chore card in Available Extras.       |
| 2. Optimistic state | Row optimistically moves to My Active section.   |
| 3. Background sync  | The mutation is enqueued in Dexie outbox.        |
| 4. Server ACK       | Server returns the updated `Chore.status = claimed`. |
| 5. Tap "Done"       | Kid marks the chore done.                        |
| 6. Optimistic points | Balance updates immediately (US 22).            |
| 7. Celebrate toast  | Toast "Nice work!" fires on success.              |
| 8. Server ledger    | Non-review-flagged: points appended immediately.  |
| 9. Balance persists | Updated via WS fan-out to parent (US 47).        |

## Visual sequence

```
                  ┌── Available Extras ──┐                 ┌── My Active ──┐
                  │ [Make bed] [N pts]    │      →         │ [Make bed]    │
                  │ [Claim it]            │                │ [Done] [Skip] │
                  └────────────────────────┘                └────────────────┘
                                    ↓ tap Claim
                  ┌────────────────────────┐
                  │ row leaves Available   │
                  │ Optimistic update      │
                  │ (no spinner needed;    │
                  │ tap → instant move.)   │
                  └────────────────────────┘
                                    ↓ tap Done
                  ┌────────────────────────┐
                  │ row leaves My Active   │
                  │ Balance updates:       │
                  │ 200 → 205             │
                  │ (+celebrate pulse on   │
                  │ the points badge)      │
                  └────────────────────────┘
                                    ↓ toast
                  ┌────────────────────────┐
                  │ "Nice work!" toast     │
                  │ (auto-dismiss 3-4s)    │
                  └────────────────────────┘
```

## Steps in detail

### 1. Tap chore (Available Extras)

- Row carries `aria-label="Claim [chore]"` on its primary CTA.
- Claim button reaches 64dp (kid primary CTA min).
- The tap moves the row instantly to My Active (optimistic). No
  spinner; the action is immediate; the network mutation is
  enqueued.

### 2. My Active Done / Skip

- Done: 64dp primary CTA, sunshine.
- Skip: 64dp ghost CTA.
- Skip on a one-off deadline chore triggers a confirm bottom sheet
  ("This chore expires if you skip. Skip anyway?").

### 3. Done pressed

- Row leaves My Active.
- Balance updates the same frame (US 22).
- Review-flagged: points are NOT yet added; celebrate toast replaced
  with "Sent to a grown-up." (success, polite, no celebrate).
- Non-review-flagged: celebrate pulse on the points badge, brief
  scale `1.0 → 1.08 → 1.0` 1.2s, respects `prefers-reduced-motion`.
- Toast fires (top-center, kid SPA).

### 4. Failure modes

- Network failure mid-claim: row returns to Available Extras with
  a tiny warning chip; toast "Hmm, that didn't work. Try again?"
- Review-flagged completion failure: row stays in My Active with
  error state; toast shows retry.
- Streak milestone: if the increment pushes streak to 7 or 30, the
  celebration modal (Screen 18) appears after the toast fades.

## Components touched

- `<ChoreRow>`.
- `<BottomNav>` (no change).
- `<BalanceHero>` (number updates).
- `<Toast variant="celebrate">` for non-review-flagged.
- `<Toast variant="info">` for review-flagged.
- `<StreakMilestoneModal>` (Screen 18) on streak hit.

## Tokens touched

- `--ch-z-toast` for toast placement.
- `--ch-duration-base` for row transitions (not celebratory).
- `--ch-duration-celebrate` for celebrate pulse.
- `--ch-shadow-cta-primary` on the Done button.

## Animation

- Row move: `--ch-duration-base` standard easing.
- Balance number tick: `--ch-duration-fast` cross-fade.
- Celebrate pulse: `--ch-duration-celebrate` emphasized easing,
  disabled under reduced motion.

## States covered

| State               | Visual + interaction note                             |
|---------------------|-------------------------------------------------------|
| Optimistic update   | Instant; no spinner.                                  |
| Pending in outbox   | Top bar subtle pill "Saving…", no row layout change.  |
| Server ACK          | `pending → committed` in Dexie.                       |
| Network drop        | Row returns to Available; warm-but-clear toast.       |
| Reconnect           | Outbox replays in original order; toast "All caught up." |
| Streak milestone    | Modal appears after toast.                            |

## Accessibility

- "Claim it" → "Done" transition announced via polite live region
  ("Claimed Make bed. 5 points.").
- Balance number is in a polite live region; updates are announced.
- Skip confirm uses bottom sheet (kid-friendly; large targets).
- Toast does not steal focus.
- All primary CTAs hit 64dp.

## Composition rules

- A claimed chore cannot be claimed twice. The UI ensures it doesn't
  appear in Available Extras after the optimistic move.
- A claimed chore that the parent deletes (US open question 10:
  disappears on next sync, no points awarded) — the kid sees the
  row vanish on reconnect with a soft toast.

## Fidelity rules (UAT)

- F-9.5: My active above Available extras.
- F-3.4: single column.
- F-2.3: kid CTAs yellow.
- F-11.1: claim shows optimistic update immediately.

## Anti-patterns

- ❌ A blocking spinner on tap.
- ❌ A celebratory animation on review-flagged Done (the points
     haven't actually been awarded yet).
- ❌ A modal between Claim and Done (this flow should be one-tap
     friction).
