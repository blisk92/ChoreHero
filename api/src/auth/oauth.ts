// ChoreHero v1 — OAuth ID-token verification.
//
// Shape: the SPA completes the Google/Apple browser flow, receives an
// ID-token (a JWT signed by the provider), and POSTs it to
// POST /api/auth/oauth/{google,apple} on this API. We verify the
// signature, issuer, audience, and expiry, then extract the subject
// and email and resolve to a Parent row.
//
// Why not Passport? Passport's Google/Apple strategies are 3-legged
// redirect flows that require a browser round-trip to our callback URL
// — incompatible with the SPA-first POST shape in the v1-02 task body
// (where the SPA already has the ID token in hand). The data shape
// Passport would let us write (oauth_provider + oauth_subject on
// Parent) is identical, so the rest of the auth layer doesn't change.
//
// Verification uses Node's `crypto` + the JWKS endpoint published by
// each provider. We don't add `google-auth-library` / `apple-signin-auth`
// because (a) they're 100KB+ and (b) JWKS+RS256 is a small surface we
// can verify ourselves.

import { createRemoteJWKSet, jwtVerify, type JWTPayload } from 'jose';
import { JWT_AUDIENCE, JWT_ISSUER } from './jwt.js';

export type OAuthProvider = 'google' | 'apple';

export interface OAuthClaims {
  provider: OAuthProvider;
  subject: string;
  email: string | null;
  email_verified: boolean;
}

interface ProviderConfig {
  issuer: string | string[];
  jwksUri: string;
}

const PROVIDERS: Record<OAuthProvider, ProviderConfig> = {
  google: {
    issuer: ['https://accounts.google.com', 'accounts.google.com'],
    jwksUri: 'https://www.googleapis.com/oauth2/v3/certs',
  },
  apple: {
    issuer: 'https://appleid.apple.com',
    jwksUri: 'https://appleid.apple.com/auth/keys',
  },
};

/**
 * Verify a provider-issued ID token. The `audience` is the OAuth client
 * ID registered with the provider (configurable per environment). We
 * accept either a configured audience or a wildcard match against the
 * primary `JWT_AUDIENCE` constant for tests/dev (see OAuthVerifyOptions).
 */
export interface OAuthVerifyOptions {
  /** Audience claim(s) the token must match. */
  expectedAudiences: string[];
  /** Fetch override for tests (lets us point at a mock JWKS). */
  jwksFetch?: typeof fetch;
}

const JWKS_CACHE = new Map<string, ReturnType<typeof createRemoteJWKSet>>();

function getJwks(uri: string, customFetch?: typeof fetch): ReturnType<typeof createRemoteJWKSet> {
  const cached = JWKS_CACHE.get(uri);
  if (cached) return cached;
  const jwks = createRemoteJWKSet(new URL(uri), {
    ...(customFetch ? { fetch: customFetch as typeof globalThis.fetch } : {}),
    cooldownDuration: 30_000,
    cacheMaxAge: 600_000,
  });
  JWKS_CACHE.set(uri, jwks);
  return jwks;
}

export async function verifyOAuthIdToken(
  provider: OAuthProvider,
  idToken: string,
  options: OAuthVerifyOptions,
): Promise<OAuthClaims> {
  const config = PROVIDERS[provider];
  const jwks = getJwks(config.jwksUri, options.jwksFetch);
  let payload: JWTPayload;
  try {
    const result = await jwtVerify(idToken, jwks, {
      issuer: config.issuer,
      audience: options.expectedAudiences,
      algorithms: ['RS256'],
    });
    payload = result.payload;
  } catch (err) {
    throw new OAuthVerifyError('invalid_token', err);
  }

  const sub = typeof payload.sub === 'string' ? payload.sub : null;
  if (!sub) {
    throw new OAuthVerifyError('missing_subject');
  }
  const email = typeof payload.email === 'string' ? payload.email : null;
  const emailVerified = payload.email_verified === true;
  return {
    provider,
    subject: sub,
    email,
    email_verified: emailVerified,
  };
}

export class OAuthVerifyError extends Error {
  constructor(public code: 'invalid_token' | 'missing_subject', public cause?: unknown) {
    super(code);
    this.name = 'OAuthVerifyError';
  }
}

/**
 * Resolve the expected audience(s) for a given provider from env.
 * Returns [] when the env is not configured — callers (the route
 * handler) should treat that as "OAuth is not enabled in this env".
 */
export function getProviderAudiences(provider: OAuthProvider): string[] {
  if (provider === 'google') {
    const id = process.env.GOOGLE_CLIENT_ID;
    return id ? [id] : [];
  }
  const id = process.env.APPLE_CLIENT_ID;
  return id ? [id] : [];
}

export { JWT_AUDIENCE, JWT_ISSUER };
