# Component: Card

> The single most-used primitive. Used for chores, rewards,
> redemptions, kid dashboard tiles, parent dashboard sections.

## Anatomy

```
┌─────────────────────────────────────┐
│                                     │
│   [header / title row]              │
│                                     │
│   [body content]                    │
│                                     │
│   [footer / actions]                │
│                                     │
└─────────────────────────────────────┘
```

- Background: `--ch-surface-card` (white).
- Radius: `--ch-radius-card` (16dp).
- Shadow: `--ch-shadow-card-resting`.
- Padding: `--ch-space-card-padding` (16dp).
- Border: 1px `--ch-border-default` ONLY when used inside a tinted
  parent (e.g. inside the rewards page hero card). Default: no border
  on white-on-paper contexts.

## Variants

### Standard (parent SPA + general)

- Background: `--ch-surface-card`.
- Shadow: `--ch-shadow-card-resting`.
- Padding: 16dp.
- Optional 1px `--ch-border-default` if the card sits on a
  `--ch-surface-skeleton` background.

### Tinted (kid SPA, "Available Extras" list)

- Background: `--ch-color-brand-violet-100`.
- No border. No shadow.
- Soft visual lift instead of a hard border; kid SPA leans into
  wash-of-color more than shadow.

### Hero (kid SPA, parent SPA redemption celebration)

- Background: `--ch-surface-card-hero` (violet_600) or
  `--ch-color-accent-sunshine-500`.
- Text: `--ch-text-on-brand` or `--ch-text-on-accent`.
- Radius: `--ch-radius-card-hero` (24dp).
- Shadow: `--ch-shadow-3` (modal-class) — bigger lift.
- Padding: 24dp.
- Optional hero icon / avatar 96dp centered top.

### Interactive (chore card on kid SPA — tap to claim)

- All Standard rules PLUS:
  - Hover: shadow → `--ch-shadow-card-hover`, transform `translateY(-1px)`.
  - Active: shadow back to `--ch-shadow-card-resting`,
    transform `translateY(0)`.
  - Cursor: `pointer`.
  - `<button>` element wrapping the card OR `<article>` with a
    separate inner button — never a click handler on a `<div>`.

## Layout slots

A card has 4 slots, any combination may be used:

1. **header** — title + subtitle (e.g. "Make bed" + streak pill).
2. **media** — optional (avatar for kid card; not used for chore cards).
3. **body** — description, metadata, list of items.
4. **footer** — actions row, footer status text.

Default rendering:
- Header: `--ch-text-title-md`, color `--ch-text-primary`.
- Subtitle: `--ch-text-body-sm`, color `--ch-text-tertiary`.
- Body: `--ch-text-body-md`.
- Footer: `--ch-text-body-sm` + action buttons (`sm` size).

## States (interactive variant)

| State | Visual | Notes |
|---|---|---|
| Resting | shadow_1 | |
| Hover | shadow_2, +1dp lift | On pointer devices only; touch tap goes directly to active. |
| Focus | focus ring on the wrapping button | |
| Active/pressed | shadow_1, translateY(0) | |
| Disabled | `--ch-surface-skeleton` background, `--ch-text-disabled` | e.g. an out-of-stock reward. |
| Loading | skeleton inside body slot | Used while the card is fetching detail. |
| Success | brief 1.5s `--ch-color-success-100` background wash | Used after a kid taps "Done" to give instant confirmation. |

## Composition rules

- Do NOT nest cards. A card inside a card collapses to a flat list.
- Inside a card, use the spacing tokens, not raw px.
- A grid of cards uses `--ch-space-3` gap (mobile) or `--ch-space-4`
  gap (desktop ≥ 768dp).
- A card row in a list uses the same card visual but with smaller
  padding (`--ch-space-card-padding-compact`).

## Examples (visual recipes)

### Chore card — kid SPA "Available Extras"

```
┌─────────────────────────────────────┐
│  🔁  Make bed                       │
│      5 pts                          │
│      🔥 4 day streak                │
└─────────────────────────────────────┘
```

- Tinted variant.
- Left: kind icon (`🔁` recurring / `⭐` one-off) 24dp.
- Title: `--ch-text-title-sm`, `--ch-text-primary`.
- Points: `--ch-text-body-sm`, `--ch-text-tertiary`.
- Streak pill: chip variant (see `chip-badge.md`), only when
  `streak.current_length >= 1`.
- Wrapping element: `<button type="button">` for tap-to-claim.
- Hit target: full card, minimum 72dp tall.

### Reward card — kid SPA "Redeem"

```
┌─────────────────────────────────────┐
│  [icon]                             │
│       30 min screen time            │
│       50 pts                        │
│                                     │
│       [Redeem] (primary CTA, full width)│
└─────────────────────────────────────┘
```

- Tinted variant.
- Reward icon 32dp, centered above title (flat-vector, parent-curated).
- Title: `--ch-text-title-sm`.
- Cost: `--ch-text-body-md`, color `--ch-text-secondary`.
- CTA: variant=primary, size=xl, full width.
- Disabled state when `stock_remaining == 0`: button label "Out of
  stock", `aria-disabled="true"`, no opacity reduction.

### Chore card — parent SPA list

```
┌─────────────────────────────────────┐
│  ☐  Make bed                        │
│      Recurring · 5 pts · review ⏳   │
│      🔥 4 day streak (best: 12)     │
└─────────────────────────────────────┘
```

- Standard variant.
- Selection checkbox on the left (parent multi-select for bulk
  edit/delete).
- Title row right-aligned: `⋮` menu (Edit / Delete).
- Metadata line: kind, points, review flag indicator (`⏳` icon).
- Streak line: only when streak > 0.

### Reward card — parent SPA list

```
┌─────────────────────────────────────┐
│  30 min screen time                 │
│  50 pts · stock: unlimited          │
│                          [Edit] [✕] │
└─────────────────────────────────────┘
```

- Standard variant, padding 12dp (compact).
- Title row + metadata row + actions.
- Stock indicator: chip ("Unlimited" / "12 left").

## Accessibility

- Static cards: `<article>` or `<section>` with the appropriate
  heading level inside.
- Interactive cards: `<button>` (the entire card) OR `<div
  role="button" tabindex="0">` with explicit keyboard handling.
  Prefer the `<button>` element.
- Card title uses a heading tag (`<h2>` / `<h3>` depending on page
  hierarchy). Do not skip heading levels.
- Disabled interactive cards still render as `<button
  aria-disabled="true">` (not the HTML `disabled` attribute, so the
  screen reader announces the card and its state).
- Card focus ring renders on the wrapping interactive element, not
  on a child button inside the card.

## Fidelity rules (UAT checklist)

- [ ] Background, radius, shadow, and padding use the token names
      from this spec, not hex / px.
- [ ] Tinted cards never have a border or shadow; standard cards
      rest on `--ch-shadow-card-resting`.
- [ ] Hero cards use `--ch-radius-card-hero` and
      `--ch-shadow-modal`.
- [ ] Interactive cards wrap content in `<button>` (no `<div
      onclick>`).
- [ ] Disabled interactive cards use `aria-disabled="true"` (not
      HTML `disabled`).
- [ ] Cards in a grid use `--ch-space-3` or `--ch-space-4` gap.
- [ ] No nested cards.
- [ ] Card title uses a heading tag in document order.

## Anti-patterns

- ❌ A `<div>` with `@click` and no role/keyboard handler.
- ❌ Card with `box-shadow: 0 0 12px rgba(...)` ad-hoc.
- ❌ A card whose hit area is smaller than the visual card (the
  whole card must be tappable on kid SPA).
- ❌ A "card" that is just a `<section>` with no border, no
  shadow, and no surface change — that's a section header, not
  a card.
- ❌ Cards inside cards.