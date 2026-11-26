"""THE SILENT CODE — animated reel engine (9:16).

usage: python3 reel.py <reel_dir>          (REUSE=1 skips frame render and only re-does captions/mix/encode)

<reel_dir> needs: voice_raw.wav, words.json, script.txt, meta.json (4 steps), edit.json:
{
  "out": "file.mp4", "accent": "#5CE1E6", "accent2": "#FFFFFF",
  "grade": "<ffmpeg filter chain>",
  "music": {"root": 49.0, "chords": [[0,7,12,15], ...], "gain": 0.07},
  "particles": "dust" | "rain" | "embers" | "bokeh" | null,
  "punch": ["leaving", "goodbye"],               # words that get a zoom punch-in + caption emphasis
  "shots": [{"img": "kf/s01_10001.png", "until": "leaving", "move": "dolly_in" | "dolly_out" | "pan_left" |
             "pan_right" | "rise" | "fall" | "orbit", "focus": [0.5, 0.5], "tr": "xf" | "whip" | "flash",
             "blur": [[x0,y0,x1,y1]]}, ...]
}
Animation = 2.5D parallax from a monocular depth map (Depth Anything V2), so near and far layers move at
different speeds, plus particles, light leaks, punch-ins and kinetic captions.
"""
import json, math, os, re, subprocess, sys
import cv2
import numpy as np
import soundfile as sf
from PIL import Image, ImageFilter, ImageDraw

W, H, FPS = 1080, 1920, 30
D = sys.argv[1]
E = json.load(open(f"{D}/edit.json"))
META = json.load(open(f"{D}/meta.json"))
words = json.load(open(f"{D}/words.json"))
REUSE = os.environ.get("REUSE") == "1" and os.path.exists(f"{D}/build/raw.mp4")
os.makedirs(f"{D}/build", exist_ok=True)
norm = lambda w: re.sub(r"[^a-z0-9']", "", w.lower().replace("’", "'")).strip("'")

voice, vsr = sf.read(f"{D}/voice_raw.wav")
vdur = len(voice) / vsr
TAIL = E.get("tail", 2.4)
total = round(vdur + TAIL, 2)
N = int(total * FPS)

# ------------------------------------------------------------------ timing helpers
def word_idx(token):
    w, _, n = token.partition("#"); n = int(n or 1); c = 0
    for i, x in enumerate(words):
        if norm(x["w"]) == norm(w):
            c += 1
            if c == n: return i
    raise SystemExit(f"word not found: {token}")

def cut_after(token):
    i = word_idx(token)
    e = words[i]["e"]; s = words[i + 1]["s"] if i + 1 < len(words) else e + 0.3
    return round((e + s) / 2, 3)

shots = E["shots"]
bounds = [0.0] + [cut_after(s["until"]) for s in shots[:-1]] + [total]
print("cuts:", bounds)

# step boundaries (for the flash / hit at the payoff) from meta steps
step_starts = {}
k = 0
for name, txt in META["steps"].items():
    step_starts[name] = words[k]["s"]; k += len(txt.split())
punch_times = []
for tok in E.get("punch", []):
    i = word_idx(tok); punch_times.append(words[i]["s"])

# ------------------------------------------------------------------ audio
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", f"{D}/voice_raw.wav", "-af",
                "highpass=f=70,equalizer=f=140:t=q:w=1:g=2.5,equalizer=f=3200:t=q:w=1.2:g=1.5,"
                "equalizer=f=7000:t=q:w=2:g=-2,acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=2,"
                "aecho=0.8:0.5:35|60:0.08|0.05,aresample=48000", "-ac", "2", f"{D}/build/voice_fx.wav"], check=True)
msr = 48000
t = np.arange(int(total * msr)) / msr
m = E["music"]; chords = m["chords"]; seg = total / len(chords)
pad = np.zeros_like(t)
for ci, ch in enumerate(chords):
    env = np.clip(np.minimum((t - ci * seg + 1.5) / 2.5, (ci * seg + seg + 1.5 - t) / 2.5), 0, 1)
    env = np.sin(env * np.pi / 2) ** 2
    for kk, st in enumerate(ch):
        f = m["root"] * 2 ** (st / 12) * 2
        for det in (-0.15, 0.0, 0.15):
            ph = 2 * np.pi * (f + det) * t + 0.3 * np.sin(2 * np.pi * 0.11 * t + kk)
            pad += env * (np.sin(ph) + 0.25 * np.sin(2 * ph) + 0.08 * np.sin(3 * ph)) / 3
    pad += env * 0.6 * np.sin(2 * np.pi * m["root"] * 2 ** (ch[0] / 12) * t)
# slow heartbeat pulse under the build (tension), stops at payoff
hb = np.zeros_like(t)
b0, b1 = step_starts["build"], step_starts["payoff"]
for bt in np.arange(b0, b1 - 0.3, 1.0):
    for off, g in ((0, 1.0), (0.22, 0.6)):
        a = int((bt + off) * msr); L = int(0.18 * msr); tt = np.arange(L) / msr
        if a + L < len(hb): hb[a:a + L] += np.sin(2 * np.pi * 52 * tt) * np.exp(-tt * 22) * g
pad /= np.max(np.abs(pad)) + 1e-9
pad *= np.clip(np.minimum(t / 1.2, (total - t) / 1.8), 0, 1) * m["gain"]
sfx = hb * 0.22
rng_a = np.random.default_rng(3)
def whoosh(at, g=0.07, L=0.7):
    a = int(max(at - L * 0.6, 0) * msr); n_ = int(L * msr); tt = np.arange(n_) / msr
    nz = np.convolve(rng_a.standard_normal(n_), np.ones(30) / 30, "same")
    env = np.sin(np.pi * tt / L) ** 3
    sfx[a:a + n_] += (nz * env * g)[: len(sfx) - a]
def hit(at, g=0.35):
    a = int(at * msr); n_ = int(1.6 * msr); tt = np.arange(n_) / msr
    s_ = (np.sin(2 * np.pi * 42 * tt) + 0.5 * np.sin(2 * np.pi * 63 * tt)) * np.exp(-tt * 3.2)
    sfx[a:a + n_] += (s_ * g)[: len(sfx) - a]
for i, b in enumerate(bounds[1:-1], 1):
    whoosh(b, 0.09 if shots[i].get("tr") == "whip" else 0.05)
hit(max(step_starts["payoff"] - 0.05, 0), 0.3)
hit(0.02, 0.25)
for pt in punch_times: whoosh(pt, 0.035, 0.4)
bed = np.stack([pad + sfx, pad * 0.97 + sfx], 1)
sf.write(f"{D}/build/bed.wav", bed.astype(np.float32), msr)
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", f"{D}/build/voice_fx.wav", "-i", f"{D}/build/bed.wav",
                "-filter_complex", "[0]apad[v];[v][1]amix=inputs=2:duration=longest:normalize=0,"
                "loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000[a]", "-map", "[a]", "-t", str(total),
                f"{D}/build/mix.wav"], check=True)

# ------------------------------------------------------------------ images: upscale + depth
def upscaled(path):
    out = f"{D}/build/up_" + os.path.basename(path)
    if os.path.exists(out): return out
    import torch
    from spandrel import ModelLoader
    global _sr
    if "_sr" not in globals():
        _sr = ModelLoader().load_from_file("/root/models/RealESRGAN_x2plus.pth").eval()
    src = Image.open(f"{D}/{path}").convert("RGB")
    x = torch.from_numpy(np.asarray(src).astype(np.float32) / 255).permute(2, 0, 1)[None]
    y = torch.zeros(1, 3, x.shape[2] * 2, x.shape[3] * 2); step, p_ = 384, 16
    with torch.no_grad():
        for i in range(0, x.shape[2], step):
            for j in range(0, x.shape[3], step):
                i0, j0 = max(i - p_, 0), max(j - p_, 0)
                i1, j1 = min(i + step + p_, x.shape[2]), min(j + step + p_, x.shape[3])
                r = _sr(x[:, :, i0:i1, j0:j1]); ie, je = min(i + step, x.shape[2]), min(j + step, x.shape[3])
                y[:, :, i * 2:ie * 2, j * 2:je * 2] = r[:, :, (i - i0) * 2:(i - i0) * 2 + (ie - i) * 2, (j - j0) * 2:(j - j0) * 2 + (je - j) * 2]
    up = Image.fromarray((y[0].permute(1, 2, 0).clamp(0, 1).numpy() * 255).round().astype(np.uint8))
    Image.blend(up, src.resize(up.size, Image.LANCZOS), 0.45).save(out)
    return out

def depth_of(path):
    out = f"{D}/build/depth_" + os.path.basename(path).replace(".png", ".npy")
    if os.path.exists(out): return np.load(out)
    global _dp
    if "_dp" not in globals():
        from transformers import pipeline
        _dp = pipeline("depth-estimation", model="depth-anything/Depth-Anything-V2-Small-hf", device="cpu")
    d = np.asarray(_dp(Image.open(f"{D}/{path}").convert("RGB"))["depth"], dtype=np.float32)
    d = (d - np.percentile(d, 2)) / (np.percentile(d, 98) - np.percentile(d, 2) + 1e-6)
    d = np.clip(d, 0, 1)
    np.save(out, d); return d

def privacy_blur(im, boxes):
    if not boxes: return im
    k = im.size[0] / 768
    bl = im.filter(ImageFilter.GaussianBlur(28 * k))
    mask = Image.new("L", im.size, 0); dr = ImageDraw.Draw(mask)
    for b in boxes: dr.rounded_rectangle([v * k for v in b], radius=int(30 * k), fill=255)
    return Image.composite(bl, im, mask.filter(ImageFilter.GaussianBlur(10 * k)))

layers = []
if not REUSE:
    _vid_cache = {}
    for s in shots:
        if s.get("video"):   # talking-avatar clip (SadTalker): frames + depth of its source still
            vp = f"{D}/{s['video']}"
            if vp not in _vid_cache:
                cap = cv2.VideoCapture(vp); fr_ = []
                while True:
                    ok, f_ = cap.read()
                    if not ok: break
                    fr_.append(cv2.cvtColor(f_, cv2.COLOR_BGR2RGB))
                _vid_cache[vp] = (fr_, cap.get(cv2.CAP_PROP_FPS) or 25.0)
            frames, vfps = _vid_cache[vp]
            d = depth_of(s["img"])
            d = cv2.GaussianBlur(cv2.resize(d, (frames[0].shape[1], frames[0].shape[0]), interpolation=cv2.INTER_CUBIC), (0, 0), 9)
            layers.append(((frames, vfps), d)); continue
        im = privacy_blur(Image.open(upscaled(s["img"])).convert("RGB"), s.get("blur"))
        img = np.asarray(im).astype(np.float32)
        d = depth_of(s["img"])
        d = cv2.resize(d, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_CUBIC)
        d = cv2.GaussianBlur(d, (0, 0), 9)          # soft depth = no tearing at edges
        layers.append((img, d))

# ------------------------------------------------------------------ camera
def ease(u): return u * u * (3 - 2 * u)
def ease_out(u): return 1 - (1 - u) ** 3
rng = np.random.default_rng(11)
def smooth_noise(n, scale, speed):
    kx = np.linspace(0, n / FPS * speed, n); ph = rng.uniform(0, 100, 3)
    return scale * (np.sin(kx + ph[0]) * 0.6 + np.sin(2.3 * kx + ph[1]) * 0.3 + np.sin(4.1 * kx + ph[2]) * 0.1)
hx, hy = smooth_noise(N + 10, 5, 0.9), smooth_noise(N + 10, 4, 0.8)

ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
def punch(tt):
    v = 0.0
    for pt in punch_times:
        d_ = tt - pt
        if 0 <= d_ < 0.12: v = max(v, ease_out(d_ / 0.12))
        elif 0.12 <= d_ < 0.9: v = max(v, 1 - ease((d_ - 0.12) / 0.78))
    return v

def render(i, k, u):
    """shot i, global frame k, local progress u (0..1) -> HxWx3 float32."""
    img, dep = layers[i]; s = shots[i]
    ih, iw = dep.shape
    if isinstance(img, tuple):   # video layer: pick the frame in sync with the narration
        frames, vfps = img
        lt = s["video_offset"] + (k / FPS - s["span_start"])
        img = frames[int(min(max(lt, 0), len(frames) / vfps - 1e-3) * vfps)]
    base = max(W / iw, H / ih) * 1.12          # 12% overscan = room for parallax
    mv = s.get("move", "dolly_in"); e = ease(u); tt = k / FPS
    zoom, px, py, par = 1.0, 0.0, 0.0, 0.0     # par = parallax strength (pixels at depth 1)
    if mv == "dolly_in":  zoom = 1.0 + 0.10 * e; par = 0.06 * e
    if mv == "dolly_out": zoom = 1.10 - 0.10 * e; par = 0.06 * (1 - e)
    if mv == "pan_left":  px = (0.5 - e) * 70; zoom = 1.04
    if mv == "pan_right": px = (e - 0.5) * 70; zoom = 1.04
    if mv == "rise":      py = (0.5 - e) * 90; zoom = 1.05
    if mv == "fall":      py = (e - 0.5) * 90; zoom = 1.05
    if mv == "orbit":     px = math.sin(u * math.pi - math.pi / 2) * 60; zoom = 1.05 + 0.04 * e
    zoom *= (1 + 0.045 * punch(tt)) * s.get("zoom", 1.0)
    fx, fy = s.get("focus", (0.5, 0.5))
    # output pixel -> normalized offset from frame centre
    ox, oy = (xs - W / 2) + np.float32(hx[k]), (ys - H / 2) + np.float32(hy[k])
    # first pass: where would it sample without parallax?
    sc = base * zoom
    sx0 = (iw * fx + ox / sc).astype(np.float32); sy0 = (ih * fy + oy / sc).astype(np.float32)
    dd = cv2.remap(dep, sx0, sy0, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    # depth-dependent scale (dolly) + depth-dependent shift (pans move near layers more)
    sc_d = sc * (1 + par * dd)
    sx = iw * fx + ox / sc_d - px * (0.35 + dd) / base
    sy = ih * fy + oy / sc_d - py * (0.35 + dd) / base
    return cv2.remap(img, sx.astype(np.float32), sy.astype(np.float32), cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT).astype(np.float32)

# ------------------------------------------------------------------ particles & light
P = E.get("particles")
prng = np.random.default_rng(5)
NP = {"dust": 70, "embers": 45, "bokeh": 22, "rain": 260}.get(P, 0)
pp = prng.uniform(0, 1, (NP, 2)) * [W, H]
pv = {"dust": (6, -10), "embers": (8, -55), "bokeh": (4, -6), "rain": (-90, 1500)}.get(P, (0, 0))
psz = prng.uniform(0.6, 1.0, NP)
def particles(k):
    if not NP: return None
    ov = np.zeros((H, W), np.float32); tt = k / FPS
    for j in range(NP):
        x = (pp[j, 0] + pv[0] * tt * psz[j] + 18 * math.sin(tt * 0.7 + j)) % W
        y = (pp[j, 1] + pv[1] * tt * psz[j]) % H
        if P == "rain":
            cv2.line(ov, (int(x), int(y)), (int(x - 5), int(y + 46 * psz[j])), 0.35 * psz[j], 2, cv2.LINE_AA)
        elif P == "bokeh":
            cv2.circle(ov, (int(x), int(y)), int(26 * psz[j]), 0.16 * psz[j], -1, cv2.LINE_AA)
        else:
            tw = 0.6 + 0.4 * math.sin(tt * 3 + j * 1.7)
            cv2.circle(ov, (int(x), int(y)), int(2 + 3 * psz[j]), (0.9 if P == "embers" else 0.55) * tw * psz[j], -1, cv2.LINE_AA)
    return cv2.GaussianBlur(ov, (0, 0), 6 if P == "bokeh" else 1.4)
PCOL = np.array({"embers": (255, 170, 90), "dust": (255, 240, 220), "bokeh": (255, 225, 190), "rain": (200, 220, 255)}.get(P, (255, 255, 255)), np.float32)

leak_y = np.linspace(0, 1, H, dtype=np.float32)[:, None]
leak_x = np.linspace(0, 1, W, dtype=np.float32)[None, :]
def light_leak(tt):
    """warm diagonal light sweep at each cut, adds the 'animated' film feel."""
    a = 0.0
    for b in bounds[1:-1]:
        d_ = tt - (b - 0.15)
        if 0 <= d_ < 0.7: a = max(a, math.sin(math.pi * d_ / 0.7))
    if a <= 0: return None
    g = np.exp(-((leak_x * 0.8 + leak_y * 0.5 - 0.2 - a * 0.6) ** 2) / 0.02)
    return g * a * 0.22

# ------------------------------------------------------------------ frame loop
if not REUSE:
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "14",
                           "-pix_fmt", "yuv420p", f"{D}/build/raw.mp4"], stdin=subprocess.PIPE)
    XF = 0.3
    for k in range(N):
        tt = k / FPS
        i = max(j for j in range(len(shots)) if bounds[j] <= tt)
        a, b = bounds[i], bounds[i + 1]
        u = lambda ii, t_: (t_ - (bounds[ii] - 0.3)) / (bounds[ii + 1] + 0.3 - bounds[ii] + 0.3)
        fr = render(i, k, min(max(u(i, tt), 0), 1))
        # transition into shot i (centred on cut a)
        if i > 0 and tt < a + XF / 2:
            w = (tt - (a - XF / 2)) / XF
            prev = render(i - 1, k, min(u(i - 1, tt), 1))
            tr = shots[i].get("tr", "xf")
            if tr == "whip":
                w_ = ease(min(max(w, 0), 1)); sh = int(W * 0.9 * w_)
                ker = max(3, int(60 * math.sin(math.pi * w_))) | 1
                comp = np.concatenate([prev[:, sh:], fr[:, :sh]], 1) if sh else prev
                fr = cv2.blur(comp, (ker, 1))
            elif tr == "flash":
                fr = prev if w < 0.5 else fr
                fr = fr + (255 - fr) * max(0, 1 - abs(w - 0.5) * 3.2) * 0.85
            else:
                fr = prev * (1 - ease(w)) + fr * ease(w)
        elif i < len(shots) - 1 and tt > b - XF / 2:
            w = (tt - (b - XF / 2)) / XF
            nxt = render(i + 1, k, max(u(i + 1, tt), 0))
            tr = shots[i + 1].get("tr", "xf")
            if tr == "whip":
                w_ = ease(min(max(w, 0), 1)); sh = int(W * 0.9 * w_)
                ker = max(3, int(60 * math.sin(math.pi * w_))) | 1
                comp = np.concatenate([fr[:, sh:], nxt[:, :sh]], 1) if sh else fr
                fr = cv2.blur(comp, (ker, 1))
            elif tr == "flash":
                fr = fr if w < 0.5 else nxt
                fr = fr + (255 - fr) * max(0, 1 - abs(w - 0.5) * 3.2) * 0.85
            else:
                fr = fr * (1 - ease(w)) + nxt * ease(w)
        po = particles(k)
        if po is not None: fr = fr + po[..., None] * PCOL
        lk = light_leak(tt)
        if lk is not None: fr = fr + lk[..., None] * np.array([255, 190, 120], np.float32)
        ff.stdin.write(np.clip(fr, 0, 255).astype(np.uint8).tobytes())
    ff.stdin.close(); ff.wait()

# ------------------------------------------------------------------ captions (ASS)
def hexass(h): h = h.lstrip("#"); return f"&H00{h[4:6]}{h[2:4]}{h[0:2]}".upper()
ACC = hexass(E["accent"])
def ts(x): x = max(x, 0); return f"{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}"
ass = [f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Big,Inter Display Black,118,&H00FFFFFF,&H00FFFFFF,&H00000000,&H9A000000,-1,0,0,0,100,100,0,0,1,9,5,5,70,70,0,1
Style: Hook,Inter Display Black,104,&H00FFFFFF,&H00FFFFFF,&H00000000,&HA0000000,-1,0,0,0,100,100,1,0,1,8,5,8,60,60,210,1
Style: Tag,Inter Display SemiBold,46,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,9,0,1,2,1,2,60,60,250,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"""]

# hook headline: words slam in one by one in the first ~2.6 s
hook_words = META["hook"] if "hook" in META else E["hook"]
hw = hook_words.split(); lines, cur = [], []
for w_ in hw:
    if cur and len(" ".join(cur + [w_])) > 14: lines.append(cur); cur = [w_]
    else: cur.append(w_)
lines.append(cur)
HOOK_END = min(2.8, step_starts["curiosity"])
d_in = 0.11
idx = 0
txt_parts = []
for li, ln in enumerate(lines):
    for w_ in ln:
        t0 = int(idx * d_in * 1000)
        col = ACC if idx == len(hw) - 1 or w_.isdigit() else "&H00FFFFFF&"
        txt_parts.append(f"{{\\alpha&HFF&\\c{col}\\t({t0},{t0 + 1},\\alpha&H00&)\\fscx100\\fscy100}}{w_}")
        idx += 1
    txt_parts.append("\\N")
ass.append(f"Dialogue: 3,{ts(0.05)},{ts(HOOK_END)},Hook,,0,0,0,,{{\\fad(0,220)\\fscx112\\fscy112\\t(0,260,\\fscx100\\fscy100)}}" + " ".join(txt_parts).replace(" \\N ", "\\N").rstrip("\\N"))

# big kinetic captions: 1-3 words, centre screen, current word pops in accent colour
PUNCH = {norm(p.partition("#")[0]) for p in E.get("punch", [])}
chunks, cur = [], []
for i, x in enumerate(words):
    cur.append(x)
    gap = words[i + 1]["s"] - x["e"] if i + 1 < len(words) else 9
    long_ = len(" ".join(w["w"] for w in cur)) > 13
    if re.search(r"[.,:!?—]$|\.\.\.$", x["w"]) or len(cur) >= 3 or gap > 0.3 or long_ or norm(x["w"]) in PUNCH:
        chunks.append(cur); cur = []
if cur: chunks.append(cur)
CAP_Y = E.get("cap_y", 1180)
for ci, ch in enumerate(chunks):
    c_end = min(chunks[ci + 1][0]["s"] if ci + 1 < len(chunks) else ch[-1]["e"] + 0.5, ch[-1]["e"] + 0.5)
    for wi, x in enumerate(ch):
        s0 = x["s"] if wi else ch[0]["s"]
        e0 = ch[wi + 1]["s"] if wi + 1 < len(ch) else c_end
        if e0 - s0 < 0.02: continue
        parts = []
        for wj, y in enumerate(ch):
            txt = y["w"].replace("—", "").strip().upper()
            if not txt: continue
            if wj == wi:
                big = 128 if norm(y["w"]) in PUNCH else 116
                parts.append(f"{{\\c{ACC}\\fscx{big}\\fscy{big}\\t(0,110,\\fscx{big - 12}\\fscy{big - 12})}}{txt}{{\\c&H00FFFFFF&\\fscx100\\fscy100}}")
            elif wj > wi:
                parts.append(txt)
            else:
                parts.append(txt)
        intro = f"\\move(540,{CAP_Y + 26},540,{CAP_Y},0,120)\\fad(80,0)" if wi == 0 else f"\\pos(540,{CAP_Y})"
        ass.append(f"Dialogue: 1,{ts(s0)},{ts(e0)},Big,,0,0,0,,{{{intro}}}" + " ".join(parts))

tag_s = vdur + 0.25
ass.append(f"Dialogue: 2,{ts(tag_s)},{ts(total)},Tag,,0,0,0,,{{\\fad(450,350)\\fs26\\c{ACC}}}━━━━━━{{\\r}}\\N{{\\fad(450,350)}}THE SILENT CODE")
open(f"{D}/build/captions.ass", "w").write("\n".join(ass) + "\n")

# ------------------------------------------------------------------ final encode
vf = (f"{E['grade']},vignette=angle=PI/5:mode=forward,noise=alls=5:allf=t,"
      f"fade=t=in:st=0:d=0.25,fade=t=out:st={total - 0.6}:d=0.6,ass={D}/build/captions.ass,format=yuv420p")
out = f"{D}/{E['out']}"
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", f"{D}/build/raw.mp4", "-i", f"{D}/build/mix.wav", "-vf", vf,
                "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-maxrate", "16M",
                "-bufsize", "32M", "-profile:v", "high", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                "-movflags", "+faststart", "-metadata", "title=" + META["title"], "-shortest", out], check=True)
print("wrote", out, total, "s")
