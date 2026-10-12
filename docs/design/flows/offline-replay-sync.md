# Flow: offline replay + sync

> US 46 (kid works offline), US 47 (parent sees near-real-time),
> US 48 (offline edits flow in cleanly), US 49 (per-field
> last-write-wins).

## Triggers

- WS drops, navigator offline, or kid device is in airplane mode.
- Mutations enqueue to Dexie outbox.
- On reconnect: outbox replays in order, then live updates flow.

## Visual sequence (kid offline)

```
   ┌──────────────────┐
   │ Top bar: pill    │
   │ "Offline"        │   ← subtle, top-right of kid top bar
   └──────────────────┘
   
   kid claims chore → optimistic move to My Active
   
   kid marks Done → optimistic balance update
   
   toast: "Saved on this device."
   
   reconnect →
   WS connects
   outbox replays
   toast: "All caught up."
```

## Detailed steps

### 1. Detection

- Top-bar pill: "Offline" appears within 2s of WS drop or
  navigator offline event.
- Pill color: `--ch-color-warning-600` ink on `--ch-color-warning-100`
  bg.
- Pill is `role="status"` with `aria-live="polite"`.
- Inline mutation row does NOT block input.

### 2. Mutation

- Every mutation (claim, done, skip, redeem) goes to Dexie outbox.
- Each row carries its original `updated_at`.
- A stable operation ID is generated client-side; replay uses it
  for idempotency.

### 3. Reconnect

- WS reconnects.
- Outbox flushed in original order.
- Server applies each mutation with per-field last-write-wins.
- Toast top-center: "All caught up." (variant `success`).
- WS resumes; subsequent server pushes flow in.

### 4. Conflict (per-field last-write-wins)

- Parent edited a chore while kid had it claimed.
- On reconnect, kid's claim is honored (status = claimed) but the
  parent's edit to `point_value` is also applied.
- Each field carries its own `updated_at`; the server resolves
  per-field, not whole-row.

## Components touched

- Top-bar pill.
- Outbox toast.
- Reconciliation toast (success, kid SPA).

## Tokens touched

- `--ch-color-warning-600` / `--ch-color-warning-100` for pill.
- Standard toast tokens.

## Animation

- Pill fades in/out (`--ch-duration-base`).
- Outbox replay is silent (no per-row loader); only "All caught up"
  fires once.

## States

| State                | How                                                |
|----------------------|----------------------------------------------------|
| Online (default)     | No pill.                                           |
| WS drop              | Pill "Offline" (warning, polite).                  |
| Reconnecting         | Pill "Reconnecting…" (info).                        |
| Replay in progress    | Status pill silent; toast at the end.               |
| All caught up        | Toast fires; pill gone.                              |

## Accessibility

- Pill is `role="status"` and updates politely.
- "All caught up." toast is `role="status"` too.
- Optimistic balance update still announces via aria-live.
- The pill does not steal focus; the kid SPA navigation stays
  usable.

## Composition rules

- A pill that is visible for >30s escalates to a soft "Connection
  trouble?" hint with a retry button.
- Outbox rows older than 24h surface a manual retry surface (rare).

## Fidelity rules (UAT)

- F-11.1: optimistic update on offline claim.
- F-11.2: outbox replays + toast.
- F-11.3: parent edit preserved on kid reconnect.
- F-11.4: subtle reconnecting pill.

## Anti-patterns

- ❌ A blocking modal "You're offline".
- ❌ A spinner during replay (silent in the background).
- ❌ A whole-row overwrite that loses one side's intent (must be
     per-field LWW).
