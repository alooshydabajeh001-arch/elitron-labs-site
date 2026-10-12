"""Render sample frames of each shot into a contact sheet for review."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import engine
from PIL import Image
out = os.path.join(engine.WORK, "review")
names = sys.argv[1:] or [n for n, _ in engine.CUTS["main"]]
durs = dict(engine.CUTS["main"])
for name in names:
    dur = durs[name]; n = int(round(dur * engine.FPS)); picks = {int(n * 0.08), n // 2, n - 6}
    thumbs = []
    for i, fr in enumerate(engine.SHOTS[name](dur)):
        if i in picks: thumbs.append(fr.resize((640, 360)))
    sheet = Image.new("RGB", (640 * len(thumbs), 360))
    for k, im in enumerate(thumbs): sheet.paste(im, (640 * k, 0))
    sheet.save(os.path.join(out, f"pv_{name}.jpg"), quality=82)
    print("ok", name, flush=True)
