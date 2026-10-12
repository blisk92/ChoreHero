# Component: Select

> Single-select dropdown for parent SPA. The kid SPA uses chips/buttons
> instead of a dropdown for its small option sets (chore kind, etc.)
> — see the chore editor screen for that pattern.

## Anatomy

```
Label

┌──────────────────────────────────────┐
│  Selected option label         ▾    │
└──────────────────────────────────────┘

[helper text or error]
```

- Closed state visually identical to a text input (`--ch-surface-card`,
  `--ch-border-default`, `--ch-radius-input`).
- Chevron `▾` on the right, 20dp, `--ch-text-tertiary`.
- Selected value uses `--ch-text-body-md`, color `--ch-text-primary`.

## Trigger

- `<button type="button" aria-haspopup="listbox" aria-expanded="false">`
  wraps the visible selected text and chevron.
- Keyboard:
  - `Enter` / `Space` → open
  - `Escape` → close (focus returns to trigger)
  - `ArrowDown` / `ArrowUp` while closed → open + focus first/last option
  - `Home` / `End` while open → first / last option
  - `Tab` → close + move focus naturally

## Listbox (opened)

- Position: anchored below the trigger (`--ch-z-dropdown`).
- Background: `--ch-surface-card`, shadow `--ch-shadow-2`,
  radius `--ch-radius-md`, padding `--ch-space-1` vertical.
- Max-height: 320dp with internal scroll.
- Each option: `--ch-text-body-md`, padding `--ch-space-3`
  horizontal, `--ch-space-2` vertical. Min hit height: `--ch-touch-min`.

### Option states

| State | Background | Notes |
|---|---|---|
| Default | `--ch-surface-card` | |
| Hover / focus | `--ch-surface-skeleton` | |
| Selected | `--ch-color-brand-violet-100` | Checkmark `✓` 16dp on the right; text `--ch-text-primary` bold. |
| Disabled | `--ch-surface-card` | Text `--ch-text-disabled`. |

## Sizes

Same as Input (`md` default, `lg` for kid — but kid rarely uses
selects).

## Accessibility

- The listbox element has `role="listbox"`.
- Each option is `role="option"` with `aria-selected="true|false"`.
- `aria-activedescendant` on the listbox tracks the focused option
  by id.
- Type-ahead: typing a printable character jumps focus to the first
  option whose label starts with that character.
- Multi-select: NOT supported in v1; if a story needs it, build a
  separate component (chip-multi-select) and route to it.

## Validation

- Same pattern as Input: validate on blur, `aria-invalid`,
  helper/error text slot, persistent label.
- `required` option at the top of the list reads "Choose..." (not
  empty) so screen readers announce it.

## Fidelity rules (UAT checklist)

- [ ] Trigger is a `<button>` with `aria-haspopup="listbox"` +
      `aria-expanded` toggling correctly.
- [ ] Listbox has `role="listbox"`, options `role="option"`.
- [ ] `aria-activedescendant` follows keyboard focus.
- [ ] Selected option shows visually AND `aria-selected="true"`.
- [ ] `Escape` closes the listbox AND returns focus to the trigger.
- [ ] Type-ahead works for the first letter.
- [ ] Focus ring renders on `:focus-visible` for both trigger and options.

## Anti-patterns (rework triggers)

- ❌ Native `<select>` without custom styling (looks alien on kid SPA;
  no brand color surface).
- ❌ Options without `role="option"`.
- ❌ Disabled options that still receive focus.
- ❌ A listbox that closes when the mouse leaves the trigger before
  the user has clicked an option (hostile UX).