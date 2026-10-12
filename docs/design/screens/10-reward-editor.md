# Screen 10 — Reward editor (modal)

> US 28, US 29, US 36 (stock-limited refund UX in catalog). Captures
> name, description, point cost, optional stock.

## Trigger

- "+ Add reward" on /rewards or Edit on a reward card.

## Layout (modal)

```
┌──────────────────────────────────────────────────────────────┐
│  Title                                  ✕                  │
├──────────────────────────────────────────────────────────────┤
│  Name                                                       │
│  [ 30 min screens                                       ]   │
│  Helper: 1-60 chars.                                        │
│                                                              │
│  Description (optional)                                      │
│  [ ............................................. ]           │
│  Helper: Up to 200 chars. Shown on the kid catalog.          │
│                                                              │
│  Points cost                                                │
│  [ 50 ] pts   (stepper)                                      │
│                                                              │
│  ☑ Limit number of redemptions                              │
│  When on, shows: [ N ] redemptions allowed   (default 1)     │
│                                                              │
│  Preview (right side on desktop, below on mobile):          │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  30 min screens                                      │    │
│  │  50 pts                                              │    │
│  │  "Up to 200 chars description…"                      │    │
│  │  Stock: 3 left                                        │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  [ Cancel ]                       [ Save reward ]            │
└──────────────────────────────────────────────────────────────┘
```

## Copy

| Element       | Copy                                                            |
|---------------|-----------------------------------------------------------------|
| Title         | "Add reward" / "Edit [name]"                                    |
| Name helper   | "Keep it short. Kids see this name."                             |
| Description helper | "Optional. Shown on the kid catalog under the name."        |
| Points helper | "How many points the kid spends to claim this."                |
| Switch lbl    | "Limit the number of redemptions"                              |
| Switch helper | "Off = unlimited. On = this many redemptions, then it's gone."  |
| Cancel        | "Cancel"                                                        |
| Save          | "Save reward" / "Save changes"                                  |

## Tokens used

- Modal: standard.
- Stepper: standard.
- Switch: standard.
- Preview card: `--ch-surface-card-tinted` (so the parent can
  see the kid-side color without using sunshine on the parent SPA).

## Components used

- `<Modal>`.
- `<Input>` for name.
- `<Textarea>` for description.
- `<Stepper>` for points.
- `<Switch>` for stock toggle.
- `<Stepper>` for stock count (when switch on).
- `<Button>` Cancel + Save.

## Hierarchy

- H2: modal title.

## Tab order

1. Close.
2. Name.
3. Description.
4. Points.
5. Switch.
6. Stock count (when visible).
7. Cancel.
8. Save.

## States

| State                | How                                             |
|----------------------|-------------------------------------------------|
| Default              | Name + cost required; description + stock optional. |
| Stock just turned off| Stock input hides; existing stock remains at stored value (server keeps hidden until 0). |
| Saving               | Spinner.                                         |
| Save success         | Toast + close.                                   |
| Save error           | Inline error.                                    |
| Edits to stock>0     | Save validates stock count ≥ remaining (clamp or warn). |

## Validation

| Field      | Rule                                                                |
|------------|---------------------------------------------------------------------|
| Name       | 1-60 chars.                                                          |
| Description| ≤ 200 chars.                                                         |
| Points     | 1-1000 integer.                                                      |
| Stock      | Optional. When on, 1-999 integer ≥ currently remaining redemptions. |

## Accessibility

- Standard modal.
- Switch exposed with `role="switch"` + `aria-checked`.
- Preview is `aria-hidden="true"` (decorative; the live values
  appear in the form fields).

## Composition rules

- Save disabled while name OR points is empty.
- Stock limit is the only field that can be turned off
  permanently; if the parent wants unlimited, no count needed.

## Fidelity rules (UAT)

- F-7.x: a11y.
- F-3.1: touch targets.

## Anti-patterns

- ❌ Image upload for reward art (v1 has no reward images).
- ❌ Editing cost of an existing reward to less than the lowest
     redemption-requested cost (clamp or warn).
