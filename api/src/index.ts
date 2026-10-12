// ChoreHero API entrypoint. v1-01 only exposes the LWW sync primitive; auth
// and household endpoints land in v1-02.

import express from 'express';
import http from 'node:http';
import { WebSocketServer } from 'ws';
import { PrismaClient } from '@prisma/client';
import { mountSyncRoutes } from './sync/lww.js';

const PORT = Number.parseInt(process.env.PORT ?? '3000', 10);
const DATABASE_URL = process.env.DATABASE_URL ?? 'mysql://root:root@127.0.0.1:3306/chorehero';

export const prisma = new PrismaClient({ datasourceUrl: DATABASE_URL });

const app = express();
app.use(express.json({ limit: '1mb' }));

app.get('/api/health', (_req, res) => {
  res.json({ ok: true, service: 'chorehero-api', version: '0.1.0' });
});

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