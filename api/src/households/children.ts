// Household-scoped child profile endpoints.
//
// Wire shape:
//   POST /api/households/{id}/children  (Bearer) { name, avatar_id } -> { child }
//   GET  /api/households/{id}/children  (Bearer) -> { child } | { children: [] }
//
// v1 spec §Out of Scope says exactly one Child per Household. POST returns
// 409 if the household already has a child — the SPA uses this to detect
// "already onboarded" and skip the onboarding wizard.
//
// Mutations to a child's `name` and `avatar_id` go through
// `/api/sync/apply` (the v1-01 LWW helper). This module only handles the
// create-then-freeze lifecycle; in-flight edits are routed by mountSyncRoutes
// and use the per-field LWW columns (name_updated_at, avatar_id_updated_at)
// already defined on the Child model.

import type { Express, Request, Response } from 'express';
import { z } from 'zod';
import type { PrismaClient } from '@prisma/client';
import type { JwtConfig } from '../auth/jwt.js';
import { attachParentAuth, requireParent } from '../auth/middleware.js';

const childCreateSchema = z.object({
  name: z.string().min(1).max(80).transform((v) => v.trim()),
  avatar_id: z
    .string()
    .min(1)
    .max(80)
    // avatar_id may carry an extension (.svg) or a slug. Allow alnum, dash,
    // underscore, dot; nothing exotic.
    .regex(/^[a-zA-Z0-9._-]+$/, 'avatar_id must be alphanumeric/dash/underscore/dot'),
});

export interface ChildView {
  id: string;
  householdId: string;
  name: string;
  avatarId: string;
  createdAt: string;
  /** Server-tracked LWW version timestamps for name and avatar_id. */
  nameUpdatedAt: string | null;
  avatarIdUpdatedAt: string | null;
}

/**
 * Render a Child row to its wire shape. `nameUpdatedAt` and
 * `avatarIdUpdatedAt` come back as ISO strings so the SPA can store them
 * verbatim and feed them into /api/sync/apply without re-parsing.
 */
function toChildView(c: {
  id: string;
  householdId: string;
  name: string;
  avatarId: string;
  createdAt: Date;
  nameUpdatedAt: Date | null;
  avatarIdUpdatedAt: Date | null;
}): ChildView {
  return {
    id: c.id,
    householdId: c.householdId,
    name: c.name,
    avatarId: c.avatarId,
    createdAt: c.createdAt.toISOString(),
    nameUpdatedAt: c.nameUpdatedAt ? c.nameUpdatedAt.toISOString() : null,
    avatarIdUpdatedAt: c.avatarIdUpdatedAt
      ? c.avatarIdUpdatedAt.toISOString()
      : null,
  };
}

/**
 * Authorize the household param against the authenticated session.
 *
 * The session carries `householdId`; if it doesn't match the URL param,
 * this is a cross-household probe and we 404 (not 403 — we don't reveal
 * whether the target household exists).
 *
 * Returns the matched Parent+Household pair on success, or null if the
 * caller should stop (already sent a response).
 */
function authorizeHouseholdAccess(
  req: Request,
  res: Response,
  prisma: PrismaClient,
  householdId: string,
):
  | Promise<{ parent: { id: string; householdId: string }; household: { id: string } } | null>
  | null {
  const session = requireParent(req, res);
  if (!session) return null;

  if (session.householdId !== householdId) {
    // 404 (not 403) — don't leak existence of other households.
    res.status(404).json({ error: 'not_found' });
    return null;
  }
  // We don't strictly need to re-fetch the household; the JWT already
  // attests to its existence at sign time. But the parent might have been
  // deleted since — let the prisma calls below surface that case via
  // empty-result errors. For now we trust the session.
  return Promise.resolve({
    parent: { id: session.parentId, householdId: session.householdId },
    household: { id: session.householdId },
  });
}

/**
 * Build the children router. Exported for use in contract tests; the
 * production caller is `mountChildrenRoutes` below.
 */
export function buildChildrenRouter(prisma: PrismaClient, _jwtConfig: JwtConfig) {
  return {
    create: async (req: Request, res: Response): Promise<void> => {
      const householdId = req.params.id;
      if (!householdId) {
        res.status(400).json({ error: 'invalid_household_id' });
        return;
      }
      const ok = await authorizeHouseholdAccess(req, res, prisma, householdId);
      if (!ok) return;

      const parsed = childCreateSchema.safeParse(req.body);
      if (!parsed.success) {
        res.status(400).json({
          error: 'invalid_payload',
          issues: parsed.error.issues,
        });
        return;
      }
      const { name, avatar_id: avatarId } = parsed.data;

      // 409 if a child already exists for this household.
      const existing = await prisma.child.findFirst({
        where: { householdId },
      });
      if (existing) {
        res.status(409).json({ error: 'child_already_exists' });
        return;
      }

      const now = new Date();
      const created = await prisma.child.create({
        data: {
          householdId,
          name,
          avatarId,
          createdAt: now,
          // Set the LWW timestamps on create so the first /sync/apply on
          // either field is "strictly greater" and applies cleanly.
          nameUpdatedAt: now,
          avatarIdUpdatedAt: now,
        },
      });
      res.status(201).json({ child: toChildView(created) });
    },

    list: async (req: Request, res: Response): Promise<void> => {
      const householdId = req.params.id;
      if (!householdId) {
        res.status(400).json({ error: 'invalid_household_id' });
        return;
      }
      const ok = await authorizeHouseholdAccess(req, res, prisma, householdId);
      if (!ok) return;

      const children = await prisma.child.findMany({
        where: { householdId },
        orderBy: { createdAt: 'asc' },
      });
      if (children.length === 0) {
        // Spec: at most one child, but a household may legitimately have
        // zero (e.g. parent hasn't onboarded yet). Return an empty list
        // shape rather than 404 so the SPA can render the dashboard.
        res.json({ children: [] });
        return;
      }
      // Spec: at most one child. We send a list shape so the API can
      // expand to multi-child later without a breaking change, but the
      // contract test asserts the singular-in-practice behaviour.
      res.json({
        children: children.map(toChildView),
      });
    },
  };
}

/** Mount the children endpoints. Auth is JWT (parent session). */
export function mountChildrenRoutes(
  app: Express,
  prisma: PrismaClient,
  jwtConfig: JwtConfig,
): void {
  const router = buildChildrenRouter(prisma, jwtConfig);
  const optional = attachParentAuth(jwtConfig);
  app.post('/api/households/:id/children', optional, router.create);
  app.get('/api/households/:id/children', optional, router.list);
}