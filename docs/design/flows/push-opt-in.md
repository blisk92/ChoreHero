# Flow: push opt-in (parent)

> US 45. The parent toggles "Allow push" per device.

## Visual sequence

```
  After first sign-up:
  Dashboard banner → "Get lock-screen pings for reviews
                     and redemptions." → [Allow] [Not now]

  → tap Allow
  → /settings/notifications (Screen 14)
  → tap "Turn on push notifications"
  → browser perm dialog
  → granted: persisted; toast "Push on for this device."
  → denied: inline error; "Try again or change in browser settings."
```

## Detailed steps

### 1. First-run banner on dashboard

- Banner appears under the top nav; one line of copy + Allow + Not now.
- Tap Allow → navigate to /settings/notifications.
- Tap Not now → banner hides for 14 days; a smaller "Enable push"
  link remains in Settings.

### 2. Settings screen

- Lock-screen preview card shows a sample notification ("ChoreHero
  · Maya: Wants to redeem 30 min screens for 50 pts").
- Primary CTA "Turn on push notifications".
- After first denial, primary CTA changes to "Push is on for this
  device." + "Turn off" link.

### 3. Browser permission

- Native OS / browser perm prompt appears only on tap.
- After perm dialog: result handled server-side; WS confirms the
  subscription.

### 4. Subsequent updates

- Web-push payloads: app icon + kid first name + reward/chore name
  (per open question 9 default).
- Default template on parent device:

```
  ChoreHero
  Maya wants to redeem "30 min screens" for 50 pts.
  Tap to review.
```

## Components touched

- Dashboard banner.
- Settings screen.
- Native browser perm dialog.
- WS push handler in service worker.

## Tokens touched

- Banner: `--ch-color-brand-violet-100` bg; CTA primary.

## Animation

- Banner slides in on first load; static thereafter.

## States

| State            | How                                                |
|------------------|----------------------------------------------------|
| Banner shown     | First sign-in or after expired Not now.             |
| Banner hidden    | After Not now, hide for 14 days.                    |
| Perm granted     | Persisted; banner gone.                             |
| Perm denied      | Inline error; banner shown; link to browser settings.|
| Perm unknown (browser doesn't support push) | Inline: "Push isn't available in this browser." |

## Accessibility

- Banner is `role="region"` with `aria-labelledby` to its text.
- Settings screen shows preview as `role="img"` with
  `aria-label` that reads the full body.
- Perm grant/deny is announced via toast (`role="status"`).
- Reduced motion: no slide.

## Composition rules

- Banner shows only for parents with at least 1 active session.
- Web-push opt-in is per-device. Each device subscribed separately.
- Kid devices never receive web-push and never see this screen.

## Fidelity rules (UAT)

- F-9.10: opt-in screen affordance + Not now.
- F-13.1: defaults to off.
- F-13.2: perm asked once.
- F-13.3: no equivalent on kid SPA.
- F-12.4: lock-screen copy follows the format.

## Anti-patterns

- ❌ Pre-permission prompting on page load (browsers block).
- ❌ A persistent nag after explicit "Not now".
- ❌ Web-push to kid devices.
