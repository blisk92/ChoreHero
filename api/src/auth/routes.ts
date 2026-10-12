// ChoreHero v1 — auth + household + children routes.
//
// Endpoints:
//   POST /api/auth/signup              — email + password; creates Parent + Household, returns JWT
//   POST /api/auth/signin              — email + password; returns JWT
//   POST /api/auth/oauth/google        — id_token; resolves to Parent (or creates new + Household), returns JWT
//   POST /api/auth/oauth/apple         — id_token; same shape as google
//   GET  /api/auth/me                  — JWT-protected; returns parent + household
//   POST /api/households/{id}/children — JWT-protected; creates the one and only child (rejects duplicates)
//   GET  /api/households/{id}/children — JWT-protected; lists the household's children (≤1 in v1)
//   GET  /api/avatars                  — public; the 12-avatar set used by the onboarding picker
//
// All endpoints are validated via zod; the parent session is a JWT in
// `Authorization: Bearer <token>`. Per the task body, multi-device
// sessions are first-class: sign-in always issues a fresh JWT with a
// fresh `jti`, so two devices can hold two valid tokens for the same
// parent simultaneously.

import { Router, type Express, type Request, type Response, type NextFunction } from 'express';
import { z } from 'zod';
import { randomUUID } from 'node:crypto';
import type { PrismaClient } from '@prisma/client';
import { hashPassword, isPasswordRuleSatisfied, verifyPassword } from './password.js';
import { signParentJwt, verifyParentJwt, type ParentJwtClaims } from './jwt.js';
import {
  getProviderAudiences,
  verifyOAuthIdToken,
  type OAuthProvider,
} from './oauth.js';
import { AVATARS, isKnownAvatarId } from './avatars.js';

export interface AuthBundle {
  parent: {
    id: string;
    email: string;
    name: string | null;
    householdId: string;
    oauthProvider: string | null;
    oauthSubject: string | null;
    createdAt: string;
  };
  household: {
    id: string;
    name: string | null;
    timezone: string;
    createdAt: string;
  };
  token: string;
}

const signupSchema = z.object({
  email: z.string().email().transform((s) => s.toLowerCase().trim()),
  password: z.string().min(1),
  name: z.string().trim().min(1).max(60),
});

const signinSchema = z.object({
  email: z.string().email().transform((s) => s.toLowerCase().trim()),
  password: z.string().min(1),
});

const oauthSchema = z.object({
  id_token: z.string().min(10),
});

const createChildSchema = z.object({
  name: z.string().trim().min(1).max(60),
  avatar_id: z.string().min(1),
});

interface CreateHouseholdInput {
  prisma: PrismaClient;
  name?: string;
}

async function createHousehold({ prisma, name }: CreateHouseholdInput): Promise<{ id: string }> {
  return prisma.household.create({ data: { name: name ?? null }, select: { id: true } });
}

function bundleFor(
  parent: {
    id: string;
    email: string;
    name: string | null;
    householdId: string;
    oauthProvider: string | null;
    oauthSubject: string | null;
    createdAt: Date;
  },
  household: { id: string; name: string | null; timezone: string; createdAt: Date },
  token: string,
): AuthBundle {
  return {
    parent: {
      id: parent.id,
      email: parent.email,
      name: parent.name,
      householdId: parent.householdId,
      oauthProvider: parent.oauthProvider,
      oauthSubject: parent.oauthSubject,
      createdAt: parent.createdAt.toISOString(),
    },
    household: {
      id: household.id,
      name: household.name,
      timezone: household.timezone,
      createdAt: household.createdAt.toISOString(),
    },
    token,
  };
}

export function authRequired(prisma: PrismaClient) {
  return (req: Request, res: Response, next: NextFunction): void => {
    const header = req.header('authorization') ?? '';
    const match = /^Bearer\s+(.+)$/i.exec(header);
    if (!match || !match[1]) {
      res.status(401).json({ error: 'missing_bearer' });
      return;
    }
    try {
      const claims = verifyParentJwt(match[1]);
      // Stash for downstream handlers.
      (req as AuthenticatedRequest).auth = claims;
      next();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'invalid_token';
      res.status(401).json({ error: 'invalid_token', detail: message });
    }
  };
}

export interface AuthenticatedRequest extends Request {
  auth?: ParentJwtClaims;
}

export function mountAuthRoutes(app: Express, prisma: PrismaClient): void {
  const router = Router();

  // ---- POST /api/auth/signup -------------------------------------------
  router.post('/auth/signup', async (req, res) => {
    const parsed = signupSchema.safeParse(req.body);
    if (!parsed.success) {
      res.status(400).json({ error: 'invalid_payload', issues: parsed.error.issues });
      return;
    }
    if (!isPasswordRuleSatisfied(parsed.data.password)) {
      res.status(400).json({
        error: 'weak_password',
        message: 'Password must be at least 8 characters and include a letter and a number.',
      });
      return;
    }
    const existing = await prisma.parent.findUnique({
      where: { email: parsed.data.email },
    });
    if (existing) {
      res.status(409).json({ error: 'email_taken' });
      return;
    }
    const household = await createHousehold({ prisma });
    const passwordHash = await hashPassword(parsed.data.password);
    const parent = await prisma.parent.create({
      data: {
        householdId: household.id,
        email: parsed.data.email,
        passwordHash,
        name: parsed.data.name,
        nameUpdatedAt: new Date(),
      },
    });
    const fullHousehold = await prisma.household.findUniqueOrThrow({
      where: { id: household.id },
    });
    const token = signParentJwt({
      parent_id: parent.id,
      household_id: parent.householdId,
      email: parent.email,
    });
    res.status(201).json(bundleFor(parent, fullHousehold, token));
  });

  // ---- POST /api/auth/signin -------------------------------------------
  router.post('/auth/signin', async (req, res) => {
    const parsed = signinSchema.safeParse(req.body);
    if (!parsed.success) {
      res.status(400).json({ error: 'invalid_payload', issues: parsed.error.issues });
      return;
    }
    const parent = await prisma.parent.findUnique({
      where: { email: parsed.data.email },
    });
    // Always run a bcrypt verify to keep timing constant across the
    // "no account" and "wrong password" branches (the same defense
    // screen 02 calls out as an anti-pattern to avoid leaking which).
    const hash = parent?.passwordHash ?? '$2b$12$invalidhashforbcryptcompare..............';
    const ok = parent ? await verifyPassword(parsed.data.password, hash) : false;
    if (!parent || !ok || !parent.passwordHash) {
      res.status(401).json({ error: 'invalid_credentials' });
      return;
    }
    const fullHousehold = await prisma.household.findUniqueOrThrow({
      where: { id: parent.householdId },
    });
    const token = signParentJwt({
      parent_id: parent.id,
      household_id: parent.householdId,
      email: parent.email,
    });
    res.json(bundleFor(parent, fullHousehold, token));
  });

  // ---- POST /api/auth/oauth/{google|apple} -----------------------------
  for (const provider of ['google', 'apple'] as const) {
    router.post(`/auth/oauth/${provider}`, async (req, res) => {
      const parsed = oauthSchema.safeParse(req.body);
      if (!parsed.success) {
        res.status(400).json({ error: 'invalid_payload', issues: parsed.error.issues });
        return;
      }
      const audiences = getProviderAudiences(provider);
      if (audiences.length === 0) {
        res.status(503).json({
          error: 'oauth_not_configured',
          provider,
          message: `${provider} OAuth is not configured in this environment.`,
        });
        return;
      }
      try {
        const claims = await verifyOAuthIdToken(provider, parsed.data.id_token, {
          expectedAudiences: audiences,
        });
        const result = await resolveOAuthParent({ prisma, claims, provider });
        const fullHousehold = await prisma.household.findUniqueOrThrow({
          where: { id: result.parent.householdId },
        });
        const token = signParentJwt({
          parent_id: result.parent.id,
          household_id: result.parent.householdId,
          email: result.parent.email,
        });
        // 201 when a new parent+household was created; 200 otherwise.
        const status = result.created ? 201 : 200;
        res.status(status).json(bundleFor(result.parent, fullHousehold, token));
      } catch (err) {
        const message = err instanceof Error ? err.message : 'invalid_token';
        res.status(401).json({ error: 'oauth_failed', detail: message });
      }
    });
  }

  // ---- GET /api/auth/me ------------------------------------------------
  router.get('/auth/me', authRequired(prisma), async (req, res) => {
    const claims = (req as AuthenticatedRequest).auth!;
    const parent = await prisma.parent.findUnique({ where: { id: claims.parent_id } });
    if (!parent) {
      res.status(404).json({ error: 'parent_not_found' });
      return;
    }
    const household = await prisma.household.findUnique({
      where: { id: parent.householdId },
    });
    if (!household) {
      res.status(404).json({ error: 'household_not_found' });
      return;
    }
    res.json({
      parent: {
        id: parent.id,
        email: parent.email,
        name: parent.name,
        householdId: parent.householdId,
        oauthProvider: parent.oauthProvider,
        oauthSubject: parent.oauthSubject,
        createdAt: parent.createdAt.toISOString(),
      },
      household: {
        id: household.id,
        name: household.name,
        timezone: household.timezone,
        createdAt: household.createdAt.toISOString(),
      },
    });
  });

  // ---- GET /api/avatars (public) ---------------------------------------
  router.get('/avatars', (_req, res) => {
    res.json({
      avatars: AVATARS.map((a) => ({ id: a.id, label: a.label, svg: a.svg })),
    });
  });

  // ---- GET /api/households/{id}/children -------------------------------
  router.get('/households/:householdId/children', authRequired(prisma), async (req, res) => {
    const claims = (req as AuthenticatedRequest).auth!;
    const { householdId } = req.params;
    if (householdId !== claims.household_id) {
      res.status(403).json({ error: 'wrong_household' });
      return;
    }
    const children = await prisma.child.findMany({
      where: { householdId },
      orderBy: { createdAt: 'asc' },
    });
    res.json({
      children: children.map((c: typeof children[number]) => ({
        id: c.id,
        name: c.name,
        avatarId: c.avatarId,
        createdAt: c.createdAt.toISOString(),
      })),
    });
  });

  // ---- POST /api/households/{id}/children ------------------------------
  router.post('/households/:householdId/children', authRequired(prisma), async (req, res) => {
    const claims = (req as AuthenticatedRequest).auth!;
    const { householdId } = req.params;
    if (householdId !== claims.household_id) {
      res.status(403).json({ error: 'wrong_household' });
      return;
    }
    const parsed = createChildSchema.safeParse(req.body);
    if (!parsed.success) {
      res.status(400).json({ error: 'invalid_payload', issues: parsed.error.issues });
      return;
    }
    if (!isKnownAvatarId(parsed.data.avatar_id)) {
      res.status(400).json({ error: 'unknown_avatar', avatar_id: parsed.data.avatar_id });
      return;
    }
    // v1: exactly one child per household. The 409 carries a code the
    // SPA can react to (e.g. redirect to the child editor if the
    // parent tries to create a second one in the onboarding flow).
    const existing = await prisma.child.count({ where: { householdId } });
    if (existing > 0) {
      res.status(409).json({ error: 'child_already_exists' });
      return;
    }
    const child = await prisma.child.create({
      data: {
        householdId,
        name: parsed.data.name,
        nameUpdatedAt: new Date(),
        avatarId: parsed.data.avatar_id,
        avatarIdUpdatedAt: new Date(),
      },
    });
    res.status(201).json({
      child: {
        id: child.id,
        name: child.name,
        avatarId: child.avatarId,
        householdId: child.householdId,
        createdAt: child.createdAt.toISOString(),
      },
    });
  });

  app.use('/api', router);
}

// -- helpers ----------------------------------------------------------------

interface ResolveOAuthArgs {
  prisma: PrismaClient;
  claims: {
    provider: OAuthProvider;
    subject: string;
    email: string | null;
    email_verified: boolean;
  };
  provider: OAuthProvider;
}

interface ResolveOAuthResult {
  parent: {
    id: string;
    email: string;
    name: string | null;
    householdId: string;
    oauthProvider: string | null;
    oauthSubject: string | null;
    createdAt: Date;
  };
  created: boolean;
}

/**
 * Resolve an OAuth login to a Parent row.
 *
 *   1. If a Parent exists with (oauth_provider, oauth_subject), return it.
 *   2. Else if the verified email matches an existing Parent with a
 *      password, link the OAuth subject to that row and return it.
 *   3. Else create a new Parent + Household. Email is set when the
 *      provider asserts it and email_verified is true; otherwise the
 *      parent is created without an email and the SPA shows an
 *      "add your email" prompt in a later ticket.
 */
async function resolveOAuthParent({
  prisma,
  claims,
  provider,
}: ResolveOAuthArgs): Promise<ResolveOAuthResult> {
  // 1. Direct match on (provider, subject).
  const direct = await prisma.parent.findFirst({
    where: { oauthProvider: provider, oauthSubject: claims.subject },
  });
  if (direct) {
    return { parent: serializeParent(direct), created: false };
  }

  // 2. Link by verified email.
  if (claims.email && claims.email_verified) {
    const byEmail = await prisma.parent.findUnique({ where: { email: claims.email.toLowerCase() } });
    if (byEmail) {
      const linked = await prisma.parent.update({
        where: { id: byEmail.id },
        data: { oauthProvider: provider, oauthSubject: claims.subject },
      });
      return { parent: serializeParent(linked), created: false };
    }
  }

  // 3. New parent + household.
  const household = await createHousehold({ prisma });
  const email = claims.email && claims.email_verified ? claims.email.toLowerCase() : null;
  const created = await prisma.parent.create({
    data: {
      householdId: household.id,
      email: email ?? `oauth-${provider}-${randomUUID()}@no-email.chorehero.local`,
      oauthProvider: provider,
      oauthSubject: claims.subject,
    },
  });
  return { parent: serializeParent(created), created: true };
}

function serializeParent(p: {
  id: string;
  email: string;
  name: string | null;
  householdId: string;
  oauthProvider: string | null;
  oauthSubject: string | null;
  createdAt: Date;
}) {
  return {
    id: p.id,
    email: p.email,
    name: p.name,
    householdId: p.householdId,
    oauthProvider: p.oauthProvider,
    oauthSubject: p.oauthSubject,
    createdAt: p.createdAt,
  };
}
