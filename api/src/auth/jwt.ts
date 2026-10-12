// JWT helpers for parent sessions.
//
// Tokens are signed with HS256 using JWT_SECRET from env. The payload is the
// minimum needed to identify a parent and their household; nothing else
// belongs in here. Tokens expire after 7 days — long enough that an active
// parent doesn't get logged out across reloads, short enough that a stolen
// token has a bounded blast radius. See tickets/v1-mvp/02.

import jwt from 'jsonwebtoken';
import { z } from 'zod';

const TOKEN_TTL_SECONDS = 60 * 60 * 24 * 7; // 7 days

export const parentSessionSchema = z.object({
  parentId: z.string().min(1),
  householdId: z.string().min(1),
});

export type ParentSession = z.infer<typeof parentSessionSchema>;

export interface JwtConfig {
  secret: string;
  ttlSeconds: number;
}

/**
 * Reads JWT_SECRET from env. In test/dev, callers may pass an explicit
 * override via the second argument (e.g. to inject a deterministic secret
 * from the test harness). Production callers pass nothing and rely on env.
 */
export function loadJwtConfig(override?: { secret?: string; ttlSeconds?: number }): JwtConfig {
  const secret = override?.secret ?? process.env.JWT_SECRET;
  if (!secret || secret.length < 16) {
    throw new Error(
      'JWT_SECRET is required and must be at least 16 chars (set it in env or pass an override)',
    );
  }
  return {
    secret,
    ttlSeconds: override?.ttlSeconds ?? TOKEN_TTL_SECONDS,
  };
}

export function signParentToken(config: JwtConfig, session: ParentSession): string {
  return jwt.sign(session, config.secret, {
    algorithm: 'HS256',
    expiresIn: config.ttlSeconds,
  });
}

/**
 * Verify a token. Returns the parsed session on success, or `null` on any
 * failure (expired, malformed, bad signature). Callers turn `null` into a
 * 401 response; the JWT library's own error objects stay internal so we
 * never leak whether the token expired vs. was forged.
 */
export function verifyParentToken(config: JwtConfig, token: string): ParentSession | null {
  try {
    const decoded = jwt.verify(token, config.secret, { algorithms: ['HS256'] });
    const parsed = parentSessionSchema.safeParse(decoded);
    return parsed.success ? parsed.data : null;
  } catch {
    return null;
  }
}

/**
 * Decode without verifying — useful for diagnostics only. Never use this for
 * auth decisions; the signature must be checked.
 */
export function decodeParentTokenUnsafe(token: string): ParentSession | null {
  const decoded = jwt.decode(token);
  if (!decoded || typeof decoded === 'string') return null;
  const parsed = parentSessionSchema.safeParse(decoded);
  return parsed.success ? parsed.data : null;
}