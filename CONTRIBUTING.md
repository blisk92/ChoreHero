# Contributing to ChoreHero

## CI Gates

Every PR to `master` must pass the following checks before it can be merged:

| Job | What it does | When it runs |
|-----|-------------|--------------|
| `prisma-migrate-smoke` | Runs `prisma migrate deploy` and `prisma migrate status` against a MariaDB 11.8 service container. Exits 0 only if the migration applies cleanly and the database is in a known state. | On every push/PR to `master` |
| `api-contract` | Boots MariaDB 11.8, applies migrations, runs `pnpm --filter api test:contract` (the API contract test suite). | On every push/PR to `master` |
| `lint` | Runs `pnpm lint` at the monorepo root. | Skipped until M3 lands the frontend SPAs on `master` |

### Skipped paths

Changes to the following directories do **not** trigger the CI workflow:

- `tools/merge-review/**` — has its own independent test suite
- `docs/**`

### Running CI locally

You can replicate the CI environment locally with [Act](https://github.com/nektos/act):

```bash
# Run all jobs
act

# Run only the migration smoke test
act -j prisma-migrate-smoke

# Run only the contract tests
act -j api-contract
```

For the contract tests job, Act will automatically spin up the `mariadb:11.8` service
container and expose it on port 3306.

### Adding a new contract test

1. Create the test file under `api/test/contract/` (e.g. `my-feature.spec.ts`).
2. Use the same pattern as `sync-lww.spec.ts`: import the migration SQL, spin up a MariaDB
   container, apply migrations, and exercise the HTTP endpoint.
3. The test will be picked up automatically by `pnpm --filter api test:contract`.

## Getting help

If a CI job fails, the run log will show the step that failed and the error output.
The `api-contract` job also uploads the vitest report as an artifact on failure.
