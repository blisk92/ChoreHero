// ChoreHero v1 — JWT helpers.
//
// The parent session is a signed JWT carried in `Authorization: Bearer
// <token>`. We don't use refresh tokens in v1; expiry is 30 days. Per the
// task body, the SPA stores the token in memory only (not localStorage)
// until v1-09 (refresh-token rotation) is requested.
//
// The signing secret is read from JWT_SECRET. In tests, callers may pass
// an explicit secret to signAndIssue() to override the env-derived default
// (handy for the contract test, which needs a stable, known-good signature).

import jwt from 'jsonwebtoken';
import type { SignOptions } from 'jsonwebtoken';

export const JWT_AUDIENCE = 'chorehero:parent';
export const JWT_ISSUER = 'chorehero-api';

export interface ParentJwtClaims {
  parent_id: string;
  household_id: string;
  email: string;
}

const DEFAULT_TTL_SECONDS = 60 * 60 * 24 * 30; // 30 days

export function getJwtSecret(): string {
  const s = process.env.JWT_SECRET;
  if (!s || s.length < 16) {
    throw new Error('JWT_SECRET is required (>=16 chars). Set it in .env.');
  }
  return s;
}

export function signParentJwt(claims: ParentJwtClaims, secret = getJwtSecret()): string {
  const opts: SignOptions = {
    audience: JWT_AUDIENCE,
    issuer: JWT_ISSUER,
    expiresIn: DEFAULT_TTL_SECONDS,
    algorithm: 'HS256',
  };
  return jwt.sign(claims, secret, opts);
}

export function verifyParentJwt(token: string, secret = getJwtSecret()): ParentJwtClaims {
  const decoded = jwt.verify(token, secret, {
    audience: JWT_AUDIENCE,
    issuer: JWT_ISSUER,
    algorithms: ['HS256'],
  });
  if (typeof decoded === 'string') {
    throw new Error('unexpected_jwt_shape');
  }
  const claims = decoded as Record<string, unknown>;
  if (
    typeof claims.parent_id !== 'string' ||
    typeof claims.household_id !== 'string' ||
    typeof claims.email !== 'string'
  ) {
    throw new Error('invalid_jwt_claims');
  }
  return {
    parent_id: claims.parent_id,
    household_id: claims.household_id,
    email: claims.email,
  };
}
