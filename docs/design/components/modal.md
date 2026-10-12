# Component: Modal

> Dialog overlay for focused tasks (chore editor, reward editor,
> child profile creation, redemption action, deny-reason prompt,
> regenerate-code confirm, link-kid-device child profile picker).

## Anatomy

```
┌────────────────────────────────────────────┐
│  ✕                                [Title]  │
│                                            │
│  [body content: form / list / message]     │
│                                            │
│                                            │
│                          [Cancel]  [Save]  │
└────────────────────────────────────────────┘
```

- Centered on a `--ch-surface-overlay` backdrop.
- Background: `--ch-surface-card`.
- Radius: `--ch-radius-modal` (24dp).
- Shadow: `--ch-shadow-modal`.
- Padding: `--ch-space-modal-padding` (24dp) all sides.
- Max-width: 480dp (mobile full-width minus 32dp margin each side)
  / 560dp (desktop).
- Max-height: 80vh with internal scroll on the body.

## Header

- Title: `--ch-text-title-lg` (28dp) on parent SPA;
  `--ch-text-title-md` (22dp) on kid SPA.
- Close button (`✕` icon, 24dp) top-right.
- Optional sub-title / context line below title:
  `--ch-text-body-sm`, `--ch-text-tertiary`.

## Body

- Form fields stacked with `--ch-space-form-field-gap`.
- Lists inside modal use the same compact list rules.
- When the body is content-heavy (> 5 fields or any field with
  > 1 line description), the title row sticks to the top and the
  body scrolls.

## Footer

- Action row right-aligned.
- Primary action right, secondary action left.
- Buttons: parent SPA uses `lg` size; kid SPA uses `md` (no kid
  modal is large enough to need `lg`).
- `Enter` triggers the primary action; `Escape` triggers the
  secondary action (Cancel / Close).

## Variants

### Standard modal (parent SPA chore editor, reward editor)

- As described above.
- Open from a button click on the page.
- Close via `✕`, `Escape`, backdrop tap, or Cancel button.

### Confirmation modal (parent SPA "Regenerate code?", "Delete chore?")

- Smaller: max-width 400dp.
- Body is a short paragraph + optional consequences list
  ("This will: invalidate the current code, require the parent to
  re-link all kid devices").
- Footer: `Cancel` (secondary) + `Confirm` (primary, danger if
  destructive).

### Bottom sheet (kid SPA "Skip this chore?" confirm)

- Slides up from the bottom; max-height 50vh.
- Has a drag handle (24dp wide, 4dp tall, `--ch-color-neutral-ink-300`,
  8dp from top) to indicate swipe-to-dismiss.
- On mobile only. Parent SPA never uses bottom sheets.

### Nested confirm (rare; e.g. "Approve + notify kid?" if dual-action)

- Uses `--ch-z-modal-nested`. Backdrop is `--ch-surface-overlay`
  with 70% opacity over the parent modal's backdrop.
- Otherwise same as Standard modal.

## Lifecycle

- Open: backdrop fades in 180ms; modal scales from 0.96 → 1.0 over
  260ms with `--ch-easing-emphasized`.
- Close: reverse; total 260ms.
- Focus management:
  - On open: focus moves to the first focusable element in the body,
    OR to the modal container itself (`tabindex="-1"` + `.focus()`)
    if the body has no focusable element initially.
  - While open: focus is trapped inside the modal (`Tab` cycles).
  - On close: focus returns to the element that opened the modal.
- `aria-modal="true"` on the modal container.
- `role="dialog"` and `aria-labelledby` pointing to the title.

## States

| State | Notes |
|---|---|
| Open | Backdrop + modal visible. Body scroll locked. |
| Closing | Animating out. Focus remains on the modal until animation completes. |
| Closed (unmounted) | Removed from DOM. Focus restored. |

Loading state for async actions inside a modal: the primary
action button transitions to loading (spinner inside, label
preserved); secondary action is disabled during the in-flight
request to prevent cancel-mid-save.

## Copy guidance

- Modal title states the task ("Edit chore", "Add reward", "Create
  child profile"). Not "Form" or "Modal".
- Body copy is plain. Parent SPA quietly functional, kid SPA
  plain-but-warm.
- Destructive confirmations lead with the consequence: "This will
  delete 3 chores. You can't undo this." Not "Are you sure?"
- Buttons: parent "Save" / "Cancel" / "Delete" / "Regenerate"; kid
  "Save it" / "Skip" / "Got it".

## Accessibility

- `role="dialog"` + `aria-modal="true"` + `aria-labelledby="title-id"`.
- Focus trap inside the modal.
- Background page is `inert` (or `aria-hidden="true"`) while modal is
  open.
- `Escape` closes the modal (acts as the secondary action).
- Close button has `aria-label="Close"`.
- Confirmations announce their destructive nature to screen readers
  (`aria-describedby` points to the consequences paragraph).
- Focus ring on every focusable element inside the modal on
  `:focus-visible`.
- Bottom sheet: announce as `role="dialog"` (NOT `role="complementary"`).
  Drag handle is decorative (`aria-hidden`); swipe-to-dismiss is
  supplemental — `Escape` and the close button remain the
  keyboard-accessible paths.

## Fidelity rules (UAT checklist)

- [ ] Backdrop uses `--ch-surface-overlay` token.
- [ ] Modal uses `--ch-surface-card`, `--ch-radius-modal`,
      `--ch-shadow-modal`, `--ch-space-modal-padding`.
- [ ] Title is rendered with `aria-labelledby` + heading tag
      (order-appropriate `<h2>` / `<h3>`).
- [ ] Focus is trapped inside the modal while open.
- [ ] On close, focus returns to the opener element.
- [ ] `Escape` triggers the secondary action.
- [ ] Background page cannot receive focus while modal is open.
- [ ] Destructive confirmations name the consequence in the body
      and announce it via `aria-describedby`.
- [ ] Loading button preserves the label (does not collapse label
      to icon).
- [ ] Bottom sheet has a visible drag handle (kid SPA only).

## Anti-patterns

- ❌ A modal whose title is "Form" or generic.
- ❌ A modal without focus trap (Tab escapes into the background).
- ❌ A confirmation that asks "Are you sure?" without naming the
  consequence.
- ❌ A modal that closes on backdrop click without explicit
  confirmation when there's unsaved input (loses data).
- ❌ Multiple modals stacked without z-index discipline.
- ❌ A modal on the parent SPA using the bottom-sheet pattern.