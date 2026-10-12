# Screen 12 — Redemption action modal

> The composite modal used for deny-with-reason and reverse-with-
> reason flows. Lives at `/redemptions`, opened from the queue.

## User story

- US 34 (deny with optional reason).
- US 35 (reverse approved redemption).

## Trigger

- "Deny" or "Reverse" on a redemption row.

## Layout

```
┌──────────────────────────────────────────────────────────────┐
│  Title (Deny or Reverse)                       ✕             │
├──────────────────────────────────────────────────────────────┤
│  Body:                                                       │
│  "[Kid] wants [reward]. Costs [N] pts."                      │
│  "[Kid]'s balance: [M] pts."                                 │
│                                                              │
│  Reason                                                      │
│  [ textarea                                            ]     │
│  Helper: "Optional. The kid sees your reason."               |
│  Counter: "0 / 200"                                          │
│                                                              │
│  Consequence row (icon + 1-line):                            │
│  Deny:   "Denying won't refund the points they haven't       │
│           spent yet — they were never debited."              │
│  Reverse:"[Kid] will get [cost] points back. The reward       │
│           stock increments by 1."                            │
│                                                              │
│  [ Cancel ]                         [ Confirm ]              │
│                                                              │
│  Danger styling on Confirm (Deny → danger, Reverse → violet).│
└──────────────────────────────────────────────────────────────┘
```

## Copy

| Element        | Copy                                                            |
|----------------|-----------------------------------------------------------------|
| Title (deny)   | "Deny redemption"                                                |
| Title (reverse)| "Reverse approval"                                              |
| Reason helper  | "Optional. The kid sees your reason."                            |
| Reason counter | "[N] / 200"                                                     |
| Consequence (deny) | "Denying doesn't refund points — they were never debited."   |
| Consequence (reverse) | "[Kid] gets [cost] points back. Reward stock increments by 1."|
| Cancel         | "Cancel"                                                        |
| Confirm (deny) | "Deny request" → intent `deny`.                                 |
| Confirm (reverse)| "Reverse approval" → intent `reverse`.                       |

## Tokens used

- Modal: standard.
- Confirm button: intent variant per copy table.
- Consequence row: `--ch-color-neutral-paper-100` background, ink
  text.

## Components used

- `<Modal>`.
- `<Avatar>` (size sm).
- `<Textarea>` with character counter.
- `<Button>` Cancel + Confirm.

## Tab order

1. Close.
2. Reason (textarea).
3. Cancel.
4. Confirm.

## States

| State       | How                                              |
|-------------|--------------------------------------------------|
| Default     | Reason empty; Confirm enabled.                   |
| Confirming  | Spinner + "Sending…"; Cancel disabled.           |
| Success     | Modal closes; toast as documented.               |
| Error       | Inline: "Couldn't apply. Try again?"             |

## Validation

| Field   | Rule                       |
|---------|----------------------------|
| Reason  | ≤ 200 chars, optional.    |

## Accessibility

- Modal standard.
- Textarea `aria-describedby` reason helper + character counter.
- Confirm intent styling never stands alone (always with text +
  icon).

## Composition rules

- Approve does NOT use this modal (it is a single tap from the row
  per US 33).
- Reverse is destructive on a kid's balance; the consequence row
  makes that explicit.

## Fidelity rules (UAT)

- F-7.x: a11y.
- F-9.9: deny requires confirmation modal.

## Anti-patterns

- ❌ An "approve with edits" affordance (counter-offers out of scope).
- ❌ Editing the cost of the reward from this modal.
