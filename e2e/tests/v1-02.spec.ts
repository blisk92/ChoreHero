// v1-02 e2e suite.
//
// Two tests cover the parent-onboarding path end-to-end against a
// live API + SPA pair:
//
//   1. Sign up through the SPA → onboarding step → create child
//      profile → reload SPA → sign in again → child row is still
//      present on the dashboard. This is the exact "reload and the
//      child row is still there" check the spec calls out — since
//      v1 deliberately keeps the JWT in memory (no refresh-token
//      rotation yet), the reload effectively logs the parent out, and
//      the recovery loop is a sign-in that re-fetches the children
//      list.
//
//   2. Sign in from a second browser context with the same credentials
//      and confirm both sessions can call /api/auth/me — proves
//      multi-device parent sessions are first-class.
//
// API base URL defaults to staging; override with E2E_API_URL /
// E2E_SPA_URL when running elsewhere.
import { test, expect, type APIRequestContext, type BrowserContext } from '@playwright/test';
import { env } from '../playwright.config';
import { randomUUID } from 'node:crypto';

interface ChildRow {
  id: string;
  name: string;
  avatarId: string;
}

async function getChildren(
  req: APIRequestContext,
  token: string,
  householdId: string,
): Promise<ChildRow[]> {
  const res = await req.get(`${env.API_BASE_URL}/api/households/${householdId}/children`, {
    headers: { authorization: `Bearer ${token}` },
  });
  expect(res, 'GET /children').toBeOK();
  const json = (await res.json()) as { children: ChildRow[] };
  return json.children;
}

test('v1-02: sign up through SPA → create child → reload → child row still present', async ({ browser }) => {
  const ctx: BrowserContext = await browser.newContext();
  const email = `e2e-${randomUUID()}@example.com`;
  const password = 'hunter2hunter';
  const childName = 'Maya';

  // 1. Sign up via the SPA's sign-up screen.
  const spa = await ctx.newPage();
  await spa.goto(`${env.SPA_BASE_URL}/sign-up`);
  await spa.fill('input[type="text"]', 'E2E Parent');
  await spa.fill('input[type="email"]', email);
  await spa.fill('input[autocomplete="new-password"]', password);
  await spa.locator('input[type="password"]').nth(1).fill(password);
  await spa.click('button[type="submit"]');
  await spa.waitForURL('**/onboarding/child');

  // 2. Pick name + avatar in the onboarding step.
  await spa.fill('input[type="text"]', childName);
  await spa.locator('button.tile').first().click();
  await spa.click('button[type="submit"]');
  await spa.waitForURL('**/dashboard');

  // 3. Reload the SPA. The token lives in memory so this logs the
  // parent out; the dashboard /onboarding route guard redirects to
  // /sign-in.
  await spa.reload();
  await spa.waitForURL('**/sign-in');

  // 4. Sign back in through the SPA — proves the second device /
  // recovery loop works.
  await spa.fill('input[type="email"]', email);
  await spa.fill('input[type="password"]', password);
  await spa.click('button[type="submit"]');
  await spa.waitForURL('**/dashboard');

  // 5. The household + child row lives on the server, not in memory.
  // Sign back in via API and confirm the child row is present.
  const req = await ctx.request;
  const signin = await req.post(`${env.API_BASE_URL}/api/auth/signin`, {
    data: { email, password },
  });
  expect(signin, 'sign-in OK').toBeOK();
  const bundle = (await signin.json()) as { token: string; parent: { householdId: string } };
  const children = await getChildren(req, bundle.token, bundle.parent.householdId);
  expect(children).toHaveLength(1);
  expect(children[0]!.name).toBe(childName);

  await ctx.close();
});

test('v1-02: parallel parent sessions on a second browser context', async ({ browser, request }) => {
  // First sign-up establishes a parent.
  const email = `e2e-parallel-${randomUUID()}@example.com`;
  const password = 'hunter2hunter';
  const signup = await request.post(`${env.API_BASE_URL}/api/auth/signup`, {
    data: { email, password, name: 'Parallel Parent' },
  });
  expect(signup, 'signup OK').toBeOK();
  const bundle1 = (await signup.json()) as { token: string; parent: { id: string; householdId: string } };

  // Second sign-in from a fresh browser context (simulates a second
  // device). Same email/password. The v1 spec explicitly rejects
  // 401'ing concurrent sessions; both tokens must be valid.
  const ctx2: BrowserContext = await browser.newContext();
  const signin = await (await ctx2.request).post(`${env.API_BASE_URL}/api/auth/signin`, {
    data: { email, password },
  });
  expect(signin, 'second sign-in OK').toBeOK();
  const bundle2 = (await signin.json()) as { token: string; parent: { id: string; householdId: string } };

  // Same Parent.id, distinct tokens, both can call /api/auth/me.
  expect(bundle2.parent.id).toBe(bundle1.parent.id);
  expect(bundle2.token).not.toBe(bundle1.token);

  for (const [label, token] of [['first', bundle1.token], ['second', bundle2.token]] as const) {
    const me = await request.get(`${env.API_BASE_URL}/api/auth/me`, {
      headers: { authorization: `Bearer ${token}` },
    });
    expect(me.ok(), `me OK on ${label} session`).toBe(true);
  }

  await ctx2.close();
});
