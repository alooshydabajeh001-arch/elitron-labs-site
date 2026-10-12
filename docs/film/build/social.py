"""Social versions with burned-in captions.

vertical: 1080x1920 framed-film layout — the full 16:9 film sharp in the middle, a blurred
          extension of itself behind, brand lockup above, large captions below.
wide:     1920x1080 with burned-in captions (for muted autoplay feeds such as LinkedIn).
Usage: python3 social.py <cut> <vertical|wide> <out.mp4>
"""
import os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image, ImageDraw, ImageFilter
import engine
from engine import FF, FPS, Video, font, _mark

OUT = os.path.join(engine.WORK, "out")

def cues(vtt):
    t = lambda s: sum(float(x) * m for x, m in zip(s.split(":"), (3600, 60, 1)))
    out = []
    for a, b, text in re.findall(r"(\d\d:\d\d:\d\d\.\d+) --> (\d\d:\d\d:\d\d\.\d+)\n(.+?)\n", open(vtt).read()):
        out.append((t(a), t(b), text.strip()))
    return out

def wrap(text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if fnt.getlength(test) <= width: cur = test
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def caption(d, text, cx, top, fnt, width, line_h):
    lines = wrap(text, fnt, width)
    for i, line in enumerate(lines):
        y = top + i * line_h
        w = fnt.getlength(line)
        d.rounded_rectangle((cx - w / 2 - 18, y - line_h / 2 - 4, cx + w / 2 + 18, y + line_h / 2 + 2), 12, fill=(8, 15, 30, 190))
        d.text((cx, y), line, font=fnt, fill=(255, 255, 255, 255), anchor="mm")

def render(cut, layout, out):
    src = os.path.join(OUT, f"{cut}.master.mp4")
    cs = cues(os.path.join(OUT, f"{cut}.vtt"))
    dur = float(re.search(r"Duration: (\d+):(\d+):([\d.]+)", subprocess.run([FF, "-i", src], capture_output=True, text=True).stderr).group(3))
    n = int(round(dur * FPS))
    size = (1080, 1920) if layout == "vertical" else (1920, 1080)
    v = Video(src, 0)
    p = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{size[0]}x{size[1]}", "-r", str(FPS), "-i", "-",
                          "-i", src, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p",
                          "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", out], stdin=subprocess.PIPE)
    cap_f = font(500, 50 if layout == "vertical" else 42)
    brand_f = font(600, 44)
    mark = _mark(96, 1.0)
    for i in range(n):
        t = i / FPS
        fr = v.next()
        if layout == "vertical":
            bg = fr.resize((480, 270)).filter(ImageFilter.GaussianBlur(14))
            bg = engine.view(bg, 240, 135, 1920 / 270, (1080, 1920))  # fill the 9:16 frame from the blurred film
            bg = engine.fade(bg, engine.NAVY, 0.55)
            canvas = bg.convert("RGBA")
            film = fr.resize((1080, 608), Image.LANCZOS)
            canvas.paste(film, (0, 640))
            d = ImageDraw.Draw(canvas)
            d.line((0, 639, 1080, 639), fill=(255, 255, 255, 40)); d.line((0, 1248, 1080, 1248), fill=(255, 255, 255, 40))
            canvas.alpha_composite(mark, (540 - 48, 300))
            engine._tracked(d, (540, 455), "ELITRON LABS", brand_f, (255, 255, 255, 255), 9)
            for a, b, text in cs:
                if a <= t < b: caption(d, text, 540, 1360, cap_f, 900, 70)
        else:
            canvas = fr.convert("RGBA"); d = ImageDraw.Draw(canvas)
            for a, b, text in cs:
                if a <= t < b: caption(d, text, 960, 950, cap_f, 1500, 58)
        p.stdin.write(canvas.convert("RGB").tobytes())
    v.close(); p.stdin.close(); p.wait()
    print("wrote", out, f"{n / FPS:.2f}s")

if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2], sys.argv[3])
