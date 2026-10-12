# Component: Avatar

> The kid's chosen character is the hero of the kid SPA. The avatar
> is everywhere the kid needs a moment of recognition. This component
> is used in parent SPA too (kid card, redemption row, device list)
> but never as decoration.

## Anatomy

```
     ╭───────────╮
    ╱      ◕      ╲
   │    happy    │
    ╲    face    ╱
     ╰───────────╯
        ↑
   radius: --ch-radius-avatar (pill → circle)
```

- Container is always a circle. The SVG inside is square and clipped
  to the circle. There is no rectangular variant in v1.
- Default source: one of 12 pre-shipped SVG characters (open question
  1 default). Photo upload is out of scope for v1.
- The ChoreHero emblem (`docs/design/components/...` lives in the app
  icon and empty-state illustrations. It is NOT a kid avatar.

## Sizes

| Size     | Diameter | Where                                                    |
|----------|----------|----------------------------------------------------------|
| `xs`     | 24dp     | Compact list rows (parent SPA: kid row in streak list).  |
| `sm`     | 32dp     | Device list, comment attribution.                        |
| `md`     | 40dp     | Inline metadata, table rows.                             |
| `lg`     | 56dp     | Default. Chore card, redemption row, balance card.       |
| `xl`     | 80dp     | Notification hero, redemption action banner.             |
| `hero`   | 96dp     | Streak milestone celebration, kid welcome screen.        |
| `kiosk`  | 160dp    | Kid SPA header (kiosk-style framing).                    |

Default = `lg` (56dp). Sizes larger than `lg` are reserved for
celebratory surfaces (US 54: avatar is the hero).

## Variants

| Variant      | Background                      | Notes                              |
|--------------|----------------------------------|------------------------------------|
| `default`    | transparent                      | SVG sits on the host surface.      |
| `tinted`     | `--ch-color-brand-violet-100`    | Reserved for kid SPA header.       |
| `ring`       | transparent + 3px brand-violet-500 ring | Used in celebratory + welcome. |
| `kiosk`      | `--ch-color-brand-violet-050`    | 160dp hero on kid SPA.              |

The ring variant pairs with the streak milestone and welcome screens
to give the avatar a stadium feel without competing imagery.

## States

| State        | How it's expressed                                          |
|--------------|--------------------------------------------------------------|
| Default      | Static SVG.                                                  |
| Hover (interactive) | Slight scale `1.0 → 1.04` (`--ch-duration-fast`).         |
| Pulse (celebration) | Subtle `scale 1.0 ↔ 1.05` 1.2s loop until modal closed. `prefers-reduced-motion: reduce` → no pulse. |
| Loading      | Renders a circular skeleton at the same diameter.            |

## Composition rules

- Avatar is always accompanied by an accessible name on screens
  where the kid's identity matters. Default `alt="[kid name]'s
  avatar"`. On parent SPA rows, the row's `aria-label` already names
  the kid; the avatar itself is decorative.
- Two avatars side-by-side: minimum 16dp gap (parent SPA devices
  list rows).
- Avatar + streak badge: badge sits at the bottom-right of the
  avatar (the only place a streak counter is allowed to attach to an
  avatar).

## Accessibility

- Decorative avatar: `alt=""` + `role="presentation"`.
- Identity avatar: `alt="[kid name]'s avatar"` + the hosting element
  carries the kid's name in text or `aria-label`.
- In a celebration, the avatar is announced first so a screen reader
  user knows whose moment it is.
- Color is not used to differentiate avatars (the SVG itself is the
  identifier); therefore no contrast pair applies.
- Hit target: when avatar is interactive (e.g. tapping opens the
  profile), pad to `--ch-touch-min` (56dp on kid SPA).

## What the 12 pre-shipped avatars look like

Briefs for the illustrators. Each is monochrome line + 2 fills,
hand-drawn organic lines (per `CONTEXT.md`). Diversity in skin tone,
hair, glasses, hat, and accessories — no gender markers. The set is
labelled, not numbered:

1. Bunny (light pink fill, long ears).
2. Fox (orange fill, white belly).
3. Robot (silver fill, antenna).
4. Astronaut (white suit, violet visor).
5. Pirate (red bandana, eye patch).
6. Wizard (blue robe, star on hat).
7. Cat (gray fill, whiskers).
8. Dinosaur (green fill, tiny arms).
9. Panda (black + white).
10. Superhero (yellow cape, violet mask).
11. Unicorn (white, rainbow mane).
12. Dragon (teal, friendly snout).

Names like "the bunny" or "your fox" are used in celebration copy.

## Fidelity rules (UAT checklist)

- [ ] Avatar is a circle, not a rounded rectangle.
- [ ] Avatar source is one of the 12 SVG files (no photo upload UI).
- [ ] Streak milestone avatar is `hero` (96dp) with `ring` variant.
- [ ] Avatar never appears smaller than the ChoreHero emblem on the
      same screen.
- [ ] Avatar always carries an accessible name on screens where the
      kid's identity matters.
- [ ] Celebration pulse does not fire on
      `prefers-reduced-motion: reduce`.

## Anti-patterns (rework triggers)

- ❌ An avatar placeholder that shows the ChoreHero emblem (it is
     the brand mark, not a kid identity).
- ❌ An avatar < 56dp on any kid SPA surface.
- ❌ A celebration screen that uses anything else (illustration,
     emoji) as the hero.
- ❌ Two celebrations running their own avatars in parallel.
