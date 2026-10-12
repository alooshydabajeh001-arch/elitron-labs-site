"use strict";
// POST /api/contact — receives website leads and forwards them to configured sinks.
//
// Configure in Vercel → Project → Settings → Environment Variables (never in code):
//   LEAD_WEBHOOK_URL      optional  n8n (or other) webhook that receives the lead as JSON
//   LEAD_WEBHOOK_SECRET   optional  HMAC-SHA256 key; signature sent as X-Elitron-Signature: sha256=<hex>
//   RESEND_API_KEY        optional  sends a notification email via Resend
//   LEAD_NOTIFY_TO        optional  notification recipient (default admin@elitronlabs.io)
//   LEAD_NOTIFY_FROM      optional  verified sender, e.g. "Elitron Labs <leads@elitronlabs.io>"
//   ALLOWED_ORIGINS       optional  comma-separated extra origins allowed to post (previews)
// At least one sink must be configured; otherwise the endpoint returns 503 and the page
// shows the direct email/phone fallback. Success is reported only after a sink accepts.

const crypto = require("node:crypto");
const { validateLead, safeCell, escapeHtml, makeReference } = require("./_lib/lead.js");

const DEFAULT_ORIGINS = ["https://www.elitronlabs.io", "https://elitronlabs.io"];
const hits = new Map(); // best-effort per-instance rate limit (serverless instances are ephemeral)
const WINDOW_MS = 10 * 60 * 1000, MAX_PER_WINDOW = 5;

function originAllowed(origin, host) {
  if (!origin) return false;
  const extra = (process.env.ALLOWED_ORIGINS || "").split(",").map((s) => s.trim()).filter(Boolean);
  if (DEFAULT_ORIGINS.concat(extra).includes(origin)) return true;
  try { return new URL(origin).host === host; } catch { return false; } // same-origin (incl. Vercel previews)
}

function rateLimited(ip) {
  const now = Date.now();
  const list = (hits.get(ip) || []).filter((t) => now - t < WINDOW_MS);
  list.push(now);
  hits.set(ip, list);
  if (hits.size > 5000) hits.clear();
  return list.length > MAX_PER_WINDOW;
}

async function withRetry(fn, attempts = 3) {
  let last;
  for (let i = 0; i < attempts; i++) {
    try { return await fn(); } catch (e) { last = e; if (e.permanent) break; await new Promise((r) => setTimeout(r, 300 * 2 ** i)); }
  }
  throw last;
}

async function postJson(url, body, headers) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), 8000);
  try {
    const res = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json", ...headers }, body, signal: ctrl.signal });
    if (!res.ok) { const err = new Error(`sink responded ${res.status}`); err.permanent = res.status >= 400 && res.status < 500 && res.status !== 429; throw err; }
    return true;
  } finally { clearTimeout(t); }
}

function sendWebhook(payload) {
  const url = process.env.LEAD_WEBHOOK_URL;
  const body = JSON.stringify(payload);
  const headers = {};
  if (process.env.LEAD_WEBHOOK_SECRET) {
    const ts = String(Math.floor(Date.now() / 1000));
    headers["X-Elitron-Timestamp"] = ts;
    headers["X-Elitron-Signature"] = "sha256=" + crypto.createHmac("sha256", process.env.LEAD_WEBHOOK_SECRET).update(ts + "." + body).digest("hex");
  }
  return withRetry(() => postJson(url, body, headers));
}

function sendEmail(payload) {
  const d = payload.data;
  const rows = Object.entries(d).map(([k, v]) => `<tr><td style="padding:4px 12px 4px 0;color:#555"><b>${escapeHtml(k)}</b></td><td style="padding:4px 0">${escapeHtml(v).replace(/\n/g, "<br>")}</td></tr>`).join("");
  const label = payload.path === "preview" ? "Free website preview" : "Discovery call";
  const body = JSON.stringify({
    from: process.env.LEAD_NOTIFY_FROM,
    to: [process.env.LEAD_NOTIFY_TO || "admin@elitronlabs.io"],
    reply_to: d.email,
    subject: `[Website lead] ${label}: ${(d.organization || d.business || d.name).slice(0, 80)} (${payload.reference})`,
    html: `<p><b>${label}</b> request ${payload.reference} received ${payload.received_at}.</p><table>${rows}</table><p style="color:#777">Reply goes to the sender. Review before responding.</p>`,
  });
  return withRetry(() => postJson("https://api.resend.com/emails", body, { Authorization: `Bearer ${process.env.RESEND_API_KEY}` }));
}

module.exports = async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store");
  if (req.method !== "POST") { res.setHeader("Allow", "POST"); return res.status(405).json({ ok: false, error: "method_not_allowed" }); }
  if (!String(req.headers["content-type"] || "").includes("application/json")) return res.status(415).json({ ok: false, error: "unsupported_media_type" });
  if (!originAllowed(req.headers.origin, req.headers.host)) return res.status(403).json({ ok: false, error: "forbidden_origin" });

  const ip = String(req.headers["x-forwarded-for"] || "").split(",")[0].trim() || "unknown";
  if (rateLimited(ip)) return res.status(429).json({ ok: false, error: "rate_limited" });

  let input = req.body;
  if (typeof input === "string") { try { input = JSON.parse(input); } catch { input = null; } }
  if (input && JSON.stringify(input).length > 20000) return res.status(413).json({ ok: false, error: "too_large" });

  const result = validateLead(input);
  if (result.spam) return res.status(200).json({ ok: true, reference: makeReference() }); // silent drop
  if (!result.ok) return res.status(result.status).json({ ok: false, error: result.error, fields: result.fields });

  const hasWebhook = !!process.env.LEAD_WEBHOOK_URL;
  const hasEmail = !!(process.env.RESEND_API_KEY && process.env.LEAD_NOTIFY_FROM);
  if (!hasWebhook && !hasEmail) {
    console.error("contact: no lead sink configured");
    return res.status(503).json({ ok: false, error: "not_configured" });
  }

  const reference = makeReference();
  const data = Object.fromEntries(Object.entries(result.lead.data).map(([k, v]) => [k, safeCell(v)]));
  const payload = {
    reference, received_at: new Date().toISOString(), source: "elitronlabs.io",
    path: result.lead.path, request_id: result.lead.request_id, page: result.lead.page, data,
  };

  const jobs = [];
  if (hasWebhook) jobs.push(sendWebhook(payload));
  if (hasEmail) jobs.push(sendEmail(payload));
  const outcomes = await Promise.allSettled(jobs);
  const delivered = outcomes.filter((o) => o.status === "fulfilled").length;
  outcomes.filter((o) => o.status === "rejected").forEach((o) => console.error("contact: sink failed:", o.reason && o.reason.message));

  if (!delivered) return res.status(502).json({ ok: false, error: "delivery_failed" });
  console.log(`contact: lead ${reference} (${payload.path}) delivered to ${delivered}/${jobs.length} sink(s)`);
  return res.status(200).json({ ok: true, reference });
};
