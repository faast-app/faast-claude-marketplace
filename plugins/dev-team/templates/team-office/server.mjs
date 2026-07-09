#!/usr/bin/env node
// Team Office — servidor local de la oficina virtual del dev-team.
// Sin dependencias: Node >= 18. Uso:
//   node server.mjs [--dir /ruta/a/.coordination] [--port 4321]
// Sirve office.html, expone /state (JSON) y /events (SSE) con la actividad
// de .coordination/metrics/activity.jsonl y .coordination/handoffs/.

import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const getArg = (name, dflt) => {
  const i = args.indexOf(name);
  return i >= 0 && args[i + 1] ? args[i + 1] : dflt;
};
const COORD = path.resolve(getArg('--dir', './.coordination'));
const PORT = parseInt(getArg('--port', '4321'), 10);
const ACTIVITY = path.join(COORD, 'metrics', 'activity.jsonl');
const HANDOFFS = path.join(COORD, 'handoffs');

const AGENTS = [
  'setup','product-owner','architect','ui-designer','lead','backend','frontend',
  'dba','qa','qa-frontend','qa-backend','release-manager','infra','cybersec','tech-writer',
];

function readEvents(limit = 400) {
  try {
    const raw = fs.readFileSync(ACTIVITY, 'utf8');
    const lines = raw.split('\n').filter(Boolean);
    return lines.slice(-limit).map((l) => {
      try { return JSON.parse(l); } catch { return null; }
    }).filter(Boolean);
  } catch { return []; }
}

function readHandoffs() {
  try {
    return fs.readdirSync(HANDOFFS)
      .filter((f) => f.endsWith('.md'))
      .map((f) => {
        // convencion: {from}-to-{to}-{timestamp}.md
        const m = f.match(/^(.+?)-to-(.+?)-\d/);
        const st = fs.statSync(path.join(HANDOFFS, f));
        return { file: f, from: m?.[1] ?? '?', to: m?.[2] ?? '?', mtime: st.mtimeMs };
      })
      .sort((a, b) => b.mtime - a.mtime);
  } catch { return []; }
}

function buildState() {
  const events = readEvents();
  const handoffs = readHandoffs();
  const agents = {};
  for (const a of AGENTS) agents[a] = { agent: a, status: 'idle', task: null, lastEvent: null, lastTs: null, counts: {} };
  for (const ev of events) {
    const a = agents[ev.agent];
    if (!a) continue;
    a.counts[ev.event] = (a.counts[ev.event] || 0) + 1;
    a.lastEvent = ev.event; a.lastTs = ev.ts; a.lastDetail = ev.detail || '';
    if (ev.event === 'task_start') { a.status = 'working'; a.task = ev.task || null; }
    else if (ev.event === 'task_end') { a.status = 'idle'; a.task = null; }
    else if (ev.event === 'blocked') { a.status = 'blocked'; a.task = ev.task || a.task; }
    else if (ev.event === 'unblocked') { a.status = 'working'; }
  }
  // working sin señal hace > 30 min → stale
  const now = Date.now();
  for (const a of Object.values(agents)) {
    if (a.status === 'working' && a.lastTs && now - Date.parse(a.lastTs) > 30 * 60 * 1000) a.status = 'stale';
  }
  return { ts: new Date().toISOString(), agents: Object.values(agents), events: events.slice(-120), handoffs };
}

// --- SSE ---
const clients = new Set();
let debounce = null;
function broadcast() {
  clearTimeout(debounce);
  debounce = setTimeout(() => {
    const data = `data: ${JSON.stringify(buildState())}\n\n`;
    for (const res of clients) res.write(data);
  }, 250);
}
function watchSafe(target, opts) {
  try { fs.watch(target, opts, broadcast); } catch { /* aparecerá después */ }
}
watchSafe(path.dirname(ACTIVITY), {});
watchSafe(HANDOFFS, {});
setInterval(broadcast, 5000); // heartbeat: re-evalúa stale y handoffs

const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);
  if (url.pathname === '/' || url.pathname === '/index.html') {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(fs.readFileSync(path.join(__dirname, 'office.html')));
  } else if (url.pathname === '/state') {
    res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
    res.end(JSON.stringify(buildState()));
  } else if (url.pathname === '/events') {
    res.writeHead(200, {
      'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache', Connection: 'keep-alive',
    });
    res.write(`data: ${JSON.stringify(buildState())}\n\n`);
    clients.add(res);
    req.on('close', () => clients.delete(res));
  } else {
    res.writeHead(404); res.end('not found');
  }
});

server.listen(PORT, () => {
  console.log(`🏢 Team Office → http://localhost:${PORT}`);
  console.log(`   coordinación: ${COORD}`);
  if (!fs.existsSync(ACTIVITY)) console.log('   (aún no existe metrics/activity.jsonl — la oficina se verá vacía hasta que los agentes registren eventos)');
});
