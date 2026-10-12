// Copies partials/header.html and partials/footer.html into every page between
// <!-- @header --> / <!-- /@header --> and <!-- @footer --> / <!-- /@footer --> markers,
// and marks the current page's nav link with aria-current. Run: node scripts/sync-partials.mjs
import { readFileSync, writeFileSync, readdirSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const header = readFileSync(join(root, "partials/header.html"), "utf8").trim();
const footer = readFileSync(join(root, "partials/footer.html"), "utf8").trim();
const SKIP = new Set(["demo-summit-hvac.html"]);

const inject = (html, name, block) => {
  const re = new RegExp(`<!-- @${name} -->[\\s\\S]*?<!-- /@${name} -->`);
  if (!re.test(html)) throw new Error(`missing @${name} markers`);
  return html.replace(re, `<!-- @${name} -->\n${block}\n<!-- /@${name} -->`);
};

for (const file of readdirSync(root).filter((f) => f.endsWith(".html") && !SKIP.has(f))) {
  const path = join(root, file);
  let html = readFileSync(path, "utf8");
  if (!html.includes("<!-- @header -->")) continue;
  const current = header.replace(
    new RegExp(`(<nav class="(?:nav-links|mobile-nav)"[\\s\\S]*?)<a href="${file}">`, "g"),
    `$1<a href="${file}" aria-current="page">`
  );
  html = inject(inject(html, "header", current), "footer", footer);
  writeFileSync(path, html);
  console.log("synced", file);
}
