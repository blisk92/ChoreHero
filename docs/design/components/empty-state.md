# Component: Empty State

> Every screen that can show nothing must show this. Kid-side states
> are warm and pointed; parent-side states are functional with a
> single obvious next action.

## Anatomy

```
            ╭────────────────╮
           ╱                  ╲
          │     illustration   │      ← flat vector + hand-drawn
           ╲                  ╱         accent stroke, 96-128dp
            ╰────────────────╯

              Heading (1 line)

        Supporting copy (1 sentence, ≤ 16 words).

           [ Primary CTA ]
           [ Secondary link ]   ← optional, ≤ 1
```

- Container: vertical stack, centered, max-width 360dp parent /
  440dp kid.
- Vertical rhythm: illustration → 24dp → heading → 8dp → copy →
  24dp → CTA stack.

## Variants (tone)

| Variant       | Surface              | Voice     | Copy examples                                              |
|---------------|----------------------|-----------|-------------------------------------------------------------|
| `kid`         | `--ch-surface-app-kid` | Cheerful | "No chores yet. Ask a grown-up to add some."                |
| `kid-welcome` | `--ch-color-brand-violet-050` | Cheerful | "Welcome, [name]! 👋"                                  |
| `parent`      | `--ch-surface-app-parent` | Functional | "No chores yet. Add your first chore to get started."  |
| `parent-rewards` | `--ch-surface-app-parent` | Functional | "Add your first reward. Examples: 30 min screen time." |
| `error`       | `--ch-surface-card`  | Direct    | "Something went wrong. Try again?"                          |
| `offline`     | `--ch-surface-card`  | Direct    | "You're offline. Changes will sync when you're back online." |

## Illustration library

Each empty-state variant maps to a pre-drawn illustration path:

| Variant          | Illustration cue                              |
|------------------|-----------------------------------------------|
| `kid`            | Empty basket / folded towel — chores absent.  |
| `kid-welcome`    | Big waving hand + sparkles.                   |
| `parent`         | Open notebook with a single page.             |
| `parent-rewards` | Wrapped gift box, ribbon untied.              |
| `error`          | Cloud with a single raindrop.                 |
| `offline`        | Plug with a small "x" through it.             |

All illustrations are SVG, monochrome, hand-drawn line + 2 fills.
Kid illustrations carry one warm fill (`--ch-color-accent-sunshine-200`)
inside an otherwise violet line drawing.

## Sizes

The illustration scales with the container:

| Surface  | Illustration size | Heading token          | Body token         |
|----------|-------------------|------------------------|--------------------|
| Kid SPA  | 128dp             | `--ch-text-title-lg` (Fraunces on welcome, Inter otherwise) | `--ch-text-body-lg` |
| Parent SPA | 96dp            | `--ch-text-title-md`   | `--ch-text-body-md` |

## States

| State             | How it's expressed                                       |
|-------------------|-----------------------------------------------------------|
| Default           | Static.                                                   |
| Loading initial   | Skeleton cards in place of the empty state for ≤ 1.2s; transition to empty state after. |
| Error during fetch | Same illustration as `error` variant + retry link.       |
| First-run (parent first chore / first reward) | Reuses `parent` variant but the heading copy is "Add your first chore." / "Add your first reward." |

## Composition rules

- One primary CTA per empty state. Secondary link is optional
  (`Learn how chores work` parent / `Tap the bell to ask a grown-up`
  kid).
- CTAs never repeat a control that's already in the page chrome
  (e.g. an empty-state CTA inside the parent SPA dashboard should
  not duplicate the "Add chore" tab if a tab bar exists; instead
  the illustration invites the user to use the existing control).
- Empty state for a list shows the same shape as a real list row
  would (same radius, same padding); it just sits where the row
  would have been, so the layout is preserved when items return.

## Accessibility

- Container has `role="region"` + `aria-labelledby` pointing to the
  heading.
- Heading is a real `<h2>` (or appropriate level for the page).
- Illustration: `aria-hidden="true"`; do not announce decorative
  imagery.
- Primary CTA inherits the focus style of a button. Focus must
  NOT auto-move to the CTA; the user must opt in via Tab.
- Copy must be in the language of the surface (kid voice vs. parent
  voice), and never assume prior context.

## Copy guidance

| Surface        | Heading examples                                          |
|----------------|------------------------------------------------------------|
| Kid no-chores  | "No chores yet."                                          |
| Kid welcome    | "Welcome, [name]!"                                        |
| Parent chores  | "No chores yet." (CTA: "Add your first chore")            |
| Parent rewards | "No rewards yet." (CTA: "Add your first reward")          |
| Error          | "Something went wrong."                                   |
| Offline        | "You're offline."                                         |

Sentence case, no exclamations on parent side. Kid side may use one
emoji at most (👋 / 🎉 / 🔥 / ⭐), only on celebration moments, not
on every empty state.

## Fidelity rules (UAT checklist)

- [ ] Empty state appears within ≤ 1.2s of the underlying list
      resolving to zero.
- [ ] Illustration is one of the documented variants, not a stock
      graphic.
- [ ] Heading is rendered as the appropriate heading level.
- [ ] Single primary CTA; secondary link is optional and rare.
- [ ] Empty state copy matches the documented voice for the surface.
- [ ] Welcome empty state uses Fraunces for the heading.
- [ ] Error empty state has an aria-live="polite" wrapper on the
      retry link so screen readers announce the retry availability.

## Anti-patterns (rework triggers)

- ❌ Two CTAs of equal weight (creates ambiguity, contradicts the
     whole point of an empty state).
- ❌ An empty state that disappears the moment the data starts
     loading (causes layout flash; show skeleton first).
- ❌ A photo-realistic illustration (palette restraint rule).
- ❌ An empty state whose illustration competes with the kid avatar
     on a celebratory surface.
