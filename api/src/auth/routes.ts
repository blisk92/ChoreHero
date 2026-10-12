// Auth routes for parents: signup, signin, me.
//
// Endpoints:
//   POST /api/auth/signup  { email, password, displayName } -> { token, parent, household }
//   POST /api/auth/signin  { email, password }              -> { token, parent, household }
//   GET  /api/auth/me      (Bearer)                         -> { parent, household }
//
// Signup is the household-creation step too: every parent gets a fresh
// Household on first signup. Re-signups for the same email are rejected
// (409). Sign-in looks up by email and bcrypt-verifies the stored hash —
// wrong password or unknown email both 401 (never leak which one failed).
//
// We don't set cookies. The client receives the JWT in the response body
// and stores it where it wants (localStorage, sessionStorage, in-memory —
// that's its decision, per scope-brief §6).

import bcrypt from 'bcryptjs';
import type { Express, Request, Response } from 'express';
import { z } from 'zod';
import type { PrismaClient } from '@prisma/client';
import { signParentToken, type JwtConfig, type ParentSession } from './jwt.js';
import { attachParentAuth, requireParent } from './middleware.js';

const BCRYPT_COST = 10; // v1 minimum. Bump to 12 once we measure login latency.

// Password rule (single line, per the ticket acceptance criterion):
// minimum 8 characters, no other constraints in v1.
const MIN_PASSWORD_LENGTH = 8;

const signupSchema = z.object({
  email: z.string().email().max(254).transform((v) => v.toLowerCase().trim()),
  password: z.string().min(MIN_PASSWORD_LENGTH).max(200),
  displayName: z.string().min(1).max(80).transform((v) => v.trim()),
});

const signinSchema = z.object({
  email: z.string().email().max(254).transform((v) => v.toLowerCase().trim()),
  password: z.string().min(1).max(200),
});

/** Shape returned to the client. Password hashes never leave the server. */
export interface AuthResponse {
  token: string;
  parent: {
    id: string;
    email: string;
    name: string | null;
  };
  household: {
    id: string;
    name: string | null;
    timezone: string;
  };
}

function toAuthResponse(args: {
  token: string;
  parent: { id: string; email: string; name: string | null };
  household: { id: string; name: string | null; timezone: string };
}): AuthResponse {
  return args;
}

/**
 * Build the auth router. Takes the shared Prisma client and a JWT config so
 * tests can inject a deterministic secret. Exported for use in contract
 * tests; the production caller is `mountAuthRoutes` below.
 */
export function buildAuthRouter(prisma: PrismaClient, jwtConfig: JwtConfig) {
  return {
    signup: async (req: Request, res: Response): Promise<void> => {
      const parsed = signupSchema.safeParse(req.body);
      if (!parsed.success) {
        res.status(400).json({ error: 'invalid_payload', issues: parsed.error.issues });
        return;
      }
      const { email, password, displayName } = parsed.data;

      // Race-free duplicate-email check: rely on Parent.email's @unique
      // constraint at the DB level and translate the throw into a 409.
      const existing = await prisma.parent.findUnique({ where: { email } });
      if (existing) {
        res.status(409).json({ error: 'email_taken' });
        return;
      }

      const passwordHash = await bcrypt.hash(password, BCRYPT_COST);

      // Create the household and parent in a single transaction so a failure
      // on either side rolls both back. Parent.household_id has FK + NOT
      // NULL so we can't create a parent without a household first. We let
      // Prisma's @default(cuid()) generate the IDs so they fit the
      // VARCHAR(30) id columns in the migration.
      const now = new Date();

      let householdId: string;
      let parentId: string;
      try {
        const created = await prisma.$transaction(async (tx) => {
          const household = await tx.household.create({
            data: {
              name: null,
              timezone: 'UTC',
              createdAt: now,
            },
          });
          const parent = await tx.parent.create({
            data: {
              householdId: household.id,
              email,
              passwordHash,
              oauthProvider: null,
              oauthSubject: null,
              createdAt: now,
              name: displayName,
              nameUpdatedAt: now,
            },
          });
          return { householdId: household.id, parentId: parent.id };
        });
        householdId = created.householdId;
        parentId = created.parentId;
      } catch (err) {
        // Race: two concurrent signups for the same email. Surface as 409
        // rather than a 500 so the client can retry cleanly.
        if (isUniqueConstraintError(err, 'parent.email') || isUniqueConstraintError(err, 'parent')) {
          res.status(409).json({ error: 'email_taken' });
          return;
        }
        throw err;
      }

      const session: ParentSession = { parentId, householdId };
      const token = signParentToken(jwtConfig, session);
      res.status(201).json(
        toAuthResponse({
          token,
          parent: { id: parentId, email, name: displayName },
          household: { id: householdId, name: null, timezone: 'UTC' },
        }),
      );
    },

    signin: async (req: Request, res: Response): Promise<void> => {
      const parsed = signinSchema.safeParse(req.body);
      if (!parsed.success) {
        res.status(400).json({ error: 'invalid_payload', issues: parsed.error.issues });
        return;
      }
      const { email, password } = parsed.data;

      const parent = await prisma.parent.findUnique({
        where: { email },
        include: { household: true },
      });

      // Same response for unknown email vs wrong password — don't leak which
      // one failed. Passwordless parents (OAuth-only) can't sign in here;
      // they go through the OAuth route in v1-02's follow-up.
      if (!parent || !parent.passwordHash) {
        res.status(401).json({ error: 'invalid_credentials' });
        return;
      }

      const ok = await bcrypt.compare(password, parent.passwordHash);
      if (!ok) {
        res.status(401).json({ error: 'invalid_credentials' });
        return;
      }

      const session: ParentSession = {
        parentId: parent.id,
        householdId: parent.householdId,
      };
      const token = signParentToken(jwtConfig, session);

      res.json(
        toAuthResponse({
          token,
          parent: { id: parent.id, email: parent.email, name: parent.name },
          household: {
            id: parent.household.id,
            name: parent.household.name,
            timezone: parent.household.timezone,
          },
        }),
      );
    },

    me: async (req: Request, res: Response): Promise<void> => {
      const session = requireParent(req, res);
      if (!session) return;

      const parent = await prisma.parent.findUnique({
        where: { id: session.parentId },
        include: { household: true },
      });
      if (!parent) {
        // The token was valid but the parent was deleted (e.g. household
        // teardown). Treat the session as no longer authoritative.
        res.status(401).json({ error: 'session_invalid' });
        return;
      }

      res.json({
        parent: { id: parent.id, email: parent.email, name: parent.name },
        household: {
          id: parent.household.id,
          name: parent.household.name,
          timezone: parent.household.timezone,
        },
      });
    },
  };
}

/** Mount all three endpoints under /api/auth on the given Express instance. */
export function mountAuthRoutes(
  app: Express,
  prisma: PrismaClient,
  jwtConfig: JwtConfig,
): void {
  const router = buildAuthRouter(prisma, jwtConfig);
  // The optional auth middleware lets /me short-circuit cleanly when the
  // token is bad, while leaving /signup and /signin unauthenticated.
  const optional = attachParentAuth(jwtConfig);

  app.post('/api/auth/signup', router.signup);
  app.post('/api/auth/signin', router.signin);
  app.get('/api/auth/me', optional, router.me);
}

/**
 * Best-effort detection of a unique-constraint violation. Prisma's error
 * shape across versions is a moving target; we match on the substring that
 * has been stable in 5.x. False positives get re-thrown to the caller.
 */
function isUniqueConstraintError(err: unknown, target: string): boolean {
  if (!err || typeof err !== 'object') return false;
  const message = (err as { message?: string }).message ?? '';
  return (
    message.includes('Unique constraint') &&
    message.toLowerCase().includes(target.toLowerCase())
  );
}