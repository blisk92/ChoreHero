# Component: Input (text, email, password, number)

> Single-line text input. Email, password, and number are variations
> of this component; the underlying field is the same.

## Anatomy

```
Label (required, persistent)                    [optional helper]

┌─────────────────────────────────────────┐
│  [icon_left]   placeholder or value   [icon_right]│
└─────────────────────────────────────────┘

[error / helper / format hint]
```

- Container: `--ch-surface-card`, border `--ch-border-default`,
  radius `--ch-radius-input`, padding `--ch-space-3` horizontal.
- Label: `--ch-text-label-md`, color `--ch-text-primary`, persistent
  (does NOT float; it's always visible above the field per WCAG
  guidance for cognitive load).
- Helper text: `--ch-text-body-sm`, color `--ch-text-tertiary`,
  appears below.
- Error text: `--ch-text-body-sm`, color `--ch-color-danger-600`,
  icon `alert-circle` 16dp to the left.

## Variants

| Variant | When |
|---|---|
| `default` | Default. |
| `with-icon-left` | Search, email (`@`), currency (`$`). |
| `with-trailing-button` | Password reveal toggle, household code copy. |
| `readonly` | Field is set elsewhere (e.g. household code after generation). |
| `disabled` | Field disabled, can't be edited. |

## Sizes

| Size | Height | Font | Usage |
|---|---|---|---|
| `md` (default) | 44dp | `--ch-text-body-md` | Standard forms (parent SPA). |
| `lg` | 56dp | `--ch-text-body-lg` | Kid SPA inputs (avatar name, code entry). |

Both meet or exceed touch-target minimums.

## States

| State | Border | Background | Notes |
|---|---|---|---|
| Default | `--ch-border-default` | `--ch-surface-card` | |
| Hover | `--ch-border-strong` | `--ch-surface-card` | Cursor indicates edit. |
| Focus | `--ch-border-focus` (3px via focus ring) | `--ch-surface-card` | `--ch-focus-ring-shadow`. |
| Filled | `--ch-border-default` | `--ch-surface-card` | |
| Error | `--ch-border-danger` | `--ch-color-danger-100` | Error text + icon appear. |
| Success | `--ch-border-success` | `--ch-surface-card` | Only used after async validation (e.g. household code check). |
| Disabled | `--ch-border-default` | `--ch-surface-skeleton` | Text → `--ch-text-disabled`. |

## Validation

- Validate on blur, not on every keystroke (parent SPA) — too noisy.
  Exception: the household code field validates on every keystroke
  because the input is short and the result is binary.
- Inline error replaces helper text until resolved.
- `aria-invalid="true"` when error is shown.
- `aria-describedby` links the input to its helper OR error text
  element (the same DOM node is reused; toggle visibility, don't
  change id).
- Required fields: append `*` to the label visually AND add
  `aria-required="true"`.

## Password specifics

- Toggle visibility (eye icon) at `icon_right`. Default hidden.
- The toggle is a real `<button type="button">` inside the input
  wrapper with `aria-label="Show password"` /
  `aria-label="Hide password"`.
- The toggle never moves focus away from the input.
- Password manager affordance: `autocomplete="current-password"` on
  sign-in, `autocomplete="new-password"` on sign-up.

## Household code entry (kid SPA link fallback)

- Use `lg` size with `--ch-font-mono`.
- 6 separate single-character boxes (1 box per character) is the
  preferred kid UX; show the boxes as one input visually split into
  six cells. The internal implementation can be a single `<input>` with
  `maxlength="6"` and visual segmentation, or six `<input>` with
  `inputmode="text"` auto-advance — implementer's call. The DESIGN
  spec says: 6 visible boxes, mono font, big hit target.
- Autocapitalize off, autocorrect off, spellcheck off.
- `inputmode="text"` (so the mobile keyboard stays alphabetic, not
  numeric).

## Copy guidance

- Labels are sentence case ("Email address", not "EMAIL ADDRESS").
- Helper text is one short sentence ("We'll never share this").
- Errors are one short sentence, plain-but-warm (kid) or direct
  (parent):
  - Kid: "Hmm, that didn't work. Try again?"
  - Parent: "Email is required." / "That code doesn't match. Check
    the parent's screen."

## Accessibility

- `<label>` is associated via `for` matching the input's `id`; do not
  rely on placeholder-as-label (placeholder disappears on input).
- Required indicator `*` is paired with `aria-required="true"` so
  the asterisk is announced as "required" by screen readers.
- Focus ring is always visible on `:focus-visible`.
- Color is never the only signal: error state pairs red border +
  red icon + red text.
- `autocomplete` attributes set per field per the WHATWG autofill
  spec (`email`, `current-password`, `new-password`, `given-name`).
- Don't put the password reveal toggle inside the input element
  itself; it's a sibling button to keep the input a clean `<input>`.

## Fidelity rules (UAT checklist)

- [ ] Label is visible at all times (no floating-label pattern).
- [ ] Hit target ≥ 44dp (parent) / 56dp (kid).
- [ ] Focus ring renders on `:focus-visible`.
- [ ] Error state pairs border + icon + text (not border alone).
- [ ] Helper and error text share an `aria-describedby` target.
- [ ] Password reveal toggle is a `<button>` with `aria-label`,
      does not steal focus.
- [ ] Household code entry has 6 visible boxes, mono font, autocapitalize off.
- [ ] Required fields show `*` AND `aria-required="true"`.

## Anti-patterns (rework triggers)

- ❌ Label-as-placeholder (placeholder that disappears on focus).
- ❌ Floating label (extra cognitive load; not WCAG-friendly).
- ❌ Error state without text (red border alone is invisible to
  color-blind users).
- ❌ Helper text permanently visible next to errors (they fight for
  the same slot — show one or the other).
- ❌ A password field without `autocomplete`.