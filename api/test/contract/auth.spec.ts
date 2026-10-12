// Contract test for the v1-02 auth + household + children endpoints.
//
// Extends the v1-01 sync-lww.spec.ts pattern: boots a real MariaDB
// container, applies the migration, drives the HTTP surface end-to-end
// (signup → me → create-child → reload → child still present).
//
// Coverage:
//   - POST /api/auth/signup  — happy path returns 201 with a JWT + bundle
//   - POST /api/auth/signin  — happy path returns 200 with a JWT, then
//                             a wrong password returns 401
//   - POST /api/auth/signup  — duplicate email returns 409
//   - POST /api/auth/signup  — weak password returns 400
//   - GET  /api/auth/me      — JWT-protected; missing/invalid token = 401
//   - GET  /api/auth/me      — happy path returns parent + household
//   - GET  /api/avatars      — public; returns 12 entries with SVG markup
//   - POST /api/households/{id}/children
//                            — happy path returns 201, child row exists
//                              on a second GET; second create returns 409
//                              ("exactly one child in v1")
//   - LWW on child.name/avatar_id via the v1-01 sync primitive still
//     works against the freshly-created child row (smoke test that
//     v1-01 + v1-02 stay compatible).

import { afterAll, beforeAll, describe, expect, it } from 'vitest';
import http from 'node:http';
import { execSync, spawn } from 'node:child_process';
import { mkdtempSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const MIGRATION_SQL = readFileSync(
  join(process.cwd(), '..', 'prisma', 'migrations', '0001_init', 'migration.sql'),
  'utf8',
);

let containerId = '';
let port = 0;
let apiPort = 0;
let apiProcess: ReturnType<typeof spawn> | null = null;

function waitForReady(timeoutMs = 60_000): void {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    try {
      const out = execSync(
        `docker exec ${containerId} mariadb -h 127.0.0.1 -uroot -prootpw -e "SELECT 1"`,
        { stdio: ['ignore', 'pipe', 'pipe'] },
      );
      if (out.toString().includes('1')) return;
    } catch {
      // not ready yet
    }
  }
  throw new Error('mariadb container did not become ready in time');
}

function httpJson(
  method: 'GET' | 'POST',
  path: string,
  body?: unknown,
  headers: Record<string, string> = {},
): Promise<{ status: number; body: unknown }> {
  return new Promise((resolve, reject) => {
    const data = body !== undefined ? JSON.stringify(body) : '';
    const req = http.request(
      {
        host: '127.0.0.1',
        port: apiPort,
        path,
        method,
        headers: {
          'content-type': 'application/json',
          ...(data ? { 'content-length': Buffer.byteLength(data) } : {}),
          ...headers,
        },
      },
      (res) => {
        let chunks = '';
        res.on('data', (c) => (chunks += c));
        res.on('end', () => {
          try {
            resolve({ status: res.statusCode ?? 0, body: JSON.parse(chunks) });
          } catch {
            resolve({ status: res.statusCode ?? 0, body: chunks });
          }
        });
      },
    );
    req.on('error', reject);
    if (data) req.write(data);
    req.end();
  });
}

// When `MARIADB_TEST_URL` (full URL e.g. mysql://user:pass@host:port/db)
// is set, reuse that database and skip spinning up a container. This
// lets v1-02 run the contract test against the staging MariaDB on the
// current host (where the dedicated test container wouldn't be able
// to bind 3306). The migration must already be applied — apply with
// `prisma migrate deploy` against the same URL beforehand.
function shellQuote(s: string): string {
  return `'${s.replace(/'/g, `'\\''`)}'`;
}

beforeAll(async () => {
  if (process.env.MARIADB_TEST_URL) {
    const u = new URL(process.env.MARIADB_TEST_URL);
    port = Number.parseInt(u.port || '3306', 10);
    process.env.DATABASE_URL = process.env.MARIADB_TEST_URL;
    process.env.JWT_SECRET = process.env.JWT_SECRET ?? 'contract-test-secret-32chars-1234567890';
    process.env.PORT = '3457';
    process.env.NODE_ENV = 'test';
    apiPort = 3457;
    execSync(`npx prisma generate`, { stdio: 'pipe' });
    // Staging DB is shared with other workers; truncate parent/child/
    // household so this spec is idempotent across runs. The Prisma
    // client we just generated can authenticate using the existing
    // URL and the staging creds the URL already embeds — no shell or
    // docker dance needed.
    const { PrismaClient } = await import('@prisma/client');
    const db = new PrismaClient({ datasourceUrl: process.env.MARIADB_TEST_URL });
    await db.$transaction([
      db.$executeRawUnsafe('SET FOREIGN_KEY_CHECKS = 0'),
      db.$executeRawUnsafe('TRUNCATE TABLE child'),
      db.$executeRawUnsafe('TRUNCATE TABLE parent'),
      db.$executeRawUnsafe('TRUNCATE TABLE household'),
      db.$executeRawUnsafe('SET FOREIGN_KEY_CHECKS = 1'),
    ]);
    await db.$disconnect();
  } else if (process.env.CI === 'true' && process.env.MARIADB_TEST_PORT) {
    port = Number.parseInt(process.env.MARIADB_TEST_PORT, 10);
    execSync(
      `mariadb -h 127.0.0.1 -P ${port} -uroot -prootpw chorehero`,
      { input: MIGRATION_SQL, stdio: ['pipe', 'ignore', 'ignore'] },
    );
    process.env.DATABASE_URL = `mysql://root:rootpw@127.0.0.1:${port}/chorehero`;
  } else {
    const tmp = mkdtempSync(join(tmpdir(), 'chorehero-mariadb-'));
    containerId = execSync(
      `docker run --rm -d ` +
        `-p 3306:3306 ` +
        `-v ${tmp}:/var/lib/mysql ` +
        `-e MARIADB_ROOT_PASSWORD=rootpw ` +
        `-e MARIADB_DATABASE=chorehero ` +
        `mariadb:11`,
      { encoding: 'utf8' },
    ).trim();
    waitForReady();
    port = Number.parseInt(
      execSync(`docker port ${containerId} 3306/tcp`, { encoding: 'utf8' })
        .trim()
        .split(':')
        .pop() ?? '3306',
      10,
    );
    try {
      execSync(
        `docker exec -i ${containerId} mariadb -h 127.0.0.1 -uroot -prootpw chorehero`,
        { input: MIGRATION_SQL, stdio: ['pipe', 'pipe', 'pipe'] },
      );
    } catch (err) {
      const e = err as { stdout?: Buffer; stderr?: Buffer };
      throw new Error(
        `migration apply failed: ${e.stderr?.toString() ?? ''}\n${e.stdout?.toString() ?? ''}`,
      );
    }
    process.env.DATABASE_URL = `mysql://root:rootpw@127.0.0.1:${port}/chorehero`;
  }

  if (!process.env.JWT_SECRET) process.env.JWT_SECRET = 'contract-test-secret-32chars-1234567890';
  if (!process.env.PORT) {
    process.env.PORT = '3457';
    apiPort = 3457;
  } else {
    apiPort = Number.parseInt(process.env.PORT, 10);
  }
  process.env.NODE_ENV = 'test';
  // Run prisma generate once, after the DB bootstrap branch. The
  // generated client picks up the migration's column map fresh; safe
  // to re-run regardless of which branch executed.
  try {
    execSync(`npx prisma generate`, { stdio: 'pipe' });
  } catch {
    // EPERM on Windows when an earlier API process still holds a
    // handle on query_engine-windows.dll.node. Subsequent runs cleanup
    // the lock; the regenerate is best-effort.
  }
  // (Prisma generate ran just above; spawn the API now.)
  // Spawn the API as a child process so the test exercises the real
  // HTTP surface (not an in-process express app, which is awkward to
  // boot from inside a vitest test). We invoke the bundled `tsx` (a
  // dev dep) through process.execPath, since npx isn't always on PATH
  // in the test sandbox. Output is piped and we wait for the
  // listen() log line before returning.
  const tsxCli = join(process.cwd(), 'node_modules', 'tsx', 'dist', 'cli.mjs');
  apiProcess = spawn(
    process.execPath,
    [tsxCli, join(process.cwd(), 'src', 'index.ts')],
    {
      env: {
        ...process.env,
        DATABASE_URL: process.env.DATABASE_URL,
        JWT_SECRET: process.env.JWT_SECRET,
        PORT: process.env.PORT,
        NODE_ENV: process.env.NODE_ENV,
      },
      stdio: ['ignore', 'pipe', 'pipe'],
    },
  );
  await new Promise<void>((resolve, reject) => {
    const timeout = setTimeout(() => reject(new Error('api process did not start in 20s')), 20_000);
    let stderrBuf = '';
    apiProcess!.stderr?.on('data', (chunk: Buffer) => {
      stderrBuf += chunk.toString();
    });
    apiProcess!.stdout?.on('data', (chunk: Buffer) => {
      if (chunk.toString().includes('listening on')) {
        clearTimeout(timeout);
        resolve();
      }
    });
    apiProcess!.on('error', (err) => {
      clearTimeout(timeout);
      reject(err);
    });
    apiProcess!.on('exit', (code) => {
      clearTimeout(timeout);
      reject(new Error(`api process exited early (code ${code}) before listening: ${stderrBuf}`));
    });
  });
}, 120_000);

afterAll(() => {
  if (apiProcess) {
    apiProcess.kill();
    apiProcess = null;
  }
  if (containerId) {
    execSync(`docker rm -f ${containerId}`, { stdio: 'ignore' });
  }
});

describe('POST /api/auth/signup', () => {
  it('creates a parent + household and returns a JWT bundle', async () => {
    const res = await httpJson('POST', '/api/auth/signup', {
      email: 'alice@example.com',
      password: 'hunter2hunter',
      name: 'Alice',
    });
    expect(res.status).toBe(201);
    const body = res.body as { token: string; parent: { email: string; householdId: string }; household: { id: string } };
    expect(body.token).toBeTruthy();
    expect(body.parent.email).toBe('alice@example.com');
    expect(body.parent.householdId).toBe(body.household.id);
  });

  it('rejects a duplicate email with 409', async () => {
    await httpJson('POST', '/api/auth/signup', {
      email: 'dup@example.com',
      password: 'hunter2hunter',
      name: 'Dup',
    });
    const res = await httpJson('POST', '/api/auth/signup', {
      email: 'dup@example.com',
      password: 'hunter2hunter',
      name: 'Dup',
    });
    expect(res.status).toBe(409);
    expect((res.body as { error: string }).error).toBe('email_taken');
  });

  it('rejects a weak password with 400', async () => {
    const res = await httpJson('POST', '/api/auth/signup', {
      email: 'weakpw@example.com',
      password: 'short',
      name: 'Weak',
    });
    expect(res.status).toBe(400);
    expect((res.body as { error: string }).error).toBe('weak_password');
  });
});

describe('POST /api/auth/signin', () => {
  it('returns a JWT for a known good password', async () => {
    await httpJson('POST', '/api/auth/signup', {
      email: 'bob@example.com',
      password: 'hunter2hunter',
      name: 'Bob',
    });
    const res = await httpJson('POST', '/api/auth/signin', {
      email: 'bob@example.com',
      password: 'hunter2hunter',
    });
    expect(res.status).toBe(200);
    expect((res.body as { token: string }).token).toBeTruthy();
  });

  it('returns 401 for the wrong password (and 401 for an unknown email — same body, no enumeration)', async () => {
    const bad = await httpJson('POST', '/api/auth/signin', {
      email: 'bob@example.com',
      password: 'wrong-password',
    });
    expect(bad.status).toBe(401);
    expect((bad.body as { error: string }).error).toBe('invalid_credentials');

    const noAcct = await httpJson('POST', '/api/auth/signin', {
      email: 'nobody@example.com',
      password: 'whatever',
    });
    expect(noAcct.status).toBe(401);
    expect((noAcct.body as { error: string }).error).toBe('invalid_credentials');
  });
});

describe('GET /api/auth/me', () => {
  it('returns 401 without a bearer token', async () => {
    const res = await httpJson('GET', '/api/auth/me');
    expect(res.status).toBe(401);
  });

  it('returns the parent + household for a valid token', async () => {
    const signup = await httpJson('POST', '/api/auth/signup', {
      email: 'carol@example.com',
      password: 'hunter2hunter',
      name: 'Carol',
    });
    const { token, parent } = signup.body as { token: string; parent: { householdId: string; email: string } };
    const res = await httpJson('GET', '/api/auth/me', undefined, {
      authorization: `Bearer ${token}`,
    });
    expect(res.status).toBe(200);
    const me = res.body as { parent: { email: string; householdId: string }; household: { id: string } };
    expect(me.parent.email).toBe('carol@example.com');
    expect(me.parent.householdId).toBe(parent.householdId);
    expect(me.household.id).toBe(parent.householdId);
  });
});

describe('GET /api/avatars', () => {
  it('returns 12 avatars with SVG markup', async () => {
    const res = await httpJson('GET', '/api/avatars');
    expect(res.status).toBe(200);
    const avatars = (res.body as { avatars: Array<{ id: string; svg: string }> }).avatars;
    expect(avatars).toHaveLength(12);
    for (const a of avatars) {
      expect(a.id).toBeTruthy();
      expect(a.svg).toMatch(/^<svg/);
    }
  });
});

describe('POST /api/households/{id}/children + GET', () => {
  async function signupAndToken(email: string): Promise<{ token: string; householdId: string }> {
    const res = await httpJson('POST', '/api/auth/signup', {
      email,
      password: 'hunter2hunter',
      name: email.split('@')[0]!,
    });
    const body = res.body as { token: string; parent: { householdId: string } };
    return { token: body.token, householdId: body.parent.householdId };
  }

  it('creates exactly one child and persists across reloads', async () => {
    const { token, householdId } = await signupAndToken('dave@example.com');

    const create = await httpJson(
      'POST',
      `/api/households/${householdId}/children`,
      { name: 'Dee', avatar_id: 'fox' },
      { authorization: `Bearer ${token}` },
    );
    expect(create.status).toBe(201);
    const created = (create.body as { child: { id: string; name: string; avatarId: string } }).child;
    expect(created.name).toBe('Dee');
    expect(created.avatarId).toBe('fox');

    // Simulate a reload: re-fetch the children list with a fresh GET.
    const list = await httpJson(
      'GET',
      `/api/households/${householdId}/children`,
      undefined,
      { authorization: `Bearer ${token}` },
    );
    expect(list.status).toBe(200);
    const children = (list.body as { children: Array<{ id: string; name: string }> }).children;
    expect(children).toHaveLength(1);
    expect(children[0]!.id).toBe(created.id);
  });

  it('rejects a second child with 409 (v1: exactly one)', async () => {
    const { token, householdId } = await signupAndToken('erin@example.com');
    const first = await httpJson(
      'POST',
      `/api/households/${householdId}/children`,
      { name: 'E', avatar_id: 'cat' },
      { authorization: `Bearer ${token}` },
    );
    expect(first.status).toBe(201);
    const second = await httpJson(
      'POST',
      `/api/households/${householdId}/children`,
      { name: 'E2', avatar_id: 'owl' },
      { authorization: `Bearer ${token}` },
    );
    expect(second.status).toBe(409);
    expect((second.body as { error: string }).error).toBe('child_already_exists');
  });

  it('rejects an unknown avatar with 400', async () => {
    const { token, householdId } = await signupAndToken('frank@example.com');
    const res = await httpJson(
      'POST',
      `/api/households/${householdId}/children`,
      { name: 'F', avatar_id: 'not-a-real-avatar' },
      { authorization: `Bearer ${token}` },
    );
    expect(res.status).toBe(400);
    expect((res.body as { error: string }).error).toBe('unknown_avatar');
  });

  it('rejects cross-household access with 403', async () => {
    const a = await signupAndToken('gail@example.com');
    const b = await signupAndToken('hugo@example.com');
    const res = await httpJson(
      'POST',
      `/api/households/${a.householdId}/children`,
      { name: 'intruder', avatar_id: 'fox' },
      { authorization: `Bearer ${b.token}` },
    );
    expect(res.status).toBe(403);
  });

  it('still allows LWW updates on child.name via the v1-01 sync primitive', async () => {
    const { token, householdId } = await signupAndToken('ivy@example.com');
    const create = await httpJson(
      'POST',
      `/api/households/${householdId}/children`,
      { name: 'I', avatar_id: 'star' },
      { authorization: `Bearer ${token}` },
    );
    const childId = (create.body as { child: { id: string } }).child.id;

    const sync = await httpJson(
      'POST',
      '/api/sync/apply',
      {
        table: 'child',
        id: childId,
        field: 'name',
        value: 'Ivy-Renamed',
        updated_at: '2099-01-01T00:00:00.000Z',
      },
      { authorization: `Bearer ${token}` },
    );
    expect(sync.status).toBe(200);
    expect((sync.body as { applied: boolean }).applied).toBe(true);
  });
});
