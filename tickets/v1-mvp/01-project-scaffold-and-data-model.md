# 01: Project scaffold and data model

**What to build:** Greenfield scaffolding for ChoreHero — a monorepo containing a Vue 3 parent SPA, a Vue 3 kid SPA, and a Node.js + Express API, plus the Prisma schema for MariaDB. `docker compose up` brings up `nginx`, `node`, and `mariadb`; Prisma migrations apply clean against the database. CI runs a Prisma migration smoke test that boots a fresh MariaDB, applies all migrations, and asserts the schema version. No business behaviour yet — only scaffolds and the data model that everything else will hang from.

This is intentionally a horizontal slice (scaffolding, not a tracer bullet) because no vertical slice is possible without it.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] Repo has a `parent/` (Vue 3 + Vite + vite-plugin-pwa), `kid/` (Vue 3 + Vite + vite-plugin-pwa), `api/` (Express + Prisma), and `web/` (static marketing page served by nginx) workspace layout.
- [ ] `docker-compose.yml` defines `nginx`, `node`, `mariadb` services with a persistent volume for the database; `docker compose up` brings the stack healthy.
- [ ] Prisma schema matches the spec sketch — `Household`, `Parent`, `Child`, `KidDevice`, `HouseholdCode`, `Chore`, `Streak`, `Reward`, `Redemption`, `PointsLedger`, `Notification`. Every domain term used in the schema matches the glossary in `CONTEXT.md` (e.g. the entity is called `KidDevice`, not `ChildSession`).
- [ ] ADR-0001's data-model implication is honored: there is no `Child` auth row; identity at the kid layer is `KidDevice.device_token_hash`.
- [ ] All updatable columns on per-record state (e.g. `Chore.status`, `Reward.point_cost`) carry an `updated_at` to support the per-field last-write-wins sync policy.
- [ ] Per-field last-write-wins primitive lives in the API: an endpoint accepts partial updates with `updated_at` per field and applies only if `received.updated_at > stored.updated_at`. No CRDT, no vector clocks.
- [ ] CI runs the migration smoke test on every PR: `prisma migrate deploy` against a fresh MariaDB completes without error; a known query (e.g. `SELECT 1 FROM Household`) returns rows after seeding.
- [ ] nginx serves the parent and kid SPAs (built assets) and proxies `/api/` to the `node` container; TLS termination is wired (self-signed cert in dev is fine).
- [ ] `tickets/v1-mvp/` exists and contains this file plus the rest of the ticket set.
