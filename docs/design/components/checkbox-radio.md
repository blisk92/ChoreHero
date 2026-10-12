# Components: Checkbox & Radio

> Single-select and multi-select primitives. Both share visuals; only
> the selection model and ARIA contract differ.

## Anatomy

### Checkbox

```
┌───┐
│ ✓ │  Label text
└───┘
```

- Box 20dp square, border `--ch-border-strong`, radius `--ch-radius-xs`.
- Filled: background `--ch-color-brand-violet-600`,
  checkmark `✓` 16dp white, centered.
- Hit target 44dp square via padding (the visible box is smaller).
- Indeterminate: same dimensions, dash icon (–) instead of check.
  Used for the "Select all chores" pattern in the parent chores
  list (US 10-12): partial selection.

### Radio

```
( • )  Label text
( ◯ )  Label text
```

- Outer ring 20dp, 2px border `--ch-border-strong`, ring shape.
- Selected: dot 10dp `--ch-color-brand-violet-600` centered.
- Hit target 44dp via padding.

## Layout

- Vertical stack by default (`flex-direction: column`, gap
  `--ch-space-2`).
- Horizontal stack allowed only when labels are short (< 16 chars)
  AND the count is ≤ 4 (e.g. Chore kind: Recurring / One-off).
- Each option is a `<label>` wrapping the input + label text, so
  clicking the text selects the input.

## States

| State | Checkbox | Radio |
|---|---|---|
| Unchecked | Empty box, default border | Empty ring, default border |
| Focus | `--ch-focus-ring-shadow` on the box/ring | Same |
| Hover | Border → `--ch-border-focus` | Same |
| Checked / Selected | Filled violet, checkmark | Filled violet, dot |
| Indeterminate | Filled violet, dash | N/A |
| Disabled | `--ch-surface-skeleton`, text `--ch-text-disabled` | Same |
| Error (parent SPA form validation) | Border `--ch-border-danger`; helper text below the group | Same |

## Group container

- Group label: `--ch-text-label-md`, persistent (always visible).
- Group error text: `--ch-text-body-sm`, `--ch-color-danger-600`,
  one per group, below the last option.
- `role="group"` on the wrapper, `aria-labelledby` points to the
  group label.
- Required indicator `*` next to the group label when any option
  must be selected.

## Usage sites

- Checkbox (single): "I want this chore reviewed before points are
  awarded" (review-flag toggle in chore editor).
- Checkbox (group): "Mark which days the recurring chore is active"
  — wait, that doesn't exist in v1 (streaks are based on
  completeness, not schedule). Remove.
- Checkbox (group): only "Days of week" would apply, but v1 has no
  chore schedule. **No checkbox-group use in v1.**
- Radio group: Chore kind (Recurring / One-off). Reward stock toggle
  ("Unlimited" / "Limited to N"). Deadline toggle ("No deadline" /
  "By..."). Review-flag toggle ("Auto-approve" / "Parent approves").

## Accessibility

- Native `<input type="checkbox">` / `<input type="radio">`
  elements. The visible styling is custom but the underlying input
  is real.
- Native inputs handle keyboard interaction (`Space` toggles
  checkbox; arrow keys move radio selection within a `name` group).
- `aria-required="true"` on the group when at least one option
  must be selected.
- `aria-invalid="true"` on the group when validation fails.
- Focus ring on the visible box/ring, not the wrapping `<label>`.

## Copy guidance

- Option labels are sentence case ("Recurring", "One-off", "Parent
  approves", "Auto-approve").
- No question marks in option labels; the group label asks the
  question, the options answer.
- Optional "(optional)" suffix on individual options that are not
  required by the form.

## Fidelity rules (UAT checklist)

- [ ] Visible box/ring + label both inside one `<label>` so clicking
      either toggles the input.
- [ ] Native `<input type="checkbox|radio">` underneath.
- [ ] Focus ring on the visible control, not the label wrapper.
- [ ] Group has `role="group"` + `aria-labelledby` linking the
      group label.
- [ ] Indeterminate checkbox state implemented (when used).
- [ ] Disabled option has `disabled` attribute AND visible style
      AND skipped from radio's keyboard navigation.

## Anti-patterns

- ❌ A "checkbox group" where each option has its own group label.
- ❌ Custom div-based checkbox without `<input type="checkbox">`.
- ❌ Keyboard handling that overrides native (Space, arrows) —
  the browser already does the right thing if you use a real input.
- ❌ A radio group where one option is `disabled` and tabbing
  skips it but arrow keys still land on it.