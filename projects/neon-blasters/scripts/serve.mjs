import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { extname, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(fileURLToPath(new URL('../src/', import.meta.url)));
const types = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.json': 'application/json; charset=utf-8' };
const server = createServer(async (request, response) => {
  try {
    const pathname = decodeURIComponent(new URL(request.url, 'http://localhost').pathname);
    const relative = pathname === '/' ? 'index.html' : pathname.replace(/^\/+/, '');
    const file = resolve(root, relative);
    if (file !== root && !file.startsWith(root + sep)) { response.writeHead(403).end('Forbidden'); return; }
    const info = await stat(file);
    if (!info.isFile()) throw new Error('Not a file');
    const content = await readFile(file);
    response.writeHead(200, { 'content-type': types[extname(file)] || 'application/octet-stream', 'content-length': content.length, 'cache-control': 'no-store' });
    response.end(content);
  } catch {
    response.writeHead(404, { 'content-type': 'text/plain; charset=utf-8' }).end('Not found');
  }
});
const requestedPort = Number(process.env.PORT);
const port = Number.isInteger(requestedPort) && requestedPort > 0 && requestedPort <= 65535 ? requestedPort : 8792;
server.listen(port, '127.0.0.1', () => console.log(`Neon Blasters listening at http://127.0.0.1:${port}/`));
