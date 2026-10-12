# 08: Deadline expiry and notifications

**What to build:** Two pieces pulled from the same "scheduled time + in-app feed" backbone:
1. **Deadline expiry** — one-off chores with a `due_at` flip status to `expired` if not completed by that time. A scheduled job (cron-style inside the API container) passes over `claimed` / `pool` one-off chores whose `due_at < now` and transitions them. Parent is notified. Chore is archived from the kid's view but retained in the parent's "Past" view for audit.
2. **In-app notifications** — a notification feed on both the parent SPA and kid SPA, backed by `Notification` rows. The full ping matrices from `CONTEXT.md` are wired up:
   - Parent pings (in-app, default): review-flagged chore completed, deadline chore expired, redemption requested, recurring pool empty.
   - Kid pings (in-app, default): new chore added to pool, streak milestone reached, point balance increased after approval, redemption approved or denied.
   - Web push (parent only, opt-in per device) lands in ticket 09; this ticket is in-app only.

Both pieces land together because the deadline-expired event is itself a parent ping — separating them would force an interim state where one notification type works and others don't.

**Blocked by:** 07

**Status:** ready-for-agent

- [ ] Parent can set `due_at` on a one-off chore at creation time. UI uses the household timezone (set at household creation in ticket 02; one timezone per household in v1).
- [ ] A scheduled job runs at a sensible interval (suggest: every minute in v1, tunable later) and flips one-off `claimed` or `pool` chores with `due_at < now` to `expired`.
- [ ] Expiry emits a `Notification` row addressed to the parent (kind: `deadline_expired`, payload includes chore name + child name).
- [ ] Kid device hides `expired` chores from the pools; parent dashboard surfaces them under a "Past" / archive tab with date stamps.
- [ ] A reusable notification surface exists on both SPAs:
  - Parent SPA: a bell icon with an unread count, opening a dropdown feed.
  - Kid SPA: a similar bell icon, kid-tone copy per `CONTEXT.md` ("New chore in your pool!" / "Nice work — 7-day streak!").
- [ ] Every ping in the parent and kid matrices above is wired to fire from the corresponding action (`chore:created`, `chore:review_completed`, `chore:expired`, `redemption:requested`, `redemption:approved`, `redemption:denied`, `streak:milestone`, `points:increased`, `pool:empty`).
- [ ] `pool:empty` parent ping is computed lazily when the parent opens the dashboard (no need to push real-time) and suppresses itself if the pool fills within the same session.
- [ ] `streak:milestone` kid ping fires exactly at 7, 14, 30, 60, 100 day marks (hardcoded per spec; configurable later).
- [ ] Streak notification fires idempotently — completing a chore on a day that's already triggered the milestone for that chore doesn't fire a second time.
- [ ] Playwright e2e covers: setting a deadline in 2 minutes → waiting briefly (with clock injection) → chore transitions to expired → parent feed shows the deadline-expired ping.
- [ ] API contract tests: scheduled-job behaviour, notification creation on each ping source, suppression rules for `pool:empty` and duplicate `streak:milestone`.
- [ ] Per `CONTEXT.md`: notification copy uses kid voice on kid surfaces and parent voice on parent surfaces.
