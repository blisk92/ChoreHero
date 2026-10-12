// ChoreHero API entrypoint. v1-01 exposes the LWW sync primitive; v1-02 adds
// the parent auth + household provisioning endpoints on top.

import express from 'express';
import http from 'node:http';
import { WebSocketServer } from 'ws';
import { PrismaClient } from '@prisma/client';
import { mountSyncRoutes } from './sync/lww.js';
import { mountAuthRoutes } from './auth/routes.js';
import { mountOAuthRoutes } from './auth/oauth.js';
import { mountChildrenRoutes } from './households/children.js';
import { loadJwtConfig } from './auth/jwt.js';

const PORT = Number.parseInt(process.env.PORT ?? '3000', 10);
const DATABASE_URL = process.env.DATABASE_URL ?? 'mysql://root:***@127.0.0.1:3306/chorehero';

export const prisma = new PrismaClient({ datasourceUrl: DATABASE_URL });

// In test mode we let the caller pass a deterministic JWT secret (or accept
// the env) so contract tests don't have to spin a separate auth harness.
// JWT_SECRET is required at boot for production; the test harness in
// test/contract/ sets one before this module loads.
const jwtConfig = loadJwtConfig(
  process.env.NODE_ENV === 'test' && process.env.JWT_SECRET === undefined
    ? { secret: 'test-secret-do-not-use-in-prod' }
    : undefined,
);

const app = express();
app.use(express.json({ limit: '1mb' }));

app.get('/api/health', (_req, res) => {
  res.json({ ok: true, service: 'chorehero-api', version: '0.1.0' });
});

mountAuthRoutes(app, prisma, jwtConfig);
mountOAuthRoutes(app, prisma, jwtConfig);
mountChildrenRoutes(app, prisma, jwtConfig);
mountSyncRoutes(app, prisma);

const server = http.createServer(app);
const wss = new WebSocketServer({ server, path: '/ws' });

wss.on('connection', (socket) => {
  // v1-04 wires parent-session JWT handshake + kid-activity broadcast.
  // v1-01 only proves the upgrade + WS lifecycle works end-to-end.
  socket.send(JSON.stringify({ type: 'hello', service: 'chorehero-api' }));
});

if (process.env.NODE_ENV !== 'test') {
  server.listen(PORT, () => {
    console.log(`[chorehero-api] listening on :${PORT} (ws path /ws)`);
  });
}

export { app, server, wss };