"""Elitron Labs brand film: frame engine.

Renders every shot as PIL frames at 24 fps and pipes them to FFmpeg.
Readable UI is never generated: it comes from real HTML captures (docs/film/work/cap)
and is animated here. Generated footage (docs/film/work/src) is trimmed and re-timed.

Usage: python3 engine.py <cut> <out.mp4>    cut in: main, c30, c15, vertical
Env: FFMPEG (path to ffmpeg binary), FILM_WORK (docs/film/work)
"""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

FF = os.environ["FFMPEG"]
WORK = os.environ.get("FILM_WORK", os.path.join(os.path.dirname(__file__), "..", "work"))
SRC, CAP, FONTS = (os.path.join(WORK, d) for d in ("src", "cap", "fonts"))
W, H, FPS = 1920, 1080, 24
NAVY = (8, 15, 30)
BLUE = (75, 139, 255)
VIOLET = (138, 124, 255)

# ---------------------------------------------------------------- helpers
def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)

def lerp(a, b, t):
    return a + (b - a) * t

def font(weight, size):
    return ImageFont.truetype(os.path.join(FONTS, f"Geist-{weight}.ttf"), int(size))

def cap(name):
    return Image.open(os.path.join(CAP, name)).convert("RGB")

def view2(img2x, cx, cy, zoom, out=(W, H)):
    """Camera on a 2x-density capture, in 1x coordinates (keeps UI text sharp when zoomed)."""
    return view(img2x, cx * 2, cy * 2, zoom / 2, out)

def view(img, cx, cy, zoom, out=(W, H)):
    """Camera: crop a window centred on (cx, cy) at `zoom` (1 = native) and resize to out."""
    w, h = out[0] / zoom, out[1] / zoom
    x0, y0 = cx - w / 2, cy - h / 2
    return img.transform(out, Image.EXTENT, (x0, y0, x0 + w, y0 + h), Image.BICUBIC)

def fade(img, color, a):
    if a <= 0: return img
    return Image.blend(img, Image.new("RGB", img.size, color), min(1.0, a))

def xfade(a, b, t):
    return b if t >= 1 else a if t <= 0 else Image.blend(a, b, t)

_radial = {}
def radial(size, cx, cy, r):
    key = (size, int(cx), int(cy), int(r))
    if key not in _radial:
        yy, xx = np.mgrid[0:size[1], 0:size[0]]
        d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / max(r, 1)
        _radial[key] = np.clip(1 - d, 0, 1) ** 1.6
    return _radial[key]

def glow(img, cx, cy, r, color, strength):
    """Additive soft light."""
    if strength <= 0: return img
    m = radial(img.size, cx, cy, r)[..., None] * strength
    a = np.asarray(img).astype(np.float32)
    a = a + m * np.array(color, np.float32)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

def zoom_blur(img, cx, cy, amount):
    """Push-through blur: average of progressively scaled copies."""
    if amount <= 0.001: return img
    acc = np.asarray(img).astype(np.float32)
    n = 5
    for i in range(1, n):
        z = 1 + amount * i / n
        acc += np.asarray(view(img, cx, cy, z, img.size)).astype(np.float32)
    return Image.fromarray((acc / n).astype(np.uint8))

def whip(img, a):
    """Horizontal motion blur + drift used for whip-pan transitions (a: 0..1)."""
    if a <= 0: return img
    r = int(4 + 90 * a)
    k = img.filter(ImageFilter.BoxBlur(0)).resize((img.size[0] // 4, img.size[1] // 4))
    k = k.filter(ImageFilter.GaussianBlur(0))
    arr = np.asarray(k).astype(np.float32); acc = np.zeros_like(arr)
    for i in range(-r // 4, r // 4 + 1): acc += np.roll(arr, i, axis=1)
    acc /= (2 * (r // 4) + 1)
    out = Image.fromarray(acc.astype(np.uint8)).resize(img.size, Image.BILINEAR)
    return Image.blend(img, fade(out, NAVY, 0.25 * a), min(1, a * 1.4))

def focus(img, radius):
    return img if radius < 0.4 else img.filter(ImageFilter.GaussianBlur(radius))

_edge = {}
def edge_soften(img, radius=4):
    """Lens-like softness only toward the corners (centre 60% stays sharp)."""
    if img.size not in _edge:
        yy, xx = np.mgrid[0:img.size[1], 0:img.size[0]]
        d = np.sqrt(((xx - img.size[0] / 2) / (img.size[0] / 2)) ** 2 + ((yy - img.size[1] / 2) / (img.size[1] / 2)) ** 2) / math.sqrt(2)
        _edge[img.size] = Image.fromarray((np.clip((d - 0.6) / 0.4, 0, 1) * 255).astype(np.uint8))
    return Image.composite(img.filter(ImageFilter.GaussianBlur(radius)), img, _edge[img.size])

def gain(img, g):
    return Image.fromarray(np.clip(np.asarray(img).astype(np.float32) * g, 0, 255).astype(np.uint8))

class Video:
    """Sequential frame reader (ffmpeg pipe) with optional speed change."""
    def __init__(self, path, start, speed=1.0, size=(W, H)):
        self.size = size
        vf = f"setpts=PTS/{speed},scale={size[0]}:{size[1]}:flags=lanczos,fps={FPS}"
        self.p = subprocess.Popen([FF, "-v", "error", "-ss", str(start), "-i", path, "-vf", vf,
                                   "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        self.last = None
    def next(self):
        n = self.size[0] * self.size[1] * 3
        buf = self.p.stdout.read(n)
        if len(buf) == n:
            self.last = Image.frombytes("RGB", self.size, buf)
        return self.last  # holds the final frame if the source runs out
    def close(self):
        self.p.kill()

def frames(dur):
    n = int(round(dur * FPS))
    for i in range(n):
        yield i, i / FPS, n

# ---------------------------------------------------------------- shots
def s1_establish(dur):
    v = Video(os.path.join(SRC, "C1.mp4"), 1.0)
    for i, t, n in frames(dur):
        f = v.next()
        if t < 0.5: f = fade(f, NAVY, 1 - t / 0.5)  # open from navy
        yield f
    v.close()

def s2_missed(dur):
    states = [cap(f"s2-k{k}@2x.png") for k in (1, 2, 3, 4)]  # 7680x2160
    times = [0.0, 0.55, 1.1, 1.65]
    for i, t, n in frames(dur):
        k = max(j for j, tt in enumerate(times) if t >= tt)
        img = states[k]
        if k + 1 < len(states) and t > times[k + 1] - 0.12:
            img = xfade(img, states[k + 1], (t - (times[k + 1] - 0.12)) / 0.12)
        # hold on the inbox while requests arrive, then drift right to the empty CRM
        p = ease((t - 2.0) / (dur - 2.0))
        cx = lerp(820, 1950, p)
        f = view2(img, cx, 545, lerp(1.22, 1.16, p) + 0.03 * ease(t / 2.0))
        f = gain(edge_soften(f, 4), 1.18)
        # faint glass reflection carrying the window light from shot 1
        f = glow(f, 1500, 120, 900, (40, 60, 110), 0.18)
        # outro: monitor light blooms across the frame
        if t > dur - 0.5:
            a = ease((t - (dur - 0.5)) / 0.5)
            f = glow(f, 960, 540, 300 + 1800 * a, (110, 160, 255), 1.6 * a)
        yield f

def s3_connect(dur):
    from PIL import ImageEnhance
    v = Video(os.path.join(SRC, "C3.mp4"), 1.0, speed=(4.04 / dur))
    for i, t, n in frames(dur):
        f = ImageEnhance.Color(v.next()).enhance(0.78)  # tame the model's magenta on the right panel
        if t < 0.35:  # arrive out of the bloom
            a = 1 - ease(t / 0.35)
            f = glow(f, 960, 540, 2100, (110, 160, 255), 1.6 * a)
        yield f
    v.close()

def s4_architecture(dur):
    v = Video(os.path.join(SRC, "C4.mp4"), 0.9)
    for i, t, n in frames(dur):
        f = v.next()
        if t > dur - 0.42:  # push through the website panel
            a = ease((t - (dur - 0.42)) / 0.42)
            f = zoom_blur(view(f, 960, 560, 1 + 0.6 * a), 960, 560, 0.35 * a)
            f = fade(f, (190, 210, 255), 0.55 * a)
        yield f
    v.close()

# --- shot 5: real site on the K5 desk (screen replacement)
def _quad(mask):
    ys, xs = np.nonzero(mask)
    pts = np.stack([xs, ys], 1)
    s, d = pts.sum(1), pts[:, 0] - pts[:, 1]
    return [tuple(pts[s.argmin()]), tuple(pts[d.argmax()]), tuple(pts[s.argmax()]), tuple(pts[d.argmin()])]  # tl,tr,br,bl

def _persp_coeffs(dst, src):
    """Coefficients mapping output (dst quad) -> input (src quad) for Image.PERSPECTIVE."""
    A, b = [], []
    for (x, y), (u, v) in zip(dst, src):
        A += [[x, y, 1, 0, 0, 0, -u * x, -u * y], [0, 0, 0, x, y, 1, -v * x, -v * y]]
        b += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(b, float)).tolist()

def _screens(bg):
    a = np.asarray(bg).astype(int)
    r, g, b_ = a[..., 0], a[..., 1], a[..., 2]
    gray = (abs(r - g) < 12) & (abs(g - b_) < 12) & (r > 95) & (r < 200)
    from scipy import ndimage  # noqa
    gray = ndimage.binary_opening(gray, structure=np.ones((21, 21)))  # cut thin links (e.g. the gray monitor neck)
    lab, n = ndimage.label(gray)
    sizes = ndimage.sum(gray, lab, range(1, n + 1))
    order = np.argsort(sizes)[::-1][:2]
    quads = [_quad(lab == (k + 1)) for k in order]
    quads.sort(key=lambda q: q[0][0])  # left = monitor, right = phone
    return quads

def _site_strip():
    a, b = cap("site-desktop-1.png"), cap("site-desktop-2.png")  # scroll 0 and 830
    strip = Image.new("RGB", (1920, 1910), NAVY)
    strip.paste(b.crop((0, 72, 1920, 1080)), (0, 902))
    strip.paste(a.crop((0, 0, 1920, 902)), (0, 0))
    header = a.crop((0, 0, 1920, 72))
    return strip, header

def s5_website(dur):
    bg = Image.open(os.path.join(SRC, "K5.png")).convert("RGB").resize((W, H), Image.LANCZOS)
    mon, ph = _screens(bg)
    strip, header = _site_strip()
    mobile = cap("site-mobile-1.png")
    def paste_quad(base, content, quad, inset=2):
        q = [(x + (inset if i in (0, 3) else -inset), y + (inset if i in (0, 1) else -inset)) for i, (x, y) in enumerate(quad)]
        cw, ch = content.size
        co = _persp_coeffs(q, [(0, 0), (cw, 0), (cw, ch), (0, ch)])
        warped = content.transform(base.size, Image.PERSPECTIVE, co, Image.BICUBIC)
        m = Image.new("L", base.size, 0); ImageDraw.Draw(m).polygon(q, fill=255)
        m = m.filter(ImageFilter.GaussianBlur(0.8))
        return Image.composite(warped, base, m), m
    phone_screen = mobile.crop((0, 0, 1170, 2532))
    for i, t, n in frames(dur):
        scroll = ease((t - 0.3) / 2.3) * 830
        page = strip.crop((0, int(scroll) + 72, 1920, int(scroll) + 1080))
        screen = Image.new("RGB", (1920, 1080)); screen.paste(header, (0, 0)); screen.paste(page, (0, 72))
        f, mm = paste_quad(bg, screen, mon)
        f, pm = paste_quad(f, phone_screen, ph, 3)
        mx = sum(p[0] for p in mon) / 4; my = sum(p[1] for p in mon) / 4
        f = glow(f, mx, my, 900, (40, 70, 140), 0.25)
        # rack focus monitor -> phone at 2.3-3.1s
        k = ease((t - 2.3) / 0.8)
        blur_all = f.filter(ImageFilter.GaussianBlur(4.5))
        phone_soft = Image.composite(blur_all, f, pm)          # phone soft, rest sharp
        mon_soft = Image.composite(f, blur_all, pm)            # phone sharp, rest soft
        f = xfade(phone_soft, mon_soft, k)
        p = ease(t / dur)
        f = view(f, lerp(900, 1060, p), lerp(560, 545, p), lerp(1.06, 1.12, p))
        if t > dur - 0.35:  # whip-pan out
            a = ease((t - (dur - 0.35)) / 0.35)
            f = whip(f, a)
        yield f

def s6_software(dur):
    bg = cap("s6-nocard@2x.png"); full = cap("s6-full@2x.png")
    card = full.crop((862, 390, 1512, 626))
    for i, t, n in frames(dur):
        f = bg.copy()
        m = ease((t - 0.7) / 0.9)
        x = int(lerp(862, 1551, m)); y = int(390 - 20 * math.sin(math.pi * m))
        if 0 < m < 1:
            f = glow(f, x + 325, y + 118, 520, (60, 110, 230), 0.35)
        f.paste(card, (x, y))
        p = ease(t / dur)
        f = gain(view2(f, lerp(1090, 1000, p), 370, 1.55), 1.15)
        f = focus(f, max(0.0, 5 * (1 - t / 0.9)))           # focus pull in
        if t > dur - 0.33: f = focus(f, 6 * ease((t - (dur - 0.33)) / 0.33))  # defocus out
        if t < 0.3:  # land the whip-pan from shot 5
            f = whip(f, 1 - ease(t / 0.3))
        yield f

def s7_ai(dur):
    st = [cap(f"s7-n{k}.png") for k in range(6)]
    times = [0, 1.0, 1.35, 1.7, 2.05, 2.4]
    for i, t, n in frames(dur):
        k = max(j for j, tt in enumerate(times) if t >= tt)
        f = st[k]
        if k + 1 < 6 and t > times[k + 1] - 0.1:
            f = xfade(f, st[k + 1], (t - (times[k + 1] - 0.1)) / 0.1)
        if 0.1 < t < 0.95:  # violet AI scan line over the document
            y = int(lerp(110, 960, (t - 0.1) / 0.85))
            f = f.copy(); d = ImageDraw.Draw(f, "RGBA")
            for k2, alpha in ((0, 220), (3, 90), (8, 40), (16, 18)):
                d.rectangle((96, y - k2, 876, y + k2 + 2), fill=VIOLET + (alpha,))
        p = ease(t / dur)
        f = view(f, 960, 540, lerp(1.0, 1.04, p))
        if t < 0.33: f = focus(f, 6 * (1 - ease(t / 0.33)))
        if t > dur - 0.42:
            a = ease((t - (dur - 0.42)) / 0.42)
            f = zoom_blur(view(f, 1400, 540, 1 + 0.45 * a), 1400, 540, 0.2 * a)
            f = fade(f, (190, 210, 255), 0.55 * a)
        yield f

def s8_inquiry(dur):
    st = [cap(f"s8-{k}@2x.png") for k in range(4)]
    times = [0, 0.35, 1.05, 1.75]
    fx, fy, fw, fh = 392, 110, 692, 841       # form rect
    bx, by, bw, bh = 433, 862, 258, 48        # submit button
    for i, t, n in frames(dur):
        k = max(j for j, tt in enumerate(times) if t >= tt)
        f = st[k]
        if k + 1 < 4 and t > times[k + 1] - 0.15:
            f = xfade(f, st[k + 1], (t - (times[k + 1] - 0.15)) / 0.15)
        f = f.copy()
        if 2.25 < t < 2.45:  # button press
            d = ImageDraw.Draw(f, "RGBA"); d.rounded_rectangle((2 * bx, 2 * by, 2 * (bx + bw), 2 * (by + bh)), 24, fill=(255, 255, 255, 60))
        if t < 2.5:
            p = ease(t / 2.5)
            f = view2(f, lerp(700, 740, p), lerp(470, 560, p), lerp(1.45, 1.25, p))
            if t < 0.35: f = fade(f, (190, 210, 255), 0.5 * (1 - ease(t / 0.35)))  # arrive from push-through
        else:
            # the submitted form condenses into a glowing card that travels right
            a = ease((t - 2.5) / (dur - 2.5))
            base = view2(f, 740, 560, 1.25)
            base = fade(base, NAVY, 0.85 * a)
            form = st[3].crop((2 * fx, 2 * fy, 2 * (fx + fw), 2 * (fy + fh))).resize((fw, fh), Image.LANCZOS)
            sc = lerp(0.9, 0.18, a)
            cw, ch = int(fw * sc), int(fh * sc)
            card = form.resize((cw, ch), Image.LANCZOS)
            x = int(lerp(560, 1980, a ** 1.6)); y = int(lerp(110, 540 - ch / 2, a))
            base = glow(base, x + cw / 2, y + ch / 2, 220 + 200 * a, (80, 140, 255), 0.6 * a)
            base.paste(card, (x, y))
            f = base
        yield f

def _light_track(path, start, speed, dur):
    """x position of the travelling light in the workflow plate, per output frame."""
    v = Video(path, start, speed, size=(480, 270)); xs = []
    for i, t, n in frames(dur):
        a = np.asarray(v.next().convert("L")).astype(int)
        band = a[110:160]
        col = band.max(0)
        xs.append(int(col.argmax()) * 4)
    v.close()
    return xs

def s9_workflow(dur):
    path = os.path.join(SRC, "workflow-loop-src.mp4")
    start, speed = 0.6, 2.0
    track = _light_track(path, start, speed, dur)
    v = Video(path, start, speed)
    stations = [364, 676, 984, 1304, 1646]
    labels = ["Customer inquiry", "AI processing", "Lead qualification", "CRM record", "Booking"]
    f_lab, f_num, f_tag = font(500, 30), font(500, 18), font(500, 17)
    lit = [None] * 5
    for i, t, n in frames(dur):
        f = v.next().copy()
        f = Image.blend(f, Image.new("RGB", f.size, NAVY), 0.22)
        for s, sx in enumerate(stations):
            if lit[s] is None and (track[i] >= sx - 40 or (s == 0 and t > 0.1)):
                lit[s] = t
        d = ImageDraw.Draw(f, "RGBA")
        for s, sx in enumerate(stations):
            on = 0 if lit[s] is None else ease((t - lit[s]) / 0.3)
            col = tuple(int(lerp(c0, c1, on)) for c0, c1 in zip((100, 116, 139), (255, 255, 255)))
            num = f"0{s + 1}"
            d.text((sx, 690), num, font=f_num, fill=(75, 139, 255, int(120 + 135 * on)), anchor="mm")
            d.text((sx, 728), labels[s], font=f_lab, fill=col + (255,), anchor="mm")
            d.rounded_rectangle((sx - 70, 760, sx + 70, 763), 2, fill=(75, 139, 255, int(255 * on)))
            if s == 2 and on > 0:
                d.rounded_rectangle((sx - 52, 395, sx + 52, 427), 16, fill=(138, 124, 255, int(60 * on)), outline=(138, 124, 255, int(200 * on)))
                d.text((sx, 411), "PRIORITY", font=f_tag, fill=(214, 208, 255, int(255 * on)), anchor="mm")
        if t < 0.25: f = fade(f, NAVY, 0.6 * (1 - t / 0.25))
        if t > dur - 0.4:  # CRM/booking node scales up into the booking UI
            a = ease((t - (dur - 0.4)) / 0.4)
            f = zoom_blur(view(f, 1646, 540, 1 + 1.2 * a), 1646, 540, 0.3 * a)
            f = fade(f, NAVY, 0.6 * a)
        yield f
    v.close()

def s10_booking(dur):
    a, b, c = cap("s10-slots@2x.png"), cap("s10-picked@2x.png"), cap("s10-confirm@2x.png")
    cx, cy = 1196, 300
    for i, t, n in frames(dur):
        f = a if t < 0.55 else xfade(a, b, (t - 0.55) / 0.1) if t < 0.65 else b if t < 1.3 else xfade(b, c, (t - 1.3) / 0.15)
        p = ease(t / dur)
        f = view2(f, cx, cy, lerp(2.35, 2.45, p))
        if t < 0.3: f = fade(f, NAVY, 0.6 * (1 - t / 0.3))
        if t > dur - 0.5:  # blue lines converge to centre
            k = ease((t - (dur - 0.5)) / 0.5)
            f = fade(f, NAVY, 0.9 * k).copy(); d = ImageDraw.Draw(f, "RGBA")
            for (x0, y0) in ((0, 540), (1920, 540), (960, 0), (960, 1080), (0, 0), (1920, 1080), (1920, 0), (0, 1080)):
                x1, y1 = lerp(x0, 960, k), lerp(y0, 540, k)
                d.line((lerp(x0, 960, max(0, k - 0.35)), lerp(y0, 540, max(0, k - 0.35)), x1, y1), fill=(75, 139, 255, 230), width=3)
            f = glow(f, 960, 540, 200 + 300 * k, (110, 160, 255), 0.8 * k)
        yield f

def s11_aperture(dur):
    v = Video(os.path.join(SRC, "C11.mp4"), 0.0, speed=(4.6 / dur))
    for i, t, n in frames(dur):
        f = v.next()
        if t < 0.3: f = glow(f, 960, 540, 500, (110, 160, 255), 0.8 * (1 - ease(t / 0.3)))
        yield f
    v.close()

def _mark(size, progress):
    """The real Elitron mark (assets/icons.svg#mark) drawn with stroke-on animation, 4x supersampled."""
    S = size * 4 / 32.0
    im = Image.new("RGBA", (size * 4, size * 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    tile_a = ease(progress / 0.25)
    d.rounded_rectangle((1 * S, 1 * S, 31 * S, 31 * S), 8 * S, fill=(17, 28, 48, int(255 * tile_a)), outline=(42, 59, 92, int(255 * tile_a)), width=int(1.5 * S))
    w = int(2.4 * S)
    def seg(x0, y0, x1, y1, p, col):
        if p <= 0: return
        xe, ye = lerp(x0, x1, p), lerp(y0, y1, p)
        d.line((x0 * S, y0 * S, xe * S, ye * S), fill=col, width=w)
        r = w / 2
        for (x, y) in ((x0, y0), (xe, ye)):
            d.ellipse((x * S - r, y * S - r, x * S + r, y * S + r), fill=col)
    seg(10, 9, 10, 23, ease((progress - 0.15) / 0.3), BLUE + (255,))
    seg(10, 9, 22, 9, ease((progress - 0.35) / 0.3), BLUE + (255,))
    seg(10, 23, 22, 23, ease((progress - 0.35) / 0.3), BLUE + (255,))
    seg(10, 16, 18, 16, ease((progress - 0.55) / 0.25), VIOLET + (255,))
    dot = ease((progress - 0.75) / 0.2)
    if dot > 0:
        r = 1.8 * S * dot
        d.ellipse((22 * S - r, 16 * S - r, 22 * S + r, 16 * S + r), fill=VIOLET + (255,))
    return im.resize((size, size), Image.LANCZOS)

def _tracked(d, xy, text, fnt, fill, tracking):
    x, y = xy
    widths = [fnt.getlength(ch) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x -= total / 2
    for ch, w_ in zip(text, widths):
        d.text((x, y), ch, font=fnt, fill=fill, anchor="lm"); x += w_ + tracking

def s12_logo(dur, hold_black=0.25):
    v = Video(os.path.join(SRC, "C11.mp4"), 4.95)
    bg = v.next().copy(); v.close()
    f_word, f_tag = font(600, 66), font(450, 34)
    for i, t, n in frames(dur):
        f = view(bg, 960, 540, 1 + 0.02 * (t / dur))
        f = Image.blend(f, Image.new("RGB", f.size, NAVY), 0.5)
        f = glow(f, 960, 420, 460, (60, 100, 220), 0.35 * ease(t / 0.8))
        layer = Image.new("RGBA", f.size, (0, 0, 0, 0))
        mark = _mark(180, t / 1.1)
        layer.alpha_composite(mark, (960 - 90, 392 - 90 - 40))
        d = ImageDraw.Draw(layer)
        wa = ease((t - 0.7) / 0.5)
        if wa > 0:
            _tracked(d, (960, 566 + 6 * (1 - wa)), "ELITRON LABS", f_word, (255, 255, 255, int(255 * wa)), 12)
        ta = ease((t - 1.1) / 0.5)
        if ta > 0:
            d.text((960, 628 + 6 * (1 - ta)), "Intelligent Technology. Real Business Growth.", font=f_tag, fill=(203, 213, 225, int(255 * ta)), anchor="mm")
        # one light sweep across the mark
        sw = (t - 1.2) / 0.6
        if 0 < sw < 1:
            band = Image.new("L", f.size, 0); bd = ImageDraw.Draw(band)
            x = lerp(820, 1100, sw)
            bd.polygon([(x, 210), (x + 40, 210), (x - 40, 430), (x - 80, 430)], fill=110)
            band = band.filter(ImageFilter.GaussianBlur(12))
            mask = ImageChops.multiply(band, layer.getchannel("A"))
            layer = Image.composite(Image.new("RGBA", f.size, (255, 255, 255, 255)), layer, mask) if False else layer
            f = Image.composite(Image.new("RGB", f.size, (230, 238, 255)), f, mask)
        f = f.convert("RGBA"); f.alpha_composite(layer); f = f.convert("RGB")
        end = dur - hold_black
        if t > end - 0.6: f = fade(f, (0, 0, 0), ease((t - (end - 0.6)) / 0.6))
        yield f

# ---------------------------------------------------------------- cuts
SHOTS = {
    "s1": s1_establish, "s2": s2_missed, "s3": s3_connect, "s4": s4_architecture, "s5": s5_website,
    "s6": s6_software, "s7": s7_ai, "s8": s8_inquiry, "s9": s9_workflow, "s10": s10_booking,
    "s11": s11_aperture, "s12": s12_logo,
}
CUTS = {
    # (shot, duration) — main is timed to the recorded narration (see timeline.json)
    "main": [("s1", 3.0), ("s2", 4.2), ("s3", 4.0), ("s4", 4.0), ("s5", 5.2), ("s6", 3.0), ("s7", 3.0),
             ("s8", 4.0), ("s9", 4.0), ("s10", 3.0), ("s11", 3.8), ("s12", 5.6)],
    "c30": [("s1", 2.6), ("s2", 3.4), ("s5", 4.6), ("s8", 3.4), ("s9", 4.0), ("s10", 3.0), ("s11", 2.6), ("s12", 5.6)],
    "c15": [("s5", 3.6), ("s9", 3.6), ("s10", 2.4), ("s12", 5.4)],
}

def render(cut, out, vertical=False, focal=None):
    plan = CUTS["main" if cut == "vertical" else cut]
    size = (1080, 1920) if vertical else (W, H)
    p = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{size[0]}x{size[1]}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "14",
                          "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    total = 0
    for name, dur in plan:
        for fr in SHOTS[name](dur):
            if vertical:
                fx = (focal or {}).get(name, 960)
                fr = view(fr, fx, 540, 1.0, (608, 1080)).resize(size, Image.LANCZOS)
            p.stdin.write(fr.tobytes()); total += 1
        print(f"{name} done ({total} frames)", flush=True)
    p.stdin.close(); p.wait()
    print(f"wrote {out}: {total / FPS:.2f}s")

if __name__ == "__main__":
    cut, out = sys.argv[1], sys.argv[2]
    if cut == "vertical":
        focal = {"s1": 820, "s2": 960, "s3": 960, "s4": 900, "s5": 1260, "s6": 760, "s7": 1350, "s8": 860,
                 "s9": 960, "s10": 1180, "s11": 960, "s12": 960}
        render(cut, out, vertical=True, focal=focal)
    else:
        render(cut, out)
