# Component: Textarea

> Multi-line text input. Used for: chore description (optional),
> reward description, denial reason, `child_id` profile description
> (no — child profile has no description field), chore edit notes
> (no). Basically: optional rich-text-free prose.

## Anatomy

Same as Input but with auto-resizing vertical extent.

```
Label

┌──────────────────────────────────────┐
│                                      │
│  text area                           │
│                                      │
│                                      │
└──────────────────────────────────────┘

[helper text / char counter]
```

## Sizes

- Min height: 80dp (3 lines at `--ch-text-body-md`).
- Auto-grow up to max-height 240dp, then internal scroll.
- Optional `max-rows` prop sets the auto-grow ceiling.

## States

Inherits all Input states (default, hover, focus, error, disabled,
readonly). The border / background rules are identical.

## Character counter

- When `maxlength` is set, render "{count}/{max}" at the right of the
  helper line.
- Color: `--ch-text-tertiary` until 80% of max, then
  `--ch-color-warning-600`, then `--ch-color-danger-600` at 100%.
- Counter is a visual aid only; the input still hard-blocks over-max
  input.
- `aria-describedby` includes the counter element so screen readers
  announce remaining count.

## Resize

- Resize handle disabled (use `resize: none` in CSS). Auto-grow
  handles expansion; user resizing creates inconsistent layouts.
- This is a deliberate accessibility call: WCAG 2.1.1 (no keyboard
  trap) and consistent cross-device UX.

## Copy guidance

- Same as Input.
- Deny reason (parent SPA, redemption flow): placeholder "Why? (optional)".
- Reward description (parent SPA, reward editor): placeholder
  "What is it? (optional)".

## Accessibility

Inherits Input a11y rules +:

- `aria-describedby` includes helper AND counter when present.
- Resize is not user-controlled; auto-grow is keyboard- and
  screen-reader-neutral.

## Fidelity rules (UAT checklist)

- [ ] Min height ≥ 80dp.
- [ ] Resize handle disabled.
- [ ] Counter announces remaining characters via `aria-describedby`.
- [ ] Focus ring renders on `:focus-visible`.

## Anti-patterns

- ❌ User-resizable textarea (visual inconsistency + a11y risk).
- ❌ Counter without `aria-describedby` link.
- ❌ Hard `rows="N"` without auto-grow.