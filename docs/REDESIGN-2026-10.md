# Elitron Labs website redesign — October 2026

Branch: `redesign/2026-10`. **Update 2026-10-12:** Ali approved the merge; `main` @ `24c3297` has been production since then
(deployment `dpl_21jCdGwRftZS4v9jZ3ULGw8nb2tq`; rollback target `dpl_EEA5j9KDZ3TTC2GoyD2iGgJHUq6E`). Phase 2 work is on
`phase2/brand-film` and is not in production until Ali approves.

## 1. Audit of the previous site (main @ f0a4a37)
**Worked well:** fast static HTML/CSS/JS with no dependencies; a clear free-preview offer; honest labels on concept
demos (from the earlier fix); real contact details; a working Summit HVAC demo.

**Problems found**
- Positioning: "Websites & AI Automation for Local Businesses" and "Your customers are searching…" framed the company as
  a low-cost local web agency, with nothing for software or automation buyers.
- **Contact form was broken by design:** `action="mailto:…" method="post"` depends on the visitor's mail client.
  Most browsers open a blank email or nothing, and no lead is recorded.
- Unsupported claims: "live in 5–7 days", "24/7", "never sleeps", "runs on autopilot", "ranks on Google".
- Visuals: emoji icons, gradient text-blocks as project thumbnails, no imagery.
- SEO/tech: no canonical, OG, sitemap, robots or structured data; no security headers; no favicon; generic titles.
- Accessibility: menu button without a label or `aria-expanded`; no skip link or visible focus styles; `onclick`
  attributes; reveal animations ignored reduced-motion.

## 2. Decision: keep plain HTML/CSS/JS (no Next.js migration)
A static site with nine pages and one form doesn't need a framework. Staying static keeps it fast (no hydration),
cheap to host, and simple for Ali to edit. Shared header and footer live in `partials/`; `npm run sync` copies them
into each page. The one dynamic piece is a Vercel serverless function (`api/contact.js`).

## 3. What changed
| Area | Change |
|---|---|
| Positioning & copy | All pages rewritten around "Intelligent Technology. Real Business Growth." Requested replacements applied. Removed or softened unverifiable claims. |
| Design system | `styles.css` rebuilt: tokens (#080F1E / #111C30 / #4B8BFF / #8A7CFF / #CBD5E1), Geist variable font (self-hosted), components, WCAG-checked contrast (body 11.5:1, muted 7.4:1, button text 4.9:1). |
| Navigation | Home · Solutions · Our Work · Industries · About · Contact, plus a primary "Book a Discovery Call". Accessible mobile menu. |
| Home | Cinematic hero (video over a poster), 4 solution cards, **interactive automation demo** (5 steps, synthetic data, runs in-browser), industries, labelled work, process with deliverables and approval points, "Why", final CTA. |
| New pages | `industries.html`, `privacy.html`, `terms.html`, `404.html`. |
| Work | Status system (Live / Internal / Prototype / Concept) with filters. Fictional brands are called fictional. LIGHTNX is shown for brand/web only, with a link to its public site. |
| Contact | Two paths. **A:** Free Website Preview (business, site, contact, industry, goal). **B:** Discovery Call (organization, inquiry type, problem, integrations, timeline, budget). Consent checkbox with privacy link. |
| Lead intake | `POST /api/contact`: origin check, JSON-only, size limit, honeypot plus minimum fill time, per-IP rate limit, strict server-side validation, formula-injection guard, retries with backoff, HMAC-signed webhook, optional Resend email. Reports success only after a destination accepts the lead. |
| SEO | Unique titles and descriptions, canonical, OG/Twitter tags, Organization JSON-LD, `sitemap.xml`, `robots.txt`, one H1 per page. |
| Security | `vercel.json`: strict CSP (no inline script/style on redesigned pages), HSTS, nosniff, frame DENY, Referrer-Policy, Permissions-Policy, COOP. A looser CSP applies only to the legacy Summit HVAC demo page. |
| Analytics | None added. `app.js` fires `elitron:track` DOM events on CTA clicks, demo steps and successful submissions. Nothing is sent until an approved, consent-aware provider is wired to them. |

## 4. Lead delivery: email to admin@elitronlabs.io (Ali, 2026-10-12)
Leads are emailed to **admin@elitronlabs.io** through Resend (free tier). Reply-To is set to the visitor's address, so
"Reply" goes straight to them. Until `RESEND_API_KEY` is set, the endpoint returns 503 and the page shows the
email and phone fallback, keeping what the visitor typed.

**One-time setup (Ali only, about 5 minutes, $0):**
1. Sign up at resend.com **using admin@elitronlabs.io** as the account email. With the default sender
   `onboarding@resend.dev`, Resend only delivers to the account's own address, so no DNS changes are needed.
2. Resend → API Keys → create a key with "Sending access" only.
3. Vercel → elitron-labs-site → Settings → Environment Variables → add `RESEND_API_KEY` (Production + Preview) → Save.
4. Vercel → Deployments → latest production → Redeploy (env vars apply on the next deployment).
5. Submit a test inquiry on www.elitronlabs.io and confirm the email arrives (check spam the first time).

Optional later: verify elitronlabs.io in Resend (DNS records; needs Ali's approval) and set
`LEAD_NOTIFY_FROM="Elitron Labs <leads@elitronlabs.io>"` for a branded sender.
Other supported variables: `LEAD_NOTIFY_TO` (default admin@elitronlabs.io), `LEAD_WEBHOOK_URL` / `LEAD_WEBHOOK_SECRET`
(signed n8n webhook, if wanted later), `ALLOWED_ORIGINS`.

## 5. Items confirmed by Ali (2026-10-12: "keep them")
1. **Prices** on Solutions → "Digital Presence: from $799 + optional $79/mo" are carried over from the old site.
   Confirm they're still current (task queue notes a newer Motown offer price).
2. **Timeline language:** "Standard websites can often launch within 1–2 weeks of design approval" replaces "5–7 days".
3. **Founder section** (About) names Ali and makes no credential claims. Remove it or extend it with verified background.
4. **Engineering background line** on About and Home ("electrical and computer engineering…") comes from Ali's brief.
5. **Privacy and Terms** are plain-language drafts. Have counsel review them before relying on them.
6. **LIGHTNX card:** brand and web work only, no CAGE/UEI or defense details, links to the public site. Remove it if
   you'd rather not cross-link the two companies.

## 6. Testing
- `npm test` → 16/16 pass (validation, spam, consent, formula guard, origin/method/content-type, signed webhook,
  retries, 502 on sink failure, rate limit, 503 when unconfigured).
- Local browser checks (Chrome via the dev server with production headers): no console errors or CSP violations;
  demo flow end to end with HTML-escaping verified; form validation and focus management; 503 fallback message;
  mobile menu open/close/Escape; no horizontal scroll at 375px; video not loaded on mobile.
- Link and anchor checker: 0 broken internal links, anchors or icon references; one H1 per page; all images have alt.
- Lighthouse and Core Web Vitals: measured on the Vercel preview (see the PR description).

## 7. Rollback
Production is unaffected until merge. After merge, use "Instant Rollback" to the previous production deployment in
Vercel, or revert the merge commit.

### Preview measurements (2026-10-12, deployment dpl_7yHZv8VNm9gFrqBGaBZ5diw6Horf)
- Lighthouse mobile (home): Accessibility 100, Best Practices 92, SEO 69, Agentic Browsing 100.
  The SEO and Best Practices deductions come from the preview environment itself: Vercel adds `x-robots-tag: noindex`
  to preview URLs and injects the vercel.live feedback script, which the CSP blocks. Neither applies on the production
  domain. The one real finding (brand link accessible name ≠ visible text) is fixed in the follow-up commit.
- Performance trace, mobile (412px, Slow 4G, 4× CPU): LCP 1.24 s (hero poster image), CLS 0.00. Desktop in-browser:
  LCP 1.10 s, CLS 0. Lab numbers, possibly warm cache. Field Core Web Vitals (CrUX/INP) need real traffic.
- Live checks: security headers present; looser CSP applied only to the Summit demo; `POST /api/contact` → 503
  `not_configured` (expected until env vars are set); GET → 405; unknown path → 404 page; sitemap 200.
