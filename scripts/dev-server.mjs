// Local preview server: serves the static site, applies vercel.json headers (incl. CSP),
// and routes POST /api/contact to the real handler. Run: node scripts/dev-server.mjs [port]
import http from "node:http";
import { readFile, stat } from "node:fs/promises";
import { join, extname, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const require = createRequire(import.meta.url);
const handler = require(join(root, "api/contact.js"));
const vercel = JSON.parse(await readFile(join(root, "vercel.json"), "utf8"));
const port = Number(process.argv[2] || 4321);
const allowDocs = process.argv.includes("--allow-docs"); // film UI renders live in docs/film/ui
const TYPES = { ".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript", ".svg": "image/svg+xml", ".webp": "image/webp",
  ".jpg": "image/jpeg", ".png": "image/png", ".woff2": "font/woff2", ".mp4": "video/mp4", ".webm": "video/webm", ".xml": "application/xml", ".txt": "text/plain" };

function headersFor(path) {
  const out = {};
  for (const rule of vercel.headers) {
    const re = new RegExp("^" + rule.source.replace(/\(\.\*\)/g, "(.*)") + "$");
    if (re.test(path)) for (const h of rule.headers) out[h.key] = h.value;
  }
  return out;
}

http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  if (url.pathname === "/api/contact") {
    let raw = ""; req.on("data", (c) => (raw += c));
    await new Promise((r) => req.on("end", r));
    try { req.body = JSON.parse(raw || "null"); } catch { req.body = raw; }
    const shim = Object.assign(res, {
      status(c) { res.statusCode = c; return shim; },
      json(b) { res.setHeader("Content-Type", "application/json"); res.end(JSON.stringify(b)); return shim; },
    });
    return handler(req, shim);
  }
  let p = url.pathname === "/" ? "/index.html" : decodeURIComponent(url.pathname);
  let file = join(root, p);
  if (!file.startsWith(root) || (/\/(api|tests|scripts|partials|node_modules|\.git)\//.test(p) || (!allowDocs && p.startsWith("/docs/")))) file = join(root, "404.html");
  let status = 200;
  try { if (!(await stat(file)).isFile()) throw 0; } catch { file = join(root, "404.html"); status = 404; }
  const body = await readFile(file);
  const range = req.headers.range;
  const headers = { "Content-Type": TYPES[extname(file)] || "application/octet-stream", ...(allowDocs && p.startsWith("/docs/") ? {} : headersFor(p)), "Accept-Ranges": "bytes" };
  if (range && status === 200) {
    const [s, e] = range.replace("bytes=", "").split("-").map(Number);
    const end = Math.min(e || body.length - 1, body.length - 1);
    res.writeHead(206, { ...headers, "Content-Range": `bytes ${s}-${end}/${body.length}`, "Content-Length": end - s + 1 });
    return res.end(body.subarray(s, end + 1));
  }
  res.writeHead(status, headers);
  res.end(body);
}).listen(port, () => console.log(`http://localhost:${port}`));
