"""Storyboard sheets for the Oct 2026 Elitron film campaign (Films 01-03).

Usage: python3 docs/film/build/storyboard.py
Reads keyframes from docs/film/work/campaign-2026-10/keyframes and UI captures from docs/film/work/cap,
writes docs/film/work/campaign-2026-10/storyboards/F0{1,2,3}-storyboard.jpg.
"""
from pathlib import Path
import textwrap
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1] / "work"
KF = ROOT / "campaign-2026-10" / "keyframes"
CAP = ROOT / "cap"
OUT = ROOT / "campaign-2026-10" / "storyboards"

NAVY, SLATE, BLUE, AMBER, WHITE, MUTED = (8, 15, 30), (22, 32, 54), (47, 107, 255), (235, 160, 40), (240, 244, 250), (150, 162, 185)
TAG = {"GENERATED": BLUE, "COMPOSITE": (60, 170, 120), "EDIT": (150, 110, 230), "REUSED": (120, 130, 150)}


def font(size, bold=False):
    for p in ["/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
              "/System/Library/Fonts/Helvetica.ttc"]:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def placeholder(label, w, h):
    im = Image.new("RGB", (w, h), NAVY)
    d = ImageDraw.Draw(im)
    d.rectangle([6, 6, w - 7, h - 7], outline=SLATE, width=2)
    for i, line in enumerate(textwrap.wrap(label, 34)):
        d.text((w // 2, h // 2 - 22 + i * 22), line, fill=MUTED, font=font(17), anchor="mm")
    return im


def panel_image(src, inset, w, h):
    if src.startswith("PH:"):
        return placeholder(src[3:], w, h)
    path = KF / src if (KF / src).exists() else CAP / src
    im = Image.open(path).convert("RGB")
    im = im.resize((w, int(im.height * w / im.width)))
    if im.height < h:
        bg = Image.new("RGB", (w, h), NAVY); bg.paste(im, (0, (h - im.height) // 2)); im = bg
    im = im.crop((0, (im.height - h) // 2, w, (im.height - h) // 2 + h))
    if inset:
        ins = Image.open(CAP / inset).convert("RGB")
        iw = w // 3
        ins = ins.resize((iw, int(ins.height * iw / ins.width)))
        ins = ins.crop((0, 0, iw, min(ins.height, h // 2)))
        im.paste(ins, (w - iw - 10, h - ins.height - 10))
        ImageDraw.Draw(im).rectangle([w - iw - 11, h - ins.height - 11, w - 10, h - 10], outline=WHITE, width=2)
    return im


def sheet(name, title, sub, shots, cols=4):
    pw, ph, pad, txt = 440, 248, 22, 150
    rows = (len(shots) + cols - 1) // cols
    W, H = cols * pw + (cols + 1) * pad, 120 + rows * (ph + txt + pad) + pad
    s = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(s)
    d.text((pad, 26), title, fill=WHITE, font=font(34, True))
    d.text((pad, 74), sub, fill=MUTED, font=font(18))
    for i, sh in enumerate(shots):
        x = pad + (i % cols) * (pw + pad)
        y = 120 + (i // cols) * (ph + txt + pad)
        s.paste(panel_image(sh["img"], sh.get("inset"), pw, ph), (x, y))
        tag = sh["tag"]
        d.rectangle([x, y, x + 12 + 9 * len(tag), y + 24], fill=TAG[tag])
        d.text((x + 6, y + 4), tag, fill=WHITE, font=font(14, True))
        d.text((x, y + ph + 8), f'{sh["id"]}  ·  {sh["tc"]}', fill=WHITE, font=font(18, True))
        d.text((x, y + ph + 34), "“" + sh["vo"] + "”", fill=(205, 215, 235), font=font(16))
        for j, line in enumerate(textwrap.wrap(sh["note"], 52)[:4]):
            d.text((x, y + ph + 60 + j * 20), line, fill=MUTED, font=font(14))
    OUT.mkdir(parents=True, exist_ok=True)
    s.save(OUT / f"{name}-storyboard.jpg", quality=88)
    return OUT / f"{name}-storyboard.jpg"


F1 = [
    dict(id="S01", tc="00:00-00:04", tag="GENERATED", img="F1-S01.png", vo="Every business runs on thousands of small decisions.", note="Fade in. Slow 50mm push-in on the pre-dawn desk. Clock tick, soft pulse."),
    dict(id="S02", tc="00:04-00:08", tag="GENERATED", img="F1-S02.png", vo="But too many still happen the hard way.", note="Hard cut on a key click. Overhead descent. Owner = the S11 woman (continuity fixed)."),
    dict(id="S03", tc="00:08-00:12", tag="GENERATED", img="F1-S03.png", inset="s2-k2@2x.png", vo="Calls go unanswered. Information gets trapped.", note="Unanswered phone, rack focus to the unattended monitor. Inset: real composited inbox illustration from the Oct film."),
    dict(id="S04", tc="00:12-00:16", tag="GENERATED", img="F1-S04.png", vo="And valuable time slips between disconnected systems.", note="Pull back through dark glass. Three light flows stop short. Ambient sound thins out."),
    dict(id="S05", tc="00:16-00:20", tag="GENERATED", img="F1-S05.png", vo="At Elitron Labs, we design a better flow.", note="Match cut. 120-degree orbit as one light joins the systems. SAMPLE SHOT DONE (3ce6b9b8). Grade violet down."),
    dict(id="S06", tc="00:20-00:24", tag="COMPOSITE", img="F1-S06.png", inset="site-desktop-1.png", vo="Modern websites turn attention into real opportunities.", note="Side track across the workstation. Real elitronlabs.io captures mapped onto the laptop and phone screens."),
    dict(id="S07", tc="00:24-00:28", tag="COMPOSITE", img="F1-S07.png", vo="AI assistants qualify inquiries and help customers connect.", note="Track phone to laptop. Waveform plus a human-approved reply preview composited, tagged 'Illustration'. No deployed-agent claim."),
    dict(id="S08", tc="00:28-00:32", tag="REUSED", img="F1-S08-reuse.png", vo="Automation carries work forward across your existing tools.", note="Reused workflow-loop footage from the Oct film with composited labels: intake, CRM, scheduling, notifications."),
    dict(id="S09", tc="00:32-00:36", tag="COMPOSITE", img="F1-S09.png", inset="s6-full@2x.png", vo="Custom software brings clarity to complex operations.", note="Over the shoulder. Dashboard = composited illustration (sample data). Exit on chart-line direction."),
    dict(id="S10", tc="00:36-00:40", tag="GENERATED", img="F1-S10.png", vo="With human approval wherever judgment matters most.", note="85mm close-up. Deliberate approve touch. Blue light follows the finger. Soft confirm click."),
    dict(id="S11", tc="00:40-00:44", tag="GENERATED", img="F1-S11.png", vo="Less busywork. More momentum. Built to grow.", note="Same desk, morning light, organized queue. Slow dolly out. Music peaks."),
    dict(id="S12", tc="00:44-00:48", tag="EDIT", img="PH:Navy frame - silver-blue light sweep reveals the real Elitron mark (added in edit)", vo="Elitron Labs. Intelligent technology. Real business growth.", note="Logo from assets/icons.svg#mark plus the Geist tagline. Website CTA 'Discuss Your Project' sits outside the video."),
]
F2 = [
    dict(id="S01", tc="00:00-00:04", tag="GENERATED", img="F2-S01.png", vo="The workday ends. Your customers don't.", note="Dusk exterior of a fictional home-services office. Lights switch off. Track toward the window."),
    dict(id="S02", tc="00:04-00:08", tag="COMPOSITE", img="F2-S02.png", inset="case-hvac@2x.png", vo="A new request arrives while your team is away.", note="85mm on the customer's phone. Service-request UI composited from the Summit HVAC demo (fictional brand)."),
    dict(id="S03", tc="00:08-00:12", tag="GENERATED", img="F2-S03.png", vo="The inquiry enters one connected workflow.", note="Match cut from the phone glow. Follow the signal as the nodes light in sequence (Film 01 glass motif)."),
    dict(id="S04", tc="00:12-00:16", tag="COMPOSITE", img="case-demo-qualify@2x.png", vo="AI organizes the details for review.", note="Real lead-automation demo: structured fields + visible scoring factors. Label: synthetic data. Rule-based today, so the VO says 'organizes', not 'decides'."),
    dict(id="S05", tc="00:16-00:20", tag="COMPOSITE", img="case-demo-crm@2x.png", vo="The right record reaches the right place.", note="CRM-style record from the real demo. One restrained confirmation tone."),
    dict(id="S06", tc="00:20-00:24", tag="COMPOSITE", img="s10-slots@2x.png", vo="Available times are offered. People retain control.", note="Real demo appointment slots, labelled illustrative. Slow horizontal slide."),
    dict(id="S07", tc="00:24-00:28", tag="COMPOSITE", img="s10-confirm@2x.png", vo="A customer chooses. The team receives confirmation.", note="Split: customer confirmation / business queue update. Motivated match cut."),
    dict(id="S08", tc="00:28-00:32", tag="GENERATED", img="F2-S08.png", vo="One connected process. More time for real work.", note="Morning operator opens the schedule. End card: 'Your tools. One intelligent workflow.' + disclosure line."),
]
F3 = [
    dict(id="S01", tc="00:00-00:04", tag="GENERATED", img="F3-S01.png", vo="One incorrect detail can become an expensive decision.", note="Macro on a fictional supplier quote + PO. Brushed steel, cool raking light."),
    dict(id="S02", tc="00:04-00:08", tag="COMPOSITE", img="F3-S02.png", vo="An AI agent prepares an order from a supplier quote.", note="One move from paper to screen. Screen panes replaced with the rendered VERIFAI testbed documents (synthetic)."),
    dict(id="S03", tc="00:08-00:12", tag="GENERATED", img="F3-S03.png", vo="But what if the price or revision is wrong?", note="Extreme close-up. One field pair turns amber. Slow push-in, restrained tension."),
    dict(id="S04", tc="00:12-00:16", tag="GENERATED", img="F3-S04.png", vo="VERIFAI asks where every important fact came from.", note="Evidence threads from each order field to its source; one amber thread stops halfway."),
    dict(id="S05", tc="00:16-00:20", tag="COMPOSITE", img="PH:TO BUILD: HTML render of real VERIFAI testbed rows (claim / source / status), synthetic data", vo="It compares the proposed action with its evidence.", note="Rendered from repos/elitron-verifai results/decisions.csv: real prototype output, not an invented UI."),
    dict(id="S06", tc="00:20-00:24", tag="EDIT", img="PH:Amber field + flow stops at a review gate (motion graphic in edit)", vo="Unsupported details are flagged, not invented.", note="Camera holds. Music drops to near-silence for one beat."),
    dict(id="S07", tc="00:24-00:28", tag="GENERATED", img="F3-S07.png", vo="A person decides what happens next.", note="Reviewer examines the flag with the paper quote in hand. Grounded close-up."),
    dict(id="S08", tc="00:28-00:32", tag="EDIT", img="PH:Navy end frame - evidence links converge under 'VERIFAI'; Elitron mark in edit", vo="VERIFAI. Research toward more accountable AI decisions.", note="End card + mandatory disclosure: 'Research prototype. Synthetic scenarios. Not commercially validated.'"),
]

if __name__ == "__main__":
    for n, t, sub, sh in [
        ("F01", "Film 01 - Intelligent Technology. Real Business Growth.", "48 s - homepage brand film - 12 shots - friction > recognition > connection > capability > confidence", F1),
        ("F02", "Film 02 - From Inquiry to Action", "32 s - AI Automation section - 8 shots - fictional HVAC business, synthetic data, not a client deployment", F2),
        ("F03", "Film 03 - VERIFAI: Intelligence You Can Verify", "32 s - VERIFAI case study - 8 shots - research prototype, synthetic scenarios", F3),
    ]:
        print(sheet(n, t, sub, sh))
