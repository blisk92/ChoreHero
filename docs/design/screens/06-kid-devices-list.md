# Screen 06 — Kid devices list

> US 8 (list and revoke kid devices). The parent sees every
> registered `KidDevice` and can revoke one. Lives at
> `/settings/kid-devices`.

## User story

- US 8.

## Route

- `/settings/kid-devices` (parent SPA).

## Layout

```
┌────────────────────────────────────────────────────────────┐
│  ← Back   H1: Kid devices               [+ Link new device]│
├────────────────────────────────────────────────────────────┤
│  Helper: Up to [N] device(s) can be linked at once.        │
│                                                            │
│  List (one Card per device):                               │
│  ┌────────────────────────────────────────────────────┐   │
│  │ Tablet · "Maya's iPad" · Last seen 2h ago           │   │
│  │ Linked Sept 12, 2026                              · · ·│
│  │                                          [ Revoke ] │   │
│  └────────────────────────────────────────────────────┘   │
│  ... more rows ...                                         │
│                                                            │
│  Empty state (no devices):                                 │
│  illustration · "No devices linked yet."                   │
│                   · "Link your first kid device →"          │
└────────────────────────────────────────────────────────────┘
```

## Copy

| Element        | Copy                                                  |
|----------------|-------------------------------------------------------|
| H1             | "Kid devices"                                          |
| Helper         | "Each device runs the kid app for the chosen child."  |
| Link new       | "Link new device"                                      |
| Device row     | Friendly name + last-seen relative time.               |
| Linked date    | "Linked [relative date]."                              |
| Revoke         | "Revoke"                                               |
| Revoke confirm | "Revoke [name]? It will stop working immediately."     |
| Revoke success | Toast "[Name] has been revoked."                       |
| Empty state    | "No devices linked yet." → "Link your first kid device." |

## Tokens used

- Background: `--ch-surface-app-parent`.
- Cards: `--ch-surface-card`, `--ch-radius-card`,
  `--ch-shadow-card-resting`.
- Revoke is intent `danger` (per Button spec).
- Confirm modal: standard.

## Components used

- `<TopNav variant="parent-app">`.
- `<Card>`.
- `<EmptyState variant="parent">`.
- `<Button variant="primary">` for "Link new device".
- `<Button variant="secondary" intent="danger">` for "Revoke".
- `<Modal variant="confirm">`.
- `<Toast variant="success">`.

## Hierarchy

- H1.
- H2 inside confirm modal only.

## Tab order

1. Back / "Link new device" (top-bar).
2. Each device row's overflow menu (or Revoke button).
3. Per-modal Cancel / Revoke (when confirm is open).

## States

| State              | How                                                  |
|--------------------|------------------------------------------------------|
| Default list       | Card per device.                                     |
| Loading            | 3× skeleton card.                                    |
| Empty              | EmptyState variant "parent".                          |
| Revoke confirm     | Modal traps focus.                                   |
| Revoke success     | Row removed from list; toast shown.                   |
| Revoke error       | Modal-level "Couldn't revoke. Try again?"             |
| Last-seen unknown  | "Last seen unknown."                                 |

## Accessibility

- Each row has `role="article"` (or wrapped in `<ul>`/`<li>`).
- Revoke action has unique `aria-label="Revoke [name]"` so
  multiple rows are distinguishable.
- "Last seen" is `aria-label="Last seen [relative time]"` (screen
  readers read "Last seen 2 hours ago" naturally).
- Confirm modal standard pattern.
- Touch targets 44dp+.

## Composition rules

- The "Link new device" button opens the modal at Screen 05.
- A revoked device can be re-added later; revocation only ends the
  active session.
- "Last seen" updates live via WS (poll-free); on offline, fall
  back to the value at last WS message.

## Fidelity rules (UAT)

- F-2.2: parent palette.
- F-7.x: a11y.
- F-9.10 partial: revocation is a destructive parent action; needs
  the confirm modal.

## Anti-patterns

- ❌ A bulk revoke action (v1 keeps it per-device for safety).
- ❌ A "rename" flow (parent can only rename at link time; renaming
     later is v2).
