# ChoreHero API

Node 20 / Express 4 / Prisma 5 / `ws`. v1-01 ships only the per-field LWW sync
primitive and the WebSocket upgrade lifecycle. Auth, OAuth, household, child,
chore, reward, redemption, and ledger endpoints land in v1-02 through v1-08.

## Scripts

- `npm run dev` — `tsx watch src/index.ts`, listens on `:3000` (overridable
  via `PORT`).
- `npm run build` — `tsc -p tsconfig.json`, emits `dist/`.
- `npm start` — runs the compiled `dist/index.js`.
- `npm run migrate` — `prisma migrate dev` (interactive; local dev).
- `npm run migrate:deploy` — `prisma migrate deploy` (CI / production).
- `npm run generate` — `prisma generate` (regenerate the typed client).
- `npm test` — `vitest run`.

## Required env (set by docker-compose for the local stack)

- `DATABASE_URL` — MariaDB connection string. In compose:
  `mysql://chorehero:chorehero@mariadb:3306/chorehero`.
- `PORT` — HTTP port. Defaults to `3000`.
- `JWT_SECRET`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`,
  `APPLE_CLIENT_ID`, `APPLE_TEAM_ID`, `APPLE_KEY_ID`, `APPLE_PRIVATE_KEY` —
  required by v1-02 (auth). Read by v1-01 as a no-op so the same compose
  service can boot before that ticket lands.

## LWW sync primitive

`POST /api/sync/apply`

```json
{
  "table": "chore",
  "id": "ch_abc123",
  "field": "point_value",
  "value": 25,
  "updated_at": "2026-12-01T00:00:00.000Z"
}
```

The server applies only if `incoming.updated_at > stored.<field>_updated_at`.
The set of writable `(table, field)` pairs is whitelisted in
`src/sync/lww.ts`. Returns `{ applied: true }` or
`{ applied: false, reason: 'stale' | 'unknown_field' | 'not_found' }`.

## ADR-0001 invariant

There is no `Child` auth row. The kid presents `KidDevice.device_token_hash`
on every request; that flow is plumbed in v1-03.