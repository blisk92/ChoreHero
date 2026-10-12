// ChoreHero API entrypoint. v1-02 layers auth, household, and child
// routes on top of the v1-01 sync primitive.

import express from 'express';
import cors from 'cors';
import http from 'node:http';
import { WebSocketServer } from 'ws';
import { PrismaClient } from '@prisma/client';
import { mountSyncRoutes } from './sync/lww.js';
import { mountAuthRoutes } from './auth/routes.js';

const PORT = Number.parseInt(process.env.PORT ?? '3000', 10);
const DATABASE_URL = process.env.DATABASE_URL ?? 'mysql://root:root@127.0.0.1:3306/chorehero';

export const prisma = new PrismaClient({ datasourceUrl: DATABASE_URL });

const app = express();
app.use(express.json({ limit: '1mb' }));
// v1-02: the parent SPA is served from a different origin in dev
// (Vite on :5173) and the same origin in prod. Permit both with a
// permissive CORS for the API — auth is JWT-based, not cookie-based,
// so CSRF is not a concern; we just need to allow the SPA to read
// the response.
app.use(
  cors({
    origin: true,
    credentials: false,
    methods: ['GET', 'POST', 'OPTIONS'],
    allowedHeaders: ['content-type', 'authorization'],
  }),
);

app.get('/api/health', (_req, res) => {
  res.json({ ok: true, service: 'chorehero-api', version: '0.2.0' });
});

mountAuthRoutes(app, prisma);
mountSyncRoutes(app, prisma);

const server = http.createServer(app);
const wss = new WebSocketServer({ server, path: '/ws' });

wss.on('connection', (socket) => {
  // v1-04 wires parent-session JWT handshake + kid-activity broadcast.
  // v1-02 only proves the upgrade + WS lifecycle works end-to-end.
  socket.send(JSON.stringify({ type: 'hello', service: 'chorehero-api' }));
});

// Listen when a PORT is configured. The contract tests set PORT to a
// fixed value so they can drive the HTTP surface in-process; production
// and `npm run dev` get the same behavior. If PORT is unset we keep
// the module side-effect-only so tools that import it (e.g. the
// prisma-client typecheck) don't open a stray socket.
if (process.env.PORT) {
  server.listen(Number.parseInt(process.env.PORT, 10), () => {
    console.log(`[chorehero-api] listening on :${process.env.PORT} (ws path /ws)`);
  });
}

export { app, server, wss };