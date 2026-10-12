# Component: Toast

> Short-lived feedback after a mutation. Kid SPA gets upbeat
> confirmation; parent SPA gets plain-but-direct confirmation. No
> toast in this app collects the user's attention for more than a few
> seconds — anything important belongs in the notification list.

## Anatomy

```
┌───────────────────────────────────────┐
│ [icon] Title text                     │
│        Optional supporting line.       │
└───────────────────────────────────────┘
   ↑ width: 320dp parent / full-width-32dp-from-edges kid
   ↑ radius: --ch-radius-toast
   ↑ shadow: --ch-shadow-toast
```

- Padding: `--ch-space-3` `--ch-space-4` (compact); `--ch-space-4`
  `--ch-space-5` (with supporting line).
- Position:
  - Parent SPA: top-right, 16dp from edges, stacked.
  - Kid SPA: top-center, 12dp from top, full-width minus 32dp, single
    visible at a time.
- Z-index: `--ch-z-toast`.
- Auto-dismiss: 4s default; 6s if a supporting line is present; never
  exceeds 8s.

## Variants (intent)

| Variant         | Background                | Icon            | Title text             |
|-----------------|---------------------------|-----------------|------------------------|
| `success`       | `--ch-color-success-100`  | ✓ (success_600) | Success_600            |
| `info`          | `--ch-surface-card`       | ⓘ (info_600)    | Info_600               |
| `warning`       | `--ch-color-warning-100`  | ⚠ (warning_600) | Warning_600            |
| `danger`        | `--ch-color-danger-100`   | ✕ (danger_600)  | Danger_600             |
| `celebrate`     | `--ch-surface-card-hero`  | avatar (24dp)   | `--ch-text-on-brand`   |

The `celebrate` variant is reserved for kid-side post-action feedback
after "Done" (when chore is non-review-flagged and points are awarded
immediately) or after a redemption request is sent. Uses
`--ch-font-display-kid` for the title to add warmth without losing
clarity.

## Sizes

| Size   | Title token           | Supporting token    |
|--------|-----------------------|---------------------|
| `md`   | `--ch-text-label-lg`  | `--ch-text-body-sm` |
| `lg`   | `--ch-text-title-sm`  | `--ch-text-body-md` |

Default = `md`. Use `lg` only for celebrate variant.

## States

| State       | How it's expressed                                                      |
|-------------|--------------------------------------------------------------------------|
| Entering    | Slide in + fade (`--ch-duration-slow`, `--ch-easing-emphasized`).        |
| Visible     | Static.                                                                  |
| Hovering    | Pause auto-dismiss while `:hover` or `:focus-within` (desktop parent).   |
| Dismissing  | Slide out + fade (`--ch-duration-base`, `--ch-easing-exit`).             |
| Paused (kid)| Tap to dismiss (kid SPA); no auto-dismiss for `danger` toasts.           |

## Animation

- Enter: `translateY(-8px) → 0`, opacity `0 → 1`.
- Exit: `translateY(0 → -8px)`, opacity `1 → 0`.
- Respect `prefers-reduced-motion`: clamp durations to 0ms; fade only.

## Copy guidance

- Title: 1 line, ≤ 6 words.
- Supporting line: optional, ≤ 12 words. Use only when the outcome
  needs a second beat (e.g. "Approved! Points have been added.").
- Parent voice: direct, no exclamation.
- Kid voice: at most one celebratory phrase per milestone.
  Toast titles: "Nice work!" "Saved." "Sent to a grown-up."
- Errors are warm-but-clear on the kid side ("Hmm, that didn't
  work. Try again?"), direct on the parent side ("Couldn't save
  the chore.").

## Accessibility

- `role="status"` for success/info/celebrate; `role="alert"` for
  warning/danger.
- `aria-live="polite"` for status, `"assertive"` for alert.
- Each toast has a visible dismiss button on the parent SPA
  (`aria-label="Dismiss notification"`). On the kid SPA, dismiss is
  implicit (tap toast).
- Focus must NOT move into the toast; toasts are an out-of-band
  channel. Exception: the parent SPA includes a focusable action in
  the toast only when there is exactly one obvious follow-up (e.g.
  "Undo" on a destructive action); in that case toast takes
  `role="alertdialog"`.
- Color is never the only signal: icon + title text accompany the
  background.
- Touch targets: 44dp on the dismiss button (parent), the full toast
  is the hit target on the kid SPA.

## Composition rules

- Stack limit: 3 visible at once (parent); 1 at a time (kid).
- A new celebrate toast replaces any visible celebrate toast.
- A danger toast does NOT replace a visible info toast; danger is
  queued and shown when the queue clears.
- Closing one toast does not dismiss the others.

## Fidelity rules (UAT checklist)

- [ ] Toast uses token values for color, padding, radius, shadow.
- [ ] Toast position matches the surface (top-right parent,
      top-center kid).
- [ ] Toast auto-dismisses within 8s.
- [ ] Danger toast shows the retry-able affordance on parent SPA
      (`"Try again"` link).
- [ ] A danger toast is never replaced by a non-danger one before
      it expires.
- [ ] Toast does not steal focus from the active element.
- [ ] `role` and `aria-live` correctly distinguished per intent.
- [ ] `prefers-reduced-motion: reduce` clamps the entrance to a fade
      with no translation.

## Anti-patterns (rework triggers)

- ❌ A toast that requires user action to make sense (use a modal).
- ❌ A toast that lives longer than 8s.
- ❌ A toast without a `role`.
- ❌ Multiple stacked toasts with the same intent on screen at once.
- ❌ A toast whose title is the same as the underlying button label
      (creates echo effect).
