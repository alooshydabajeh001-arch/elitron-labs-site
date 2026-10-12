# Media assets — origin, usage, settings

All imagery and video on the site is original, generated for Elitron Labs with Higgsfield on 2026-10-12.
No stock photography, third-party logos, people, fabricated statistics or readable text.

## Shared art direction
Midnight navy `#080F1E`, electric blue `#4B8BFF`, restrained soft violet `#8A7CFF`; premium CGI, cinematic lighting,
shallow depth of field, calm motion, no text, no logos.

## Stills — model `gpt_image_2_5` (0.25 credits each)
| File (`assets/img/`) | Job ID | Aspect | Used on |
|---|---|---|---|
| hero-lattice-{720,1344}.webp, og-image.jpg | 45e4c986-51e9-4f28-adef-b699d514b180 | 16:9 | Home hero poster, OG image, Work (site card) |
| svc-web-* | a999de14-54c5-41df-b938-8945b97dbe62 | 16:9 | Home + Solutions: Websites |
| svc-automation-* | 05a7e209-b804-4d49-bdb2-a0ee46f688eb | 16:9 | Home + Solutions: Automation |
| svc-agents-* | 46c9ebb0-3bad-4049-ada7-433edb334bdc | 16:9 | Home + Solutions: AI Agents |
| svc-software-* | f135b18f-7c9a-4c58-ad1d-867ae8d148ff | 16:9 | Home + Solutions: Custom Software |
| workflow-path-* | 59fcbcdd-019b-4f7d-acbb-b1c44a3b3bc9 | 16:9 | Demo poster, Work (demo card) |
| bg-texture-* | db7f028a-9f05-4b25-8e73-e3e4feb83630 | 21:9 | Inner-page hero and CTA backgrounds |
| studio-bench-* | 73395751-60de-4b2b-88d4-a786be58076a | 16:9 | Home "Why", About |

Source PNGs are 1344px wide; exported as WebP q76–78 at 720w and 1344w (`srcset`).

## Video — model `kling3_0`, mode `pro`, 10 s, silent, 16:9 (17.5 credits each)
Image-to-video with the still as both start and end frame for a seamless loop.
| File (`assets/media/`) | Job ID | Source still | Post-processing |
|---|---|---|---|
| hero-loop.{webm,mp4} | 86419f48-a206-4094-96a5-614233f51a6a | hero-lattice | 1280w, `gblur sigma=2.2` (softens model-added pseudo-text strokes on glass panels into abstract light texture), VP9 CRF36 / H.264 CRF24, no audio track |
| workflow-loop.{webm,mp4} | 5b5f307e-9f63-4f44-b848-decc469c3215 | workflow-path | 1280w, VP9 CRF36 / H.264 CRF24, no audio track |

Rejected: first hero render 59868110-1fcb-450f-8e9c-3721b51cd6c1 (visible pseudo-text on the central panel).

**Credits spent: 8 × 0.25 + 3 × 17.5 = 54.5** (approved budget ≈40, hard cap 60).

## Loading behaviour
- Hero: poster image is the LCP element (preloaded, `fetchpriority=high`). Video sources are attached only after `load`,
  only at ≥760px wide, and never with `prefers-reduced-motion` or Save-Data. Pause/play control provided.
- Workflow loop: lazy-attached when the demo scrolls into view; paused when off-screen; hidden on small screens.
- No audio tracks exist in any file.
