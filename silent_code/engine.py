"""The Silent Code — procedural video engine.

Each video lives in videos/vNN_*.py and defines:
  TITLE, VOICES {speaker: (kokoro_voice, speed)}, BEATS [dict(say, who, v, gap)],
  MUSIC dict, and class Style(Base).
Run:  python3 engine.py 1 [2 ...]   (or "all")
"""
import os, re, sys, math, hashlib, subprocess, importlib, glob
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from draw import *  # noqa

BUILD = os.path.join(ROOT, "build")
OUT = os.path.join(ROOT, "out")
SR = 24000
TTS_DIR = os.environ.get("KOKORO_DIR", "/tmp/claude-0/tts")

# ------------------------------------------------------------------ TTS
_k = None


def kokoro():
    global _k
    if _k is None:
        from kokoro_onnx import Kokoro
        _k = Kokoro(os.path.join(TTS_DIR, "kokoro-v1.0.onnx"),
                    os.path.join(TTS_DIR, "voices-v1.0.bin"))
    return _k


def tts(text, voice, speed):
    lang = "en-gb" if voice.startswith("b") else "en-us"
    h = hashlib.md5(f"{voice}|{speed}|{text}".encode()).hexdigest()[:16]
    p = os.path.join(BUILD, "tts", h + ".npy")
    if os.path.exists(p):
        return np.load(p)
    s, sr = kokoro().create(text, voice=voice, speed=speed, lang=lang)
    s = np.asarray(s, dtype=np.float32)
    idx = np.where(np.abs(s) > 0.015)[0]
    if len(idx):
        s = s[max(0, idx[0] - int(.02 * SR)): idx[-1] + int(.06 * SR)]
    os.makedirs(os.path.dirname(p), exist_ok=True)
    np.save(p, s)
    return s


def word_weights(words):
    out = []
    for w in words:
        core = len(re.sub(r"[^\w]", "", w)) or 1
        speak = 1.2 + 0.62 * core
        pause = 0.0
        if re.search(r"[.!?][\"'”’)]*$", w):
            pause = 4.5
        elif re.search(r"[,;:][\"'”’)]*$", w) or w.endswith("—"):
            pause = 2.6
        out.append((speak, pause))
    return out


# ------------------------------------------------------------------ timeline
GAPDEF = [0.45]


class Beat:
    def __init__(self, i, d):
        self.i = i
        self.say = d.get("say", "")
        self.who = d.get("who", "n")
        self.v = d.get("v", {})
        self.gap = d.get("gap", GAPDEF[0])
        self.d = d


class Timeline:
    def __init__(self, mod):
        self.mod = mod
        GAPDEF[0] = getattr(mod, "GAP", 0.45)
        self.beats = [Beat(i, b) for i, b in enumerate(mod.BEATS)]
        self.words = []
        voice_parts = []
        cur = getattr(mod, "LEAD", 0.2)
        for b in self.beats:
            b.t0 = cur
            if b.say:
                vname, speed = mod.VOICES[b.who]
                a = tts(b.say, vname, speed)
                b.dur = len(a) / SR
                voice_parts.append((cur, a))
                ws = b.say.split()
                wt = word_weights(ws)
                tot = sum(s + p for s, p in wt)
                c = cur
                b.words = []
                for w, (s, p) in zip(ws, wt):
                    t0 = c
                    t1 = c + b.dur * s / tot
                    c = t1 + b.dur * p / tot
                    rec = dict(w=w, t0=t0, t1=t1, beat=b.i, who=b.who)
                    self.words.append(rec)
                    b.words.append(rec)
            else:
                b.dur = 0
                b.words = []
            b.t1 = cur + b.dur + b.gap
            cur = b.t1
        self.total = cur + getattr(mod, "END_HOLD", 3.0)
        self.beats[-1].t1 = self.total
        self.voice = np.zeros(int(self.total * SR) + SR, np.float32)
        for t0, a in voice_parts:
            s = int(t0 * SR)
            self.voice[s:s + len(a)] += a
        self._chunk()

    def _chunk(self, maxw=None):
        maxw = maxw or getattr(self.mod, "CAP_WORDS", 5)
        self.chunks = []
        cur = []
        for k, w in enumerate(self.words):
            cur.append(w)
            nxt = self.words[k + 1] if k + 1 < len(self.words) else None
            end = (nxt is None or nxt["beat"] != w["beat"] or len(cur) >= maxw or
                   (len(cur) >= 2 and re.search(r"[.!?,;:—][\"'”’)]*$", w["w"])))
            if end:
                self.chunks.append(cur)
                cur = []

    def beat_at(self, t):
        for b in self.beats:
            if t < b.t1:
                return b
        return self.beats[-1]

    def chunk_at(self, t):
        best = None
        for c in self.chunks:
            if c[0]["t0"] <= t + 0.02:
                best = c
            else:
                break
        if best and t <= best[-1]["t1"] + 0.5:
            return best
        return None


# ------------------------------------------------------------------ audio
def lowpass(x, cutoff):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, len(x)).astype(np.float32)


def highpass(x, cutoff):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 - 1 / (1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, len(x)).astype(np.float32)


def env_ad(n, a, r):
    e = np.ones(n, np.float32)
    na, nr = int(a * SR), int(r * SR)
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


MINOR = [0, 3, 7, 12]
MAJOR = [0, 4, 7, 12]


def music(cfg, total, seed=0):
    rng = np.random.default_rng(seed)
    n = int(total * SR) + SR
    out = np.zeros(n, np.float32)
    root = cfg.get("root", 110.0)
    prog = cfg.get("prog", [0, -4, 3, -2])
    bar = cfg.get("bar", 8.0)
    kind = cfg.get("kind", "pad")
    qual = cfg.get("qual", ["m", "M", "M", "M"])
    t_all = np.arange(n) / SR
    # pad chords
    if "pad" in kind or "piano" in kind or "drone" in kind:
        k = 0
        start = 0.0
        while start < total:
            p = prog[k % len(prog)]
            q = MINOR if qual[k % len(qual)] == "m" else MAJOR
            L = bar + 2.5
            m = int(L * SR)
            s0 = int(start * SR)
            seg = np.zeros(m, np.float32)
            tt = np.arange(m) / SR
            if "pad" in kind:
                for iv in q:
                    f = root * 2 ** ((p + iv) / 12)
                    for det in (-0.35, 0.35):
                        seg += np.sin(2 * np.pi * (f + det) * tt + rng.uniform(0, 6)) * 0.22
                        seg += np.sin(2 * np.pi * 2 * (f + det) * tt) * 0.05
                seg *= env_ad(m, 2.0, 2.5)
            if "drone" in kind:
                f = root / 2 * 2 ** (p / 12)
                seg += (np.sin(2 * np.pi * f * tt) * 0.5 + np.sin(2 * np.pi * f * 1.5 * tt) * 0.12) * env_ad(m, 2.5, 2.5)
            e = min(n, s0 + m)
            out[s0:e] += seg[:e - s0]
            if "piano" in kind:
                step = cfg.get("step", 0.5)
                notes = [root * 2 ** ((p + iv) / 12) * 2 for iv in q[:3] + [q[1] + 12]]
                pat = cfg.get("pat", [0, 1, 2, 3, 2, 1])
                j = 0
                tn = start
                while tn < start + bar and tn < total:
                    f = notes[pat[j % len(pat)]]
                    ln = int(2.2 * SR)
                    tt2 = np.arange(ln) / SR
                    tone = (np.sin(2 * np.pi * f * tt2) + 0.35 * np.sin(4 * np.pi * f * tt2) +
                            0.12 * np.sin(6 * np.pi * f * tt2)) * np.exp(-tt2 * 2.6) * 0.35
                    a = int(tn * SR)
                    b2 = min(n, a + ln)
                    out[a:b2] += tone[:b2 - a]
                    tn += step
                    j += 1
            start += bar
            k += 1
    if "noise" in kind or "drone" in kind:
        nz = lowpass(rng.standard_normal(n).astype(np.float32), cfg.get("nzcut", 400)) * 0.25
        lfo = 0.6 + 0.4 * np.sin(2 * np.pi * t_all / 11.0)
        out += nz * lfo
    if "pulse" in kind:
        bpm = cfg.get("bpm", 70)
        per = 60 / bpm
        ln = int(0.5 * SR)
        tt = np.arange(ln) / SR
        kick = np.sin(2 * np.pi * (45 + 60 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 7) * 1.1
        tp = cfg.get("pulse_start", 0.0)
        while tp < total - 1:
            a = int(tp * SR)
            b2 = min(n, a + ln)
            out[a:b2] += kick[:b2 - a]
            tp += per
    if "hats" in kind:
        bpm = cfg.get("bpm", 80)
        per = 60 / bpm
        ln = int(0.06 * SR)
        tp = per / 2
        while tp < total - 1:
            hz = highpass(rng.standard_normal(ln).astype(np.float32), 6000) * np.exp(-np.arange(ln) / SR * 60) * 0.25
            a = int(tp * SR)
            out[a:a + ln] += hz[:len(out[a:a + ln])]
            tp += per
    if "tick" in kind:
        ln = int(0.03 * SR)
        tt = np.arange(ln) / SR
        tk = np.sin(2 * np.pi * 2400 * tt) * np.exp(-tt * 200) * 0.6
        tp = 0.0
        while tp < total - 1:
            a = int(tp * SR)
            out[a:a + ln] += tk[:len(out[a:a + ln])]
            tp += cfg.get("tick_every", 1.0)
    pk = np.max(np.abs(out)) or 1
    out = out / pk
    fade = env_ad(n, 1.5, 3.0)
    return out * fade


def sfx(name, rng):
    if name == "boom":
        ln = int(2.0 * SR)
        tt = np.arange(ln) / SR
        s = np.sin(2 * np.pi * (38 + 40 * np.exp(-tt * 4)) * tt) * np.exp(-tt * 1.8)
        s += lowpass(rng.standard_normal(ln).astype(np.float32), 200) * np.exp(-tt * 3) * 0.8
        return s * 0.9
    if name == "whoosh":
        ln = int(0.55 * SR)
        e = np.sin(np.linspace(0, np.pi, ln)) ** 2
        return highpass(lowpass(rng.standard_normal(ln).astype(np.float32), 2500), 300) * e * 0.35
    if name in ("pen", "chalk"):
        ln = int(0.9 * SR)
        x = highpass(rng.standard_normal(ln).astype(np.float32), 2500 if name == "pen" else 1500)
        am = (0.5 + 0.5 * np.sin(np.arange(ln) / SR * 2 * np.pi * 9) ** 2) * env_ad(ln, 0.05, 0.2)
        return x * am * (0.05 if name == "pen" else 0.09)
    if name == "page":
        ln = int(0.5 * SR)
        x = highpass(rng.standard_normal(ln).astype(np.float32), 900)
        e = np.exp(-((np.arange(ln) / SR - 0.15) ** 2) / 0.006)
        return x * e * 0.22
    if name == "tick":
        ln = int(0.08 * SR)
        tt = np.arange(ln) / SR
        return np.sin(2 * np.pi * 1800 * tt) * np.exp(-tt * 70) * 0.5
    if name == "hit":
        ln = int(1.2 * SR)
        tt = np.arange(ln) / SR
        s = np.sin(2 * np.pi * (55 + 80 * np.exp(-tt * 20)) * tt) * np.exp(-tt * 4)
        return s * 0.8
    if name == "ding":
        ln = int(1.5 * SR)
        tt = np.arange(ln) / SR
        return (np.sin(2 * np.pi * 1320 * tt) + 0.4 * np.sin(2 * np.pi * 2640 * tt)) * np.exp(-tt * 4) * 0.22
    if name == "scratch":  # cross-out
        ln = int(0.35 * SR)
        x = highpass(rng.standard_normal(ln).astype(np.float32), 1200) * env_ad(ln, 0.02, 0.1)
        return x * 0.2
    if name == "riser":
        ln = int(1.6 * SR)
        tt = np.arange(ln) / SR
        f = 200 + 900 * (tt / tt[-1]) ** 2
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * (tt / tt[-1]) ** 2 * 0.12
    return np.zeros(10, np.float32)


def build_audio(tl, style, path):
    mod = tl.mod
    n = len(tl.voice)
    v = tl.voice.copy()
    pk = np.max(np.abs(v)) or 1
    v = v / pk * 0.9
    m = music(mod.MUSIC, tl.total, seed=hash(mod.TITLE) % 1000)[:n]
    m = np.pad(m, (0, n - len(m)))
    # sidechain ducking
    envv = np.abs(v)
    k = int(0.25 * SR)
    envv = np.convolve(envv, np.ones(k) / k, mode="same")
    duck = 1 - 0.55 * np.clip(envv * 9, 0, 1)
    mix_ = v + m * mod.MUSIC.get("vol", 0.12) * duck
    rng = np.random.default_rng(7)
    for t, name, vol in style.sfx_events():
        s = sfx(name, rng).astype(np.float32) * vol
        a = int(t * SR)
        b = min(n, a + len(s))
        if a < n:
            mix_[a:b] += s[:b - a]
    mix_ = mix_ / max(1.0, np.max(np.abs(mix_)) / 0.97)
    sf.write(path, mix_, SR)


# ------------------------------------------------------------------ style base
class Base:
    xfade = 0.35
    cap = None  # dict(font,size,y,fill,hl,hlbox,bar,upper,stroke,sfill,maxw)

    def __init__(self, tl):
        self.tl = tl
        self.beats = tl.beats
        self.setup()

    def setup(self):
        self.BG = Image.new("RGB", (W, H), (10, 10, 12))

    def bg(self, t):
        return self.BG.copy()

    def draw(self, img, b, lt, t):
        pass

    def overlay(self, img, b, lt, t):
        pass

    def cross(self, b):
        return True

    def sfx_events(self):
        ev = []
        for b in self.beats:
            for name, off, vol in b.d.get("sfx", []):
                ev.append((b.t0 + off, name, vol))
        return ev

    def frame(self, t):
        b = self.tl.beat_at(t)
        lt = t - b.t0
        img = self.bg(t)
        self.draw(img, b, lt, t)
        if self.xfade and b.i > 0 and lt < self.xfade and self.cross(b):
            p = self.beats[b.i - 1]
            prev = self.bg(t)
            self.draw(prev, p, p.t1 - p.t0, t)
            img = Image.blend(prev, img, ease(lt / self.xfade))
        self.overlay(img, b, lt, t)
        if self.cap and self.show_cap(b):
            self.captions(img, t)
        return img

    def show_cap(self, b):
        return True

    def cap_style(self, ch):
        return self.cap

    def captions(self, img, t):
        ch = self.tl.chunk_at(t)
        if not ch:
            return
        c = self.cap_style(ch)
        if not c:
            return
        font = F(c["font"], c["size"], c.get("w"))
        words = [w["w"].upper() if c.get("upper") else w["w"] for w in ch]
        cur = -1
        for k, w in enumerate(ch):
            if w["t0"] <= t + 0.03:
                cur = k
        sp = font.getlength(" ")
        widths = [font.getlength(w) for w in words]
        maxw = c.get("maxw", 1500)
        lines = [[]]
        lw = 0
        for k, wd in enumerate(widths):
            if lines[-1] and lw + wd > maxw:
                lines.append([])
                lw = 0
            lines[-1].append(k)
            lw += wd + sp
        d = ImageDraw.Draw(img, "RGBA")
        CX = c.get("cx", W / 2)
        lh = c["size"] * 1.3
        y0 = c["y"] - (len(lines) - 1) * lh / 2
        pop = ease((t - ch[0]["t0"]) / 0.15) if c.get("pop") else 1
        if c.get("bar"):
            tw = max(sum(widths[k] + sp for k in ln) for ln in lines)
            pad = c.get("barpad", 28)
            rrect(d, (CX - tw / 2 - pad, y0 - lh / 2 - pad * 0.45, CX + tw / 2 + pad, y0 + (len(lines) - 0.5) * lh + pad * 0.45),
                  c.get("barr", 14), fill=c["bar"])
        for li, ln in enumerate(lines):
            tw = sum(widths[k] for k in ln) + sp * (len(ln) - 1)
            x = CX - tw / 2
            y = y0 + li * lh + (1 - pop) * 20
            for k in ln:
                wd = widths[k]
                active = k == cur
                past = k < cur
                if active and c.get("hlbox"):
                    rrect(d, (x - 10, y - c["size"] * 0.62, x + wd + 10, y + c["size"] * 0.62), c.get("hlr", 10), fill=c["hlbox"])
                col = c["hl"] if active else (c.get("past", c["fill"]) if past else c["fill"])
                d.text((x, y), words[k], font=font, fill=col, anchor="lm",
                       stroke_width=c.get("stroke", 0), stroke_fill=c.get("sfill", (0, 0, 0)))
                x += wd + sp


# ------------------------------------------------------------------ render
def load(n):
    f = glob.glob(os.path.join(ROOT, "videos", f"v{int(n):02d}_*.py"))[0]
    name = os.path.splitext(os.path.basename(f))[0]
    return importlib.import_module("videos." + name), name


def render(n, preview=None):
    mod, name = load(n)
    tl = Timeline(mod)
    st = mod.Style(tl)
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(BUILD, exist_ok=True)
    if preview is not None:  # list of times -> pngs
        for t in preview:
            st.frame(t).save(os.path.join(BUILD, f"{name}_{t:06.2f}.png"))
        print(name, "total %.1fs" % tl.total)
        return
    wav = os.path.join(BUILD, name + ".wav")
    build_audio(tl, st, wav)
    os.makedirs(getattr(mod, "OUTDIR", OUT), exist_ok=True)
    out = os.path.join(getattr(mod, "OUTDIR", OUT), f"{int(n):02d} - {mod.TITLE.replace('/', '-').replace(':', ' -')}.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", str(getattr(mod, "CRF", 20)), "-pix_fmt", "yuv420p",
           "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
           "-shortest", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    N = int(tl.total * FPS)
    for fi in range(N):
        p.stdin.write(st.frame(fi / FPS).tobytes())
    p.stdin.close()
    p.wait()
    print("done", out, "%.1fs" % tl.total)


def timing(n):
    mod, name = load(n)
    tl = Timeline(mod)
    words = sum(len(b.say.split()) for b in tl.beats)
    print(f"{name}: {tl.total:.1f}s  words={words}  beats={len(tl.beats)}")
    return tl


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "time":
        for a in args[1:]:
            timing(a)
    elif args and args[0] == "preview":
        n = args[1]
        ts = [float(x) for x in args[2:]]
        render(n, preview=ts)
    else:
        for a in args:
            render(a)
