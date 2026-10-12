// Bearer-token middleware for parent endpoints.
//
// Reads `Authorization: Bearer ***`, verifies the JWT, and attaches the parsed
// `ParentSession` to `req.auth`. Endpoints that require auth call
// `requireParent(req, res)` which 401s on a missing/invalid token, or rely on
// the more permissive `optionalParent` if they want to inspect a token
// without requiring it.

import type { NextFunction, Request, Response } from 'express';
import type { JwtConfig, ParentSession } from './jwt.js';
import { verifyParentToken } from './jwt.js';

/** Pull the raw token out of the Authorization header, or null if absent. */
export function extractBearerToken(headerValue: string | undefined): string | null {
  if (!headerValue) return null;
  const match = /^Bearer\s+(.+)$/i.exec(headerValue.trim());
  return match?.[1]?.trim() ?? null;
}

export function attachParentAuth(config: JwtConfig) {
  return function parentAuthMiddleware(
    req: Request,
    _res: Response,
    next: NextFunction,
  ): void {
    const token = extractBearerToken(req.header('authorization'));
    if (!token) return next();
    const session = verifyParentToken(config, token);
    if (session) {
      (req as Request & { auth?: ParentSession }).auth = session;
    }
    next();
  };
}

/** Strict guard: 401 if no valid token. Use after attachParentAuth. */
export function requireParent(req: Request, res: Response): ParentSession | null {
  const auth = (req as Request & { auth?: ParentSession }).auth;
  if (!auth) {
    res.status(401).json({ error: 'unauthorized' });
    return null;
  }
  return auth;
}