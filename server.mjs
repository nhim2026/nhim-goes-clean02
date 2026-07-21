import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const publicDir = __dirname;
const port = Number(process.env.PORT || 3000);

const mime = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.webmanifest': 'application/manifest+json; charset=utf-8',
  '.svg': 'image/svg+xml; charset=utf-8',
  '.png': 'image/png'
};

const headers = {
  'X-Content-Type-Options': 'nosniff',
  'Referrer-Policy': 'no-referrer'
};

function sendJson(res, status, data) {
  res.writeHead(status, {...headers, 'Content-Type':'application/json; charset=utf-8', 'Cache-Control':'no-store'});
  res.end(JSON.stringify(data));
}

const server = http.createServer(async (req, res) => {
  try {
    const url = new URL(req.url, 'http://localhost');

    if (url.pathname === '/api/health') {
      return sendJson(res, 200, {
        ok: true,
        version: '1.0.2',
        aiConfigured: Boolean(process.env.OPENAI_API_KEY)
      });
    }

    if (url.pathname === '/api/ai' && req.method === 'POST') {
      let body = '';
      for await (const chunk of req) body += chunk;
      const payload = JSON.parse(body || '{}');

      if (!process.env.OPENAI_API_KEY) {
        if (payload.mode === 'fix') {
          return sendJson(res, 200, {
            correction: payload.text || '',
            explanation: 'AI chưa được cấu hình. Đây là chế độ demo.',
            naturalVersion: payload.text || '',
            examples: ['Can you say that again?', 'Could you speak more slowly?', 'I want to communicate better.']
          });
        }
        return sendJson(res, 200, {
          reply: 'Let’s keep practicing. Tell me a little more.',
          corrections: [],
          nextQuestion: 'What happened next?',
          usefulPhrase: 'Tell me a little more.',
          shouldEndSession: false
        });
      }

      return sendJson(res, 501, {error:'Live AI wiring pending production key validation'});
    }

    let pathname = url.pathname === '/' ? '/index.html' : url.pathname;
    if (!path.extname(pathname)) pathname = '/index.html';

    const safe = pathname.replace(/^\/+/, '');
    const filePath = path.join(publicDir, safe);
    if (!filePath.startsWith(publicDir)) throw new Error('Invalid path');

    const data = await fs.readFile(filePath);
    res.writeHead(200, {
      ...headers,
      'Content-Type': mime[path.extname(filePath)] || 'application/octet-stream',
      'Cache-Control': pathname === '/index.html' ? 'no-store' : 'public, max-age=3600'
    });
    res.end(data);
  } catch {
    res.writeHead(404, {...headers, 'Content-Type':'text/plain; charset=utf-8'});
    res.end('Not found');
  }
});

server.listen(port, '0.0.0.0', () => {
  console.log(`Nhím Goes running on port ${port}`);
});
