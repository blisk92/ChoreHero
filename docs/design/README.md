# ChoreHero v1 — Frontend Design Package

> The artifact the frontend developer implements against and the UAT
> engineer verifies against. If a screen isn't covered here, it isn't
> ready to ship.

## What's in here

```
docs/design/
  README.md              # this file (orientation + fidelity rules summary)
  fidelity-rules.md      # UAT verification spec (every check named)
  a11y.md                # WCAG 2.1 AA patterns + keyboard contract
  tokens/
    tokens.json          # source of truth (machine-readable)
    tokens.css           # CSS custom properties (consumed by Vue components)
  components/            # one spec per shared UI primitive
    button.md
    input.md
    select.md
    textarea.md
    checkbox-radio.md
    card.md
    nav.md
    modal.md
    table.md
    toast.md
    chip-badge.md
    avatar.md
    empty-state.md
    skeletons.md
  screens/               # annotated wireframes per user-story screen
    00-marketing.md
    01-parent-sign-up.md
    02-parent-sign-in.md
    03-parent-dashboard.md
    04-child-profile-modal.md
    05-link-kid-device.md
    06-kid-devices-list.md
    07-parent-chores.md
    08-chore-editor.md
    09-parent-rewards.md
    10-reward-editor.md
    11-parent-redemption-queue.md
    12-redemption-action-modal.md
    13-parent-notifications.md
    14-push-opt-in.md
    15-kid-welcome.md
    16-kid-today.md
    17-kid-redeem.md
    18-kid-streak-milestone.md
    19-kid-points-detail.md
    20-kid-notifications.md
    21-parent-settings.md
    22-empty-states.md
  flows/                 # interaction notes for non-trivial flows
    kid-claim-complete.md
    parent-review-approval.md
    parent-redemption-approve-deny-reverse.md
    offline-replay-sync.md
    push-opt-in.md
    deadline-expiry.md
```

## How to use this package

**Frontend developer:**
1. Wire `tokens/tokens.css` into the global stylesheet (do not duplicate
   values in component `<style scoped>`).
2. Implement shared primitives by reading the matching
   `components/<name>.md` and ONLY that file. If a state is missing,
   flag it; do not invent.
3. Implement screens by reading `screens/<id>.md`. Each wireframe names
   the exact token the layout relies on (e.g. "card uses
   `--ch-surface-card` + `--ch-radius-card`").
4. For non-trivial flows, read `flows/<name>.md` BEFORE writing the
   component, not after.

**UAT engineer:**
1. Run through `fidelity-rules.md`. Every check is keyed back to a
   token or component spec, so a failure is unambiguous.
2. Cross-check any visual decision against `tokens/tokens.json` —
   the JSON file is authoritative if there is ever a conflict with
   the CSS file.

## Decision ownership (locked by the designer)

These are decisions made by the designer that downstream lanes must
not re-decide. Each is justified; push back on the justification, not
the choice.

| Decision | Value | Rationale |
|---|---|---|
| Primary typeface | Inter (system fallback) | Crisp at small sizes; free; ships everywhere. |
| Kid celebratory typeface | Fraunces (serif) | Adds storybook warmth to milestones without going "cute". |
| Kid SPA background | `--ch-color-brand-violet-050` | Soft violet wash differentiates the kid's space from the parent's neutral paper. |
| Parent SPA background | `--ch-color-neutral-paper-050` | Quiet; "parent's phone is not a toddler's toy" (US 55). |
| Accent / CTA color on kid side | sunshine yellow on violet | Highest perceptual pop; aligns with `CONTEXT.md`. |
| Accent / CTA color on parent side | violet on paper | Restrained; matches "quiet accents". |
| Avatar shape | circle, 56dp default, 96dp hero | Mascot rule (US 54): avatar is always the hero. |
| Avatar set (v1) | 12 pre-shipped SVG (default, open question 1) | Avoids upload pipeline + moderation work in v1. |
| Streak milestone list | {7, 30} days (open question 2 default) | Spec calls out both; not configurable in v1. |
| Touch target (kid) | ≥ 56dp, primary CTAs ≥ 64dp | Children need larger hit targets than adults. |
| Touch target (parent) | ≥ 44dp (WCAG 2.5.5 AAA) | Standard. |
| Modal pattern | Centered, max-width 480dp on mobile / 560dp on desktop | Centered is unambiguous; bottom-sheet reserved for kid confirm-only flows. |
| Toasts | Top-right (parent SPA) / Top-center (kid SPA) | Kid glances up after a tap; parent glances up-right while typing. |
| Notification list | Inline list inside the relevant section, NOT a separate "Notifications" page | Notifications are contextual, not their own destination. |
| Empty states | Always have a small flat-vector illustration + 1 sentence + 1 CTA | US 50/51/52; never leave a screen visibly blank. |
| Card grid breakpoint | 2-up @ ≥ 768dp, 3-up @ ≥ 1024dp | Parent SPA rewards/streaks grid; kid SPA is single-column. |
| Kid SPA layout | Single column, large touch, full-width cards | Kid's screen is a kiosk; do not over-design. |
| Parent SPA layout | Single column < 768dp, 2-column ≥ 1024dp (sidebar nav + content) | Manager pattern. |

## Out of scope (do not design for)

These come from `spec-v1-mvp.md` and `CONTEXT.md`. The design must
not produce assets or specs covering any of them; if a request asks
for them, push back to the orchestrator.

- Second parent, second child.
- Chore categories / difficulty tiers / age tiers.
- Chore templates or starter library.
- Sibling leaderboards.
- Photo / video proof for chores.
- Native mobile shell (Capacitor, React Native).
- Internationalisation (English only).
- In-app chat.
- Configurable streak milestones.
- Push to kid devices.

## Style authority

- `tokens/tokens.json` is the single source of truth. The CSS
  variables file (`tokens.css`) is a flat rendering of the same
  values. If they diverge, fix both; do not let one drift.
- `CONTEXT.md` and `docs/adr/0001-kid-identity-is-the-device.md`
  are the voice and identity contract for copy and mascot
  decisions.

## Accessibility contract

`docs/design/a11y.md` defines the keyboard, ARIA, and contrast rules
every component and screen must meet. Every component spec quotes the
relevant subset; every screen spec quotes its tab order and focus
management. UAT verifies against `a11y.md` and the per-component
quotes.

## Fidelity rules summary

`fidelity-rules.md` is the verification list. Excerpt of the rules
that drive the most common rework risk:

1. Every screen uses only token values. No hard-coded color / size /
   spacing in component CSS unless the value is in the token file.
2. The kid SPA uses `sunshine` and `violet` for action surfaces;
   the parent SPA uses `violet` only (with quiet accents).
3. Every interactive element meets the touch-target minimum for its
   surface (44dp parent, 56dp kid, 64dp kid primary CTA).
4. Every text/background pair in the palette passes WCAG AA contrast.
5. Every screen has a documented empty state, loading state, and
   error state.
6. The kid avatar is round and always larger than the ChoreHero
   emblem when both appear.
7. The streak milestone celebration is the only screen allowed to
   use the `--ch-shadow-brand` glow AND a serif display font.

---

For details on any specific decision, read the linked file. If a screen
or component spec contradicts this README, the spec wins for that
specific surface — flag the conflict in the next design review.