# "What We Build at Elitron Labs" — production notes

Completed 2026-10-12 on branch `phase2/brand-film`. Plan: [PRODUCTION-PLAN.md](PRODUCTION-PLAN.md).

## Deliverables

| File | Spec | Where |
|---|---|---|
| Main film (master) | 46.8 s · 1920×1080 · 24 fps · H.264 High CRF 16 · AAC 256k · −16.3 LUFS · peak −3.4 dBFS | `docs/film/work/out/main.master.mp4` (local, 168 MB) |
| Main film (web) | 1080p H.264 CRF 23 (9.9 MB) and 720p (4.7 MB), lighter grain | `assets/film/elitron-film-1080.mp4`, `-720.mp4` |
| 30-second cut | 29.2 s · clean + burned-caption versions | `work/out/c30.master.mp4`, `elitron-film-30s-captioned.mp4` |
| 15-second cut | 15.0 s · clean + burned-caption versions | `work/out/c15.master.mp4`, `elitron-film-15s-captioned.mp4` |
| 9:16 vertical | 1080×1920 framed-film layout, burned captions | `work/out/elitron-film-vertical-9x16.mp4` |
| Captions | WebVTT timed to the measured narration waveforms (main 11 cues, 30 s 8, 15 s 4) | `assets/film/elitron-film.en.vtt`, `work/out/*.vtt` |
| Thumbnail | 1920×1080 and 1280×720, real mark + Geist title | `work/out/thumbnail-*.jpg` |
| Web poster / static fallback | Frame 12.2 s (connected architecture), WebP 1920/1280 | `assets/film/poster-*.webp` |
| Source footage | 5 keyframes, 4 Kling shots, 10 narration takes, reused workflow plate | `docs/film/work/src/` (local; also in the Higgsfield library) |
| UI captures | Real site and demo captures plus illustrative UI states, 1× and 2× density | `docs/film/work/cap/` (local) |
| Edit system | `build/engine.py` (picture), `build/audio.py` (score, SFX, mix, captions), `build/social.py`, `build/build.sh` | committed |

`docs/film/work/` is git-ignored (large binaries) and is never deployed (`.vercelignore`). Rebuild any cut with
`FFMPEG=… docs/film/build/build.sh main|c30|c15`.

## What is generated vs composited vs real

| Shot | Time | Content | Source |
|---|---|---|---|
| 1 | 0:00–0:03 | Office establishing dolly-in | **Generated** (K1 → Kling i2v) |
| 2 | 0:03–0:07 | Unanswered inbox → empty CRM | **Composited illustration** (HTML, sample data, "Illustration" tag) |
| 3 | 0:07–0:11 | Panels lift and connect | **Generated** (K3 → Kling, end frame K4) |
| 4 | 0:11–0:15 | Website → AI core → CRM → calendar | **Generated** (K4 → Kling) |
| 5 | 0:15–0:20 | Website on desktop and phone | Generated desk still + **real elitronlabs.io captures** mapped onto the screens |
| 6 | 0:20–0:23 | Operations dashboard | **Composited illustration** (sample data, tagged) |
| 7 | 0:23–0:26 | Document → extracted record | **Composited illustration** (sample document, tagged) |
| 8 | 0:26–0:30 | Inquiry on the contact form | **Real website** (sample values typed; never submitted) |
| 9 | 0:30–0:34 | Inquiry → AI → qualification → CRM → booking | **Reused** workflow-loop footage + composited labels |
| 10 | 0:34–0:37 | Appointment selected → confirmed | **Real site demo** (synthetic data) |
| 11 | 0:37–0:41 | Light aperture aligns | **Generated** (K11 → Kling) |
| 12 | 0:41–0:47 | Logo reveal | **Real mark** (`assets/icons.svg#mark`) + Geist, animated in the edit |

No AI-generated logo, text or interface. No customers, testimonials or results are depicted.

## Higgsfield ledger

| Item | Model | Job IDs | Credits |
|---|---|---|---|
| Keyframes K1, K3, K4, K5, K11 | gpt_image_2_5 | 5d3040cc, ff00c216, 87e14f29, f277028d, 08af7eb0 | 1.25 |
| Shots C1, C3, C4, C11 (5 s, pro, silent) | kling3_0 | 9074072e, cff2750d, abb4f600, f7498bab | 35.00 |
| Narration ×10 (8 lines + 2 audition takes) | text2speech_v2 / ElevenLabs engine, preset "Arthur" (audition: "Helena") | 1988ed18, 7c122a8a, 86e7db38, 7aab73ac, 1e537638, a2114648, 36781418, 4a225b3e, f1753741, 166ba5d5 | ~3.6 |
| **Total (balance 2,173.45 → 2,133.60)** | | | **39.85** |

No re-renders were needed (2 contingency slots unused). The Higgsfield tool tried to substitute a stock "IN THE DARK"
preset for two shots; I declined it and resubmitted the directed prompts.

## Audio and licensing
- **Narration:** Higgsfield text-to-speech (ElevenLabs engine), generated on Ali's Higgsfield plan. Commercial use is
  subject to Higgsfield's terms for that plan. Ali should confirm before paid advertising.
- **Music and sound design:** composed and synthesized in code (`build/audio.py`): pads, sub pulse, arpeggio,
  synthesized kick and hats, risers, UI ticks, and the two-note sonic signature (D5 → A5). No samples, loops or
  third-party audio, so it is wholly original.
- **Mix:** music ducked −9 dB under narration; loudness normalised to −16 LUFS (EBU R128); master peaks −2.2 to −3.4 dBFS.
- The ElevenLabs API key in this workspace returned 401, so ElevenLabs Music was not used.

## Director's quality review
| Question | Assessment |
|---|---|
| Hook in 3 s? | Yes: a premium, still office with a single unanswered notification, plus narration from 0.3 s. |
| Clear to a non-technical owner? | Yes: problem (inbox, "No record found") → idea (systems connect) → three services → one concrete workflow → booked appointment. |
| Visually connected? | Yes: one palette and grade throughout; matched continuity S3 → S4 (end frame = start frame); the light path ties S4, S9 and S11. |
| Intentional camera? | Each move has one job: dolly-in (attention), lateral (problem), push-through (transition), rack focus (desktop → mobile), pullback (resolution). |
| Consistent objects and interfaces? | Same desk materials in S1/S5; all UI shares the site's design system. |
| Natural narration? | Timing and levels verified by measurement. **Naturalness must be judged by ear (Ali).** An alternative voice take is in `work/src/Helena-*.mp3`. |
| Music supports the story? | Minor-key tension → lift on "What if…" → groove under services → restrained swell → signature on the logo. |
| Professional transitions? | Light bloom, push-throughs, whip-pan, focus pull, converging lines. No cross-dissolve stacks. |
| Communicates offerings? | Websites, custom software, AI applications, automation and integrations each get a dedicated beat. |
| Memorable ending? | Mark draws on with its own two-note chime; tagline lands with the final narration line. |
| Credible in a client presentation? | Yes, with honest labels: illustrations are tagged on screen, and real software is real. |

## Known limitations
- Generated shots are ~1924×1076 upscaled to 1080p (Kling Pro output); composited shots are rendered natively at 1080p from 2× captures.
- The 9:16 version uses a framed-film layout rather than re-composed vertical shots (cropping the UI to 9:16 made text unreadable).
- The film shows the demo's synthetic data and fictional names ("Jordan Example", "Summit HVAC (demo)") by design.
