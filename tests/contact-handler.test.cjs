// Exercises the serverless handler end-to-end with a mocked fetch and mocked req/res.
const test = require("node:test");
const assert = require("node:assert");
const crypto = require("node:crypto");

function mockRes() {
  const res = { statusCode: 200, headers: {}, body: null };
  res.setHeader = (k, v) => { res.headers[k.toLowerCase()] = v; };
  res.status = (c) => { res.statusCode = c; return res; };
  res.json = (b) => { res.body = b; return res; };
  return res;
}
const lead = { path: "preview", elapsed_ms: 9000, consent: "yes", business: "Example HVAC", name: "Pat", email: "pat@example.com", industry: "HVAC", goal: "More online bookings", notes: "=cmd" };
const req = (over = {}) => ({ method: "POST", headers: { "content-type": "application/json", origin: "https://www.elitronlabs.io", host: "www.elitronlabs.io", "x-forwarded-for": over.ip || "1.1.1.1" }, body: lead, ...over });
const load = () => { delete require.cache[require.resolve("../api/contact.js")]; return require("../api/contact.js"); };

test("503 when no sink configured", async () => {
  delete process.env.LEAD_WEBHOOK_URL; delete process.env.RESEND_API_KEY;
  const res = mockRes(); await load()(req({ ip: "2.2.2.2" }), res);
  assert.equal(res.statusCode, 503);
});
test("rejects wrong method, content type and foreign origin", async () => {
  const h = load();
  let res = mockRes(); await h({ ...req(), method: "GET" }, res); assert.equal(res.statusCode, 405);
  res = mockRes(); await h(req({ headers: { "content-type": "text/plain", origin: "https://www.elitronlabs.io", host: "x" } }), res); assert.equal(res.statusCode, 415);
  res = mockRes(); await h(req({ headers: { "content-type": "application/json", origin: "https://evil.example", host: "www.elitronlabs.io" } }), res); assert.equal(res.statusCode, 403);
});
test("forwards signed webhook and returns reference", async () => {
  process.env.LEAD_WEBHOOK_URL = "https://hooks.example.invalid/lead"; process.env.LEAD_WEBHOOK_SECRET = "s3cret";
  let seen;
  global.fetch = async (url, opts) => { seen = { url, opts }; return { ok: true, status: 200 }; };
  const res = mockRes(); await load()(req({ ip: "3.3.3.3" }), res);
  assert.equal(res.statusCode, 200); assert.equal(res.body.ok, true); assert.match(res.body.reference, /^EL-/);
  const body = seen.opts.body; const ts = seen.opts.headers["X-Elitron-Timestamp"];
  const expect = "sha256=" + crypto.createHmac("sha256", "s3cret").update(ts + "." + body).digest("hex");
  assert.equal(seen.opts.headers["X-Elitron-Signature"], expect);
  assert.equal(JSON.parse(body).data.notes, "'=cmd");
});
test("502 when sink keeps failing; retries transient errors", async () => {
  process.env.LEAD_WEBHOOK_URL = "https://hooks.example.invalid/lead";
  let calls = 0; global.fetch = async () => { calls++; return { ok: false, status: 500 }; };
  const res = mockRes(); await load()(req({ ip: "4.4.4.4" }), res);
  assert.equal(res.statusCode, 502); assert.equal(calls, 3);
});
test("rate limit after 5 requests per IP", async () => {
  process.env.LEAD_WEBHOOK_URL = "https://hooks.example.invalid/lead";
  global.fetch = async () => ({ ok: true, status: 200 });
  const h = load(); let last;
  for (let i = 0; i < 6; i++) { last = mockRes(); await h(req({ ip: "5.5.5.5" }), last); }
  assert.equal(last.statusCode, 429);
});
test("spam is silently accepted but not forwarded", async () => {
  process.env.LEAD_WEBHOOK_URL = "https://hooks.example.invalid/lead";
  let calls = 0; global.fetch = async () => { calls++; return { ok: true, status: 200 }; };
  const res = mockRes(); await load()(req({ ip: "6.6.6.6", body: { ...lead, fax: "x" } }), res);
  assert.equal(res.body.ok, true); assert.equal(calls, 0);
});
