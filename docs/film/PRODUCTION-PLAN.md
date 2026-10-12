# "What We Build at Elitron Labs" — Director's production plan

Runtime **45.0 s** · 16:9 master at 1920×1080, 24 fps · cutdowns 30 s, 15 s, 9:16 vertical
Status: **approved by Ali 2026-10-12 (cap 60 credits) · produced, 39.85 credits spent.** See PRODUCTION-NOTES.md.

---

## 1. Asset and model audit

**Brand assets in the repo.** The only Elitron mark is `assets/icons.svg#mark` / `assets/favicon.svg` (created in the
October redesign, replacing the old CSS "E" tile). No other logo file exists on this machine. The film uses that mark,
redrawn as vector, and the Geist typeface already self-hosted on the site. No AI-generated logo.

**Reusable media (docs/MEDIA.md)**

| Asset | Reuse in film? | Why |
|---|---|---|
| hero-loop (lattice, blurred) | Backup plate for Shot 11 only | Its blur and loop design suit a background, not a featured shot |
| workflow-loop (light path + 5 stations) | **Yes, Shot 9 background plate** under the composited pipeline graphic | Matches the story beat and the palette |
| svc-automation / svc-software stills | Style references for new keyframes | Keeps glass-panel material and lighting consistent |
| hero-lattice still | Colour and material reference | Sets the grade target |

**Real software available for screens (no fabrication).** These are real and screenshot-able:
- the live elitronlabs.io pages (home, solutions, contact form)
- the site's interactive automation demo (inquiry form, qualification score, CRM record, appointment slots, confirmation)
- the Summit HVAC demo site (fictional brand, labelled as such)

No real customer dashboard or AI document product exists. Shots 6 and 7 use **purpose-built illustrative interfaces**
with sample data, and carry an on-screen "Illustration" label.

**Models (from Higgsfield catalogue, preflighted 2026-10-12)**

| Need | Model | Why | Cost |
|---|---|---|---|
| Keyframes (composition lock) | `gpt_image_2_5` | Best prompt adherence for precise layout; 16:9 | 0.25 / image |
| Motion shots | `kling3_0` **pro**, 5 s, sound off | Start **and end** frame control, so I can direct match cuts between shots; best physical camera behaviour in prior tests | 8.75 / 5 s shot |
| Narration | `text2speech_v2` / ElevenLabs engine, preset voice | Most natural engine available here; one take per line for precise sync | 0.45 / line |
| Music, sound design | **Composed and synthesized locally** (Python/numpy + FFmpeg) | Fully original, so no licence question. The ElevenLabs music API key in this workspace is invalid, and Higgsfield's music model is game-pipeline-only | $0 |

Rejected: Seedance 2.5 1080p (96 cr per 8 s clip; no end-frame control). Kling "std" (saves 15% but softer detail).

## 2. Production approach: what is generated vs composited

The video model is never asked to draw readable text or interfaces. Readable UI is real HTML rendered by Chrome at
1920×1080 and animated in the edit.

| Shot | Method | Higgsfield? |
|---|---|---|
| 1 Office establishing | Keyframe K1 → Kling i2v | **Yes** |
| 2 Missed inquiries | Composited real HTML "inbox / CRM / calendar" screen, lateral camera move in edit | No |
| 3 Systems begin connecting | Keyframe K3 → Kling i2v **with end frame K4** | **Yes** |
| 4 Engineering a better system | Kling i2v **starting on K4** (seamless continuation of 3) | **Yes** |
| 5 Website development | Keyframe K5 (desk with blank screens) + **real elitronlabs.io screenshots** perspective-mapped onto the monitor and phone; 2.5D camera move in edit | Still only |
| 6 Custom software | Illustrative dashboard (HTML, sample data, "Illustration" tag); lateral track + focus pull in edit | No |
| 7 AI applications | Illustrative document-intelligence UI (HTML); fields extract sequentially | No |
| 8 Customer inquiry | **Real** elitronlabs.io contact form; typing animation from real states | No |
| 9 AI processing → CRM | Pipeline graphic (Inquiry → AI processing → Qualification → CRM record) over **reused workflow-loop** | No (reuse) |
| 10 Automated booking | **Real** site demo: appointment slots → confirmation | No |
| 11 Connected technology | Keyframe K11 → Kling i2v, symmetric pullback | **Yes** |
| 12 Logo reveal | Real mark + Geist wordmark + tagline animated in edit over Shot 11's final frame | No |

**Grade (applied to every shot):** shadows lifted to navy `#080F1E` (never pure black), highlights biased toward
`#4B8BFF`, violet `#8A7CFF` limited to rim and accent light, saturation −8%, gentle S-curve, 2% film grain,
soft vignette. Composited UI gets the same grade plus a screen-glow bloom so it sits in the same world.

## 3. Narration (one take per line; timings are when each line starts)

| Line | In | Text | ~Length |
|---|---|---|---|
| N1 | 0:00.6 | "Every opportunity matters. But missed inquiries and disconnected systems can slow a growing business." | 6.0 s |
| N2 | 0:08.0 | "What if your technology worked together, instead of getting in the way?" | 4.0 s |
| N3 | 0:15.6 | "At Elitron Labs, we build high-performance websites, custom software, and AI-powered solutions around your goals." | 6.5 s |
| N4 | 0:26.8 | "From intelligent assistants to automated follow-ups, we connect the steps that turn interest into action." | 6.0 s |
| N5 | 0:37.6 | "Less friction. More possibility." | 2.2 s |
| N6 | 0:41.3 | "Elitron Labs. Intelligent Technology. Real Business Growth." | 3.4 s |

Cutdown-only lines: **C15a** "Websites, custom software, and AI, built around your goals." **C30a** "Missed inquiries and
disconnected systems slow a growing business." Voice audition: two preset voices read N1 and N3, and Ali picks one.
I can verify timing, loudness and clipping, but **naturalness has to be judged by ear: Ali's sign-off.**

**Music cue sheet (original score):**
- 0:00–0:07 low sustained pad (D minor), soft sub pulse at 92 bpm rising slightly, sparse notification "ticks" left unresolved
- 0:07 resolve to D major lift, filtered sweep
- 0:15–0:37 confident pulse: arpeggiated synth, muted orchestral-style string pad, light percussion, UI clicks on the cut points
- 0:37 riser into a restrained swell
- 0:41.3 music drops to a single sustained chord plus the **sonic signature**: a two-note rising chime (D5→A5) with a soft sub-thump on the logo
- 0:44–0:45 fade to silence and black

Mix: dialogue −16 LUFS integrated master, music ducked −9 dB under narration via sidechain, true peak ≤ −1 dBTP.

---

## 4. Shot specifications

Every Higgsfield prompt below is final copy. Negatives apply in addition to the global list:
**GLOBAL NEGATIVES:** no text, letters, numbers, captions, code or symbols on any surface; no logos or brand marks;
no people or hands unless specified; no robots; no floating holograms; no particle storms; no lens flares beyond
one subtle highlight; no camera roll or spin; no morphing furniture; no flicker.

### SHOT 1: Establishing the problem · 0:00.0–0:03.0 (3.0 s)
1. **ID/duration:** S1 · 3.0 s (generated 5 s; best 3 s used)
2. **Purpose:** Hook. A premium, believable business setting, quiet tension, something waiting.
3. **Setting:** Modern office after hours, floor-to-ceiling window behind with defocused night city.
4. **Subjects:** Walnut desk; two slim black monitors; low-profile keyboard; smartphone face-up; ceramic cup. Nothing else.
5. **Opening composition:** Medium-wide, seated eye height; monitors slightly left of centre; window bokeh upper right.
6. **Action:** A soft blue notification glow blooms in the top-right of the left monitor and pulses once. The room is still.
7. **Camera:** Slow straight dolly-in, ~30% closer over the shot; no rotation, no shake.
8. **Lens/DoF:** 35 mm, f/2; focus on monitors; keyboard foreground soft.
9. **Light/colour:** Cool blue monitor spill on desk, neutral warm-gray ambient, navy shadows, faint violet rim on monitor edges.
10. **Timing:** Constant slow speed; the glow appears at ~40% of the clip.
11. **Final frame:** Left monitor fills centre-left; screen at roughly 45% of frame width.
12. **Transition →2:** Match cut on the monitor. Shot 2 opens on the same monitor at screen-filling scale (straight cut on the pulse).
13. **Narration:** N1 starts 0:00.6.
14. **Sound:** Room tone, low pad enters, a single soft notification tick at 0:01.4.
15. **Keyframe prompt (K1, gpt_image_2_5, 16:9):**
    > Photoreal cinematic film still, medium-wide shot at seated eye height of a premium modern office workstation in the evening. A clean walnut desk holds two slim black frameless monitors side by side, a low-profile aluminium keyboard, a smartphone lying face-up to the right, and a small matte ceramic cup. Nothing else is on the desk. Both monitors show soft, slightly out-of-focus application layouts built only from blurred rectangles of light (a narrow list column, a calendar grid, a simple table), with no readable characters. Cool blue monitor light spills across the desk; neutral warm-gray ambient light; behind the desk a floor-to-ceiling window shows defocused night city lights in deep navy. 35mm lens, f/2, shallow depth of field, focus on the monitors, gentle reflections on the screen glass. Colour palette: midnight navy shadows, electric blue highlights, a faint violet rim light on the monitor edges. Calm, premium, realistic textures. No people, no text, no logos.
    **Video prompt (C1, kling3_0 pro, 5 s, start=K1):**
    > The camera performs one slow, perfectly steady dolly-in straight toward the two monitors, travelling about one third of the distance over five seconds at seated eye height, with no rotation, tilt or shake. At about two seconds, a small soft blue glow appears in the top-right corner of the left monitor, pulses gently once, and remains. Everything in the room stays physically still; only the reflections on the screen glass shift naturally with the camera's movement. Focus stays on the monitors. The final frame shows the left monitor filling the centre-left of the frame. No text appears anywhere, no people, no new objects.
16. **Negatives:** readable UI, extra monitors appearing, desk items moving, warped keyboard, people's reflections.

### SHOT 2: Missed opportunities · 0:03.0–0:07.0 (4.0 s) · composited, $0
1. S2 · 4.0 s
2. **Purpose:** Make the problem concrete for a non-technical viewer: requests pile up, and the systems don't talk to each other.
3. **Setting:** Screen-filling view of the left monitor (subtle bezel edge at frame left, glass reflection layer).
4. **Subjects (real HTML, sample data):** an inbox column with four new requests ("Service estimate", "Pricing question",
   "Appointment request", "Callback request") marked *Unanswered* with ages; a separate CRM panel showing *No record*; a
   calendar with open slots; a dashed "copy manually" indicator between inbox and CRM. Corner tag: *Illustration*.
5. **Opening:** Inbox column centred; the newest request slides in at the top (continuing Shot 1's pulse).
6. **Action:** Requests stack one by one (every 0.6 s), each with a soft red dot. The view drifts right to the empty CRM panel.
7. **Camera (edit):** Lateral track left→right across a 3840-px-wide render; 2% push-in; slight barrel distortion and glass reflection.
8. **Lens/DoF:** 50 mm feel; graduated blur at frame edges.
9. **Light:** Screen glow; reflection layer carries a faint window-bokeh echo from Shot 1.
10. **Timing:** Ease-in-out pan over 4 s.
11. **Final frame:** CRM panel "No record" centred.
12. **Transition →3:** The monitor's blue light blooms outward across the full frame (12-frame light expansion), revealing Shot 3.
13. **Narration:** N1 continues to ~0:06.6.
14. **Sound:** Three soft unanswered notification ticks, slightly detuned; pulse rises; whoosh on the bloom.
15. **Prompt:** n/a (composite). Source: `docs/film/ui/s2-inbox.html`.
16. **Negatives:** no real names, emails or phone numbers. Sample labels only.

### SHOT 3: Systems begin connecting · 0:07.0–0:11.0 (4.0 s)
1. S3 · 4.0 s (generated 5 s)
2. **Purpose:** The turn. Disconnected tools lift apart and start linking: the idea of integration, made visual.
3. **Setting:** The monitor surface dissolving into a deep navy space.
4. **Subjects:** Three translucent glass panels (a list, a calendar grid, a table, all made of light blocks, no text) and a thin electric-blue line forming between them.
5. **Opening (K3):** Close-up: the three panels sit flat against a dark monitor surface, dim and separated, with a faint blue glow behind.
6. **Action:** Panels lift forward off the surface and drift apart into space. Thin electric-blue lines extend between them one at a time (list→calendar, then calendar→table). The room falls away into navy.
7. **Camera:** Controlled forward push with a slight rise (crane up ~5°); no roll.
8. **Lens/DoF:** 40 mm, f/2.8; panels sharp, background soft.
9. **Light:** Navy void, panels edge-lit in electric blue, violet only on the far panel's rim.
10. **Timing:** Panels separate in 0–2 s, lines draw in 2–4.5 s.
11. **Final frame (= K4):** The structured system composition below, so Shot 4 continues seamlessly.
12. **Transition →4:** Seamless continuation (same frame), with a soft 6-frame dissolve to hide any micro-difference.
13. **Narration:** N2 at 0:08.0.
14. **Sound:** Tension resolves; filtered sweep opens; soft "connect" tones as each line completes.
15. **Keyframe prompt (K3, gpt_image_2_5, 16:9):**
    > Photoreal cinematic close-up of the glass surface of a dark computer monitor in a dim room. Three separate translucent glass interface panels rest flat against the screen, each built only from soft glowing blocks of light: a narrow vertical list panel on the left, a calendar grid panel in the centre, and a table panel on the right. They are dim, slightly misaligned and clearly not connected to each other. Faint electric blue backlight, deep midnight navy surroundings, a hint of soft violet on the right panel's edge. 40mm lens, f/2.8, shallow depth of field. Elegant, minimal, realistic glass material with subtle reflections. No readable text, no numbers, no logos.
    **Video prompt (C3, kling3_0 pro, 5 s, start=K3, end=K4):**
    > The three translucent glass panels slowly lift forward away from the monitor surface and drift apart into a deep navy space as the monitor and room behind them fade into darkness. Thin, precise electric-blue lines of light then extend between them one at a time: first from the list panel to the calendar panel, then from the calendar panel to the table panel. The camera moves smoothly forward and rises slightly, with no rotation. The motion is calm, deliberate and physically believable. The shot ends on the final composition shown in the end frame. No text, no particles, no holograms, no new objects except the connecting lines.
16. **Negatives:** panels melting or merging, text glyphs inside panels, particle bursts, spinning.

### SHOT 4: Engineering a better system · 0:11.0–0:15.0 (4.0 s)
1. S4 · 4.0 s (generated 5 s)
2. **Purpose:** Show the solution as understandable architecture: a website feeding a CRM and calendar through an AI layer.
3. **Setting:** Navy void with a faint reflective floor plane.
4. **Subjects:** Four glass components in a clean diagram layout: a wide **website panel** on the left (browser-window shape), a **CRM panel** (table) top centre, a **calendar panel** (grid) right, and a small softly glowing **AI core** (rounded glass cube) below centre. Electric-blue lines connect website→AI core→CRM and AI core→calendar.
5. **Opening (K4):** Symmetric-leaning three-quarter view of the full system, every component visible.
6. **Action:** A single light pulse travels website→AI core→CRM→calendar; each panel brightens slightly as the pulse passes.
7. **Camera:** Smooth lateral tracking left→right while slowly pushing toward the website panel; no roll.
8. **Lens/DoF:** 35 mm, f/4 (more in focus: this is "the architecture").
9. **Light:** Blue key light from the components, violet only on the AI core, navy fill.
10. **Timing:** Pulse 0.5–3.5 s; push accelerates gently in the last second.
11. **Final frame:** The website panel fills the centre third of frame.
12. **Transition →5:** Push-through: a 10-frame zoom-blur into the website panel, cutting to Shot 5's monitor showing the real site.
13. **Narration:** N2 tail ends ~0:12.0; music lifts.
14. **Sound:** Pulse "tick-tick-tick" on each panel; whoosh into the push-through.
15. **Keyframe prompt (K4, gpt_image_2_5, 16:9):**
    > Premium cinematic CGI still of a clean, structured digital system floating in a deep midnight navy space above a faint reflective floor. Four translucent glass components are arranged like an elegant architecture diagram: on the left, a wide panel shaped like a browser window containing soft blocks of light; at top centre, a table-like panel; on the right, a calendar-grid panel; and below the centre, a small rounded glass cube glowing softly in violet. Thin precise electric-blue lines connect the browser panel to the glass cube, and the cube to the table panel and the calendar panel. Three-quarter view from slightly above, 35mm lens, f/4, everything crisp. Blue light from the components, restrained violet on the cube only, navy shadows. Orderly, calm, premium, physically believable glass and light. No readable text, no numbers, no logos, no particles, no people.
    **Video prompt (C4, kling3_0 pro, 5 s, start=K4):**
    > A single small pulse of electric-blue light travels along the connecting lines: from the browser-shaped panel on the left into the glowing glass cube, then up into the table panel, then across to the calendar panel, and each panel brightens slightly as the pulse passes through it. At the same time, the camera tracks smoothly from left to right while slowly pushing in toward the browser-shaped panel, ending with that panel filling the centre third of the frame. Calm, precise, physically stable; no rotation, no new objects, no text.
16. **Negatives:** extra components appearing, lines tangling, panel content becoming text-like.

### SHOT 5: Website development · 0:15.0–0:20.0 (5.0 s) · still + real screenshots
1. S5 · 5.0 s
2. **Purpose:** Concrete proof of the first service: a real, live Elitron Labs website on desktop and mobile.
3. **Setting:** The same office desk as Shot 1 (continuity), now brighter and calmer.
4. **Subjects:** A large desktop monitor and a smartphone on a small stand, both screens showing the **real elitronlabs.io** (desktop home hero; mobile home hero).
5. **Opening:** Desktop screen fills ~60% of frame, phone soft at right.
6. **Action:** The desktop site scrolls gently (real page capture scrolling hero → solutions); the focus shifts to the phone, which shows the same site's mobile layout.
7. **Camera (2.5D in edit):** Slow arc-feel move left→right with parallax (phone layer moves faster than the monitor layer).
8. **Lens/DoF:** 50 mm feel; rack focus from monitor to phone at 0:17.5.
9. **Light:** Matches K1 but the screens are the key light; warmer neutral ambient.
10. **Timing:** Scroll 0:15.3–0:17.5, rack 0:17.5–0:18.3, hold.
11. **Final frame:** Phone screen centre-right, sharp.
12. **Transition →6:** Lateral slide-wipe (the phone screen sweeps left and becomes Shot 6's dashboard).
13. **Narration:** N3 starts 0:15.6.
14. **Sound:** Music in full confident pulse; a soft UI click on the rack focus.
15. **Keyframe prompt (K5, gpt_image_2_5, 16:9):**
    > Photoreal cinematic still of the same premium walnut desk in a modern office in the evening, now calm and orderly. On the left stands a large slim black desktop monitor angled slightly toward camera; on the right, a smartphone sits upright on a minimal aluminium stand. Both screens display a perfectly flat, uniform medium-gray color with no content (for screen replacement), with crisp straight screen edges and no glare. Neutral warm ambient light, cool blue accent light, defocused navy night window in the background, 50mm lens, f/2.8, focus on the monitor. No text, no logos, no people.
    Screens are replaced in the edit with real captures (`docs/film/captures/site-desktop-*.png`, `site-mobile-*.png`).
16. **Negatives:** reflections on the gray screens (would break the screen replacement), curved screens.

### SHOT 6: Custom software · 0:20.0–0:23.0 (3.0 s) · composited, $0
1. S6 · 3.0 s
2. **Purpose:** The second service: custom business software.
3. **Setting:** Full-frame application UI with depth (layered panels).
4. **Subjects:** "Operations" web app (HTML): sidebar, pipeline columns (*New / Qualified / Scheduled / Done*) with sample job cards, today's schedule, task list. **No KPIs or performance figures.** Tag: *Illustration · sample data*.
5. **Opening:** Pipeline columns centred, background panels defocused.
6. **Action:** One sample card moves *New → Qualified* (shows the software doing work).
7. **Camera (edit):** Slow lateral track right→left with focus pull from the background panel to the pipeline.
8. **Lens:** 85 mm feel, shallow DoF via layered blur.
9. **Light:** Screen-light grade; blue accents from the design system.
10. **Timing:** Card move 0:20.8–0:21.8.
11. **Final frame:** The moved card is centred.
12. **Transition →7:** Focus-pull cross-dissolve (8 frames).
13. **Narration:** N3 continues.
14. **Sound:** Soft UI "slot" on the card move.
15. Source: `docs/film/ui/s6-dashboard.html`.
16. **Negatives:** no revenue, conversion or "+x%" figures; no real names.

### SHOT 7: AI applications · 0:23.0–0:26.0 (3.0 s) · composited, $0
1. S7 · 3.0 s
2. **Purpose:** The third service: AI that reads and organises information.
3. **Setting:** Split UI: a scanned sample service-request document (left) and a structured record (right).
4. **Subjects:** A document with highlighted regions; extracted fields (*Customer, Service, Location, Requested date, Urgency*) filling in one by one, each with a thin blue connector from its source highlight. Tag: *Illustration · sample document*.
5. **Opening:** Document left-of-centre, empty fields right.
6. **Action:** A scan line passes down the document (0.8 s); five fields populate sequentially (every 0.35 s).
7. **Camera (edit):** Gentle push-in 4%.
8. **Lens:** 50 mm feel.
9. **Light:** Screen grade; violet used only for the "AI" scan line.
10. **Timing:** As above; last field lands 0:25.5.
11. **Final frame:** Completed record.
12. **Transition →8:** The completed record panel zooms through to the website (push-through, 10 frames).
13. **Narration:** N3 ends ~0:22.1; a breath of music.
14. **Sound:** A delicate scan shimmer; five micro-ticks.
15. Source: `docs/film/ui/s7-docai.html`.
16. **Negatives:** no claim that this is a deployed client product.

### SHOT 8: Customer inquiry · 0:26.0–0:30.0 (4.0 s) · real website, $0
1. S8 · 4.0 s
2. **Purpose:** Start the automation story on the **real** Elitron Labs contact form.
3. **Setting:** Close-up of the real elitronlabs.io Contact page (Free Website Preview form) on a monitor with a subtle glass layer.
4. **Subjects:** Real form fields filled progressively with sample text; the "Request" button.
5. **Opening:** Form centred, cursor in the first field.
6. **Action:** Fields fill (sample: "Summit HVAC"–style fictional demo values); the button is pressed; the form compresses into a glowing card that travels right.
7. **Camera (edit):** Starts tight on the fields, eases back 6%, then follows the card right (pan).
8. **Lens:** 50 mm feel, shallow edge blur.
9. **Light:** Screen grade.
10. **Timing:** Typing 0:26.2–0:28.4; submit 0:28.6; card travel 0:29–0:30.
11. **Final frame:** The card arrives at the left edge, entering Shot 9's first node.
12. **Transition →9:** Graphic match: the card becomes node 1.
13. **Narration:** N4 at 0:26.8.
14. **Sound:** Soft key taps (synthesized), submit click, whoosh.
15. Sources: real captures of `contact.html?path=preview` in several filled states (sample data; nothing is submitted).
16. **Negatives:** never submit the live form; no personal data.

### SHOT 9: AI processing and CRM · 0:30.0–0:34.0 (4.0 s) · reuse + graphic, $0
1. S9 · 4.0 s
2. **Purpose:** Make the workflow legible in one glance.
3. **Setting:** **Reused `workflow-loop`** footage (light travelling along glass stations), graded darker, as the background plate.
4. **Subjects (graphic overlay, Geist type):** four labelled nodes, *Customer inquiry → AI processing → Lead qualification → CRM record*, aligned to the footage's stations.
5. **Opening:** Node 1 lit (the card from Shot 8 lands in it).
6. **Action:** Each node activates in sequence (ring fill + label brighten), the light travelling between them; the qualification node shows a small "Priority" tag.
7. **Camera:** Inherits the plate's slow push-in.
8. **Lens:** n/a (plate).
9. **Light:** Plate plus overlay glow.
10. **Timing:** Node activations at 0:30.2 / 0:31.1 / 0:32.0 / 0:32.9.
11. **Final frame:** All four nodes lit; the CRM node pulses.
12. **Transition →10:** The CRM node expands and becomes the booking UI (scale-through).
13. **Narration:** N4 continues to ~0:32.8.
14. **Sound:** Ascending four-step tone sequence.
15. Plate: `assets/media/workflow-loop.mp4` (job 5b5f307e). No new generation.
16. **Negatives:** the label text is composited, never generated.

### SHOT 10: Automated booking · 0:34.0–0:37.0 (3.0 s) · real demo, $0
1. S10 · 3.0 s
2. **Purpose:** Pay off the workflow with an outcome everyone understands: a booked appointment.
3. **Setting:** The real site demo's step 4 (appointment slots) and step 5 (confirmation), framed as an app panel.
4. **Subjects:** Three slot buttons; one gets selected; the confirmation card with check icon.
5. **Opening:** Slots visible.
6. **Action:** The middle slot highlights (0:34.6), then crossfades to the confirmation (0:35.4).
7. **Camera (edit):** Subtle push-in 3%.
8. **Lens:** 50 mm feel.
9. **Light:** Screen grade, green confirmation accent kept subtle.
10. **Timing:** As above.
11. **Final frame:** Confirmation card centred.
12. **Transition →11:** Blue lines from the panel edges converge to the centre and the UI falls away into Shot 11 (12 frames).
13. **Narration:** silence (music breathes).
14. **Sound:** Soft confirmation chime (a quieter variant of the closing signature).
15. Sources: real captures of the homepage demo (`index.html#demo`) with its synthetic data.
16. **Negatives:** the demo reference code shown is "DEMO-…" (already synthetic).

### SHOT 11: Connected technology · 0:37.0–0:41.0 (4.0 s)
1. S11 · 4.0 s (generated 5 s)
2. **Purpose:** Emotional lift: everything aligned, calm and powerful.
3. **Setting:** Abstract navy space.
4. **Subjects:** Elegant ribbons and frames of blue and violet light settling into a perfectly symmetric, nested arrangement around an empty dark centre (reads as a portal or aperture).
5. **Opening (K11):** Close and asymmetric; ribbons slightly offset.
6. **Action:** The ribbons glide into exact alignment and symmetry.
7. **Camera:** Slow cinematic pullback along the central axis, perfectly centred.
8. **Lens/DoF:** 35 mm, deep focus.
9. **Light:** Premium blue light against midnight navy; violet on the outer frames.
10. **Timing:** Alignment completes at ~3.5 s; then a hold.
11. **Final frame:** Symmetric, with a calm empty centre for the logo.
12. **Transition →12:** The logo materialises in the centre over the held last frame (no cut).
13. **Narration:** N5 at 0:37.6.
14. **Sound:** Riser into a restrained swell.
15. **Keyframe prompt (K11, gpt_image_2_5, 16:9):**
    > Premium cinematic abstract CGI, perfectly centred one-point composition. Several elegant thin ribbons and rounded-rectangle frames of electric-blue light, with the outermost frames in soft violet, are nested around an empty, calm, dark centre in a deep midnight navy space, like a refined architectural aperture made of light. The frames are slightly offset from one another, not yet aligned. Subtle volumetric haze, glossy dark floor reflection at the bottom, 35mm lens, deep focus. Restrained and premium: no particles, no sparks, no text, no logos, no symbols.
    **Video prompt (C11, kling3_0 pro, 5 s, start=K11):**
    > The camera pulls back slowly and perfectly straight along the central axis, keeping the composition exactly centred. As it pulls back, the nested ribbons and frames of blue and violet light glide smoothly into precise symmetrical alignment around the empty dark centre, settling completely by the fourth second and then holding still. Calm, elegant, controlled motion. The centre stays empty and dark. No rotation, no particles, no flashes, no text, no symbols.
16. **Negatives:** anything appearing in the centre, spiralling motion, flares.

### SHOT 12: Logo reveal · 0:41.0–0:45.0 (4.0 s) · composited, $0
1. S12 · 4.0 s
2. **Purpose:** A memorable, clean brand ending.
3. **Setting:** Shot 11's final frame (held, with a 2% slow push), slightly dimmed behind the logo.
4. **Subjects:** The **real** Elitron mark (vector from `assets/icons.svg#mark`, rendered at 4×), the wordmark **ELITRON LABS** (Geist 600, tracking +0.18em), and the tagline *Intelligent Technology. Real Business Growth.* (Geist 450).
5. **Opening:** Empty centre.
6. **Action:** The mark's strokes draw on (0.6 s, blue stroke, then violet middle bar), a soft light sweep crosses it once, the wordmark fades up with a 6-px rise, and the tagline follows 0.4 s later.
7. **Camera:** 2% push on the background only (the logo stays locked).
8. **Lens:** n/a.
9. **Light:** Soft bloom behind the mark (blue core, violet edge).
10. **Timing:** Mark 0:41.2, wordmark 0:41.9, tagline 0:42.3, hold, fade to black 0:44.4–0:45.0.
11. **Final frame:** Centred lockup on navy, then black.
12. **Transition:** Fade to black.
13. **Narration:** N6 at 0:41.3.
14. **Sound:** The sonic signature (two-note chime plus soft sub), then silence.
15. Built from repo assets; no generation.
16. **Negatives:** no generated or altered logo.

---

## 5. Cutdowns and formats

| Deliverable | Structure | New generation? |
|---|---|---|
| **30 s** | S1 (3) · S2 (3) · S5 (4) · S8+S9 (7) · S10 (3) · S11+S12 (8) + 2 s handles. VO: C30a, N3, N4, N6 | No |
| **15 s** | S5 (3) · S9 (4) · S10 (2) · S12 (6). VO: C15a, N6 | No |
| **9:16 vertical (45 s)** | Composited shots re-rendered natively at 1080×1920. Generated shots: **option A** centre-crop from 1080p (soft, $0) or **option B** generate native vertical versions of S1, S3–4, S11 (+35 cr) | A: no / B: yes |

Supporting files: thumbnail/poster (from Shot 12 or Shot 4, with real type), WebVTT captions (from the script,
timed to the actual narration waveforms), web encodes (H.264 MP4 1080p + 720p, VP9 WebM), organised `film/source/`,
and production notes listing every generated vs composited element.

## 6. Budget

| Item | Count | Unit | Credits |
|---|---|---|---|
| Keyframes K1, K3, K4, K5, K11 | 5 (+ up to 5 variants) | 0.25 | 1.25–2.50 |
| Kling 3.0 Pro 5 s: C1, C3, C4, C11 | 4 | 8.75 | 35.00 |
| Narration: 6 main + 2 cutdown lines + 2-voice audition (4 extra lines) | ~12 takes | 0.45 | ~5.40 |
| **Base total** | | | **≈ 42** |
| Contingency: up to 2 shot re-renders | 2 | 8.75 | 17.50 |
| **Cap requested** | | | **60** |
| Optional native 9:16 for 4 generated shots | 4 | 8.75 | +35 |

Higgsfield balance before production: 2,173.45.

## 7. Website integration (after the film is approved)
New homepage section **"See Elitron Labs in Action."** between Solutions and the interactive demo. It shows a
poster-image thumbnail with a play button; the video isn't loaded until click (`preload="none"`). Native controls give
sound, fullscreen and captions (WebVTT `<track default>`), followed by a "Start Your Project" CTA. Under reduced-motion
or Save-Data, only the poster shows until the visitor presses play. The silent hero loop and the interactive demo are
unchanged. Other Phase 2 content (capabilities, case studies, FAQ) follows in the same branch.
