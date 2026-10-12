# Component: Button

> Primary, secondary, ghost, and intent buttons. Kid SPA and parent SPA
> share the same component; the surrounding context (color, voice)
> drives the variant.

## Anatomy

```
┌─────────────────────────────────────────┐
│  [icon_left]  Label text   [icon_right] │
└─────────────────────────────────────────┘
        ↑ hit target ≥ min-touch (56dp kid / 44dp parent)
        ↑ height = 40dp (default) | 48dp (lg) | 56dp (xl, kid)
```

- Min hit target: `--ch-touch-min` (44dp) on parent surfaces;
  `--ch-touch-min-kid` (56dp) on kid surfaces.
- Padding: `--ch-space-touch-target-padding` vertical,
  `--ch-space-5` horizontal.
- Radius: `--ch-radius-button`.
- Border: 1px (secondary / ghost only); 0 for primary.

## Variants

### Primary (`variant="primary"`)

The dominant action of a screen or section. One per view (parent
SPA) or one per visible card (kid SPA).

| Surface | Background | Text | Shadow | Notes |
|---|---|---|---|---|
| Parent SPA | `--ch-color-brand-violet-700` | `--ch-text-on-brand` | `--ch-shadow-card-resting` | Restrained. |
| Kid SPA | `--ch-color-accent-sunshine-500` | `--ch-text-on-accent` | `--ch-shadow-cta-primary` | The brand glow. Yellow on violet wash reads instantly. |

- Hover: lift to `--ch-shadow-card-hover`; background lightens by one
  step (violet → 600, sunshine → 400).
- Focus: `--ch-focus-ring-shadow`.
- Active/pressed: shadow scale to `--ch-shadow-card-resting`,
  translate `0 1px`, transition `--ch-duration-fast`.

### Secondary (`variant="secondary"`)

Used for sibling actions, secondary CTAs in a stack, and form
"Cancel" buttons.

- Background: `--ch-surface-card`.
- Border: 1px `--ch-border-default`.
- Text: `--ch-text-primary`.

- Hover: background `--ch-surface-skeleton`; border `--ch-border-strong`.
- Focus / active: same as primary.

### Ghost (`variant="ghost"`)

Used for low-emphasis actions inside lists and tables (e.g. "Skip",
"Edit", "View").

- Background: transparent.
- Text: `--ch-text-link` (parent) / `--ch-color-brand-violet-700` (kid).
- Hover: background `--ch-color-brand-violet-050` (kid) /
  `--ch-surface-skeleton` (parent).

### Intent (`variant="approve" | "deny" | "reverse" | "complete" | "skip"`)

Reserved for actions whose outcome is structurally meaningful
(approve/deny/redemptions). Always reads as `variant="primary"` on
parent SPA (full saturation), but maps to the intent color tokens:

| Intent token | Background | Text |
|---|---|---|
| approve / complete | `--ch-color-success-600` | `--ch-text-on-success` |
| deny | `--ch-color-danger-600` | `--ch-text-on-danger` |
| reverse | `--ch-color-brand-violet-500` | `--ch-text-on-brand` |
| skip | `--ch-color-neutral-ink-500` | `--ch-text-on-brand` |

## Sizes

| Size | token | height | font | usage |
|---|---|---|---|---|
| `sm` | `--ch-space-7` (32dp) | 32dp | `--ch-text-label-md` | Inline row actions, table buttons. Min 44dp hit target must still be enforced via padding, not visual height. |
| `md` (default) | `--ch-space-9` (48dp) | 40dp | `--ch-text-label-lg` | Standard form / dialog actions. |
| `lg` | `--ch-space-10` (64dp) | 48dp | `--ch-text-title-sm` | Parent SPA hero CTAs. |
| `xl` (kid only) | `--ch-space-10` (64dp) | 56dp | `--ch-text-title-md` | Kid primary CTA (claim, done, redeem). |

> The `sm` size visually renders at 32dp but must pad to 44dp hit
> target. The CSS sets `min-height: var(--ch-touch-min)`.

## States

| State | How it's expressed |
|---|---|
| Default | Variant base style. |
| Hover | Color step up; shadow step up; transition `--ch-duration-fast`. |
| Focus-visible | `--ch-focus-ring-shadow`. Only on `:focus-visible` (keyboard). |
| Active/pressed | Shadow back to resting; `translate(0 1px)`. |
| Disabled | `aria-disabled="true"`; background → `--ch-surface-skeleton`; text → `--ch-text-disabled`; cursor `not-allowed`; click suppressed. |
| Loading | Inline spinner (16dp) replaces icon_left; label stays; `aria-busy="true"`; click suppressed. |
| Success (post-action) | Optional 1.5s green checkmark, then reverts. Used for "Claim" and "Done" on kid SPA to give instant visual reward. |

## Iconography

- Icons inside buttons: 16dp (`md`), 20dp (`lg`), 24dp (`xl`).
- Icon-only buttons: round, square hit target (`--ch-touch-min`),
  1 icon size step. `aria-label` is required.
- No icon-only buttons on the kid SPA primary surface — kids may not
  parse icons reliably. Always show label + icon.

## Copy guidance

- Parent: "Save", "Add chore", "Approve", "Deny", "Reverse",
  "Regenerate code". Imperative, plain. No exclamation marks.
- Kid: "Claim it", "Skip", "Done", "Yes please", "Not yet". Second
  person. Cheerful but short (1–3 words).
- Loading copy: parent "Saving..."; kid "Saving your chores..." (one
  place only; reuse elsewhere as "Just a sec...").

## Accessibility

- Semantic element: `<button type="button">`. Use `<a>` styled as a
  button ONLY when the action is a navigation.
- `aria-disabled` (not the HTML `disabled` attribute) so screen
  readers announce the disabled state consistently with our loading
  pattern.
- `aria-busy="true"` during loading.
- `aria-label` overrides visible text only when the visible text
  is ambiguous (e.g. icon-only).
- Focus ring is always visible on `:focus-visible`. Never removed.
- Color is never the only signal: every intent variant pairs the
  color with an icon AND label.
- Touch target meets the surface-specific minimum (44dp parent /
  56dp kid / 64dp kid primary).

## Fidelity rules (UAT checklist)

- [ ] Background uses a token, not a hex literal.
- [ ] Hit target meets surface-specific minimum even at `sm` size.
- [ ] Focus ring renders on `:focus-visible` and passes contrast
      against the button background.
- [ ] Disabled button has `aria-disabled="true"` AND a visible style
      change AND `cursor: not-allowed`.
- [ ] Loading button has visible spinner AND `aria-busy="true"`.
- [ ] Kid SPA primary CTAs are yellow (`--ch-color-accent-sunshine-500`)
      with `--ch-shadow-cta-primary` glow.
- [ ] Parent SPA primary CTAs are violet (`--ch-color-brand-violet-700`),
      NO sunshine glow.
- [ ] No exclamation marks in any button label.
- [ ] Icon-only buttons have `aria-label`.

## Anti-patterns (rework triggers)

- ❌ A screen with two `variant="primary"` buttons visible at the same
  time (except parent SPA dialogs with explicit "Save" + "Cancel"
  pair where Cancel is `secondary`).
- ❌ A kid SPA button without a label.
- ❌ A button that uses a hard-coded color outside the intent tokens.
- ❌ A button whose loading state hides the label (accessibility
  failure; screen reader announces "button" only).
- ❌ A button that wraps a custom `<div>` instead of using
  `<button>`.