# ChoreHero v1 — Fidelity Rules (UAT verification spec)

> Every check below is keyed to a token, a component spec, or a
> screen spec. A failure is unambiguous: the check names the file
> and the token/value that the implementation diverged from.

## How to use this document

UAT reads the relevant screen spec, then walks these checks in order.
Each check is pass/fail. Failures feed back to the frontend dev with
the section name (e.g. "F-3.2 hit target") so a re-render can target
the exact fix.

## F-1. Tokens

| ID     | Check                                                                                      |
|--------|--------------------------------------------------------------------------------------------|
| F-1.1  | Every color in CSS resolves to a `var(--ch-color-*)` token, not a hex literal.             |
| F-1.2  | Every space value is `var(--ch-space-*)`, including 0 → `var(--ch-space-0)`.              |
| F-1.3  | Every radius is a token (`--ch-radius-*`). Never raw `border-radius: 16px;`.               |
| F-1.4  | Every shadow is a token (`--ch-shadow-*`). Never raw `box-shadow:` outside tokens.css.    |
| F-1.5  | Every font is a token (`--ch-font-primary` / `display-kid` / `mono`).                     |
| F-1.6  | `tokens/tokens.json` and `tokens/tokens.css` agree byte-for-byte on every value.          |
| F-1.7  | No component CSS defines a new color outside the token set.                               |

## F-2. Palette discipline

| ID     | Check                                                                                      |
|--------|--------------------------------------------------------------------------------------------|
| F-2.1  | Sunshine (`--ch-color-accent-sunshine-*`) is used only on kid SPA or in celebration-only surfaces. |
| F-2.2  | Parent SPA primary CTA is violet (`--ch-color-brand-violet-700`), no sunshine glow.        |
| F-2.3  | Kid SPA primary CTA is sunshine (`--ch-color-accent-sunshine-500`) with `--ch-shadow-cta-primary`. |
| F-2.4  | Brand glow (`--ch-shadow-brand` / `--ch-shadow-cta-primary`) is used only on kid SPA primary CTAs and the streak milestone hero. |
| F-2.5  | The streak milestone celebration surface is the ONLY screen allowed to use `--ch-font-display-kid`. |
| F-2.6  | No `#hex` literals appear in any component or screen CSS.                                   |

## F-3. Sizing

| ID     | Check                                                                                      |
|--------|--------------------------------------------------------------------------------------------|
| F-3.1  | Parent SPA touch targets ≥ 44×44 CSS px.                                                   |
| F-3.2  | Kid SPA touch targets ≥ 56×56 CSS px; primary CTAs ≥ 64×64.                                |
| F-3.3  | Parent SPA layout: single column < 768dp; 2-column (rail + content) ≥ 1024dp.              |
| F-3.4  | Kid SPA layout: single column, full-width cards, no horizontal scroll.                     |
| F-3.5  | Card grid: 1-up @ < 768dp; 2-up @ ≥ 768dp; 3-up @ ≥ 1024dp.                                |
| F-3.6  | Modal max-width 480dp on mobile, 560dp on desktop. Centered.                               |
| F-3.7  | Bottom nav height `--ch-space-nav-height-compact` (48dp).                                  |
| F-3.8  | Side nav width `--ch-space-nav-height-tall` (64dp).                                        |
| F-3.9  | Avatars: 56dp default, 80dp celebration-banners, 96dp hero. 160dp only on the kid SPA header. |
| F-3.10 | Streak milestone hero uses `--ch-radius-card-hero` and `--ch-shadow-3`.                    |

## F-4. Typography

| ID     | Check                                                                                      |
|--------|--------------------------------------------------------------------------------------------|
| F-4.1  | All text uses one of the type tokens (`--ch-text-*`). No raw `font-size:`.                 |
| F-4.2  | Headings follow heading hierarchy: one `<h1>` per screen.                                  |
| F-4.3  | Code (household code) uses `var(--ch-font-mono)` and `--ch-text-code-lg`.                  |
| F-4.4  | Streak milestone title is Fraunces (`--ch-font-display-kid`).                              |
| F-4.5  | No exclamation marks on parent SPA copy.                                                   |

## F-5. Surfaces & elevation

| ID     | Check                                                                                      |
|--------|--------------------------------------------------------------------------------------------|
| F-5.1  | Chore card uses `--ch-surface-card` + `--ch-radius-card` + `--ch-shadow-card-resting`.    |
| F-5.2  | Chore card hover uses `--ch-shadow-card-hover`.                                            |
| F-5.3  | Modal uses `--ch-surface-card` + `--ch-radius-modal` + `--ch-shadow-modal`.                |
| F-5.4  | Toast uses `--ch-shadow-toast`.                                                            |
| F-5.5  | Hero card (kid welcome, streak milestone, redemption celebration) uses `--ch-surface-card-hero` + `--ch-radius-card-hero`. |
| F-5.6  | Background tinted surface for kid side uses `--ch-color-brand-violet-050`.                 |
| F-5.7  | Background tinted surface for parent side uses `--ch-color-neutral-paper-050`.            |

## F-6. States

Every interactive surface must render these states:

| ID     | Check                                                                                      |
|--------|--------------------------------------------------------------------------------------------|
| F-6.1  | Default, hover, focus-visible, active, disabled present on every button.                    |
| F-6.2  | Disabled inputs/buttons use `aria-disabled="true"` not the HTML `disabled` attribute.      |
| F-6.3  | Loading state on async actions: spinner + `aria-busy="true"`, label preserved.             |
| F-6.4  | Error state on inputs: red border, helper text, `aria-invalid="true"`, `aria-describedby`. |
| F-6.5  | Empty state on every list view, matching the documented variant.                           |
| F-6.6  | Skeleton matches the eventual real component's bounding box exactly.                       |

## F-7. Accessibility

| ID     | Check                                                                                      |
|--------|--------------------------------------------------------------------------------------------|
| F-7.1  | Skip-to-content link is the first focusable element on every parent SPA page.              |
| F-7.2  | Tab order matches DOM order matches visual order.                                          |
| F-7.3  | Focus ring is visible against the host surface (violet ring + paper inner offset).         |
| F-7.4  | Modal traps focus; `Esc` closes; focus returns to trigger on close.                        |
| F-7.5  | Toast does not steal focus.                                                                |
| F-7.6  | Every interactive element has an accessible name (visible text or `aria-label`).           |
| F-7.7  | Color is never the only signal (every intent variant pairs color with text + icon).        |
| F-7.8  | `prefers-reduced-motion: reduce` clamps durations and disables the streak shimmer and celebration pulse. |
| F-7.9  | Forced-colors mode: brand colour is paired with a non-colour signal (border, text, icon).   |
| F-7.10 | Form fields use `<label>`; placeholders never substitute for labels.                       |
| F-7.11 | Tables use `<thead>` + `<tbody>` + `<th scope="col">`.                                    |
| F-7.12 | Live regions: `role="status"` polite for info/success/celebrate; `role="alert"` assertive for warning/danger. |

## F-8. Voice & copy

| ID     | Check                                                                                      |
|--------|--------------------------------------------------------------------------------------------|
| F-8.1  | Parent voice: short, imperative, no exclamations.                                          |
| F-8.2  | Kid voice: cheerful but not theatrical; one celebratory phrase per milestone.               |
| F-8.3  | Errors: warm-but-clear on kid side ("Hmm, that didn't work. Try again?"); direct on parent side ("Something went wrong."). |
| F-8.4  | No emoji in surface chrome (chrome icons only). Emoji allowed in kid-side celebration copy and chip values (🔥 7-day streak). |
| F-8.5  | Household code displays 6 characters, uppercase, monospace, with letter spacing.           |

## F-9. Specific screens

| ID     | Check                                                                                      |
|--------|--------------------------------------------------------------------------------------------|
| F-9.1  | Marketing screen has a primary CTA above the fold.                                         |
| F-9.2  | Parent sign-up / sign-in form has visible labels, no placeholders as labels.               |
| F-9.3  | Parent dashboard first-load is the `EmptyState variant="parent"` until ≥1 chore exists.    |
| F-9.4  | Kid welcome screen shows the avatar at `kiosk` size (160dp) with the `ring` variant.       |
| F-9.5  | Kid Today screen has "My Active" above "Available Extras".                                 |
| F-9.6  | Kid Redeem catalog renders an out-of-stock chip when `stock_remaining = 0`.                 |
| F-9.7  | Streak milestone celebration is full-bleed, avatar hero (96dp), Fraunces title.             |
| F-9.8  | Link-kid-device screen shows QR (≥ 200dp) + 6-char code in monospace.                      |
| F-9.9  | Redemption queue rows have approve/deny intent buttons; deny requires confirmation (modal). |
| F-9.10 | Push opt-in screen shows the system permission affordance and a "Not now" link.            |

## F-10. Mascot rule

| ID     | Check                                                                                      |
|--------|--------------------------------------------------------------------------------------------|
| F-10.1 | The kid's chosen avatar is the hero on every celebratory surface.                          |
| F-10.2 | The ChoreHero emblem never appears next to a kid avatar.                                   |
| F-10.3 | The ChoreHero emblem appears only in the app icon and empty-state illustrations.           |

## F-11. Sync & offline

| ID     | Check                                                                                      |
|--------|--------------------------------------------------------------------------------------------|
| F-11.1 | A kid who claims a chore offline sees the optimistic UI update immediately.                |
| F-11.2 | On reconnect, the outbox replays in order; the kid sees a single "All caught up" toast.   |
| F-11.3 | A parent editing a chore while the kid is offline sees their edit persisted; the kid sees the edit on reconnect without losing their own claim. |
| F-11.4 | WebSocket disconnect surfaces a subtle "Reconnecting…" pill; never blocks input.           |

## F-12. Notifications & toasts

| ID     | Check                                                                                      |
|--------|--------------------------------------------------------------------------------------------|
| F-12.1 | In-app notification list is rendered inline within its section (not a separate page).      |
| F-12.2 | Toast position matches surface (top-right parent, top-center kid).                        |
| F-12.3 | Toast auto-dismisses within 8s; danger toasts show a "Try again" link.                      |
| F-12.4 | Web-push icon + title follows the format: app icon + kid first name + reward/chore name.    |

## F-13. Web push lock-screen

| ID     | Check                                                                                      |
|--------|--------------------------------------------------------------------------------------------|
| F-13.1 | Web-push toggle defaults to off.                                                          |
| F-13.2 | Opt-in flow asks for permission only once.                                                |
| F-13.3 | Kid devices never receive web push (no opt-in toggle on kid SPA).                         |

## F-14. Cross-cutting anti-patterns

These are universal rework triggers; if a screen or component
violates any of them, fail the whole surface:

- ❌ A bespoke hex / px / rgba value not in tokens.
- ❌ A bespoke animation not using the motion tokens.
- ❌ A button without an accessible name.
- ❌ A modal that doesn't trap focus.
- ❌ A celebration surface using the ChoreHero emblem alongside the
     kid avatar.
- ❌ A parent SPA screen using Fraunces, sunshine, or 56dp+ targets.
- ❌ A kid SPA screen using parent-voice copy ("Something went
     wrong.") instead of warm-but-clear copy.

## Verification workflow

1. Deploy staging build (Docker Compose, parent SPA + kid SPA + API).
2. Open the target screen on a real mobile viewport for kid SPA,
   desktop viewport for parent SPA.
3. Run this checklist for that screen.
4. Failures are recorded as `F-XX.Y => <description>` so the
   frontend dev has a precise bug.
5. Pass / fail per screen is binary; do not pass a screen that has
   open failures.
