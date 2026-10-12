# Flow: deadline expiry

> US 13 (deadline on one-off). US 19 (skip on deadline chore:
> expired). US 38 (parent ping: deadline expired).

## Triggers

- A one-off chore with a `due_at` passes its deadline without
  completion.
- A skip on a deadline chore expires it instantly (per spec
  semantics on US 19 — recurring → returns to pool; deadline →
  expired; at-will → returns to pool).

## Visual sequence

```
  Parent sets a deadline on "Clean garage"
  (Tuesday 9pm, parent + kid both see it in their respective lists)
  
     Tue 21:00:00 — server expiry pass runs
                     ↓
       parent sees: in-app ping "Deadline missed: Clean garage expired."
       kid sees:   chore disappears from My Active (if it was claimed
                   and not finished) or just absent from the pool.
```

## Detailed steps

### 1. Setting the deadline (parent)

- Chore editor (Screen 08): set `due_at` for a one-off chore.
- Save → row appears with deadline chip.

### 2. Visual cue on parent side

- Deadline chip: `variant="warning"`, "Due [relative date]".
- On the kid side: deadline chip on the chore row in Available
  Extras or My Active.

### 3. Expiry

- Server-side reducer runs at the due_at tick (or shortly after on
  the next polling sweep).
- Status → `expired`.
- Parent ping fires (in-app; web-push if opted in).
- Kid device syncs: chore disappears from My Active if claimed,
  from Available Extras otherwise.
- The chore is archived from the kid's view but visible to the
  parent in a Past/archive view (per CONTEXT glossary "Expire").

### 4. Parent reaction

- Parent sees the notification.
- Optionally: parent can edit or delete the archived chore.
- Optionally: parent can revive the chore by editing it back into
  the pool (clearing the deadline or extending it).

## Components touched

- Chore row deadline chip (`variant="warning"`).
- Notification strip on both sides.
- Past/archive view (parent only).

## Tokens touched

- Standard.

## Animation

- Standard. No special motion for expiry.

## States

| State               | How                                                |
|---------------------|----------------------------------------------------|
| Upcoming deadline   | Warning chip on the row.                            |
| Deadline passed     | Server expires; status → expired.                   |
| Past/archive        | Parent-side history row, status chip "Expired".    |
| Revived             | Parent edits; status returns to pool.               |

## Accessibility

- Notification strip announces expiry politely.
- Past/archive row has accessible name including chore + status.
- Touch targets 44dp+.

## Composition rules

- An expired chore is archived; it does NOT return to the pool
  unless the parent explicitly edits it.
- An expired redemption request is impossible (redemptions are
  approved/denied/reversed, not expired — see flows/parent-
  redemption-approve-deny-reverse.md).

## Fidelity rules (UAT)

- F-12.x: notifications flow.
- F-7.x: a11y.

## Anti-patterns

- ❌ Auto-extension of deadlines.
- ❌ A reminder before the deadline (v1 has no reminders; per spec
     out-of-scope "idle-chore nudges, chore reminders").
- ❌ A modal on expiry (a notification is sufficient).
