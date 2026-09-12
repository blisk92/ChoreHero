# ChoreHero — Glossary

The vocabulary of the app itself. No implementation details, no spec prose, no scratch notes. ADRs live in `docs/adr/`.

> **Tagline:** "Your chores. Your points. Your rewards."

## People & Identity

- **Household** — The unit of data isolation. One household maps to one family and one install-universe. v1 contains exactly 1 parent and 1 child; v2 will add additional parents and children without changing this scope.
- **Parent** — The account holder who manages chores, rewards, kids, and devices. Authenticates with email+password, with optional OAuth (Google/Apple) as a faster sign-in.
- **Child** — Not a user account. A profile inside a household, named and managed by the parent.
- **Kid Device** — A specific physical device registered to a specific child profile inside a household. The kid's experience is delivered through a kid device, not an account. Each kid device holds a device-scoped session.

## Chores & Pools

- **Chore** — A unit of work a child can complete for points. Freeform, parent-created. Every chore lives in a pool until claimed.
- **Pool** — The container of claimable chores visible to a kid. Two pools:
  - **Recurring Pool** — chores that re-enter the pool after completion. Examples: "Make bed", "Feed dog".
  - **One-off Pool** — chores that exist until resolved (completed, skipped, or expired). Examples: "Clean the garage", "Organize the toy bin".
- **Recurring Chore** — A chore that returns to the pool immediately after the child resolves it (completes or skips). No deadline; rhythm of repetition comes from the child.
- **One-off Chore** — A chore with a lifecycle that ends in resolution or expiry.
- **Deadline Chore** — A one-off chore that carries an explicit `due_at`. Misses the deadline → `expired`, parent is notified.
- **At-will Chore** — A one-off chore with no `due_at`. Stays in the pool until claimed, then resolvable at any pace.
- **Review-Flagged Chore** — A chore configured by the parent to require parent approval before points are awarded, regardless of how the child marks it.

## States & Actions

- **Claim** — The child's act of pulling a chore out of a pool into their own active list. A chore can only be claimed once at a time; resolution returns it to the pool (recurring) or removes it from circulation (one-off).
- **Complete** — The child marks a claimed chore done. If review-flagged, points await parent approval. Otherwise points are awarded immediately.
- **Skip** — The child removes a claimed chore without completing it. Behavior depends on chore kind: recurring auto-resets to pool; deadline one-off `expired`; at-will one-off returns to pool.
- **Expire** — A deadline chore that was not completed in time. Parent notified. Chore archived from the kid's view; visible to the parent in a Past/archive view.

## Streaks

- **Streak** — A counter on a recurring chore that increments on each completion day and resets if a calendar day passes without one. Surfaces on the kid device home screen and the parent view.

## Rewards & Redemption

- **Reward** — A catalog item the parent sets up in advance: name, point cost, optional description. Visible to the child; redeemable from the kid device's Redeem button. Kids cannot propose new rewards in v1.
- **Reward Catalog** — The parent-managed list of available rewards. Permanent until removed; an individual reward can be marked with a `stock_remaining` to limit redemptions of tangible rewards.
- **Redemption** — A child's request to spend points on a specific catalog reward. Always routed to the parent for approval before points are deducted.
- **Approval** — A parent's action on a pending redemption. Options: Approve (points deducted, child notified) or Deny (request removed, child notified).
- **Reversal** — A parent's retroactive undo of an approved redemption. Points returned to the child, child notified. Used when the reward wasn't actually delivered after approval.

## Notifications

- **In-App Notification** — A banner / badge surfaced inside the app while the user has it open or opens it later. Always on for both parent and kid devices.
- **Web Push** — An opt-in per-device notification delivered to the lock screen / notification tray when the app is closed. Default off. Parent devices only.
- **Parent pings (in-app, default)**: review-flagged chore completed, deadline chore expired, redemption requested, recurring pool empty.
- **Kid device pings (in-app, default)**: new chore added to a pool, streak milestone reached, point balance increased after approval, redemption approved or denied.

## Authentication & Identity

- **Parent Auth** — Email + password for sign-up and sign-in. Optional OAuth (Google or Apple) available as a faster sign-in path on the login screen.
- **Household Code** — A 6-character alphanumeric code (no ambiguous characters: 0/O, 1/I/L excluded) used to link a new kid device via QR or manual entry. Generated lazily the first time the parent taps "Link a kid device"; permanent thereafter; regenerable from parent settings.
- **Kid Device Kiosk** — Single-purpose view on a kid device: Today (Available Extras / My Active), Points, Streaks, Redeem. No parent-only UI.

## Empty States

- **Kid device, no chores in pool** — "No chores yet. Ask a parent to add some." with a small illustration. Visible until any chore exists in either pool.
- **Kid device, on first link (before any chores)** — Welcome screen: "Welcome, [name]!" with the kid's chosen avatar. Auto-transitions to the regular empty state once any chore lands in either pool.
- **Kid device, 0 points** — Points badge shows `0` with no special copy. Encouraging language is implicit in the available chores, not in the balance display.
- **Parent dashboard, no chores** — Big primary CTA: "Add your first chore", with secondary copy describing kinds of chores. A first-launch nudge banner stays visible until ≥1 chore exists in either pool.
- **Parent dashboard, no rewards** — Big primary CTA: "Add your first reward", with example suggestions ("30 min screen time", "Pick dinner"). No auto-seeded rewards; parent adds their own.

## Tone & Voice

- **Parent voice** — Quietly functional. Plain short copy. No exclamation marks.
- **Kid voice** — Cheerful but not theatrical. Second person. Occasional emojis. One celebratory phrase per milestone moment (streak hit, redemption approved).
- **Internal labels** — Functional section names ("Chores", "Rewards", "History", "Settings"). No clever copy inside the app.
- **Errors** — Plain-but-warm on the kid side ("Hmm, that didn't work. Try again?"). Direct on the parent side ("Something went wrong.").

## Visual Identity

- **Mascot** — The child's chosen avatar is the hero. A generic ChoreHero emblem lives only in the app icon and empty-state illustrations; it never competes with the child's avatar in celebratory moments.
- **Color palette** — Deep violet primary with a sunshine yellow accent and call-to-action color. Parent-side surfaces reuse the same palette but with more white space and quieter accents.
- **Illustration style** — Flat vector base for icons and tiles; hand-drawn accent strokes (organic line, irregular shape) for the mascot and empty-state illustrations so the app reads human, not corporate.
