// OAuth (Google + Apple) social-auth for parents.
//
// Wire shape:
//   POST /api/auth/oauth/google  { id_token: string } -> { token, parent, household }
//   POST /api/auth/oauth/apple   { id_token: string } -> { token, parent, household }
//
// We accept the IdP's ID-token JWT in the request body (the SPA gets it from
// the platform's sign-in SDK and forwards it). The server verifies the
// signature and standard claims, then resolves `(provider, subject)` to a
// Parent row:
//
//   1. (oauth_provider, oauth_subject) match -> reuse the existing Parent.
//      This is the "log in with Google" path on subsequent visits.
//   2. No subject match, but email matches an existing Parent -> link the
//      OAuth identity to that Parent. Covers the case where the user signed
//      up with email/password first and later used Google with the same
//      email.
//   3. No subject match and no email match -> create a new Parent + Household.
//
// The verification strategy lives in `passport.Strategy` (custom strategy)
// so the OAuth routes use `passport.authenticate(...)` like any other
// Passport-based login flow — the card calls for "Passport strategies".
//
// IdP signature verification
// --------------------------
// In production we verify the JWT against the IdP's published JWKS
// (Google: https://www.googleapis.com/oauth2/v3/certs,
//  Apple:  https://appleid.apple.com/auth/keys).
// In tests we can't hit real IdPs, so the verifier accepts HS256 tokens
// signed with a shared test secret (OAUTH_TEST_HS_SECRET). Setting
// NODE_ENV=test or OAUTH_TEST_MODE=true flips the verifier into the test
// path; otherwise it fetches the real JWKS.

import passport from 'passport';
import type { Express, Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { createPublicKey } from 'node:crypto';
import { z } from 'zod';
import type { PrismaClient } from '@prisma/client';
import { signParentToken, type JwtConfig, type ParentSession } from './jwt.js';
import { attachParentAuth } from './middleware.js';

export type OAuthProvider = 'google' | 'apple';

export interface OAuthProfile {
  provider: OAuthProvider;
  /** IdP-issued subject identifier — stable per user per IdP. */
  subject: string;
  /** Verified email from the IdP. May be null if the user declined to share. */
  email: string | null;
}

/** Shape returned to the client. Mirrors signup/signin. */
export interface OAuthResponse {
  token: string;
  parent: { id: string; email: string; name: string | null };
  household: { id: string; name: string | null; timezone: string };
}

const oauthPayloadSchema = z.object({
  id_token: z.string().min(1).max(8192),
});

/** True when the verifier should accept HS256 tokens instead of fetching JWKS. */
function isOAuthTestMode(): boolean {
  return (
    process.env.NODE_ENV === 'test' ||
    process.env.OAUTH_TEST_MODE === 'true'
  );
}

const GOOGLE_JWKS_URL = 'https://www.googleapis.com/oauth2/v3/certs';
const APPLE_JWKS_URL = 'https://appleid.apple.com/auth/keys';
const GOOGLE_ISSUER = 'https://accounts.google.com';
const APPLE_ISSUER = 'https://appleid.apple.com';

/**
 * Verify an HS256-signed test token. The test harness mints these with
 * OAUTH_TEST_HS_SECRET. We deliberately do NOT fall back to this path in
 * production — see isOAuthTestMode().
 */
function verifyTestHsToken(
  token: string,
  provider: OAuthProvider,
): { sub: string; email: string | null } {
  const secret = process.env.OAUTH_TEST_HS_SECRET;
  if (!secret || secret.length < 16) {
    throw new Error('OAUTH_TEST_HS_SECRET required (>=16 chars) for HS256 test mode');
  }
  const decoded = jwt.verify(token, secret, {
    algorithms: ['HS256'],
  }) as Record<string, unknown>;
  // The token tags its own provider so a single secret doesn't let a test
  // mint tokens for both IdPs accidentally.
  if (decoded.provider !== provider) {
    throw new Error(`provider mismatch (expected ${provider})`);
  }
  return {
    sub: String(decoded.sub),
    email:
      typeof decoded.email === 'string' ? decoded.email.toLowerCase() : null,
  };
}

interface JwksCacheEntry {
  keys: Array<{ kid: string; pem: string }>;
  fetchedAt: number;
}
const jwksCache = new Map<string, JwksCacheEntry>();
const JWKS_TTL_MS = 24 * 60 * 60 * 1000; // 24h

async function getCachedJwks(url: string): Promise<Array<{ kid: string; pem: string }>> {
  const cached = jwksCache.get(url);
  if (cached && Date.now() - cached.fetchedAt < JWKS_TTL_MS) {
    return cached.keys;
  }
  const resp = await fetch(url);
  if (!resp.ok) {
    throw new Error(`jwks fetch failed: ${resp.status}`);
  }
  const body = (await resp.json()) as { keys: Array<Record<string, unknown>> };
  const keys = body.keys.map((k) => {
    if (k.kty !== 'RSA') {
      throw new Error(`unsupported jwk kty: ${String(k.kty)} (expected RSA)`);
    }
    // SubjectPublicKeyInfo PEM — the format RS256 JWT libraries accept.
    const pem = createPublicKey({ key: k as never, format: 'jwk' })
      .export({ type: 'spki', format: 'pem' }) as string;
    return { kid: String(k.kid), pem };
  });
  jwksCache.set(url, { keys, fetchedAt: Date.now() });
  return keys;
}

async function verifyWithRemoteJwks(
  token: string,
  jwksUrl: string,
  issuer: string,
  audience: string | undefined,
): Promise<{ sub: string; email: string | null }> {
  const keys = await getCachedJwks(jwksUrl);
  let lastErr: Error | null = null;
  for (const k of keys) {
    try {
      const decoded = jwt.verify(token, k.pem, {
        algorithms: ['RS256'],
      }) as Record<string, unknown>;
      if (decoded.iss !== issuer) {
        throw new Error('iss mismatch');
      }
      if (audience !== undefined && decoded.aud !== audience) {
        throw new Error('aud mismatch');
      }
      return {
        sub: String(decoded.sub),
        email:
          typeof decoded.email === 'string' ? decoded.email.toLowerCase() : null,
      };
    } catch (e) {
      lastErr = e as Error;
      // Try the next key.
    }
  }
  throw lastErr ?? new Error('no matching jwks key');
}

export async function verifyGoogleIdToken(token: string): Promise<OAuthProfile> {
  if (isOAuthTestMode()) {
    const v = verifyTestHsToken(token, 'google');
    return { provider: 'google', subject: v.sub, email: v.email };
  }
  const audience = process.env.GOOGLE_CLIENT_ID;
  const v = await verifyWithRemoteJwks(token, GOOGLE_JWKS_URL, GOOGLE_ISSUER, audience);
  return { provider: 'google', subject: v.sub, email: v.email };
}

export async function verifyAppleIdToken(token: string): Promise<OAuthProfile> {
  if (isOAuthTestMode()) {
    const v = verifyTestHsToken(token, 'apple');
    return { provider: 'apple', subject: v.sub, email: v.email };
  }
  const audience = process.env.APPLE_CLIENT_ID;
  const v = await verifyWithRemoteJwks(token, APPLE_JWKS_URL, APPLE_ISSUER, audience);
  return { provider: 'apple', subject: v.sub, email: v.email };
}

/**
 * Resolve an OAuth profile to a Parent, linking or creating as needed.
 *
 * Returns the existing-or-new Parent row plus their Household. Callers
 * sign a JWT for the resulting session — exactly the shape signup returns.
 */
export async function resolveOrCreateOAuthParent(
  prisma: PrismaClient,
  profile: OAuthProfile,
): Promise<{
  parent: { id: string; householdId: string; email: string; name: string | null };
  household: { id: string; name: string | null; timezone: string };
}> {
  // 1. Identity match.
  const existingByIdentity = await prisma.parent.findFirst({
    where: {
      oauthProvider: profile.provider,
      oauthSubject: profile.subject,
    },
    include: { household: true },
  });
  if (existingByIdentity) {
    return {
      parent: {
        id: existingByIdentity.id,
        householdId: existingByIdentity.householdId,
        email: existingByIdentity.email,
        name: existingByIdentity.name,
      },
      household: {
        id: existingByIdentity.household.id,
        name: existingByIdentity.household.name,
        timezone: existingByIdentity.household.timezone,
      },
    };
  }

  // 2. Email match -> link identity.
  if (profile.email) {
    const byEmail = await prisma.parent.findUnique({
      where: { email: profile.email },
      include: { household: true },
    });
    if (byEmail) {
      const updated = await prisma.parent.update({
        where: { id: byEmail.id },
        data: {
          oauthProvider: profile.provider,
          oauthSubject: profile.subject,
        },
      });
      return {
        parent: {
          id: updated.id,
          householdId: updated.householdId,
          email: updated.email,
          name: updated.name,
        },
        household: {
          id: byEmail.household.id,
          name: byEmail.household.name,
          timezone: byEmail.household.timezone,
        },
      };
    }
  }

  // 3. Brand-new account. The OAuth profile may omit email (Apple can do
  // that when the user picked "Hide My Email"); in that case we still need
  // an email column to satisfy Parent.email @unique. We mint a synthetic
  // one — for v1 it's a placeholder and the parent will never see it
  // because we never render it back through any UI that takes user input.
  const email =
    profile.email ??
    `${profile.provider}-${profile.subject}@oauth.local.chorehero.invalid`;

  const now = new Date();
  try {
    const created = await prisma.$transaction(async (tx) => {
      const household = await tx.household.create({
        data: { name: null, timezone: 'UTC', createdAt: now },
      });
      const parent = await tx.parent.create({
        data: {
          householdId: household.id,
          email,
          passwordHash: null,
          oauthProvider: profile.provider,
          oauthSubject: profile.subject,
          createdAt: now,
          name: null,
        },
      });
      return { household, parent };
    });
    return {
      parent: {
        id: created.parent.id,
        householdId: created.parent.householdId,
        email: created.parent.email,
        name: created.parent.name,
      },
      household: {
        id: created.household.id,
        name: created.household.name,
        timezone: created.household.timezone,
      },
    };
  } catch (err) {
    // Email-collision race with signup. Treat it like the linking case: the
    // user just registered with email/password moments ago with the same
    // email, and we link the OAuth identity to that account.
    if (profile.email && isUniqueConstraintError(err, 'parent.email')) {
      const byEmail = await prisma.parent.findUnique({
        where: { email: profile.email },
        include: { household: true },
      });
      if (byEmail) {
        const updated = await prisma.parent.update({
          where: { id: byEmail.id },
          data: {
            oauthProvider: profile.provider,
            oauthSubject: profile.subject,
          },
        });
        return {
          parent: {
            id: updated.id,
            householdId: updated.householdId,
            email: updated.email,
            name: updated.name,
          },
          household: {
            id: byEmail.household.id,
            name: byEmail.household.name,
            timezone: byEmail.household.timezone,
          },
        };
      }
    }
    throw err;
  }
}

function isUniqueConstraintError(err: unknown, target: string): boolean {
  if (!err || typeof err !== 'object') return false;
  const message = (err as { message?: string }).message ?? '';
  return (
    message.includes('Unique constraint') &&
    message.toLowerCase().includes(target.toLowerCase())
  );
}

/**
 * Passport custom strategy for ID-token bearer payloads.
 *
 * Passport expects `authenticate(req, options)` to be overridden; we read
 * `id_token` from the parsed JSON body and dispatch to the verifier. On
 * success we call `this.success(profile)` which attaches the profile to
 * `req.user`. The router then runs the resolve-or-create logic.
 */
class IdTokenStrategy extends passport.Strategy {
  override name: string;
  private verifyFn: (token: string) => Promise<OAuthProfile>;

  constructor(name: string, verifyFn: (token: string) => Promise<OAuthProfile>) {
    super();
    this.name = name;
    this.verifyFn = verifyFn;
  }

  override authenticate(req: Request, _options?: unknown): void {
    const body = (req.body ?? {}) as Record<string, unknown>;
    const idToken = body.id_token;
    if (typeof idToken !== 'string' || idToken.length === 0) {
      this.fail({ message: 'missing id_token' }, 400);
      return;
    }
    this.verifyFn(idToken).then(
      (profile) => {
        this.success(profile);
      },
      (err: Error) => {
        this.fail({ message: 'invalid_token', reason: err.message }, 401);
      },
    );
  }
}

/**
 * Mount the OAuth endpoints. Registers the Passport strategies with the
 * global passport instance, idempotently (passport.use overwrites by name).
 */
export function mountOAuthRoutes(
  app: Express,
  prisma: PrismaClient,
  jwtConfig: JwtConfig,
): void {
  passport.use(new IdTokenStrategy('google-id-token', verifyGoogleIdToken));
  passport.use(new IdTokenStrategy('apple-id-token', verifyAppleIdToken));
  passport.initialize();

  const router = buildOAuthRouter(prisma, jwtConfig);
  const optional = attachParentAuth(jwtConfig);
  app.post('/api/auth/oauth/google', optional, router.google);
  app.post('/api/auth/oauth/apple', optional, router.apple);
}

export function buildOAuthRouter(prisma: PrismaClient, jwtConfig: JwtConfig) {
  async function finalize(
    req: Request,
    res: Response,
    profile: OAuthProfile,
  ): Promise<void> {
    // Validate payload shape too — passport.Strategy already checked for
    // id_token presence, but zod enforces length and type for defence in
    // depth.
    const parsed = oauthPayloadSchema.safeParse(req.body);
    if (!parsed.success) {
      res.status(400).json({ error: 'invalid_payload', issues: parsed.error.issues });
      return;
    }
    const resolved = await resolveOrCreateOAuthParent(prisma, profile);
    const session: ParentSession = {
      parentId: resolved.parent.id,
      householdId: resolved.household.id,
    };
    const token = signParentToken(jwtConfig, session);
    const body: OAuthResponse = {
      token,
      parent: {
        id: resolved.parent.id,
        email: resolved.parent.email,
        name: resolved.parent.name,
      },
      household: resolved.household,
    };
    res.json(body);
  }

  function runStrategy(
    req: Request,
    res: Response,
    next: NextFunction,
    strategyName: string,
  ): void {
    passport.authenticate(
      strategyName,
      { session: false },
      async (
        err: unknown,
        profile: OAuthProfile | undefined,
        challenge: unknown,
        status: number | undefined,
      ) => {
        // Passport passes a real Error (e.g. token verifier threw) as `err`.
        // Authentication failures land in `challenge` + `status` with
        // `profile` === false.
        if (err) {
          const httpStatus = (err as { status?: number }).status ?? 500;
          res.status(httpStatus).json({
            error: 'oauth_error',
            detail: err instanceof Error ? err.message : String(err),
          });
          return;
        }
        if (!profile) {
          // challenge carries the reason; status carries the intended HTTP
          // code (defaults to 401, may be 400 for missing-field failures).
          const httpStatus = status ?? 401;
          const detail =
            challenge && typeof challenge === 'object' && 'message' in challenge
              ? String((challenge as { message: unknown }).message)
              : undefined;
          res.status(httpStatus).json({
            error: httpStatus === 400 ? 'invalid_payload' : 'invalid_token',
            ...(detail ? { detail } : {}),
          });
          return;
        }
        try {
          await finalize(req, res, profile);
        } catch (e) {
          next(e);
        }
      },
    )(req, res, next);
  }

  return {
    google: (req: Request, res: Response, next: NextFunction): void =>
      runStrategy(req, res, next, 'google-id-token'),
    apple: (req: Request, res: Response, next: NextFunction): void =>
      runStrategy(req, res, next, 'apple-id-token'),
  };
}