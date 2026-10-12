# Screen 14 — Push opt-in (parent)

> US 45. The parent toggles "Allow push" per device.

## User story

- US 45.

## Route

- `/settings/notifications` (parent SPA) — also reachable from a
  banner on the dashboard the first time.

## Layout

```
┌──────────────────────────────────────────────────────────────┐
│  ← Back          H1: Notifications                           │
├──────────────────────────────────────────────────────────────┤
│  H2: Push notifications                                      │
│  Helper: "Get a notification on this device when something  │
│           important happens on ChoreHero."                   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  Lock screen preview                                 │    │
│  │  ┌──────────────────────────────────────────────┐    │    │
│  │  │ 🔔 ChoreHero · Maya                            │    │    │
│  │  │ Wants to redeem "30 min screens" for 50 pts   │    │    │
│  │  └──────────────────────────────────────────────┘    │    │
│  │                                                      │    │
│  │  This is what you'll see on this device.             │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  [ Turn on push notifications ]   ← intent-primary          │
│  [ Not now ]                                                  │
│                                                              │
│  Already on? ✓   — small confirmation line                  │
│                                                              │
│  Helper copy: "You can change this any time in Settings."   │
└──────────────────────────────────────────────────────────────┘
```

## Copy

| Element       | Copy                                                            |
|---------------|-----------------------------------------------------------------|
| H1            | "Notifications"                                                |
| H2            | "Push notifications"                                            |
| Helper        | "Get a notification on this device when something important happens on ChoreHero." |
| Preview title | "ChoreHero · [Kid first name]"                                 |
| Preview body  | "[chore/reward headline]. Approve? / View"                    |
| Primary CTA   | "Turn on push notifications"                                    |
| Secondary     | "Not now"                                                        |
| Already on    | "Push is on for this device."                                   |
| Off helper    | "Push is off for this device."                                  |
| Footer helper | "You can change this any time in Settings."                     |

## Tokens used

- Background: `--ch-surface-app-parent`.
- Lock-screen preview card: `--ch-surface-card`,
  `--ch-radius-card`, `--ch-shadow-card-resting`. Inside, the
  notification art uses ink_900 text on paper_050 surface.

## Components used

- `<TopNav>`.
- `<Card>` for preview.
- `<Switch>` for the persistent on/off toggle (in the rendered
  state).
- `<Button variant="primary">` "Turn on".
- `<Button variant="secondary">` "Not now".
- `<Toast>` for system permission outcomes.

## Hierarchy

- H1.
- H2.

## Tab order

1. Back.
2. Primary CTA.
3. Secondary CTA.
4. (Persistent switch, if user has already opted in.)

## States

| State                | How                                                |
|----------------------|----------------------------------------------------|
| Default (off)        | Prompts primary CTA to opt in.                     |
| Prompting perm       | After primary CTA, native browser perm dialog.     |
| Perm granted         | On confirmation, persisted; toast "Push on."       |
| Perm denied          | Inline error: "Couldn't enable push. Try again or change in browser settings." |
| Already on           | "Push is on for this device." + "Turn off" link.    |
| Perm unknown support | Helper copy notes "Push may not be supported on this browser." |

## Accessibility

- Live region for state changes (`role="status"`).
- Persistent switch uses `role="switch"` + `aria-checked`.
- The "Turn on" CTA disables itself after the prompt asks (so the
  user doesn't double-prompt).
- The preview tile carries `role="img"` + an `aria-label` that
  reads the body text (helps screen reader users imagine the
  notification without rendering it).

## Composition rules

- The browser permission prompt is shown only once per
  device+permission lifetime. If the user previously denied, the
  inline error directs them to browser settings (no UA bypass is
  allowed).
- This screen is also accessible from a banner shown on the
  dashboard after first sign-in, until the parent opts in or
  dismisses ("Not now" hides the banner for 14 days; a second
  dismiss hides it for the session).

## Fidelity rules (UAT)

- F-9.10: push opt-in shows affordance + "Not now" link.
- F-13.1: defaults to off.
- F-13.3: kid SPA has no equivalent screen.

## Anti-patterns

- ❌ Pre-prompt UI that requests perm before the user clicks
     anything (browsers block this and warn).
- ❌ Persistent nag banner after explicit "Not now".
