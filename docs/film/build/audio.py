"""Original score, sound design and narration mix for the Elitron Labs film.

Everything musical is synthesized here (no samples, no third-party audio), so the
soundtrack is wholly owned. Narration takes come from Higgsfield TTS (docs/film/work/src).
Usage: python3 audio.py <cut> <out.wav>
"""
import json, os, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from engine import CUTS, SRC, FF

SR = 48000
BPM = 92.0
BEAT = 60.0 / BPM

def note(n):  # MIDI -> Hz
    return 440.0 * 2 ** ((n - 69) / 12)

def env_adsr(n, a, d, s, r, sr=SR):
    a, d, r = int(a * sr), int(d * sr), int(r * sr)
    e = np.full(n, s, np.float32)
    e[:a] = np.linspace(0, 1, a, False) if a else 1
    e[a:a + d] = np.linspace(1, s, min(d, max(0, n - a)), False)[: max(0, min(d, n - a))]
    if r: e[-r:] *= np.linspace(1, 0, r)
    return e

def lowpass(x, cutoff):
    """One-pole low-pass; cutoff may be an array (time-varying)."""
    c = np.broadcast_to(np.asarray(cutoff, np.float32), x.shape)
    a = np.exp(-2 * np.pi * c / SR)
    y = np.empty_like(x); prev = 0.0
    for i in range(len(x)):
        prev = (1 - a[i]) * x[i] + a[i] * prev; y[i] = prev
    return y

def saw(f, t, harmonics=14):
    out = np.zeros_like(t)
    for k in range(1, harmonics + 1):
        if f * k > 9000: break
        out += np.sin(2 * np.pi * f * k * t) / k
    return out * 0.55

class Track:
    def __init__(self, dur):
        self.n = int(dur * SR) + SR
        self.music = np.zeros(self.n, np.float32)
        self.sfx = np.zeros(self.n, np.float32)
        self.vo = np.zeros(self.n, np.float32)
    def add(self, buf, at, x, gain=1.0):
        i = int(at * SR)
        if i >= self.n: return
        x = x[: self.n - i]
        buf[i:i + len(x)] += x * gain

def pad(dur, chord, cutoff0, cutoff1, gain):
    t = np.arange(int(dur * SR)) / SR
    x = sum(saw(note(m) * (1 + d), t) for m in chord for d in (-0.003, 0.003)) / (2 * len(chord))
    x = lowpass(x.astype(np.float32), np.linspace(cutoff0, cutoff1, len(t)))
    return x * env_adsr(len(t), 1.2, 0.5, 1.0, 1.0) * gain

def pluck(freq, dur=0.5, gain=0.3):
    t = np.arange(int(dur * SR)) / SR
    x = (np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(4 * np.pi * freq * t) + 0.12 * np.sin(6 * np.pi * freq * t))
    return (x * np.exp(-t * 7) * gain).astype(np.float32)

def kick(gain=0.5):
    t = np.arange(int(0.35 * SR)) / SR
    f = 110 * np.exp(-t * 18) + 42
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * gain).astype(np.float32)

def hat(gain=0.06):
    t = np.arange(int(0.06 * SR)) / SR
    n = np.random.default_rng(3).standard_normal(len(t)).astype(np.float32)
    n = n - lowpass(n, 6000)
    return n * np.exp(-t * 70) * gain

def sub(gain=0.35, dur=0.45):
    t = np.arange(int(dur * SR)) / SR
    return (np.sin(2 * np.pi * note(26) * t) * np.exp(-t * 6) * gain).astype(np.float32)

def tick(freq=1900, gain=0.18, detune=0):
    t = np.arange(int(0.18 * SR)) / SR
    return (np.sin(2 * np.pi * freq * (1 + detune) * t) * np.exp(-t * 38) * gain).astype(np.float32)

def whoosh(dur=0.6, gain=0.22, up=True):
    t = np.arange(int(dur * SR)) / SR
    n = np.random.default_rng(7).standard_normal(len(t)).astype(np.float32)
    cut = np.linspace(400, 5000, len(t)) if up else np.linspace(5000, 400, len(t))
    x = lowpass(n, cut) - lowpass(n, cut * 0.25)
    e = np.sin(np.pi * np.linspace(0, 1, len(t))) ** 1.5
    return x * e * gain

def chime(freq, gain=0.22, dur=2.5):
    t = np.arange(int(dur * SR)) / SR
    x = np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * freq * 2.76 * t) * np.exp(-t * 4) + 0.15 * np.sin(2 * np.pi * freq * 5.4 * t) * np.exp(-t * 8)
    return (x * np.exp(-t * 1.6) * gain).astype(np.float32)

def keytap(gain=0.05):
    t = np.arange(int(0.04 * SR)) / SR
    n = np.random.default_rng().standard_normal(len(t)).astype(np.float32)
    return (n - lowpass(n, 2500)) * np.exp(-t * 120) * gain

def load_vo(name):
    p = subprocess.run([FF, "-v", "error", "-i", os.path.join(SRC, name), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True)
    return np.frombuffer(p.stdout, np.float32).copy()

# narration placement per cut: (file, offset from shot start, shot index)
VO = {
    "main": [("N1.mp3", "s1", 0.3), ("N2.mp3", "s3", 0.55), ("N3.mp3", "s5", 0.35), ("N4.mp3", "s8", 0.4),
             ("N5.mp3", "s11", 0.35), ("N6.mp3", "s12", -0.25)],
    "c30": [("C30a.mp3", "s1", 0.3), ("N3.mp3", "s5", 0.2), ("N4.mp3", "s8", 0.3), ("N6.mp3", "s12", -0.3)],
    "c15": [("C15a.mp3", "s5", 0.2), ("N6.mp3", "s12", -0.2)],
}
CAPTIONS = {
    "N1.mp3": ["Every opportunity matters.", "But missed inquiries and disconnected systems can slow a growing business."],
    "N2.mp3": ["What if your technology worked together,", "instead of getting in the way?"],
    "N3.mp3": ["At Elitron Labs, we build high-performance websites,", "custom software, and AI-powered solutions around your goals."],
    "N4.mp3": ["From intelligent assistants to automated follow-ups,", "we connect the steps that turn interest into action."],
    "N5.mp3": ["Less friction. More possibility."],
    "N6.mp3": ["Elitron Labs.", "Intelligent Technology. Real Business Growth."],
    "C15a.mp3": ["Websites, custom software, and AI,", "built around your goals."],
    "C30a.mp3": ["Missed inquiries and disconnected systems", "slow a growing business."],
}

def shot_starts(cut):
    plan = CUTS[cut]; t = 0; out = {}
    for name, d in plan:
        out[name] = (t, d); t += d
    return out, t

def speech_segments(x, thresh=0.012, gap=0.18):
    """Return (start, end) seconds of voiced regions, merging short gaps."""
    hop = int(0.02 * SR); rms = np.sqrt(np.convolve(x ** 2, np.ones(hop) / hop, "same"))
    voiced = rms > thresh; segs = []; i = 0; n = len(x)
    while i < n:
        if voiced[i]:
            j = i
            while j < n and (voiced[j] or (j + int(gap * SR) < n and voiced[j:j + int(gap * SR)].any())): j += hop
            segs.append((i / SR, min(j, n) / SR)); i = j
        i += hop
    return segs

def build(cut, out_wav):
    starts, total = shot_starts(cut)
    tr = Track(total)
    has = lambda s: s in starts
    t_lift = starts["s3"][0] if has("s3") else (starts["s5"][0] if has("s5") else 0)
    t_groove = starts["s5"][0] if has("s5") else 0
    t_end_groove = starts["s11"][0] if has("s11") else starts["s12"][0]
    t_logo = starts["s12"][0]

    # --- pads: D minor tension, then Dadd9 lift through to the end
    if t_lift > 0:
        tr.add(tr.music, 0, pad(t_lift + 1.0, [50, 53, 57, 62], 300, 900, 0.22))
    tr.add(tr.music, max(0, t_lift - 0.2), pad(total - t_lift + 0.5, [50, 54, 57, 64, 69], 700, 2600, 0.2))
    # --- sub pulse, quarter notes, rising before the lift
    t = 0.0
    while t < t_lift:
        tr.add(tr.music, t, sub(0.12 + 0.18 * t / max(t_lift, 1))); t += BEAT
    # --- groove: arpeggio + soft kick + hats
    arp = [62, 69, 66, 69, 64, 69, 66, 73]
    t, k = t_groove, 0
    while t < t_end_groove - 0.05:
        tr.add(tr.music, t, pluck(note(arp[k % 8] + 12), 0.45, 0.10 + 0.04 * min(1, (t - t_groove) / 4)))
        if k % 2 == 0: tr.add(tr.music, t, kick(0.32))
        if k % 2 == 1 and t > t_groove + 2 * BEAT: tr.add(tr.music, t, hat(0.05))
        t += BEAT / 2; k += 1
    # --- riser and swell into the logo
    rz = min(2.0, t_end_groove)
    tr.add(tr.sfx, t_end_groove - rz, whoosh(rz + 0.3, 0.18, True))
    tr.add(tr.music, t_end_groove, pad(t_logo - t_end_groove + 1.2, [50, 57, 62, 66, 69, 74], 1200, 4200, 0.16))
    # --- sonic signature on the logo
    tr.add(tr.music, t_logo + 0.15, chime(note(74), 0.24))
    tr.add(tr.music, t_logo + 0.45, chime(note(81), 0.2))
    tr.add(tr.music, t_logo + 0.15, sub(0.45, 0.9))

    # --- sound design keyed to picture
    if has("s1"): tr.add(tr.sfx, starts["s1"][0] + 1.4, tick(1800, 0.12))
    if has("s2"):
        s0, d = starts["s2"]
        for k, tt in enumerate([0.0, 0.55, 1.1, 1.65]):
            tr.add(tr.sfx, s0 + tt, tick(1650, 0.10, detune=-0.01 * k))
        tr.add(tr.sfx, s0 + d - 0.6, whoosh(0.8, 0.22))
    if has("s3"):
        s0, d = starts["s3"]
        for tt, f in ((1.9, 880), (2.9, 1108.7)): tr.add(tr.sfx, s0 + tt, chime(f, 0.06, 0.8))
    if has("s4"):
        s0, d = starts["s4"]
        for tt in (0.6, 1.4, 2.2, 2.9): tr.add(tr.sfx, s0 + tt, tick(2400, 0.07))
        tr.add(tr.sfx, s0 + d - 0.5, whoosh(0.7, 0.2))
    if has("s5"):
        s0, d = starts["s5"]
        tr.add(tr.sfx, s0 + 2.3, tick(1200, 0.08))
        tr.add(tr.sfx, s0 + d - 0.35, whoosh(0.55, 0.16, False))
    if has("s6"): tr.add(tr.sfx, starts["s6"][0] + 0.8, tick(1400, 0.08))
    if has("s7"):
        s0, d = starts["s7"]
        tr.add(tr.sfx, s0 + 0.1, whoosh(0.85, 0.07, True))
        for tt in (1.0, 1.35, 1.7, 2.05, 2.4): tr.add(tr.sfx, s0 + tt, tick(2600, 0.05))
        tr.add(tr.sfx, s0 + d - 0.45, whoosh(0.6, 0.18))
    if has("s8"):
        s0, d = starts["s8"]
        rng = np.random.default_rng(11)
        for tt in np.arange(0.35, 2.1, 0.11):
            if rng.random() > 0.25: tr.add(tr.sfx, s0 + tt, keytap(0.045))
        tr.add(tr.sfx, s0 + 2.3, tick(900, 0.1))
        tr.add(tr.sfx, s0 + 2.5, whoosh(1.2, 0.16))
    if has("s9"):
        s0, d = starts["s9"]
        for k, tt in enumerate((0.15, 0.95, 1.75, 2.55, 3.3)): tr.add(tr.sfx, s0 + tt, chime(note(74 + [0, 2, 4, 7, 9][k]), 0.05, 0.9))
    if has("s10"):
        s0, d = starts["s10"]
        tr.add(tr.sfx, s0 + 0.55, tick(1300, 0.08))
        tr.add(tr.sfx, s0 + 1.3, chime(note(86), 0.06, 1.2))

    # --- narration + captions
    cues = []
    for fname, shot, off in VO[cut]:
        x = load_vo(fname); at = starts[shot][0] + off
        tr.add(tr.vo, at, x)
        segs = speech_segments(x); lines = CAPTIONS[fname]
        # split caption lines across voiced segments in order (proportional by character count)
        total_chars = sum(len(l) for l in lines); s_start, s_end = segs[0][0], segs[-1][1]
        cursor = s_start
        for li, line in enumerate(lines):
            share = len(line) / total_chars * (s_end - s_start)
            end = s_end if li == len(lines) - 1 else cursor + share
            # snap boundaries to the nearest pause between segments
            if li < len(lines) - 1:
                gaps = [(a1, b0) for (a0, a1), (b0, b1) in zip(segs, segs[1:])]
                if gaps: end = min(gaps, key=lambda g: abs((g[0] + g[1]) / 2 - end))[0]
            cues.append((at + cursor, at + end + 0.15, line)); cursor = end
            if li < len(lines) - 1:
                nxt = [b0 for (a1, b0) in [(a1, b0) for (a0, a1), (b0, b1) in zip(segs, segs[1:])] if a1 >= end - 1e-6]
                cursor = nxt[0] if nxt else end

    # --- ducking: music -9 dB under narration (smoothed)
    hop = int(0.01 * SR)
    venv = np.sqrt(np.convolve(tr.vo ** 2, np.ones(hop * 8) / (hop * 8), "same"))
    duck = np.where(venv > 0.01, 10 ** (-9 / 20), 1.0).astype(np.float32)
    k = int(0.25 * SR); duck = np.convolve(duck, np.ones(k) / k, "same")
    mix_mono = tr.music * duck * 0.9 + tr.sfx * duck ** 0.5 + tr.vo * 1.0
    # stereo: Haas widening on music only, narration centred
    d = int(0.012 * SR)
    music_r = np.concatenate([np.zeros(d, np.float32), (tr.music * duck * 0.9)[:-d]])
    left = mix_mono
    right = mix_mono - tr.music * duck * 0.9 + music_r
    n = int(total * SR)
    fade_n = int(0.6 * SR)
    st = np.stack([left[:n], right[:n]], 1)
    st[-fade_n:] *= np.linspace(1, 0, fade_n)[:, None]
    st /= max(1e-6, np.abs(st).max()) / 0.9
    raw = out_wav.replace(".wav", ".raw.wav")
    import wave
    with wave.open(raw, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())
    # loudness: -16 LUFS integrated, -1 dBTP
    subprocess.run([FF, "-v", "error", "-y", "-i", raw, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", str(SR), out_wav], check=True)
    os.remove(raw)
    vtt = out_wav.replace(".wav", ".vtt")
    fmt = lambda s: f"{int(s // 3600):02d}:{int(s % 3600 // 60):02d}:{s % 60:06.3f}"
    with open(vtt, "w") as f:
        f.write("WEBVTT\n\n")
        for i, (a, b, line) in enumerate(cues, 1):
            f.write(f"{i}\n{fmt(a)} --> {fmt(b)}\n{line}\n\n")
    print(f"wrote {out_wav} ({total:.2f}s) and {vtt} ({len(cues)} cues)")

if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
