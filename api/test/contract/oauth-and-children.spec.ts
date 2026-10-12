// Contract test for the v1-03 OAuth (Google + Apple) and children-profile
// endpoints. Builds on the auth-routes pattern:
//
//   signup -> /me -> POST /api/households/:id/children
//           -> GET /api/households/:id/children (new request -> same row)
//           -> POST again -> 409
//
// Plus the OAuth path:
//   mint HS256 id_token -> POST /api/auth/oauth/{google,apple}
//   new email   -> creates a fresh parent + household
//   repeat      -> identity match returns the same parent
//   email-link  -> second oauth with the same email but different subject
//                  links the identity to the existing parent.
//
// Acceptance:
//   - All four endpoints exercised and green.
//   - Apple + Google mock strategies (HS256 in test) — no real IdP.
//   - 409 path for duplicate child covered.

import { afterAll, beforeAll, describe, expect, it } from 'vitest';
import http from 'node:http';
import { execSync } from 'node:child_process';
import { mkdtempSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import jwt from 'jsonwebtoken';

const MIGRATION_SQL = readFileSync(
  join(process.cwd(), '..', 'prisma', 'migrations', '0001_init', 'migration.sql'),
  'utf8',
);

const OAUTH_TEST_HS_SECRET = 'oauth-test-secret-please-do-not-use-in-prod';

let containerId = '';
let port = 0;
let serverPort = Number.parseInt(process.env.PORT ?? '0', 10);
let server: Awaited<ReturnType<typeof import('../../src/index.js')>> | undefined;

interface HttpResp {
  status: number;
  body: unknown;
}

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
          resolve({ status: res.statusCode ?? 0, body: parsed });
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

function uniqueEmail(label: string): string {
  return `${label}-${Date.now()}-${Math.floor(Math.random() * 1e6)}@example.test`;
}

/** Mint a test HS256 id_token that the OAuth verifier accepts. */
function mintIdToken(
  provider: 'google' | 'apple',
  sub: string,
  email: string | null,
): string {
  return jwt.sign(
    { sub, email, provider },
    OAUTH_TEST_HS_SECRET,
    { algorithm: 'HS256', expiresIn: 600 },
  );
}

beforeAll(async () => {
  if (!serverPort) {
    serverPort = await pickPort();
    process.env.PORT = String(serverPort);
  }
  process.env.NODE_ENV = process.env.NODE_ENV ?? 'test';
  process.env.JWT_SECRET =
    process.env.JWT_SECRET ?? 'contract-test-secret-please-do-not-use-in-prod';
  // Force the OAuth verifier into HS256 test mode. The env var is read on
  // every request, so it just needs to be set before the server handles a
  // request — no rebuild required.
  process.env.OAUTH_TEST_MODE = 'true';
  process.env.OAUTH_TEST_HS_SECRET = OAUTH_TEST_HS_SECRET;

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

  const tmp = mkdtempSync(join(tmpdir(), 'chorehero-mariadb-oauth-'));
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

  // Re-bind prisma to the docker port.
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

// ---------------------------------------------------------------------------
// Children-profile endpoints (signup -> /me -> POST child -> GET child)
// ---------------------------------------------------------------------------
describe('children profile endpoints (JWT-protected)', () => {
  async function signupParent(
    label: string,
  ): Promise<{
    token: string;
    parentId: string;
    householdId: string;
    email: string;
  }> {
    const email = uniqueEmail(label);
    const res = await httpJson('POST', '/api/auth/signup', {
      email,
      password: 'hunter22hunter',
      displayName: `${label} parent`,
    });
    expect(res.status).toBe(201);
    const body = res.body as {
      token: string;
      parent: { id: string };
      household: { id: string };
    };
    return {
      token: body.token,
      parentId: body.parent.id,
      householdId: body.household.id,
      email,
    };
  }

  it('GET /me round-trips the household id we will use for children', async () => {
    const { token, householdId, email } = await signupParent('me-roundtrip');
    const me = await httpJson('GET', '/api/auth/me', undefined, {
      authorization: `B${'earer'} ${token}`,
          });
          expect(me.status).toBe(200);
    const meBody = me.body as {
      parent: { email: string };
      household: { id: string };
    };
    expect(meBody.parent.email).toBe(email);
    expect(meBody.household.id).toBe(householdId);
  });

  it('creates a child and re-reads it across two requests (LWW version survives reload)', async () => {
    const { token, householdId } = await signupParent('child-reload');

    const create = await httpJson(
      'POST',
      `/api/households/${householdId}/children`,
      { name: 'Mira', avatar_id: 'fox.svg' },
      { authorization: `Bearer ${token}` },
    );
    expect(create.status).toBe(201);
    const createBody = create.body as {
      child: {
        id: string;
        householdId: string;
        name: string;
        avatarId: string;
        createdAt: string;
        nameUpdatedAt: string | null;
        avatarIdUpdatedAt: string | null;
      };
    };
    expect(createBody.child.name).toBe('Mira');
    expect(createBody.child.avatarId).toBe('fox.svg');
    expect(createBody.child.householdId).toBe(householdId);
    expect(createBody.child.nameUpdatedAt).toBeTruthy();
    expect(createBody.child.avatarIdUpdatedAt).toBeTruthy();

    // New "page reload" — drop the prior request context. We reuse the
    // token because it's the same session, but the GET constructs the
    // child view from a fresh DB read.
    const list = await httpJson(
      'GET',
      `/api/households/${householdId}/children`,
      undefined,
      { authorization: `Bearer ${token}` },
    );
    expect(list.status).toBe(200);
    const listBody = list.body as {
      children: Array<{
        id: string;
        name: string;
        avatarId: string;
        nameUpdatedAt: string | null;
        avatarIdUpdatedAt: string | null;
      }>;
    };
    expect(listBody.children).toHaveLength(1);
    const reloaded = listBody.children[0];
    expect(reloaded.id).toBe(createBody.child.id);
    expect(reloaded.name).toBe('Mira');
    expect(reloaded.avatarId).toBe('fox.svg');
    // LWW versions identical to the create response — the row wasn't
    // mutated, so the per-field timestamps must match byte-for-byte.
    expect(reloaded.nameUpdatedAt).toBe(createBody.child.nameUpdatedAt);
    expect(reloaded.avatarIdUpdatedAt).toBe(createBody.child.avatarIdUpdatedAt);
  });

  it('returns 409 when a second child is created for the same household', async () => {
    const { token, householdId } = await signupParent('child-dup');

    const first = await httpJson(
      'POST',
      `/api/households/${householdId}/children`,
      { name: 'First', avatar_id: 'owl.svg' },
      { authorization: `Bearer ${token}` },
    );
    expect(first.status).toBe(201);

    const second = await httpJson(
      'POST',
      `/api/households/${householdId}/children`,
      { name: 'Second', avatar_id: 'cat.svg' },
      { authorization: `Bearer ${token}` },
    );
    expect(second.status).toBe(409);
    expect((second.body as { error: string }).error).toBe('child_already_exists');
  });

  it('returns 401 on POST children without a Bearer token', async () => {
    const { householdId } = await signupParent('child-noauth');
    const res = await httpJson(
      'POST',
      `/api/households/${householdId}/children`,
      { name: 'Sneaky', avatar_id: 'ghost.svg' },
    );
    expect(res.status).toBe(401);
  });

  it('returns 404 on POST children for a household the token does not own', async () => {
    const a = await signupParent('child-foreign-a');
    const b = await signupParent('child-foreign-b');
    const res = await httpJson(
      'POST',
      `/api/households/${b.householdId}/children`,
      { name: 'Cross', avatar_id: 'crab.svg' },
      { authorization: `Bearer ${a.token}` },
    );
    expect(res.status).toBe(404);
  });

  it('rejects an invalid payload with 400', async () => {
    const { token, householdId } = await signupParent('child-bad-payload');
    const res = await httpJson(
      'POST',
      `/api/households/${householdId}/children`,
      { name: '', avatar_id: '' },
      { authorization: `Bearer ${token}` },
    );
    expect(res.status).toBe(400);
    expect((res.body as { error: string }).error).toBe('invalid_payload');
  });

  it('GET children returns an empty list for a household that never onboarded', async () => {
    const { token, householdId } = await signupParent('child-empty');
    const res = await httpJson(
      'GET',
      `/api/households/${householdId}/children`,
      undefined,
      { authorization: `Bearer ${token}` },
    );
    expect(res.status).toBe(200);
    expect((res.body as { children: unknown[] }).children).toEqual([]);
  });

  it('routes child.name mutations through /api/sync/apply (LWW apply bumps name_updated_at)', async () => {
    const { token, householdId } = await signupParent('child-lww-apply');

    const create = await httpJson(
      'POST',
      `/api/households/${householdId}/children`,
      { name: 'Original', avatar_id: 'fox.svg' },
      { authorization: `Bearer ${token}` },
    );
    expect(create.status).toBe(201);
    const childId = (create.body as { child: { id: string } }).child.id;

    const originalNameUpdatedAt = (create.body as {
      child: { nameUpdatedAt: string };
    }).child.nameUpdatedAt;

    // Apply a name mutation strictly later than create.
    const later = new Date(Date.parse(originalNameUpdatedAt) + 5_000).toISOString();
    const apply = await httpJson(
      'POST',
      '/api/sync/apply',
      {
        table: 'child',
        id: childId,
        field: 'name',
        value: 'Updated',
        updated_at: later,
      },
      { authorization: `Bearer ${token}` },
    );
    expect(apply.status).toBe(200);
    expect((apply.body as { applied: boolean }).applied).toBe(true);

    // GET children must reflect the new name AND the bumped timestamp.
    const list = await httpJson(
      'GET',
      `/api/households/${householdId}/children`,
      undefined,
      { authorization: `Bearer ${token}` },
    );
    expect(list.status).toBe(200);
    const reloaded = (list.body as {
      children: Array<{ name: string; nameUpdatedAt: string }>;
    }).children[0];
    expect(reloaded.name).toBe('Updated');
    expect(reloaded.nameUpdatedAt).toBe(later);
  });

  it('replays of an LWW mutation are no-ops (idempotent sync)', async () => {
    const { token, householdId } = await signupParent('child-lww-replay');

    const create = await httpJson(
      'POST',
      `/api/households/${householdId}/children`,
      { name: 'Replay', avatar_id: 'fox.svg' },
      { authorization: `Bearer ${token}` },
    );
    expect(create.status).toBe(201);
    const childId = (create.body as { child: { id: string } }).child.id;
    const baseTs = (create.body as {
      child: { avatarIdUpdatedAt: string };
    }).child.avatarIdUpdatedAt;

    const later = new Date(Date.parse(baseTs) + 5_000).toISOString();

    const first = await httpJson(
      'POST',
      '/api/sync/apply',
      {
        table: 'child',
        id: childId,
        field: 'avatar_id',
        value: 'panda.svg',
        updated_at: later,
      },
      { authorization: `Bearer ${token}` },
    );
    expect(first.status).toBe(200);
    expect((first.body as { applied: boolean }).applied).toBe(true);

    const replay = await httpJson(
      'POST',
      '/api/sync/apply',
      {
        table: 'child',
        id: childId,
        field: 'avatar_id',
        value: 'should-not-overwrite.svg',
        updated_at: later,
      },
      { authorization: `Bearer ${token}` },
    );
    expect(replay.status).toBe(200);
    expect((replay.body as { applied: boolean; reason?: string }).applied).toBe(false);
    expect((replay.body as { reason?: string }).reason).toBe('stale');
  });
});

// ---------------------------------------------------------------------------
// OAuth (mock HS256 IdP tokens, no real network)
// ---------------------------------------------------------------------------
describe('OAuth endpoints (Google + Apple, mock HS256 strategies)', () => {
  function authHeader(token: string): Record<string, string> {
    return { authorization: `Bearer ${token}` };
  }

  it('Google: creates a new parent + household on first sight', async () => {
    const sub = `g-sub-${Date.now()}-${Math.floor(Math.random() * 1e6)}`;
    const email = uniqueEmail('oauth-g-new');
    const idToken = mintIdToken('google', sub, email);

    const res = await httpJson('POST', '/api/auth/oauth/google', { id_token: idToken });
    expect(res.status).toBe(200);
    const body = res.body as {
      token: string;
      parent: { id: string; email: string };
      household: { id: string; timezone: string };
    };
    expect(body.token).toBeTruthy();
    expect(body.parent.email).toBe(email);
    expect(body.household.timezone).toBeTruthy();

    // JWT round-trips into /me.
    const me = await httpJson('GET', '/api/auth/me', undefined, authHeader(body.token));
    expect(me.status).toBe(200);
    expect((me.body as { parent: { id: string } }).parent.id).toBe(body.parent.id);
  });

  it('Google: same (provider, subject) returns the same parent on repeat login', async () => {
    const sub = `g-sub-repeat-${Date.now()}`;
    const email = uniqueEmail('oauth-g-repeat');
    const idToken = mintIdToken('google', sub, email);

    const first = await httpJson('POST', '/api/auth/oauth/google', { id_token: idToken });
    expect(first.status).toBe(200);
    const second = await httpJson('POST', '/api/auth/oauth/google', { id_token: idToken });
    expect(second.status).toBe(200);
    expect((second.body as { parent: { id: string } }).parent.id).toBe(
      (first.body as { parent: { id: string } }).parent.id,
    );
  });

  it('Apple: links to an existing parent when the email matches', async () => {
    // Bootstrap a parent with email/password, then sign in via Apple with
    // the same email but a different subject — we should land on the same
    // parent.
    const email = uniqueEmail('oauth-apple-link');
    const signup = await httpJson('POST', '/api/auth/signup', {
      email,
      password: 'hunter22hunter',
      displayName: 'Apple Link',
    });
    expect(signup.status).toBe(201);
    const existingParentId = (signup.body as { parent: { id: string } }).parent.id;

    const idToken = mintIdToken(
      'apple',
      `apple-sub-${Date.now()}`,
      email,
    );
    const res = await httpJson('POST', '/api/auth/oauth/apple', { id_token: idToken });
    expect(res.status).toBe(200);
    expect((res.body as { parent: { id: string } }).parent.id).toBe(existingParentId);
  });

  it('Apple: unknown email creates a fresh parent + household', async () => {
    const sub = `apple-sub-${Date.now()}`;
    const email = uniqueEmail('oauth-apple-fresh');
    const res = await httpJson('POST', '/api/auth/oauth/apple', {
      id_token: mintIdToken('apple', sub, email),
    });
    expect(res.status).toBe(200);
    expect((res.body as { parent: { email: string } }).parent.email).toBe(email);
  });

  it('rejects an id_token signed with a different provider tag', async () => {
    // Mint a Google-tagged token, post it to /api/auth/oauth/apple —
    // the verifier must reject because the embedded provider tag is wrong.
    const idToken = mintIdToken('google', 'g-sub-x', 'oops@example.test');
    const res = await httpJson('POST', '/api/auth/oauth/apple', { id_token: idToken });
    expect(res.status).toBe(401);
  });

  it('rejects an id_token signed with the wrong HS secret', async () => {
    const bogus = jwt.sign(
      { sub: 'x', email: 'x@example.test', provider: 'google' },
      'wrong-secret-wrong-secret-wrong-secret',
      { algorithm: 'HS256', expiresIn: 600 },
    );
    const res = await httpJson('POST', '/api/auth/oauth/google', { id_token: bogus });
    expect(res.status).toBe(401);
  });

  it('rejects a missing id_token with 400', async () => {
    const res = await httpJson('POST', '/api/auth/oauth/google', {});
    expect(res.status).toBe(400);
  });
});