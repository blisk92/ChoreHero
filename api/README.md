# ChoreHero API

[![CI](https://github.com/blisk92/ChoreHero/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/blisk92/ChoreHero/actions/workflows/ci.yml)

Node 20 / Express 4 / Prisma 5 / `ws`. v1-01 ships the per-field LWW sync
primitive and the WebSocket upgrade lifecycle. v1-02 adds the parent auth +
household endpoints (signup / signin / me) on top; chore, reward, redemption,
and ledger endpoints land in v1-04 through v1-08.

## Scripts

- `npm run dev` — `tsx watch src/index.ts`, listens on `:3000` (overridable
  via `PORT`).
- `npm run build` — `tsc -p tsconfig.json`, emits `dist/`.
- `npm start` — runs the compiled `dist/index.js`.
- `npm run migrate` — `prisma migrate dev` (interactive; local dev).
- `npm run migrate:deploy` — `prisma migrate deploy` (CI / production).
- `npm run generate` — `prisma generate` (regenerate the typed client).
- `npm test` — `vitest run`.
- `npm run test:contract` — `vitest run test/contract`. Runs the wire-level
  HTTP tests against a real MariaDB (set `DATABASE_URL` and `JWT_SECRET`).

## Required env (set by docker-compose for the local stack)

- `DATABASE_URL` — MariaDB connection string. In compose:
  `mysql://chorehero:***@mariadb:3306/chorehero`.
- `PORT` — HTTP port. Defaults to `3000`.
- `JWT_SECRET` — HS256 signing key for parent session JWTs. Required at boot
  in production; the contract tests provide a deterministic test secret when
  `NODE_ENV === 'test'`. OAuth env vars (`GOOGLE_CLIENT_ID`, etc.) are still
  unused — OAuth flows land in a follow-up ticket.

## Parent auth

Three endpoints under `/api/auth`. Tokens are signed with HS256, expire in
7 days, and carry `{ parentId, householdId }`. Send the token as
`Authorization: Bearer <token>` on subsequent calls. The server never sets
cookies; storage is the client's decision.

### `POST /api/auth/signup`

```json
{ "email": "alice@example.com", "password": "hunter22hunter", "displayName": "Alice" }
```

Hashes the password with bcrypt (cost 10), creates a `Household`, creates a
`Parent` linked to that household, issues a JWT, returns
`{ token, parent, household }`. Email is normalised to lowercase.
Passwords must be at least 8 characters.

### `POST /api/auth/signin`

```json
{ "email": "alice@example.com", "password": "hunter22hunter" }
```

Returns the same `{ token, parent, household }` shape on success. Unknown
email and wrong password both 401 with the same body so the server doesn't
leak which one failed.

### `GET /api/auth/me`

Requires `Authorization: Bearer ...`. Returns `{ parent, household }` for
the session's principal. 401 if the token is missing, malformed, expired,
or signed with the wrong secret.

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