# Component: Skeletons

> Loading placeholders rendered while a known-shape list or card is
> being fetched. Skeletons preserve layout so the empty state
> doesn't replace a real card with a different shape.

## Anatomy

Each skeleton is a tinted rectangle that matches the eventual real
component's bounding box exactly. There is no generic shimmer
placeholder — the skeleton is a copy of the component with text and
icons replaced by shimmer rectangles of matching size.

```
┌─────────────────────────────┐
│ ████████████                │ ← title placeholder (60% width)
│ ████████                    │ ← body line placeholder (40%)
│ ████████                    │
└─────────────────────────────┘
      ↑ radius matches the real surface
      ↑ background: --ch-surface-skeleton
```

- Background tint: `--ch-surface-skeleton` (a slightly darker variant
  of the parent paper).
- Shimmer overlay: linear gradient `--ch-surface-skeleton → paper →
  --ch-surface-skeleton`, animated `1.2s linear infinite` only when
  `prefers-reduced-motion: no-preference`.
- Border-radius: matches the surface it represents.

## Skeletons provided

| Skeleton            | Shape it pre-represents                               |
|---------------------|--------------------------------------------------------|
| `SkCard`            | Chore card, reward card, streak card                  |
| `SkChoreRow`        | Compact chore row in a list                          |
| `SkRewardRow`       | Reward row in a list                                 |
| `SkKidRow`          | Kid row in notification list                          |
| `SkBalanceHero`     | The points badge + streak counter on kid home        |
| `SkQRBlock`         | QR placeholder + code text in the link-device screen |
| `SkTableRow`        | Single table row, height 56dp                        |
| `SkNotificationRow` | Notification row, height 64dp                        |

Each skeleton preserves the host's padding and gaps exactly, so the
moment real data arrives the layout does not jump.

## Sizes

Each skeleton uses fixed bounding-box dimensions that match the real
component's max dimensions. Width is set via `width: 100%` of the
hosting element; the placeholder rectangles inside are sized as a
percent of that host so the shape is correct on every viewport.

## States

| State         | How it's expressed                                                |
|----------------|--------------------------------------------------------------------|
| Default        | Static shaded placeholder with shimmer overlay.                    |
| Reduced motion | Shimmer overlay removed; static shaded only.                       |
| Error          | Replaced by `EmptyState variant="error"`.                          |
| Empty          | Replaced by the appropriate `EmptyState` variant.                  |
| Done           | Crossfade to the real component over `--ch-duration-base`.         |

## Composition rules

- Multiple skeletons in a list: at most 5 visible at once. Beyond
  that, paginate or fall through to the empty state.
- A skeleton never renders inside a container that has real data;
  the loading path is whole-list, not per-row.
- A skeleton never blocks the UI; time out after 5s and swap to the
  empty state (with a "Still loading?" link that retries).
- Skeletons never include skeletons of skeletons (no nested
  placeholders).

## Accessibility

- Container has `aria-busy="true"` while the skeleton is visible.
- `aria-live="polite"` on the host region so the announcement is
  "Loading…" or "Chores loaded." on transition, never announces
  shape changes.
- The skeleton rectangles are `aria-hidden="true"`.
- Focus never moves into a skeleton; the user keeps their last focus
  context.

## Animation

Shimmer overlay:

```css
background: linear-gradient(
  90deg,
  var(--ch-surface-skeleton) 0%,
  var(--ch-color-neutral-paper-000) 50%,
  var(--ch-surface-skeleton) 100%
);
background-size: 200% 100%;
animation: skeletonShimmer 1.2s linear infinite;
```

When `prefers-reduced-motion: reduce`, the `animation` is removed
but the placeholder background stays (gives the user some signal that
content is coming).

## Fidelity rules (UAT checklist)

- [ ] Skeleton bounding box matches the real component's bounding
      box (no layout shift on load).
- [ ] Skeleton background uses the surface-skeleton token.
- [ ] Skeleton has `aria-busy="true"` on its host.
- [ ] Skeleton respects `prefers-reduced-motion: reduce` (no
      shimmer).
- [ ] Skeleton does not block focus.
- [ ] A skeleton never displays for longer than 5s without
      surfacing an error.

## Anti-patterns (rework triggers)

- ❌ A generic spinner in place of a shape-matching skeleton (causes
     layout shift).
- ❌ A skeleton that renders inside another skeleton.
- ❌ A skeleton that is announced as a single element to screen
     readers without `aria-busy`.
- ❌ A skeleton that lives forever (no timeout to error state).
