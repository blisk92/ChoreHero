# Component: Chip / Badge

> Small status indicators: tags, counters, streak lengths, point
> values, status pills. Chips are interactive (toggle / dismiss);
> badges are display-only counters.

## Anatomy

### Chip (interactive)

```
┌──────────────────────────────┐
│ [icon] Label        [ × ]   │  ← dismiss optional
└──────────────────────────────┘
```

- Padding: `--ch-space-1` `--ch-space-3`.
- Radius: `--ch-radius-chip` (pill).
- Min height: 24dp (sm) / 32dp (md).
- Border: 1px when on the same color as surface; otherwise no border.

### Badge (display-only)

```
┌──────────┐
│   12     │  ← numeric or single short word
└──────────┘
```

- Min height: 18dp.
- Radius: `--ch-radius-chip`.
- Padding: 0 `--ch-space-2`.

## Variants (chip)

| Variant        | Background                  | Text           | Border          |
|----------------|------------------------------|----------------|------------------|
| `neutral`      | `--ch-surface-card`         | `--ch-text-secondary` | 1px `--ch-border-default` |
| `brand`        | `--ch-color-brand-violet-100` | `--ch-color-brand-violet-700` | none     |
| `success`      | `--ch-color-success-100`   | `--ch-color-success-600`  | none |
| `warning`      | `--ch-color-warning-100`   | `--ch-color-warning-600`  | none |
| `danger`       | `--ch-color-danger-100`    | `--ch-color-danger-600`   | none |
| `sunshine` (kid) | `--ch-color-accent-sunshine-200` | `--ch-color-neutral-ink-900` | none |

Default = `neutral`.

## Variants (badge)

| Variant         | Background                | Text              |
|-----------------|---------------------------|-------------------|
| `neutral`       | `--ch-color-neutral-ink-500` | `--ch-text-on-brand` |
| `brand`         | `--ch-color-brand-violet-600` | `--ch-text-on-brand` |
| `success`       | `--ch-color-success-600`  | `--ch-text-on-success` |
| `danger`        | `--ch-color-danger-600`   | `--ch-text-on-danger` |
| `sunshine` (kid)| `--ch-color-accent-sunshine-500` | `--ch-text-on-accent` |

Default = `brand`.

## Sizes

| Size   | chip font    | chip height | badge font     | badge height |
|--------|--------------|-------------|----------------|--------------|
| `sm`   | `--ch-text-label-sm` | 24dp | `--ch-text-label-sm` | 18dp |
| `md`   | `--ch-text-label-md` | 32dp | `--ch-text-label-md` | 22dp |

Default = `md`. Kid SPA defaults to `md` for chips and `md` for badges
(points badge uses 22dp).

## States (chip)

| State       | How it's expressed                                             |
|-------------|----------------------------------------------------------------|
| Default     | Variant base.                                                  |
| Hover       | Background one step deeper; transition `--ch-duration-fast`.   |
| Focus       | `--ch-focus-ring-shadow`.                                      |
| Active      | Background stays; subtle `translate(0 1px)` for tap feedback.  |
| Selected    | Filled variant (e.g. brand filled vs. brand outlined).         |
| Disabled    | 50% opacity; `aria-disabled="true"`; no hover effect.          |
| Removable   | × button visible; hover on × inverts to `danger` background.  |

## States (badge)

| State    | How it's expressed                                              |
|----------|------------------------------------------------------------------|
| Default  | Static.                                                          |
| Pulse    | Kid-side: 1s scale `1.0 → 1.08 → 1.0` once on increment. Used for points/inbox counters as instant feedback. |
| Hidden   | When count is 0, badge does not render. Do NOT show "+0".        |

## Composition rules

- Chips row: horizontal, `--ch-space-inline-gap` between chips. Wrap
  to multiple lines on small viewports.
- Badge placement: top-right of an icon, offset `(-4px, -4px)` when
  count > 0.
- A chip with `variant="sunshine"` is reserved for kid-side milestone
  tags (e.g. "7-day streak", "First reward"). No parent-side use.

## Accessibility

- Chip:
  - Interactive chip uses `<button type="button">` with visible text.
  - `aria-pressed="true"` when used as a toggle.
  - Dismissible chip: × button is focusable; `aria-label="Remove
    [chip label]"`.
  - Disabled chip: `aria-disabled="true"`.
- Badge:
  - Always paired with the host element's `aria-label` or visible
    text (e.g. the notification bell's `aria-label="Notifications,
    3 unread"`).
  - Numeric badges render the count, not "+"; a count of 99+ becomes
    "99+" and reserves a minimum 3-char width.
- Color is never the only signal: variant distinguishes via
  background + text + (when interactive) icon.
- Hit targets: chip must reach `--ch-touch-min` (44dp parent /
  56dp kid) when interactive. Pad with negative margins if the visible
  shape is smaller.

## Copy guidance

- Chips label the category, not the action ("Recurring", not "Mark
  recurring").
- No exclamation marks.
- Kid-side streak chip on kid SPA reads as `🔥 7-day streak`. The fire
  emoji is the only allowed emoji inside chips.

## Fidelity rules (UAT checklist)

- [ ] Chip uses tokens for background, text, radius, padding.
- [ ] Chip toggle variant renders correctly selected vs unselected.
- [ ] Dismiss icon has `aria-label`.
- [ ] Badge with count 0 is not rendered.
- [ ] Badge pulse does not fire on `prefers-reduced-motion: reduce`.
- [ ] Sunshined chip is only used on kid SPA, never on parent SPA.

## Anti-patterns (rework triggers)

- ❌ A chip longer than 3 words (use a tag row in a card instead).
- ❌ A badge that shows "0".
- ❌ A chip that doesn't reach the touch target min (silent a11y fail).
- ❌ A parent SPA chip using sunshine (palette restraint rule).
