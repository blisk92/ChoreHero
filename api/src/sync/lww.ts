// Per-field Last-Write-Wins sync primitive.
//
// Wire shape:
//   POST /api/sync/apply
//     { table: 'chore' | 'reward' | 'redemption' | 'child' | 'parent' | 'kid_device' | 'streak',
//       id: string,
//       field: string,
//       value: unknown,
//       updated_at: ISO8601 string }
//
// The server writes `field` on the row `id` only if the incoming
// `updated_at` is strictly greater than the stored `<field>_updated_at`.
// Otherwise it returns 200 with { applied: false, reason: 'stale' }.
//
// Idempotent: replaying the same payload is a no-op.

import type { Express } from 'express';
import { z } from 'zod';
import type { PrismaClient } from '@prisma/client';

// Whitelist of (table, field) pairs the apply primitive is allowed to write.
// Each field is the logical column name in CONTEXT.md; the actual SQL column
// is `<field>_updated_at` for the sibling timestamp.
const FIELD_REGISTRY: Record<string, ReadonlySet<string>> = {
  chore: new Set([
    'name',
    'point_value',
    'review_flagged',
    'kind',
    'due_at',
    'status',
    'claimed_by_child_id',
    'claimed_at',
    'archived_at',
  ]),
  reward: new Set([
    'name',
    'point_cost',
    'description',
    'stock_remaining',
  ]),
  redemption: new Set([
    'status',
    'resolved_at',
    'denial_reason',
  ]),
  child: new Set(['name', 'avatar_id']),
  parent: new Set(['name']),
  kid_device: new Set(['friendly_name']),
  streak: new Set([
    'current_length',
    'longest_length',
    'last_completed_on',
  ]),
};

const applySchema = z.object({
  table: z.enum([
    'chore',
    'reward',
    'redemption',
    'child',
    'parent',
    'kid_device',
    'streak',
  ]),
  id: z.string().min(1),
  field: z.string().min(1),
  value: z.unknown(),
  updated_at: z.string().datetime({ offset: true }),
});

export type ApplyResult =
  | { applied: true; field: string; value: unknown }
  | { applied: false; reason: 'stale'; stored_updated_at: string | null }
  | { applied: false; reason: 'unknown_field' }
  | { applied: false; reason: 'not_found' };

export async function applyLww(
  prisma: PrismaClient,
  input: z.infer<typeof applySchema>,
): Promise<ApplyResult> {
  const fields = FIELD_REGISTRY[input.table];
  if (!fields || !fields.has(input.field)) {
    return { applied: false, reason: 'unknown_field' };
  }

  const tsField = `${input.field}_updated_at`;
  const incoming = new Date(input.updated_at);

  // Read stored timestamp for this field. We use $queryRawUnsafe with a
  // whitelisted column to keep the call shape explicit; the table is also
  // drawn from the whitelist above.
  const rows = await prisma.$queryRawUnsafe<Array<Record<string, unknown>>>(
    `SELECT \`${tsField}\` AS stored_ts FROM \`${input.table}\` WHERE \`id\` = ? LIMIT 1`,
    input.id,
  );

  const row = rows[0];
  if (!row) return { applied: false, reason: 'not_found' };

  const storedTs = row.stored_ts as Date | string | null;
  const storedDate = storedTs ? new Date(storedTs) : null;

  if (storedDate && storedDate.getTime() >= incoming.getTime()) {
    return {
      applied: false,
      reason: 'stale',
      stored_updated_at: storedDate.toISOString(),
    };
  }

  // Apply the write and bump the per-field timestamp atomically. We use
  // $executeRawUnsafe with the whitelisted column/table names so the
  // dispatch is dynamic but the surface is locked down.
  await prisma.$executeRawUnsafe(
    `UPDATE \`${input.table}\`
       SET \`${input.field}\` = ?, \`${tsField}\` = ?
       WHERE \`id\` = ?`,
    input.value as never,
    incoming,
    input.id,
  );

  return { applied: true, field: input.field, value: input.value };
}

export function mountSyncRoutes(app: Express, prisma: PrismaClient): void {
  app.post('/api/sync/apply', async (req, res) => {
    const parsed = applySchema.safeParse(req.body);
    if (!parsed.success) {
      res.status(400).json({ error: 'invalid_payload', issues: parsed.error.issues });
      return;
    }
    const result = await applyLww(prisma, parsed.data);
    if (!result.applied) {
      // 200 on 'stale' so a replayed mutation doesn't surface as an error
      // to the offline queue — it's an expected no-op.
      const status = result.reason === 'not_found' ? 404 : 200;
      res.status(status).json(result);
      return;
    }
    res.json(result);
  });
}