"""Oct 2026 campaign films (01 brand, 02 automation, 03 VERIFAI): edit, score, mix and captions.

Reuses engine.py (picture helpers, real logo) and audio.py (synth score, SFX, VO tools).
Generated plates: work/campaign-2026-10/shots (Kling). Narration: work/campaign-2026-10/vo (Arthur).
Readable UI is never generated: inserts are real captures (work/cap) or rendered here from the
real VERIFAI testbed (repos/elitron-verifai). Timing is narration-led.

Usage: FFMPEG=/opt/homebrew/bin/ffmpeg python3 campaign.py F01|F02|F03
Writes work/campaign-2026-10/out/<film>.mp4, .vtt, .webp
"""
import os, subprocess, sys, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(__file__))
import engine as E
import audio as A
from storyboard import F1, F2, F3

CAMP = Path(E.WORK) / "campaign-2026-10"
SHOTS, VOD, OUT = CAMP / "shots", CAMP / "vo", CAMP / "out"
SITE = Path(__file__).resolve().parents[3]
VERIFAI = SITE.parent / "elitron-verifai"
W, H, FPS = E.W, E.H, E.FPS
AMBER, RED, GREEN, SLATE = (235, 160, 40), (230, 90, 80), (70, 190, 130), (203, 213, 225)

# ---------------------------------------------------------------- look
_vig = None
def grade(img):
    """Generated plates only: pull violet toward blue, gentle S-curve, soft vignette."""
    global _vig
    a = np.asarray(img).astype(np.float32) / 255
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    vi = np.clip((b - g) * 2, 0, 1) * (r > g)
    a[..., 0] = r - 0.45 * (r - g) * vi
    a = a + 0.22 * (a * a * (3 - 2 * a) - a)
    if _vig is None:
        yy, xx = np.mgrid[0:H, 0:W]
        d = ((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2
        _vig = (1 - 0.22 * np.clip(d / 2, 0, 1) ** 1.2)[..., None]
    return Image.fromarray(np.clip(a * _vig * 255, 0, 255).astype(np.uint8))

def pill(img, text, corner="bl"):
    """Disclosure tag on screen: 'Illustration', 'Synthetic data', etc."""
    f = E.font(500, 21); text = text.upper()
    tw = f.getlength(text) + 3 * len(text)
    x0 = 56 if corner == "bl" else W - 56 - tw - 36
    y0 = H - 92
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    d.rounded_rectangle((x0, y0, x0 + tw + 36, y0 + 40), 20, fill=(8, 15, 30, 190), outline=(255, 255, 255, 70), width=1)
    E._tracked(d, (x0 + 18 + tw / 2, y0 + 20), text, f, SLATE + (255,), 3)
    out = img.convert("RGBA"); out.alpha_composite(layer); return out.convert("RGB")

# ---------------------------------------------------------------- shot builders (generators of frames)
def plate(name, dur, push=0.035, start=0.0, tag=None):
    src = 5.0 - start
    v = E.Video(str(SHOTS / f"{name}.mp4"), start, speed=min(1.0, src / dur))
    for i, t, n in E.frames(dur):
        f = grade(E.view(v.next(), W / 2, H / 2, 1 + push * t / dur))
        yield pill(f, tag) if tag else f
    v.close()

def insert(capfile, dur, cx, cy, zoom, dx=0.0, dz=0.05, tag=None, x2=False):
    img = E.cap(capfile)
    for i, t, n in E.frames(dur):
        k = E.ease(t / dur) * 0.6 + 0.4 * t / dur
        z = zoom * (1 + dz * k)
        f = (E.view2 if x2 else E.view)(img, cx + dx * k, cy, z)
        yield pill(f, tag) if tag else f

def seq_insert(capfiles, dur, tag=None):
    imgs = [E.cap(c) for c in capfiles]; step = dur / len(imgs)
    for i, t, n in E.frames(dur):
        j = min(len(imgs) - 1, int(t / step)); a = (t - j * step) / 0.25
        f = imgs[j] if j == 0 or a >= 1 else Image.blend(imgs[j - 1], imgs[j], E.ease(a))
        f = E.view(f, 960, 540, 1.02 + 0.04 * t / dur)
        yield pill(f, tag) if tag else f

def reuse_workflow(dur):
    v = E.Video(str(SITE / "assets" / "media" / "workflow-loop.mp4"), 1.0, speed=min(1.0, 9.0 / dur))
    labels = ["Intake", "CRM", "Scheduling", "Notifications"]; fl = E.font(500, 30)
    for i, t, n in E.frames(dur):
        f = E.view(v.next(), W / 2, H / 2, 1 + 0.03 * t / dur)
        layer = Image.new("RGBA", f.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
        for k, lab in enumerate(labels):
            a = E.ease((t - 0.3 - 0.45 * k) / 0.4)
            if a <= 0: continue
            x = 330 + k * 420
            d.rounded_rectangle((x - 150, 830, x + 150, 886), 28, fill=(8, 15, 30, int(200 * a)), outline=E.BLUE + (int(200 * a),), width=2)
            d.text((x, 858), lab, font=fl, fill=(240, 244, 250, int(255 * a)), anchor="mm")
            if k: d.line((x - 270, 858, x - 150, 858), fill=E.BLUE + (int(160 * a),), width=2)
        f = f.convert("RGBA"); f.alpha_composite(layer)
        yield pill(f.convert("RGB"), "Illustration")
    v.close()

def then(*parts):
    """Concatenate builders; parts are (generator_fn, dur, kwargs) evaluated lazily, with a 4-frame blend at each cut."""
    def gen(dur):
        prev = None
        for fn, d, kw in parts:
            for i, fr in enumerate(fn(dur=d, **kw)):
                if prev is not None and i < 4: fr = Image.blend(prev, fr, (i + 1) / 5)
                yield fr; last = fr
            prev = last
    return gen

# ---------------------------------------------------------------- VERIFAI renders (real testbed output)
def verifai_case():
    sys.path.insert(0, str(VERIFAI))
    from verifai.scenarios import generate
    from verifai.verifier import CombinedVerifier
    s = [s for s in generate(n_per_class=3, seed=7, split="dev") if s.error_class == "price_mismatch"][0]
    v = CombinedVerifier().verify(s)
    doc = list(s.documents.values())[0]
    return s, v, doc

def doc_card(d, box, title, sub, lines, hl=None):
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, 18, fill=(246, 248, 252), outline=(220, 226, 236), width=2)
    d.text((x0 + 36, y0 + 34), title, font=E.font(600, 34), fill=(14, 22, 40))
    d.text((x0 + 36, y0 + 82), sub, font=E.font(500, 18), fill=(110, 122, 145))
    for k, (lab, val) in enumerate(lines):
        y = y0 + 140 + k * 54
        if hl == lab: d.rounded_rectangle((x0 + 24, y - 8, x1 - 24, y + 40), 8, fill=(255, 236, 200))
        d.text((x0 + 36, y), lab, font=E.font(500, 24), fill=(90, 102, 125))
        d.text((x1 - 36, y), str(val), font=E.font(500, 26), fill=(14, 22, 40), anchor="ra")

def money(x): return f"${x:,.2f}"

def verifai_docs(dur, case):
    s, v, doc = case; f_ = s.action.fields
    q = dict(l.split(": ", 1) for l in doc.text.strip().splitlines() if ": " in l)
    for i, t, n in E.frames(dur):
        f = Image.new("RGB", (W, H), E.NAVY); f = E.glow(f, 960, 540, 900, (30, 60, 130), 0.5)
        d = ImageDraw.Draw(f)
        a = E.ease(t / 0.5); off = 30 * (1 - a)
        doc_card(d, (150, 250 + off, 900, 820 + off), "Supplier quote", f"{q['Quote No.']} · synthetic document",
                 [("Supplier", q["Supplier"]), ("Part number", q["Part Number"]), ("Quantity", q["Qty"]), ("Unit", q["UOM"]),
                  ("Unit price", q["Unit Price"]), ("Valid until", q["Valid until"])])
        b = E.ease((t - 0.6) / 0.5)
        if b > 0:
            off2 = 30 * (1 - b)
            doc_card(d, (1020, 250 + off2, 1770, 820 + off2), "Purchase order", "drafted by an AI agent · synthetic",
                     [("Supplier", f_["supplier"]), ("Part number", f_["part_number"]), ("Quantity", int(f_["quantity"])), ("Unit", f_["uom"]),
                      ("Unit price", money(f_["unit_price"])), ("Total", money(f_["total"]))])
        yield pill(f, "Synthetic data · VERIFAI testbed")

def verifai_table(dur, case):
    s, v, doc = case
    rows = [c for c in v.checks if c.assertion in ("supplier", "part_number", "quantity", "uom", "unit_price", "total")]
    fh, fr, fm = E.font(600, 26), E.font(450, 28), E.font(500, 24)
    cols = (170, 520, 900, 1290)
    for i, t, n in E.frames(dur):
        f = Image.new("RGB", (W, H), E.NAVY); f = E.glow(f, 960, 300, 900, (30, 60, 130), 0.4)
        d = ImageDraw.Draw(f)
        d.text((170, 120), "Claim-by-claim check", font=E.font(600, 44), fill=(240, 244, 250))
        d.text((170, 178), f"Proposed order vs. its source ({s.scenario_id})", font=fm, fill=(140, 152, 175))
        for c, lab in zip(cols, ("Field", "Proposed", "Source evidence", "Result")):
            d.text((c, 262), lab.upper(), font=E.font(500, 20), fill=(120, 132, 155))
        d.line((150, 300, 1770, 300), fill=(40, 55, 85), width=2)
        for k, c in enumerate(rows):
            a = E.ease((t - 0.35 - 0.32 * k) / 0.3)
            if a <= 0: continue
            y = 330 + k * 92
            bad = c.label.value == "contradicted"
            if bad: d.rounded_rectangle((150, y - 14, 1770, y + 62), 12, fill=(60, 40, 20))
            col = lambda base: tuple(int(base[j] * a + E.NAVY[j] * (1 - a)) for j in range(3))
            fmtv = lambda x: money(x) if c.assertion in ("unit_price", "total") else (str(int(x)) if isinstance(x, float) else str(x))
            d.text((cols[0], y), c.assertion.replace("_", " "), font=fr, fill=col((220, 228, 240)))
            d.text((cols[1], y), fmtv(c.claimed), font=fr, fill=col((220, 228, 240)))
            d.text((cols[2], y), fmtv(c.evidence), font=fr, fill=col((220, 228, 240)))
            d.text((cols[3], y), "Contradicted" if bad else "Supported", font=fh, fill=col(AMBER if bad else GREEN))
        yield pill(f, "Real prototype output · synthetic scenario")

def verifai_gate(dur, case):
    s, v, doc = case
    fbig, fsm = E.font(600, 58), E.font(450, 30)
    for i, t, n in E.frames(dur):
        f = Image.new("RGB", (W, H), E.NAVY)
        d = ImageDraw.Draw(f)
        p = E.ease(t / 1.1)
        for k in range(5):  # evidence lines flowing toward the gate; the amber one stops
            y = 300 + k * 70; amber = k == 2
            xe = E.lerp(200, 880 if amber else 1720, p)
            d.line((200, y, xe, y), fill=AMBER if amber else E.BLUE, width=4)
        gate = E.ease((t - 0.9) / 0.4)
        if gate > 0:
            d.rounded_rectangle((900, 250, 940, 640), 12, fill=tuple(int(c * gate) for c in AMBER))
            f = E.glow(f, 920, 440, 260, (200, 130, 30), 0.35 * gate)
            d = ImageDraw.Draw(f)
        txt = E.ease((t - 1.3) / 0.5)
        if txt > 0:
            al = lambda c: tuple(int(c[j] * txt + E.NAVY[j] * (1 - txt)) for j in range(3))
            d.text((960, 760), f"Decision: {v.decision.value.upper()}", font=fbig, fill=al(AMBER), anchor="mm")
            d.text((960, 836), "Unit price contradicts quote " + doc.doc_id + ". Nothing is sent; a person reviews it.", font=fsm, fill=al(SLATE), anchor="mm")
        yield pill(f, "Real prototype output · synthetic scenario")

# ---------------------------------------------------------------- end cards
def end_card(dur, title, sub, disclosure, mark=True, tsize=64):
    ft, fs, fd = E.font(600, tsize), E.font(450, 34), E.font(500, 30)
    for i, t, n in E.frames(dur):
        f = Image.new("RGB", (W, H), E.NAVY); f = E.glow(f, 960, 430, 700, (40, 80, 190), 0.35 * E.ease(t / 0.8))
        layer = Image.new("RGBA", f.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
        if mark: layer.alpha_composite(E._mark(120, t / 1.0), (960 - 60, 250))
        a = E.ease((t - 0.5) / 0.5)
        if a > 0: d.text((960, 470 + 8 * (1 - a)), title, font=ft, fill=(255, 255, 255, int(255 * a)), anchor="mm")
        b = E.ease((t - 0.9) / 0.5)
        if b > 0 and sub: d.text((960, 550), sub, font=fs, fill=SLATE + (int(255 * b),), anchor="mm")
        c = E.ease((t - 1.2) / 0.5)
        if c > 0: d.text((960, 930), disclosure, font=fd, fill=(190, 200, 218, int(255 * c)), anchor="mm")
        f = f.convert("RGBA"); f.alpha_composite(layer); f = f.convert("RGB")
        if t > dur - 0.5: f = E.fade(f, (0, 0, 0), E.ease((t - (dur - 0.5)) / 0.5))
        yield f

# ---------------------------------------------------------------- films
_vo = {}
def vo_len(film, k):
    if (film, k) in _vo: return _vo[(film, k)]
    x = A.load_vo_path(VOD / f"{film}-N{k:02d}.mp3"); seg = A.speech_segments(x)
    _vo[(film, k)] = (x, seg[-1][1]); return _vo[(film, k)]

def build_plan(film):
    """Return [(builder(dur), dur, vo_index_or_None, xfade_in, sfx)] with narration-led durations."""
    case = verifai_case() if film == "F3" else None
    def d_for(k, lo=3.4, hi=5.6, tail=0.5):
        return max(lo, min(hi, vo_len(film, k)[1] + tail + (0.2 if k == 1 else 0)))
    P = []
    if film == "F1":
        P = [
            (lambda d: plate("F1-S01", d, push=0.05), d_for(1), 1, 0, "tick"),
            (lambda d: plate("F1-S02", d), d_for(2), 2, 0, "key"),
            (then((plate, 1.9, dict(name="F1-S03")), (insert, 2.6, dict(capfile="s2-k2.png", cx=980, cy=540, zoom=1.0, dx=760, dz=0.03))), None, 3, 0, "tick"),
            (lambda d: plate("F1-S04", d), d_for(4), 4, 0, "thin"),
            (lambda d: plate("F1-S05", d, push=0.02), d_for(5), 5, 0.5, "whoosh"),
            (then((plate, 1.7, dict(name="F1-S06")), (insert, 2.9, dict(capfile="site-desktop-1.png", cx=960, cy=540, zoom=1.0, dz=0.06))), None, 6, 0, "tick"),
            (then((plate, 1.8, dict(name="F1-S07")), (seq_insert, 3.2, dict(capfiles=["s7-n0.png", "s7-n1.png", "s7-n3.png", "s7-n5.png"], tag="Illustration · sample document"))), None, 7, 0, "type"),
            (reuse_workflow, d_for(8), 8, 0, "chimes"),
            (then((plate, 1.6, dict(name="F1-S09", tag="Illustration")), (insert, 2.8, dict(capfile="s6-full@2x.png", cx=960, cy=540, zoom=1.0, dz=0.05, x2=True))), None, 9, 0, "tick"),
            (lambda d: plate("F1-S10", d, push=0.03), d_for(10), 10, 0, "confirm"),
            (lambda d: plate("F1-S11", d, push=-0.04), d_for(11), 11, 0, "riser"),
            (lambda d: E.s12_logo(d), max(5.6, d_for(12)), 12, 0, "logo"),
        ]
    elif film == "F2":
        P = [
            (lambda d: plate("F2-S01", d), d_for(1), 1, 0, "tick"),
            (then((plate, 1.8, dict(name="F2-S02")), (insert, 2.2, dict(capfile="case-hvac@2x.png", cx=720, cy=410, zoom=1.34, dz=0.04, x2=True, tag="Fictional business · sample content"))), None, 2, 0, "notify"),
            (lambda d: plate("F2-S03", d), d_for(3), 3, 0.4, "whoosh"),
            (lambda d: insert("case-demo-qualify@2x.png", d, 960, 400, 1.5, dz=0.06, x2=True), d_for(4), 4, 0, "tick"),
            (lambda d: insert("case-demo-crm@2x.png", d, 960, 400, 1.5, dz=0.06, x2=True), d_for(5), 5, 0, "confirm"),
            (lambda d: insert("s10-slots@2x.png", d, 960, 400, 1.5, dx=40, dz=0.03, x2=True), d_for(6), 6, 0, "tick"),
            (lambda d: insert("s10-confirm@2x.png", d, 960, 400, 1.5, dz=0.05, x2=True), d_for(7), 7, 0, "confirm"),
            (lambda d: plate("F2-S08", d, push=0.03), d_for(8), 8, 0, "riser"),
            (lambda d: end_card(d, "Your tools. One intelligent workflow.", "Elitron Labs · AI Automation & Integration",
                                "Illustrative workflow using synthetic data. Not a real client deployment.", tsize=58), 4.2, None, 0, "logo"),
        ]
    else:
        P = [
            (lambda d: plate("F3-S01", d, push=0.05), d_for(1), 1, 0, "tick"),
            (then((plate, 1.7, dict(name="F3-S02")), (verifai_docs, 2.6, dict(case=case))), None, 2, 0, "tick"),
            (lambda d: plate("F3-S03", d, push=0.06), d_for(3), 3, 0, "tension"),
            (lambda d: plate("F3-S04", d), d_for(4), 4, 0, "chimes"),
            (lambda d: verifai_table(d, case), max(4.0, d_for(5)), 5, 0, "rows"),
            (lambda d: verifai_gate(d, case), max(3.8, d_for(6)), 6, 0, "silence"),
            (lambda d: plate("F3-S07", d, push=0.03), d_for(7, lo=3.6), 7, 0, "resolve"),
            (lambda d: end_card(d, "VERIFAI", "AI Action Verification Research · Elitron Labs",
                                "Research prototype. Synthetic scenarios. Not commercially validated.", tsize=84), max(5.2, d_for(8)), 8, 0, "logo"),
        ]
    # composites: duration = sum of parts, stretched to fit the VO if needed
    out = []
    for b, d, k, xf, sfx in P:
        if d is None:
            need = vo_len(film, k)[1] + 0.5
            parts = b.__closure__[0].cell_contents if b.__closure__ else None
            base = sum(p[1] for p in parts)
            if need > base:  # extend the insert (last part) to cover the line
                fn, dd, kw = parts[-1]; parts = parts[:-1] + ((fn, dd + need - base, kw),)
                b = then(*parts)
            d = sum(p[1] for p in parts)
        out.append((b, d, k, xf, sfx))
    return out

def render_picture(film, plan, path):
    p = subprocess.Popen([E.FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", str(path)], stdin=subprocess.PIPE)
    last, total, poster = None, 0, None
    for si, (b, d, k, xf, sfx) in enumerate(plan):
        nx = int(xf * FPS)
        for i, fr in enumerate(b(d)):
            if last is not None and i < nx: fr = Image.blend(last, fr, E.ease((i + 1) / (nx + 1)))
            p.stdin.write(fr.tobytes()); total += 1; cur = fr
        last = cur
        if si == len(plan) - 2: poster = cur
        print(f"{film} shot {si + 1}/{len(plan)} done ({total / FPS:.2f}s)", flush=True)
    p.stdin.close(); p.wait()
    return poster

# ---------------------------------------------------------------- sound
def build_audio(film, plan, path):
    starts, t = [], 0.0
    for b, d, *_ in plan: starts.append(t); t += d
    total = t; tr = A.Track(total); texts = {"F1": F1, "F2": F2, "F3": F3}[film]
    n = tr.n; mg = np.ones(n, np.float32)  # music gain envelope
    # cue points
    sfxs = [p[4] for p in plan]
    lift = starts[sfxs.index("whoosh")] if "whoosh" in sfxs else starts[sfxs.index("resolve")]
    endc = starts[-1]
    groove = film != "F3"
    # pads
    A_ = A
    tr.add(tr.music, 0, A_.pad(lift + 1.0, [50, 53, 57, 62], 280, 900, 0.22))
    tr.add(tr.music, max(0, lift - 0.2), A_.pad(total - lift + 0.5, [50, 54, 57, 64, 69], 700, 2600, 0.2))
    tt = 0.0
    while tt < lift:
        tr.add(tr.music, tt, A_.sub(0.10 + 0.16 * tt / max(lift, 1))); tt += A_.BEAT
    if groove:
        arp = [62, 69, 66, 69, 64, 69, 66, 73]; tt, k = lift, 0
        while tt < endc - 0.05:
            tr.add(tr.music, tt, A_.pluck(A_.note(arp[k % 8] + 12), 0.45, 0.09 + 0.04 * min(1, (tt - lift) / 4)))
            if k % 2 == 0: tr.add(tr.music, tt, A_.kick(0.28))
            if k % 2 == 1 and tt > lift + 2 * A_.BEAT: tr.add(tr.music, tt, A_.hat(0.045))
            tt += A_.BEAT / 2; k += 1
    tr.add(tr.music, endc - 0.1, A_.pad(total - endc + 1.0, [50, 57, 62, 66, 69, 74], 1200, 4200, 0.15))
    tr.add(tr.music, endc + 0.15, A_.chime(A_.note(74), 0.22)); tr.add(tr.music, endc + 0.45, A_.chime(A_.note(81), 0.18))
    tr.add(tr.music, endc + 0.15, A_.sub(0.4, 0.9))
    # sound design
    for s0, (b, d, k, xf, sfx) in zip(starts, plan):
        if sfx == "tick": tr.add(tr.sfx, s0 + 0.05, A_.tick(1700, 0.08))
        elif sfx == "key":
            for q in np.arange(0.1, 1.2, 0.13): tr.add(tr.sfx, s0 + q, A_.keytap(0.04))
        elif sfx == "type":
            for q in np.arange(1.9, 3.2, 0.11): tr.add(tr.sfx, s0 + q, A_.keytap(0.035))
        elif sfx == "whoosh": tr.add(tr.sfx, s0 - 0.45, A_.whoosh(0.9, 0.18, True))
        elif sfx == "chimes":
            for j, q in enumerate((0.3, 1.1, 1.9, 2.7)): tr.add(tr.sfx, s0 + q, A_.chime(A_.note(74 + [0, 2, 4, 7][j]), 0.045, 0.9))
        elif sfx == "confirm": tr.add(tr.sfx, s0 + 1.2, A_.chime(A_.note(86), 0.06, 1.2))
        elif sfx == "notify": tr.add(tr.sfx, s0 + 0.5, A_.chime(A_.note(88), 0.05, 0.6))
        elif sfx == "riser": tr.add(tr.sfx, s0 + d - 1.6, A_.whoosh(1.9, 0.14, True))
        elif sfx == "rows":
            for j in range(6): tr.add(tr.sfx, s0 + 0.4 + 0.32 * j, A_.tick(2200 if j != 4 else 700, 0.06 if j != 4 else 0.12))
        elif sfx == "tension": tr.add(tr.sfx, s0 + 0.2, A_.whoosh(d, 0.06, True))
        elif sfx == "silence":  # music drops to near-silence for one beat at the review gate
            i0, i1 = int((s0 + 0.2) * A_.SR), int((s0 + d - 0.3) * A_.SR)
            ramp = int(0.25 * A_.SR); mg[i0:i1] = 0.12
            mg[i0 - ramp:i0] = np.linspace(1, 0.12, ramp); mg[i1:i1 + ramp] = np.linspace(0.12, 1, ramp)
            tr.add(tr.sfx, s0 + 1.0, A_.sub(0.3, 0.6))
        elif sfx == "thin": mg[int(s0 * A_.SR):int((s0 + d) * A_.SR)] *= 0.7
    # narration and captions
    cues = []
    for s0, (b, d, k, xf, sfx) in zip(starts, plan):
        if not k: continue
        x, _ = vo_len(film, k); seg = A.speech_segments(x)
        at = s0 + (0.35 if s0 == 0 else 0.2) - seg[0][0] * 0.5
        tr.add(tr.vo, at, x)
        cues.append((at + seg[0][0], at + seg[-1][1] + 0.2, texts[k - 1]["vo"]))
    # mix: duck music -9 dB under narration
    hop = int(0.01 * A_.SR)
    venv = np.sqrt(np.convolve(tr.vo ** 2, np.ones(hop * 8) / (hop * 8), "same"))
    duck = np.where(venv > 0.01, 10 ** (-9 / 20), 1.0).astype(np.float32)
    kk = int(0.25 * A_.SR); duck = np.convolve(duck, np.ones(kk) / kk, "same")
    mus = tr.music * duck * mg * 0.9
    dl = int(0.012 * A_.SR)
    left = mus + tr.sfx * duck ** 0.5 + tr.vo
    right = np.concatenate([np.zeros(dl, np.float32), mus[:-dl]]) + tr.sfx * duck ** 0.5 + tr.vo
    N = int(total * A_.SR); st = np.stack([left[:N], right[:N]], 1)
    fn = int(0.6 * A_.SR); st[-fn:] *= np.linspace(1, 0, fn)[:, None]
    st /= max(1e-6, np.abs(st).max()) / 0.9
    raw = str(path).replace(".wav", ".raw.wav")
    with wave.open(raw, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(A_.SR); w.writeframes((st * 32767).astype(np.int16).tobytes())
    subprocess.run([E.FF, "-v", "error", "-y", "-i", raw, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", str(A_.SR), str(path)], check=True)
    os.remove(raw)
    fmt = lambda s: f"{int(s // 3600):02d}:{int(s % 3600 // 60):02d}:{s % 60:06.3f}"
    with open(str(path).replace(".wav", ".vtt"), "w") as f:
        f.write("WEBVTT\n\n")
        for i, (a, b2, line) in enumerate(cues, 1): f.write(f"{i}\n{fmt(a)} --> {fmt(min(b2, total))}\n{line}\n\n")
    return total

def _load_vo_path(p):
    r = subprocess.run([E.FF, "-v", "error", "-i", str(p), "-ac", "1", "-ar", str(A.SR), "-f", "f32le", "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.float32).copy()
A.load_vo_path = _load_vo_path

if __name__ == "__main__":
    name = sys.argv[1]; film = name.replace("0", "")  # F01 -> F1
    OUT.mkdir(parents=True, exist_ok=True)
    plan = build_plan(film)
    total = build_audio(film, plan, OUT / f"{name}.wav")
    print(f"{name}: {len(plan)} shots, {total:.2f}s", flush=True)
    poster = render_picture(film, plan, OUT / f"{name}.picture.mp4")
    poster.save(OUT / f"{name}-poster.webp", quality=82)
    subprocess.run([E.FF, "-v", "error", "-y", "-i", str(OUT / f"{name}.picture.mp4"), "-i", str(OUT / f"{name}.wav"),
                    "-vf", "noise=alls=2:allf=t", "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-pix_fmt", "yuv420p",
                    "-profile:v", "high", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", str(OUT / f"{name}.mp4")], check=True)
    os.remove(OUT / f"{name}.picture.mp4")
    print(f"wrote {OUT / name}.mp4 ({total:.2f}s)")
