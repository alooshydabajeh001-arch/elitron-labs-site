"use strict";
// Pure validation/normalisation for website leads. No I/O: unit-tested in tests/lead.test.cjs.

const CONTROL = /[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/;
const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
const UUIDISH = /^[0-9a-zA-Z-]{8,64}$/;

const INQUIRY_TYPES = ["Website Development", "AI Automation", "AI Chatbot / Voice Agent", "Custom Software", "Partnership", "Other"];

// field: [maxLength, required]
const SCHEMAS = {
  discovery: {
    name: [120, true], organization: [160, true], email: [254, true], phone: [40, false],
    inquiry_type: [60, true], problem: [3000, true], integrations: [300, false],
    timeline: [60, false], budget: [60, false],
  },
  preview: {
    business: [160, true], site: [300, false], name: [120, true], email: [254, true],
    phone: [40, false], industry: [200, true], goal: [120, true], notes: [3000, false],
  },
};

const MIN_FILL_MS = 2500; // humans don't complete these forms in under 2.5s

function validateLead(input) {
  if (!input || typeof input !== "object" || Array.isArray(input)) return { ok: false, status: 400, error: "invalid_request" };
  const path = input.path;
  const schema = SCHEMAS[path];
  if (!schema) return { ok: false, status: 400, error: "invalid_path" };

  // Spam signals: honeypot filled or submitted implausibly fast. Report success-shaped
  // "spam" so bots get no signal, but never forward.
  if (typeof input.fax === "string" && input.fax.trim() !== "") return { ok: false, status: 200, spam: true };
  const elapsed = Number(input.elapsed_ms);
  if (!Number.isFinite(elapsed) || elapsed < MIN_FILL_MS) return { ok: false, status: 200, spam: true };

  if (input.consent !== "yes") return { ok: false, status: 400, error: "invalid_fields", fields: { consent: "Please confirm to continue." } };

  const data = {};
  const fields = {};
  for (const [key, [max, required]] of Object.entries(schema)) {
    const raw = input[key] === undefined || input[key] === null ? "" : input[key];
    if (typeof raw !== "string") { fields[key] = "Invalid value."; continue; }
    const value = raw.trim();
    if (CONTROL.test(value)) { fields[key] = "Contains unsupported characters."; continue; }
    if (value.length > max) { fields[key] = `Keep this under ${max} characters.`; continue; }
    if (required && !value) { fields[key] = "This field is required."; continue; }
    data[key] = value;
  }
  if (data.email && !EMAIL.test(data.email)) fields.email = "Enter a valid email address.";
  if (path === "discovery" && data.inquiry_type && !INQUIRY_TYPES.includes(data.inquiry_type)) fields.inquiry_type = "Choose an option from the list.";
  if (path === "preview" && data.site && !/^(https?:\/\/)?[\w-]+(\.[\w-]+)+(\/\S*)?$/i.test(data.site)) fields.site = "Enter a valid website address.";
  if (Object.keys(fields).length) return { ok: false, status: 400, error: "invalid_fields", fields };

  data.email = data.email.toLowerCase();
  const requestId = typeof input.request_id === "string" && UUIDISH.test(input.request_id) ? input.request_id : null;
  return { ok: true, lead: { path, data, request_id: requestId, page: typeof input.page === "string" ? input.page.slice(0, 100) : "" } };
}

// Neutralise spreadsheet formula injection for any downstream sheet/CRM import.
function safeCell(value) {
  return typeof value === "string" && /^[=+\-@\t\r]/.test(value) ? "'" + value : value;
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function makeReference(now = new Date(), rand = Math.random) {
  const d = now.toISOString().slice(0, 10).replace(/-/g, "");
  return `EL-${d}-${Math.floor(rand() * 0xfffff).toString(16).toUpperCase().padStart(5, "0")}`;
}

module.exports = { validateLead, safeCell, escapeHtml, makeReference, INQUIRY_TYPES, SCHEMAS, MIN_FILL_MS };
