# Screen 15 — Kid welcome

> US 9, US 53. The first screen the kid sees when they open the
> kiosk after the parent has linked this device and before any
> chore has been added. Hero avatar, celebratory tone, one tap to
> the Today screen (which will then show the empty state).

## User story

- US 9 (kid welcome on first launch).
- US 53 (kid first-link welcome).

## Route

- `/` (kid SPA) when the kid device is freshly linked and `Chore`
  count is 0 in either pool.

## Layout (single column, full-width)

```
┌──────────────────────────────────────────────────────────────┐
│         ← (no nav; this is the welcome)                        │
│                                                              │
│                  ╭─────────────────────╮                     │
│                 │                       │                    │
│                 │     [avatar 160dp]    │                    │
│                 │                       │                    │
│                  ╰─────────────────────╯                     │
│                                                              │
│            H1: "Welcome, [name]! 👋"                          │
│            (Fraunces, --ch-font-display-kid)                  │
│                                                              │
│            Body: "Let's find you something to do."            │
│                                                              │
│            [ Let's go ]   ← primary CTA (kid yellow)         │
│                                                              │
│              (small ChoreHero emblem at the bottom,           │
│              color − not competing with the avatar.)          │
└──────────────────────────────────────────────────────────────┘
```

## Copy

| Element     | Copy                                                          |
|-------------|---------------------------------------------------------------|
| H1          | "Welcome, [name]! 👋" (Fraunces, exception per F-2.5)        |
| Body        | "Let's find you something to do."                              |
| CTA         | "Let's go"                                                    |
| Emblem line | "ChoreHero"                                                   |

## Tokens used

- Background: `--ch-surface-app-kid` (`--ch-color-brand-violet-050`).
- Card-less; the whole surface is the welcome zone.
- Avatar: `variant="ring" size="kiosk"` (160dp, violet ring).
- CTA: `<Button variant="primary" size="xl">`, sunshine background,
  ink text, `--ch-shadow-cta-primary`.
- H1 font: `--ch-font-display-kid`.
- Emblem: filled violet, ink text, used as a quiet "ChoreHero" wordmark.

## Components used

- `<Avatar variant="ring" size="kiosk">`.
- `<Button variant="primary" size="xl">`.
- (No nav; no bottom bar visible — `Let's go` IS the navigation.)

## Hierarchy

- H1.

## Tab order

1. (Avatar not focusable.)
2. "Let's go" CTA (primary).

## States

| State              | How                                                  |
|--------------------|------------------------------------------------------|
| Default            | As above.                                            |
| Empty pool auto    | The moment any chore exists, this screen is auto-replaced by Screen 16 or the kid's empty state (Screen 22). |
| Reduced motion     | Avatar static; CTA pulse disabled.                   |

## Accessibility

- H1 is the page's only heading.
- "Let's go" is a `button` whose accessible name is the visible
  label.
- The avatar is decorative (`alt=""`) since the H1 names the kid.
- The 👋 emoji is rendered as text (no animation; not announced as
  emoji specifically — screen readers pronounce it as "waving
  hand"). The aria-label may append "wave" but the visible text is
  authoritative.

## Composition rules

- This screen is reachable ONLY when the kid has zero chores across
  both pools. Once any chore exists, the route is auto-redirected.
- The ChoreHero emblem is allowed here BECAUSE there is no avatar-
  chore collision. The mascot rule (F-10.2) says "next to a kid
  avatar" — the emblem is below the avatar, not adjacent; document
  this exception.
- When the kid taps "Let's go", they go to `/today`.

## Fidelity rules (UAT)

- F-9.4: avatar at kiosk size, ring variant.
- F-2.5 + F-4.4: Fraunces title.
- F-10.x: emblem placement (below, not adjacent).

## Anti-patterns

- ❌ Showing a settings gear or back button on welcome (it's a
     hello, not a destination).
- ❌ Any interactive control below the avatar except the primary
     CTA.
