# Screen 00 — Marketing landing

> Unauthenticated entry point. Both desktop and mobile layouts. The
> page exists to convert a visitor into a sign-up; it is the only
> screen that is allowed to feel "loud" because the user has not
> committed to the app yet.

## User story

- US 1 (parent sign-up entry), US 2 (parent sign-in entry).
- Anonymous visitor; deep-link target `/` (parent SPA fallback when
  unauthenticated).

## Layout (desktop, ≥ 1024dp)

```
┌──────────────────────────────────────────────────────────────┐
│  ChoreHero   Features  How it works        Sign in | Sign up │
├──────────────────────────────────────────────────────────────┤
│ ┌────────────────────────────┐  ┌───────────────────────────┐ │
│ │  EYEBROW: For families     │  │                           │ │
│ │                            │  │                           │ │
│ │  Display headline          │  │   Hero illustration       │ │
│ │  "Your chores.             │  │   (kid + parent +         │ │
│ │   Your points.             │  │    tablet, flat vector)   │ │
│ │   Your rewards."           │  │                           │ │
│ │                            │  │                           │ │
│ │  Subhead (2-3 sentences)   │  │                           │ │
│ │                            │  │                           │ │
│ │  [ Get started ]           │  │                           │ │
│ │  [ I already have an acct ]│  │                           │ │
│ │                            │  │                           │ │
│ │  "Free to start…"          │  │                           │ │
│ └────────────────────────────┘  └───────────────────────────┘ │
├──────────────────────────────────────────────────────────────┤
│  Three-up feature row                                         │
│   Card 1   Card 2   Card 3                                   │
├──────────────────────────────────────────────────────────────┤
│  Footer with sign-in link                                     │
└──────────────────────────────────────────────────────────────┘
```

- Page background: `--ch-surface-app-parent`.
- Header: sticky, `--ch-surface-card`, height 64dp.
- Hero section: 2-column above 1024dp, single-column below.
- Feature row: 3 columns ≥ 1024dp; 1 column below 1024dp.
- CTA column: max-width 480dp.

## Layout (mobile, < 768dp)

```
┌──────────────────────────────┐
│ ChoreHero          ☰ menu    │
├──────────────────────────────┤
│                              │
│   Hero illustration          │
│   (kid + parent + tablet)    │
│                              │
│   "Your chores.              │
│    Your points.              │
│    Your rewards."            │
│                              │
│   Subhead text.              │
│                              │
│   [ Get started ]            │
│   [ I already have an acct ] │
│                              │
│   "Free to start…"           │
│                              │
│   Feature 1                  │
│   Feature 2                  │
│   Feature 3                  │
│                              │
│   Footer                     │
└──────────────────────────────┘
```

## Copy

| Element       | Copy                                                         |
|---------------|--------------------------------------------------------------|
| Brand mark    | ChoreHero (logo, violet ink on paper).                       |
| Eyebrow       | "For families".                                              |
| Headline      | "Your chores. Your points. Your rewards." (exact tagline from CONTEXT.md). |
| Subhead       | "A simple chores app that turns everyday tasks into points your kid can trade for rewards you pick." |
| Primary CTA   | "Get started".                                               |
| Secondary CTA | "I already have an account" → /sign-in.                      |
| Helper        | "Free to start. No card needed."                             |
| Feature 1     | "Pick from a clear list of chores. Kids tap to claim, then mark done." |
| Feature 2     | "Points show up the moment a chore is finished — and streaks reward every day in a row." |
| Feature 3     | "Choose rewards your kid actually wants. Approve redemptions in two taps." |

## Tokens used

- Background: `--ch-surface-app-parent`.
- Card surfaces: `--ch-surface-card`.
- Primary CTA: `--ch-color-brand-violet-700` (parent-side restraint rule, F-2.2).
- Secondary CTA: `--ch-color-brand-violet-600` outline (no fill).
- Headline: `--ch-text-display-lg`.
- Subhead: `--ch-text-body-lg`.
- Section gap: `--ch-space-section-gap`.
- Card padding: `--ch-space-card-padding`.

## Components used

- `<Nav variant="compact">` (top marketing nav — see `components/nav.md` parent-variant).
- `<Button variant="primary" size="lg">` for "Get started".
- `<Button variant="secondary" size="lg">` for sign-in.
- `<Card>` for the feature row.

## Hierarchy

- H1: tagline.
- H2: section headings ("Pick from a clear list", "Points show up…",
  "Choose rewards…").
- H3: card titles (none needed; features are single-line statements).

## Accessibility

- H1 is the headline; taglines must be the only H1.
- `<nav aria-label="Marketing">` for the top bar.
- `<main>` wraps the hero + features + footer.
- Skip link visible on focus; jumps to "main".
- Illustration is `aria-hidden="true"` (decorative).
- "I already have an account" is `<a>` not `<button>` (it's a link,
  not an action).
- Both CTAs reachable via Tab; primary first.
- Color contrast: violet on paper passes AA for the headlines; body
  uses ink_900.
- Reduced motion: the hero illustration is static; no animated
  elements.

## States

| State        | How                                                                    |
|--------------|------------------------------------------------------------------------|
| Default      | As above.                                                              |
| Loading      | The hero CTA shows the navigation pre-warmed; no skeleton (one screen). |
| Error        | If the marketing page fails to load CSS, the brand name renders in `system-ui` with violet ink. Acceptable degraded mode. |
| Signed-in    | A signed-in parent who lands here is auto-redirected to `/dashboard` by the parent SPA router. Not a UI state, but specified for implementer. |

## Composition rules

- The hero illustration IS the brand mark here. The ChoreHero emblem
  is allowed next to the brand name; it is NOT allowed next to a kid
  avatar (mascot rule, F-10).
- CTAs do not open sign-up in a modal; they navigate to dedicated
  routes (`/sign-up`, `/sign-in`).

## Fidelity rules (UAT)

- F-9.1: primary CTA above the fold on both desktop + mobile.
- F-2.2: parent-side palette; primary CTA is violet, no sunshine.
- F-3.3: layout breakpoints match.
- F-7.x: all a11y rules apply.

## Anti-patterns

- ❌ A modal for sign-up.
- ❌ A two-column hero on mobile.
- ❌ A mascot/character competing with the tagline for attention.
