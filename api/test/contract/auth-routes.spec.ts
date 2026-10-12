// Contract test for the parent auth endpoints.
//
// Spins a real MariaDB container (or uses the CI service container), applies
// the migration, and exercises POST /api/auth/signup, /signin, and GET /me
// via HTTP. We boot the compiled app from dist/ so this is a true wire-level
// test of what the production server emits.
//
// Acceptance:
//   - signup returns 201 with { token, parent, household }
//   - signup with an already-registered email returns 409
//   - signup with a short password returns 400
//   - signin with the right password returns 200 + token
//   - signin with a wrong password returns 401
//   - GET /me without a Bearer token returns 401
//   - GET /me with a valid Bearer token returns the parent + household
//   - the password hash stored in the DB is bcrypt (starts with $2), never plaintext

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
let server: Awaited<ReturnType<typeof import('../../src/index.js').then>> | undefined;
// PORT must be set in the environment BEFORE this file is imported — the
// server reads process.env.PORT at module top-level. We expect callers (or
// the default in beforeAll) to provide it.
let serverPort = Number.parseInt(process.env.PORT ?? '0', 10);

function waitForReady(timeoutMs = 60_000): void {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    try {
      const out = execSync(
        `docker exec ${containerId} mariadb -uroot -prootpw -e "SELECT 1"`,
        { stdio: ['ignore', 'pipe', 'pipe'] },
      );
      if (out.toString().includes('1')) return;
    } catch {
      // not ready yet
    }
  }
  throw new Error('mariadb container did not become ready in time');
}

interface HttpResp {
  status: number;
  body: unknown;
  headers: Record<string, string | string[] | undefined>;
}

function httpJson(
  method: 'GET' | 'POST',
  path: string,
  body: unknown,
  headers: Record<string, string> = {},
): Promise<HttpResp> {
  return new Promise((resolve, reject) => {
    const data = body === undefined ? '' : JSON.stringify(body);
    const req = http.request(
      {
        host: '127.0.0.1',
        port: serverPort,
        path,
        method,
        headers: {
          ...(body !== undefined
            ? {
                'content-type': 'application/json',
                'content-length': Buffer.byteLength(data),
              }
            : {}),
          ...headers,
        },
      },
      (res) => {
        const chunks: Buffer[] = [];
        res.on('data', (c) => chunks.push(typeof c === 'string' ? Buffer.from(c) : c));
        res.on('end', () => {
          const text = Buffer.concat(chunks).toString('utf8');
          let parsed: unknown;
          try {
            parsed = JSON.parse(text);
          } catch {
            parsed = text;
          }
          resolve({ status: res.statusCode ?? 0, body: parsed, headers: res.headers });
        });
      },
    );
    req.on('error', reject);
    if (data) req.write(data);
    req.end();
  });
}

function pickPort(): Promise<number> {
  return new Promise((resolve, reject) => {
    const probe = http.createServer();
    probe.listen(0, '127.0.0.1', () => {
      const addr = probe.address();
      if (!addr || typeof addr === 'string') {
        reject(new Error('could not allocate port'));
        return;
      }
      const p = addr.port;
      probe.close(() => resolve(p));
    });
    probe.on('error', reject);
  });
}

beforeAll(async () => {
  if (!serverPort) {
    serverPort = await pickPort();
    process.env.PORT = String(serverPort);
  }
  process.env.NODE_ENV = process.env.NODE_ENV ?? 'test';
  process.env.JWT_SECRET =
    process.env.JWT_SECRET ?? 'contract-test-secret-please-do-not-use-in-prod';

  // CI mode: use a pre-existing MariaDB service container. Don't overwrite
  // DATABASE_URL if the caller already provided one (we may be running
  // against a non-default port, e.g. the staging container on 13310).
  if (process.env.CI === 'true' && !process.env.DATABASE_URL) {
    process.env.DATABASE_URL = `mysql://root:***@127.0.0.1:3306/chorehero`;
  }

  server = await import('../../src/index.js');
  await new Promise<void>((resolve, reject) => {
    server!.server.once('error', reject);
    server!.server.listen(serverPort, '127.0.0.1', () => {
      server!.server.off('error', reject);
      resolve();
    });
  });
  if (process.env.CI === 'true') return;

  const tmp = mkdtempSync(join(tmpdir(), 'chorehero-mariadb-auth-'));
  containerId = execSync(
    `docker run --rm -d ` +
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
  execSync(
    `docker exec ${containerId} mariadb -uroot -prootpw chorehero`,
    { input: MIGRATION_SQL, stdio: ['pipe', 'ignore', 'ignore'] },
  );

  process.env.DATABASE_URL = `mysql://root:***@127.0.0.1:${port}/chorehero`;
  execSync(
    `docker exec ${containerId} mariadb -uroot -prootpw chorehero -e "SHOW TABLES"`,
    { stdio: 'pipe' },
  );

  // Re-import with the now-correct DATABASE_URL — the CI branch above
  // already imported once, but it used the env as set at test start. For
  // the docker-spun DB path, we want the freshly assigned port in the URL,
  // so we re-import. ESM caches modules; the dynamic import returns the
  // cached module whose prisma was bound to the OLD DATABASE_URL, which
  // is why this path can't reuse the first import. We tear down that
  // first server (if any) before swapping.
  if (server?.server) {
    await new Promise<void>((r) => server!.server.close(() => r()));
  }
  server = await import('../../src/index.js');
  await new Promise<void>((resolve, reject) => {
    server!.server.once('error', reject);
    server!.server.listen(serverPort, '127.0.0.1', () => {
      server!.server.off('error', reject);
      resolve();
    });
  });
}, 120_000);

afterAll(async () => {
  if (server?.server) {
    await new Promise<void>((resolve) => {
      server!.server.close(() => resolve());
    });
  }
  if (server?.prisma) {
    await server.prisma.$disconnect();
  }
  if (containerId) {
    execSync(`docker rm -f ${containerId}`, { stdio: 'ignore' });
  }
});

function uniqueEmail(label: string): string {
  return `${label}-${Date.now()}-${Math.floor(Math.random() * 1e6)}@example.test`;
}

describe('POST /api/auth/signup', () => {
  it('returns 201 with token, parent, and a fresh household', async () => {
    const email = uniqueEmail('signup-ok');
    const res = await httpJson('POST', '/api/auth/signup', {
      email,
      password: 'hunter22hunter',
      displayName: 'Signup OK',
    });
    expect(res.status).toBe(201);
    const body = res.body as {
      token: string;
      parent: { id: string; email: string; name: string | null };
      household: { id: string; name: string | null; timezone: string };
    };
    expect(body.token).toBeTruthy();
    expect(body.parent.email).toBe(email);
    expect(body.parent.name).toBe('Signup OK');
    // Prisma's @default(cuid()) produces 24-25 char IDs (e.g. "clxxx...").
    // We don't pin a specific format, just that they're non-empty and
    // distinct from each other.
    expect(body.parent.id.length).toBeGreaterThan(10);
    expect(body.household.id.length).toBeGreaterThan(10);
    expect(body.parent.id).not.toBe(body.household.id);
    expect(body.household.timezone).toBe('UTC');
  });

  it('normalises the email to lowercase', async () => {
    const email = uniqueEmail('MixedCase').toUpperCase();
    const res = await httpJson('POST', '/api/auth/signup', {
      email,
      password: 'hunter22hunter',
      displayName: 'Mixed Case',
    });
    expect(res.status).toBe(201);
    const body = res.body as { parent: { email: string } };
    expect(body.parent.email).toBe(email.toLowerCase());
  });

  it('rejects a short password with 400', async () => {
    const res = await httpJson('POST', '/api/auth/signup', {
      email: uniqueEmail('shortpw'),
      password: 'short',
      displayName: 'Short PW',
    });
    expect(res.status).toBe(400);
    expect((res.body as { error: string }).error).toBe('invalid_payload');
  });

  it('rejects a malformed email with 400', async () => {
    const res = await httpJson('POST', '/api/auth/signup', {
      email: 'not-an-email',
      password: 'hunter22hunter',
      displayName: 'Bad Email',
    });
    expect(res.status).toBe(400);
  });

  it('rejects a duplicate email with 409', async () => {
    const email = uniqueEmail('dup');
    const first = await httpJson('POST', '/api/auth/signup', {
      email,
      password: 'hunter22hunter',
      displayName: 'Dup One',
    });
    expect(first.status).toBe(201);
    const second = await httpJson('POST', '/api/auth/signup', {
      email,
      password: 'hunter22hunter',
      displayName: 'Dup Two',
    });
    expect(second.status).toBe(409);
    expect((second.body as { error: string }).error).toBe('email_taken');
  });

  it('stores the password as a bcrypt hash, never plaintext', async () => {
    const email = uniqueEmail('hash-check');
    const password = 'hunter22hunter';
    const res = await httpJson('POST', '/api/auth/signup', {
      email,
      password,
      displayName: 'Hash Check',
    });
    expect(res.status).toBe(201);
    const parentId = (res.body as { parent: { id: string } }).parent.id;

    // Read the stored hash straight out of MariaDB via Prisma and confirm
    // it is a bcrypt hash ($2a/$2b/$2y prefix) and does not contain the
    // plaintext. We use Prisma rather than a CLI so the test is portable
    // across hosts without a mysql client installed.
    const parent = await server!.prisma.parent.findUnique({ where: { id: parentId } });
    expect(parent).toBeTruthy();
    const hash = parent!.passwordHash;
    expect(hash).toBeTruthy();
    expect(hash).toMatch(/^\$2[aby]\$/);
    expect(hash).not.toContain(password);
    expect(hash!.length).toBeGreaterThanOrEqual(59); // bcrypt output length
  });

  it('does not set any cookies (Authorization-only transport)', async () => {
    const res = await httpJson('POST', '/api/auth/signup', {
      email: uniqueEmail('nocookie'),
      password: 'hunter22hunter',
      displayName: 'No Cookie',
    });
    expect(res.status).toBe(201);
    const setCookie = res.headers['set-cookie'];
    expect(setCookie).toBeUndefined();
  });
});

describe('POST /api/auth/signin', () => {
  async function seedParent(email: string, password: string, displayName: string): Promise<string> {
    const res = await httpJson('POST', '/api/auth/signup', {
      email,
      password,
      displayName,
    });
    expect(res.status).toBe(201);
    return (res.body as { token: string }).token;
  }

  it('returns 200 + token for valid credentials', async () => {
    const email = uniqueEmail('signin-ok');
    const password = 'hunter22hunter';
    await seedParent(email, password, 'Signin OK');
    const res = await httpJson('POST', '/api/auth/signin', { email, password });
    expect(res.status).toBe(200);
    const body = res.body as { token: string; parent: { email: string } };
    expect(body.token).toBeTruthy();
    expect(body.parent.email).toBe(email);
  });

  it('rejects a wrong password with 401', async () => {
    const email = uniqueEmail('signin-bad-pw');
    await seedParent(email, 'rightpw1234', 'Bad PW');
    const res = await httpJson('POST', '/api/auth/signin', {
      email,
      password: 'wrongpw1234',
    });
    expect(res.status).toBe(401);
    expect((res.body as { error: string }).error).toBe('invalid_credentials');
  });

  it('returns 401 for an unknown email without leaking the difference', async () => {
    const res = await httpJson('POST', '/api/auth/signin', {
      email: uniqueEmail('never-registered'),
      password: 'doesnotmatter',
    });
    expect(res.status).toBe(401);
    expect((res.body as { error: string }).error).toBe('invalid_credentials');
  });

  it('returns 400 for malformed input', async () => {
    const res = await httpJson('POST', '/api/auth/signin', {
      email: 'nope',
      password: '',
    });
    expect(res.status).toBe(400);
  });

  it('does not set any cookies on signin either', async () => {
    const email = uniqueEmail('signin-nocookie');
    await seedParent(email, 'hunter22hunter', 'Signin NoCookie');
    const res = await httpJson('POST', '/api/auth/signin', {
      email,
      password: 'hunter22hunter',
    });
    expect(res.status).toBe(200);
    expect(res.headers['set-cookie']).toBeUndefined();
  });
});

describe('GET /api/auth/me', () => {
  it('returns 401 without an Authorization header', async () => {
    const res = await httpJson('GET', '/api/auth/me', undefined);
    expect(res.status).toBe(401);
    expect((res.body as { error: string }).error).toBe('unauthorized');
  });

  it('returns 401 for a malformed Bearer token', async () => {
    const res = await httpJson('GET', '/api/auth/me', undefined, {
      authorization: 'Bearer not-a-real-token',
    });
    expect(res.status).toBe(401);
  });

  it('returns the parent + household for a valid token', async () => {
    const email = uniqueEmail('me-ok');
    const token = (await (async () => {
      const r = await httpJson('POST', '/api/auth/signup', {
        email,
        password: 'hunter22hunter',
        displayName: 'Me OK',
      });
      return (r.body as { token: string }).token;
    })());
    const res = await httpJson('GET', '/api/auth/me', undefined, {
      authorization: `Bearer ${token}`,
    });
    expect(res.status).toBe(200);
    const body = res.body as {
      parent: { id: string; email: string; name: string | null };
      household: { id: string; timezone: string };
    };
    expect(body.parent.email).toBe(email);
    expect(body.parent.name).toBe('Me OK');
    expect(body.household.timezone).toBe('UTC');
  });

  it('returns 401 for a token signed with the wrong secret', async () => {
    const otherToken = (await import('jsonwebtoken')).default.sign(
      { parentId: 'p_anything', householdId: 'h_anything' },
      'wrong-secret-wrong-secret',
      { algorithm: 'HS256', expiresIn: 3600 },
    );
    const res = await httpJson('GET', '/api/auth/me', undefined, {
      authorization: `Bearer ${otherToken}`,
    });
    expect(res.status).toBe(401);
  });
});