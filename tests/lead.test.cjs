const test = require("node:test");
const assert = require("node:assert");
const { validateLead, safeCell, makeReference } = require("../api/_lib/lead.js");

const discovery = () => ({ path: "discovery", elapsed_ms: 9000, consent: "yes", fax: "", name: "Test Person", organization: "Example Co",
  email: "Test@Example.com", inquiry_type: "AI Automation", problem: "Leads go cold.", request_id: "123e4567-e89b-42d3-a456-426614174000" });
const preview = () => ({ path: "preview", elapsed_ms: 9000, consent: "yes", business: "Example HVAC", name: "Pat", email: "pat@example.com",
  industry: "HVAC", goal: "More online bookings", site: "examplehvac.com" });

test("valid discovery lead normalises email", () => {
  const r = validateLead(discovery());
  assert.equal(r.ok, true);
  assert.equal(r.lead.data.email, "test@example.com");
  assert.equal(r.lead.path, "discovery");
});
test("valid preview lead", () => assert.equal(validateLead(preview()).ok, true));
test("rejects unknown path and non-objects", () => {
  assert.equal(validateLead({ ...discovery(), path: "x" }).error, "invalid_path");
  assert.equal(validateLead(null).ok, false);
  assert.equal(validateLead([]).ok, false);
});
test("honeypot and fast fills are silent spam", () => {
  assert.equal(validateLead({ ...discovery(), fax: "buy now" }).spam, true);
  assert.equal(validateLead({ ...discovery(), elapsed_ms: 400 }).spam, true);
  assert.equal(validateLead({ ...discovery(), elapsed_ms: "abc" }).spam, true);
});
test("requires consent", () => assert.ok(validateLead({ ...discovery(), consent: undefined }).fields.consent));
test("required, length, type and control-char checks", () => {
  const r = validateLead({ ...discovery(), name: "", problem: "x".repeat(3001), organization: 5, email: "nope", inquiry_type: "Hacking" });
  assert.deepEqual(Object.keys(r.fields).sort(), ["email", "inquiry_type", "name", "organization", "problem"]);
  assert.ok(validateLead({ ...discovery(), name: "a\u0007b" }).fields.name);
});
test("bad website address rejected", () => assert.ok(validateLead({ ...preview(), site: "not a url" }).fields.site));
test("unexpected fields are dropped", () => {
  const r = validateLead({ ...discovery(), admin: "true", __proto__x: 1 });
  assert.equal(r.lead.data.admin, undefined);
});
test("formula injection neutralised", () => {
  assert.equal(safeCell("=HYPERLINK(1)"), "'=HYPERLINK(1)");
  assert.equal(safeCell("+1 313"), "'+1 313");
  assert.equal(safeCell("hello"), "hello");
});
test("reference format", () => assert.match(makeReference(new Date("2026-10-12T00:00:00Z"), () => 0.5), /^EL-20261012-[0-9A-F]{5}$/));
