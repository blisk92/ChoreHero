# Screen 18 — Kid streak milestone celebration

> US 27 (celebratory surface). Full-bleed overlay when the kid hits
> a 7-day or 30-day streak milestone. Avatar is the hero. The only
> screen allowed to combine Fraunces title + brand glow + ring
> avatar.

## User story

- US 27, US 42 (streak milestone notification).

## Trigger

- Streak reducer increments `current_length` to a milestone value
  (7 or 30 — defaults locked from open question 2). The kid SPA
  shows this overlay if active; otherwise the next open does.

## Layout

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│             ╭─────────────────────╮                          │
│            │   [avatar 96dp        │                          │
│            │    ring variant]       │                          │
│             ╰─────────────────────╯                          │
│                                                              │
│      H1: "Seven in a row!" (Fraunces, --ch-font-display-kid) │
│                                                              │
│      H2: "That's a streak on [chore name]."                   │
│                                                              │
│      "🔥 [N]-day streak" (chip, sunshine)                    │
│                                                              │
│      [ Awesome ]   [ Show me ]                               │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

- Full-bleed modal at `--ch-z-celebration`.
- Background: `--ch-surface-card-hero` (`--ch-color-brand-violet-600`),
  with a subtle radial spotlight centered behind the avatar.
- The ChoreHero emblem is NOT shown here (mascot rule: avatar is
  the hero).

## Copy

| Element          | Copy                                                    |
|------------------|---------------------------------------------------------|
| H1               | "[NumberInWords] in a row!" (e.g. "Seven in a row!")    |
| H2               | "That's a streak on [chore name]."                       |
| Streak chip      | "🔥 [N]-day streak"                                      |
| Awesome          | "Awesome"                                               |
| Show me          | "Show me [chore name]" → /today filtered to this chore |

## Tokens used

- Background: `--ch-surface-card-hero` with
  `--ch-shadow-modal` (radius `--ch-radius-card-hero` would be too
  big for full-bleed; the modal here has no border-radius, it's
  full screen).
- H1: `--ch-font-display-kid` (Fraunces), white, display-md size.
- Avatar: `variant="ring" size="hero"` (96dp + 3px ring).
- Streak chip: sunshine.
- Buttons: secondary fill (white on violet) for "Awesome" +
  primary (sunshine) for "Show me".

## Components used

- `<Avatar variant="ring" size="hero">`.
- `<Button variant="secondary" size="lg">` "Awesome".
- `<Button variant="primary" size="lg">` "Show me".
- `<Chip variant="sunshine">` streak.

## Hierarchy

- H1.
- H2.

## Tab order

1. "Awesome" (default focus).
2. "Show me".

## States

| State        | How                                                       |
|--------------|-----------------------------------------------------------|
| Entering     | Avatar scale 0.9 → 1.0; chip appears with delay; subtle confetti particles optional (no emoji — only SVG motif). |
| Visible      | As above.                                                  |
| Reduced motion | No entrance animation; static state.                    |
| On dismiss   | Modal closes; returns to previous screen; in-app notification chip also added. |
| Re-opened    | If dismissed, the milestone surfaces as a notification chip on the today screen until the kid taps "Awesome" on the chip. |

## Accessibility

- `role="dialog"`, `aria-modal="true"`, labelled by the H1.
- Focus moves to "Awesome" on open.
- `Esc` dismisses (closes the dialog).
- Avatar is announced first via the dialog label; alt text not used
  (decorative in context).
- Confetti / particles carry `aria-hidden="true"` if shown.

## Composition rules

- This is the ONLY surface allowed to combine Fraunces + brand
  glow + ring avatar.
- "Awesome" dismisses; "Show me" navigates to /today with the
  chore highlighted briefly.
- The chip in the notification strip persists for 24 hours
  regardless.

## Fidelity rules (UAT)

- F-10.1: avatar is hero.
- F-10.2: no ChoreHero emblem.
- F-3.10: hero radius used.
- F-2.5: Fraunces title only here.
- F-9.7: avatar 96dp, Fraunces.

## Anti-patterns

- ❌ Adding more than one avatar (no parent-child duet here).
- ❌ Adding the ChoreHero emblem.
- ❌ A second celebratory surface for the same milestone before 7
     days pass.
