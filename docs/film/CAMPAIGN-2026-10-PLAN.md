# Elitron Labs film campaign (Oct 2026): production plan and approval sample

**Status:** approval sample produced 2026-10-25. **Nothing generated at scale and nothing published.**
Source brief: Ali's "Cinematic Film Production Directive" (Films 01–03). The existing 47 s brand film stays live until a replacement is approved.

## 1. Reuse, not rebuild
The Oct 12 film pipeline (`docs/film/build/`) already covers the edit:
- `engine.py`: picture edit, compositing real UI captures.
- `audio.py`: original score and SFX synthesized in code, the mix, captions.
- Narration voice "Arthur" (Higgsfield `text2speech_v2` / ElevenLabs engine).

The campaign uses the same system, so color, sound signature and voice stay consistent with the current film.

## 2. Generated vs composited (honesty rules)
- **Video models never draw readable text, UI, logos or results.**
- Readable screens are real HTML/captures composited in the edit:
  - the elitronlabs.io site;
  - the lead-automation demo;
  - the VERIFAI testbed output.
- These are labelled "Illustration" or "Synthetic data" on screen.
- **Logo:** the real mark (`assets/icons.svg#mark`), added in the edit.
- **Disclosures:**
  - Film 02: "Illustrative workflow using synthetic data. Not a real client deployment."
  - Film 03: "Research prototype. Synthetic scenarios. Not commercially validated."
- **Wording check, Film 01, 0:24 ("AI assistants qualify inquiries…"):** this describes a service Elitron offers, not a deployed client system. It must be shown as an illustration. The AI Voice Agent is still "in development" on the site, so no voice-agent result is claimed.

## 3. Shot breakdown and generation needs
| Film | Shots | New generated motion shots | Composited / reused |
|---|---|---|---|
| 01 Intelligent Technology (48 s) | 12 | S01 desk pre-dawn, S02 overhead hands, S03 phone/inquiry micro-cuts, **S04→05 connection orbit (sample done)**, S06 workstation plate, S07 phone close-up, S09 engineer over-the-shoulder, S10 approval touch, S11 bright office → **9** | S06/S09 screens = real captures; S08 = reused workflow footage plus labels; S12 = logo in edit |
| 02 From Inquiry to Action (32 s) | 8 | dusk office exterior, customer phone hand, workflow node move, morning operator → **4** | form / CRM / scheduling = real demo captures (synthetic data) |
| 03 VERIFAI (32 s) | 8 | macro quote + PO, paper-to-screen move, field-mismatch macro, evidence light path, human reviewer → **5** | comparison screen + amber review gate = rendered from the real testbed output (`results/decisions.csv`) |
| **Total** | 28 | **18** | 10 |

## 4. Cost estimate (Higgsfield, preflighted 2026-10-25)
| Item | Unit cost | Qty (incl. retakes) | Credits |
|---|---|---|---|
| Keyframes (`gpt_image_2_5`) | 0.25 | ~60 | ~15 |
| Motion shots (`kling3_0` pro, 5 s, silent; start/end-frame control) | 8.75 | 18 + ~7 retakes | ~220 |
| Narration lines (`text2speech_v2`, Arthur) | 0.30 | 28 lines × 2 takes | ~17 |
| Music and SFX | composed locally in code | — | 0 |
| **Total estimate** | | | **~250 (requested cap 300)** |

Balance before the sample: 1,991.1 → after: **1,980.4 (10.7 credits spent)**. Arthur's voice id is `30fc8796-ceb6-4a66-b3a7-4a145ef7f346`; the name alone is rejected.

## 5. Approval sample (2026-10-25)
| Asset | File | Job |
|---|---|---|
| Keyframes F1-S01, S02, S04, S05, S10, S11 | `work/campaign-2026-10/keyframes/` + `contact-sheet.jpg` | 98911e83, 6517bc59, 7ee77a0a, 6e0d9b8d, 9dccc958, 513b79c7 |
| Motion sample F1-S04→S05 (5 s, kling3_0 pro) | `work/campaign-2026-10/sample/F1-S04-05.mp4` | 3ce6b9b8 |
| Narration lines N01, N05 (Arthur) | `work/campaign-2026-10/sample/` | 5c18f1d4, 54d526a3 |
| Preview cut (sample shot + narration + score bed) | `work/campaign-2026-10/sample/preview-F1-S04-05.mp4` | — |

**Director's notes from the sample**
1. **Continuity fix needed:** S02 shows a man's hands and S11 shows a woman. The owner must be one fictional person throughout. Recommendation: regenerate S02 to match S11 (woman, gray sweater), using S11 as the reference image.
2. S01's skyline reads as Detroit, which supports the Michigan positioning. It's a generic skyline, with no landmark logos.
3. In the S04→S05 sample the orbit lands exactly on the end frame. Violet runs stronger mid-shot than the "subtle violet" brief, so it gets graded down in the edit (no regeneration needed).
4. S04 → S05 is the campaign's central metaphor (disconnected → connected). It carries Film 01 at 0:12–0:20 and can be reused as the visual motif in Film 02 at 0:08.

## 6. Website work (from the same review, separate change)
These are copy/structure changes with no generation cost. They'll be proposed as a separate branch:
- add **Engineering capabilities** to the main navigation;
- add a VERIFAI spotlight on the homepage;
- separate the "website services" and "AI engineering" journeys;
- add FAQ entries on AI data handling.

BridgeOS / AegisFlow appear only as clearly labelled **concepts**, since neither has a working demo.

## 7. Approval gates (per the directive)
1. **Now:** Ali approves the look (keyframes + sample shot), the voice, and the ~300-credit cap.
2. Then Claude generates all keyframes for the three films, followed by a storyboard review (stills only, ~15 credits).
3. Motion shots + narration, then edited previews of the three films: a local/preview deployment only.
4. Ali reviews the films, the code diff and the performance numbers. Only then is anything replaced on the live site.

## 8. Storyboard stage (2026-10-25, Ali approved look, Arthur voice, 300-credit cap)
- **Continuity fixed:** S02 regenerated with S11 as the reference image (same woman, bun, gray sweater). S07 also uses that reference. The first S02 is kept as `F1-S02-v1-rejected.png`.
- **New keyframes (14, `gpt_image_2_5`, low/1k):**
  - F1: S02, S03, S06, S07, S09
  - F2: S01, S02, S03, S08
  - F3: S01, S02, S03, S04, S07
- **S08:** a frame from the real `assets/media/workflow-loop.mp4` (reused footage).
- **Storyboards:** `work/campaign-2026-10/storyboards/F0{1,2,3}-storyboard.jpg`, built by `docs/film/build/storyboard.py`.
- **Spend this stage:** 3.5 credits (1,980.4 → 1,976.9). **Campaign total so far: 14.2 of the 300 cap.**
- **Remaining video plan:** 18 motion shots (F1: 9 · F2: 4 · F3: 5) × 8.75 = 157.5, plus up to ~7 retakes (61), plus narration (~17) = **~236**.
  - Optional: re-render the 18 approved start frames at high/2k (2.75 each, ~50) for sharper shots. That brings the total to **~286**, still under 300.
- **Still to build in the edit (no credits):**
  - F3-S05: comparison screen rendered from the real `elitron-verifai/results/decisions.csv`.
  - F3-S06: review-gate motion graphic.
  - F1-S12 / F3-S08: logo end frames.
  - F2 S04–S07: crop the demo captures to the card area.

## 9. Motion, narration and edited previews (2026-10-25, Ali approved storyboards)
- **Start frames:** 18 re-rendered at `gpt_image_2_5` high/2k (`keyframes/hq/`).
- **Motion:** 18 `kling3_0` pro 5 s shots (`shots/`), all usable on first pass, so no retakes. S05 reuses the approved sample.
- **Narration:** 28 Arthur lines (`vo/`).
- **Spend:** balance 1,991.1 → 1,764.2. **Campaign total 226.9 of the 300 cap.**
- **Edit:** `docs/film/build/campaign.py` (reuses engine.py and audio.py).
  - Narration-led timing; generated plates graded (violet pulled to blue, S-curve, vignette).
  - Real captures as inserts.
  - Film 03 tables/gate rendered live from the VERIFAI testbed (`dev-0009-price_mismatch`, seed 7): real decision BLOCK on unit price $13.80 vs quote $16.23.
- **On-screen tags:**
  - "Illustration"
  - "Fictional business · sample content"
  - "Synthetic data · VERIFAI testbed"
  - "Real prototype output · synthetic scenario"
- **End-card disclosures:** Films 02 and 03, as required.
- **Outputs:** `work/campaign-2026-10/out/` contains F01/F02/F03 `.mp4` (H.264, AAC, -16 LUFS), `.vtt` captions, `-poster.webp`, and `preview.html` (captions on, no autoplay).
- **Runtime note:** Film 01 runs 54.1 s against the 48 s brief, because the 12 approved lines total 49 s of speech. Fix options: trim 2–3 lines and re-voice (~1 credit), or accept ~54 s.
- **Not done (needs Ali):** site integration (replace the hero film, add Films 02/03 to their pages) on a branch, then review, then deploy.
