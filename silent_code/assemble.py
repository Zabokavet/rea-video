"""THE SILENT CODE — POV Short assembler.

usage: python3 assemble.py <video_dir>
<video_dir>/edit.json drives everything:
{
  "hook": "POV: YOU STOP EXPLAINING YOURSELF",
  "accent": "#FFC247",                    # highlight colour for this video's skin
  "grade": "<ffmpeg filter chain>",       # colour skin for this video
  "tail": 2.6,                            # seconds after narration (tag shown here)
  "music": {"root": 49.0, "chords": [[0,7,12,15],[-4,3,8,12]], "gain": 0.06},
  "sfx": [{"type": "buzz", "t": 14.2, "n": 3}],
  "shots": [{"img": "kf/s1_12.png", "until": "misunderstand", "move": "push", "shake": null}, ...]
}
Shot boundaries are given as the script word (occurrence counted) after which the cut happens,
so cuts always land between spoken phrases.
"""
import json, math, os, re, subprocess, sys
import numpy as np
import soundfile as sf
from PIL import Image, ImageFilter

W, H, FPS = 1080, 1920, 30
XF = 0.4  # crossfade seconds
D = sys.argv[1]
E = json.load(open(f"{D}/edit.json"))
words = json.load(open(f"{D}/words.json"))
os.makedirs(f"{D}/build", exist_ok=True)

# ---------------------------------------------------------------- audio
voice, sr = sf.read(f"{D}/voice_raw.wav")
vdur = len(voice) / sr
total = round(vdur + E.get("tail", 2.6), 2)
N = int(total * FPS)

subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", f"{D}/voice_raw.wav", "-af",
                "highpass=f=70,equalizer=f=140:t=q:w=1:g=2.5,equalizer=f=3200:t=q:w=1.2:g=1.5,"
                "equalizer=f=7000:t=q:w=2:g=-2,acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=2,"
                "aecho=0.8:0.5:35|60:0.08|0.05,aresample=48000",
                "-ac", "2", f"{D}/build/voice_fx.wav"], check=True)

# music bed: slow warm pad, synthesized (no licensing issues)
msr = 48000
t = np.arange(int(total * msr)) / msr
m = E["music"]
pad = np.zeros_like(t)
chords = m["chords"]
seg = total / len(chords)
for ci, ch in enumerate(chords):
    env = np.clip(np.minimum((t - ci * seg + 1.5) / 2.5, (ci * seg + seg + 1.5 - t) / 2.5), 0, 1)
    env = np.sin(env * np.pi / 2) ** 2
    for k, st in enumerate(ch):
        f = m["root"] * 2 ** (st / 12) * 2
        for det in (-0.12, 0.0, 0.12):  # chorus detune
            ph = 2 * np.pi * (f + det) * t + 0.3 * np.sin(2 * np.pi * 0.11 * t + k)
            pad += env * (np.sin(ph) + 0.25 * np.sin(2 * ph) + 0.08 * np.sin(3 * ph)) / 3
    # deep sub note
    pad += env * 0.6 * np.sin(2 * np.pi * m["root"] * 2 ** (ch[0] / 12) * t)
pad /= np.max(np.abs(pad)) + 1e-9
fade = np.clip(np.minimum(t / 1.5, (total - t) / 1.8), 0, 1)
pad *= fade * m["gain"]
sfx = np.zeros_like(t)
for s in E.get("sfx", []):
    if s["type"] == "buzz":  # phone vibration: 3 short low buzzes
        for i in range(s.get("n", 3)):
            a = int((s["t"] + i * 0.55) * msr); L = int(0.32 * msr)
            tt = np.arange(L) / msr
            b = np.sign(np.sin(2 * np.pi * 172 * tt)) * 0.5 + np.sin(2 * np.pi * 344 * tt) * 0.3
            b *= np.clip(np.minimum(tt / 0.02, (0.32 - tt) / 0.04), 0, 1) * (0.6 + 0.4 * np.sin(2 * np.pi * 23 * tt))
            sfx[a:a + L] += b * s.get("gain", 0.05)
    if s["type"] == "thud":  # phone placed face down / door: soft low thump
        a = int(s["t"] * msr); L = int(0.25 * msr); tt = np.arange(L) / msr
        sfx[a:a + L] += np.sin(2 * np.pi * 70 * tt) * np.exp(-tt * 28) * s.get("gain", 0.25)
    if s["type"] == "whoosh":  # soft air whoosh for transitions
        a = int(s["t"] * msr); L = int(0.9 * msr); tt = np.arange(L) / msr
        nz = np.random.default_rng(1).standard_normal(L)
        nz = np.convolve(nz, np.ones(40) / 40, "same")
        sfx[a:a + L] += nz * np.sin(np.pi * tt / 0.9) ** 2 * s.get("gain", 0.12)
    if s["type"] == "breath":  # long exhale-like airy noise
        a = int(s["t"] * msr); L = int(1.6 * msr); tt = np.arange(L) / msr
        nz = np.random.default_rng(2).standard_normal(L)
        nz = np.convolve(nz, np.ones(12) / 12, "same")
        sfx[a:a + L] += nz * np.sin(np.pi * tt / 1.6) ** 3 * s.get("gain", 0.06)
bed = np.stack([pad + sfx, pad * 0.97 + sfx], 1)
sf.write(f"{D}/build/bed.wav", bed.astype(np.float32), msr)
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", f"{D}/build/voice_fx.wav", "-i", f"{D}/build/bed.wav",
                "-filter_complex", "[0]adelay=0|0,apad[v];[v][1]amix=inputs=2:duration=longest:normalize=0,"
                "loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000[a]", "-map", "[a]",
                "-t", str(total), f"{D}/build/mix.wav"], check=True)

# ---------------------------------------------------------------- cut points from words
def word_end(token):
    """token like 'misunderstand' or 'you#3' (3rd occurrence)."""
    w, _, n = token.partition("#"); n = int(n or 1); c = 0
    for x in words:
        if re.sub(r"[^a-z']", "", x["w"].lower()) == w.lower():
            c += 1
            if c == n: return x["e"]
    raise SystemExit(f"cut word not found: {token}")

def next_start(t_end):
    nxt = [x["s"] for x in words if x["s"] >= t_end - 1e-3]
    return nxt[0] if nxt else t_end

shots = E["shots"]
bounds = [0.0]
for s in shots[:-1]:
    te = word_end(s["until"])
    bounds.append(round((te + next_start(te)) / 2, 3))  # cut in the pause
bounds.append(total)
print("cuts:", bounds)

# ---------------------------------------------------------------- upscale keyframes (Real-ESRGAN x2)
def upscaled(path):
    out = f"{D}/build/up_" + os.path.basename(path)
    if os.path.exists(out): return out
    import torch
    from spandrel import ModelLoader
    global _sr_model
    if "_sr_model" not in globals():
        _sr_model = ModelLoader().load_from_file("/root/models/RealESRGAN_x2plus.pth").eval()
    im = np.asarray(Image.open(f"{D}/{path}").convert("RGB")).astype(np.float32) / 255
    x = torch.from_numpy(im).permute(2, 0, 1)[None]
    with torch.no_grad():
        tiles = []
        y = torch.zeros(1, 3, x.shape[2] * 2, x.shape[3] * 2)
        step, pad_ = 384, 16
        for i in range(0, x.shape[2], step):
            for j in range(0, x.shape[3], step):
                i0, j0 = max(i - pad_, 0), max(j - pad_, 0)
                i1, j1 = min(i + step + pad_, x.shape[2]), min(j + step + pad_, x.shape[3])
                r = _sr_model(x[:, :, i0:i1, j0:j1])
                y[:, :, i * 2:min(i + step, x.shape[2]) * 2, j * 2:min(j + step, x.shape[3]) * 2] = \
                    r[:, :, (i - i0) * 2:(i - i0) * 2 + (min(i + step, x.shape[2]) - i) * 2,
                          (j - j0) * 2:(j - j0) * 2 + (min(j + step, x.shape[3]) - j) * 2]
    up = Image.fromarray((y[0].permute(1, 2, 0).clamp(0, 1).numpy() * 255).round().astype(np.uint8))
    # blend 70/30 with lanczos to keep natural film texture (ESRGAN alone looks waxy)
    lz = Image.open(f"{D}/{path}").convert("RGB").resize(up.size, Image.LANCZOS)
    Image.blend(up, lz, 0.45).save(out)
    return out

def privacy_blur(im, boxes):
    """Heavy feathered blur over screen regions (boxes in keyframe px, 768x1344) so no text is readable."""
    if not boxes: return im
    from PIL import ImageDraw
    k = im.size[0] / 768
    bl = im.filter(ImageFilter.GaussianBlur(28 * k))
    mask = Image.new("L", im.size, 0); d = ImageDraw.Draw(mask)
    for b in boxes:
        d.rounded_rectangle([v * k for v in b], radius=int(30 * k), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(10 * k))
    return Image.composite(bl, im, mask)

imgs = [] if os.environ.get("REUSE") == "1" else [privacy_blur(Image.open(upscaled(s["img"])).convert("RGB"), s.get("blur")) for s in shots]

# ---------------------------------------------------------------- motion
rng = np.random.default_rng(7)
def smooth_noise(n, scale, speed):
    k = np.linspace(0, n / FPS * speed, n)
    ph = rng.uniform(0, 100, 3)
    return scale * (np.sin(k + ph[0]) * 0.6 + np.sin(2.3 * k + ph[1]) * 0.3 + np.sin(4.1 * k + ph[2]) * 0.1)

hx, hy = smooth_noise(N, 9, 1.1), smooth_noise(N, 7, 0.9)  # handheld POV drift (px)
hr = smooth_noise(N, 0.25, 0.7)                            # micro roll (deg)

def ease(u): return u * u * (3 - 2 * u)

def frame_of(i, k, tl):
    """render shot i at local progress tl (0..1) for global frame k."""
    s, im = shots[i], imgs[i]
    iw, ih = im.size
    base = max(W / iw, H / ih)
    mv = s.get("move", "push")
    u = ease(tl)
    z0, z1 = {"push": (1.06, 1.16), "pull": (1.17, 1.06), "rise": (1.10, 1.14),
              "panL": (1.14, 1.14), "panR": (1.14, 1.14), "walk": (1.08, 1.22), "still": (1.08, 1.10)}[mv]
    z = (z0 + (z1 - z0) * u) * s.get("zoom", 1.0)
    cw, ch = W / (base * z), H / (base * z)
    fx, fy = s.get("center", (0.5, 0.5))
    cx, cy = iw * fx, ih * fy
    if mv == "panL": cx += (0.5 - u) * (iw - cw) * 0.6
    if mv == "panR": cx -= (0.5 - u) * (iw - cw) * 0.6
    if mv == "rise": cy += (0.5 - u) * (ih - ch) * 0.7
    if mv == "walk":  # forward walk with gentle step bob
        tt = k / FPS
        cy += math.sin(tt * 2 * math.pi * 1.8) * 5 / base
        cx += math.sin(tt * math.pi * 1.8) * 4 / base
    amp = s.get("handheld", 1.0)
    cx += hx[k] * amp / base; cy += hy[k] * amp / base
    sh = s.get("shake")
    if sh:  # phone buzz: short high-frequency jitter while it vibrates
        tt = k / FPS
        for b0 in sh:
            for j in range(3):
                d = tt - (b0 + j * 0.55)
                if 0 <= d < 0.32:
                    cx += math.sin(d * 2 * math.pi * 31) * 2.2 / base
                    cy += math.cos(d * 2 * math.pi * 27) * 1.6 / base
    cx = min(max(cx, cw / 2), iw - cw / 2); cy = min(max(cy, ch / 2), ih - ch / 2)
    x0, y0 = cx - cw / 2, cy - ch / 2
    fr = im.transform((W, H), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BICUBIC)
    rot = hr[k] * amp
    if abs(rot) > 0.01:
        fr = fr.rotate(rot, Image.BICUBIC, expand=False)
        # rotation leaves corners; we zoomed >= 1.06 so crop-scale a hair to hide them
        m_ = 0.012
        fr = fr.transform((W, H), Image.EXTENT, (W * m_, H * m_, W * (1 - m_), H * (1 - m_)), Image.BICUBIC)
    return fr

REUSE = os.environ.get("REUSE") == "1" and os.path.exists(f"{D}/build/raw.mp4")
ff = None if REUSE else subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                       "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "14",
                       "-pix_fmt", "yuv420p", f"{D}/build/raw.mp4"], stdin=subprocess.PIPE)
for k in ([] if REUSE else range(N)):
    tt = k / FPS
    i = max(j for j in range(len(shots)) if bounds[j] <= tt)
    a, b = bounds[i], bounds[i + 1]
    # shots extend XF/2 either side so crossfades centre on the cut
    lo, hi = a - (XF / 2 if i else 0), b + (XF / 2 if i < len(shots) - 1 else 0)
    fr = frame_of(i, k, (tt - lo) / (hi - lo))
    if i < len(shots) - 1 and tt > b - XF / 2:
        w = (tt - (b - XF / 2)) / XF
        a2, b2 = bounds[i + 1], bounds[i + 2]
        lo2, hi2 = a2 - XF / 2, b2 + (XF / 2 if i + 1 < len(shots) - 1 else 0)
        fr = Image.blend(fr, frame_of(i + 1, k, (tt - lo2) / (hi2 - lo2)), ease(w))
    elif i > 0 and tt < a + XF / 2:
        w = (tt - (a - XF / 2)) / XF
        a0, b0 = bounds[i - 1], bounds[i]
        lo0, hi0 = a0 - (XF / 2 if i - 1 else 0), b0 + XF / 2
        fr = Image.blend(frame_of(i - 1, k, (tt - lo0) / (hi0 - lo0)), fr, ease(w))
    ff.stdin.write(fr.tobytes())
if ff: ff.stdin.close(); ff.wait()

# ---------------------------------------------------------------- ASS: hook, word-highlight captions, tag
def hexass(h):  # #RRGGBB -> &H00BBGGRR
    h = h.lstrip("#"); return f"&H00{h[4:6]}{h[2:4]}{h[0:2]}".upper()
ACC = hexass(E["accent"])
def ts(x):
    x = max(x, 0); h = int(x // 3600); m_ = int(x % 3600 // 60); s_ = x % 60
    return f"{h}:{m_:02d}:{s_:05.2f}"

ass = [f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter Display ExtraBold,84,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,6,3,2,90,90,560,1
Style: Hook,Inter Display Black,96,&H00FFFFFF,&H00FFFFFF,&H00000000,&HA0000000,-1,0,0,0,100,100,1,0,1,7,4,8,70,70,190,1
Style: Tag,Inter Display SemiBold,46,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,9,0,1,2,1,2,60,60,250,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"""]

# hook: first 3 s, "POV:" in accent colour, pops in
hook = E["hook"]
pre, _, rest = hook.partition(":")
lines, cur_ = [], ""
for wd in rest.split():
    if cur_ and len(cur_) + 1 + len(wd) > 15: lines.append(cur_); cur_ = wd
    else: cur_ = (cur_ + " " + wd).strip()
lines.append(cur_)
rest = "\\N".join(lines)
ass.append(f"Dialogue: 2,{ts(0.0)},{ts(3.0)},Hook,,0,0,0,,{{\\fad(150,250)\\fscx88\\fscy88\\t(0,180,\\fscx100\\fscy100)}}"
           f"{{\\c{ACC}}}{pre}:{{\\c&H00FFFFFF&}}\\N{rest.strip()}")

# captions: chunk into short phrases (break on punctuation / max 3 words / long gaps)
chunks, cur = [], []
for i, x in enumerate(words):
    cur.append(x)
    gap = words[i + 1]["s"] - x["e"] if i + 1 < len(words) else 9
    if re.search(r"[.,:!?…—]$|\.\.\.$", x["w"]) or len(cur) >= 3 or gap > 0.35 or \
            (len(cur) == 2 and len("".join(w["w"] for w in cur)) > 16):
        chunks.append(cur); cur = []
if cur: chunks.append(cur)
for ci, ch in enumerate(chunks):
    c_end = chunks[ci + 1][0]["s"] if ci + 1 < len(chunks) else ch[-1]["e"] + 0.6
    c_end = min(c_end, ch[-1]["e"] + 0.6)
    for wi, x in enumerate(ch):
        s0 = x["s"] if wi else ch[0]["s"]
        e0 = ch[wi + 1]["s"] if wi + 1 < len(ch) else c_end
        parts = []
        for wj, y in enumerate(ch):
            txt = y["w"].replace("—", "").strip()
            if wj == wi:
                parts.append(f"{{\\c{ACC}\\fscx110\\fscy110}}{txt}{{\\c&H00FFFFFF&\\fscx100\\fscy100}}")
            else:
                parts.append(txt)
        pop = "\\fscx92\\fscy92\\t(0,90,\\fscx100\\fscy100)" if wi == 0 else ""
        ass.append(f"Dialogue: 1,{ts(s0)},{ts(e0)},Cap,,0,0,0,,{{{pop}}}" + " ".join(p for p in parts if p))

# tag at the end
tag_s = vdur + 0.2
ass.append(f"Dialogue: 2,{ts(tag_s)},{ts(total)},Tag,,0,0,0,,{{\\fad(500,400)\\fs26\\c{ACC}}}━━━━━━{{\\r}}\\N{{\\fad(500,400)}}THE SILENT CODE")
open(f"{D}/build/captions.ass", "w").write("\n".join(ass) + "\n")

# ---------------------------------------------------------------- final: grade + grain + vignette + captions + audio
vf = (f"{E['grade']},vignette=angle=PI/5:mode=forward,noise=alls=5:allf=t,"
      f"fade=t=in:st=0:d=0.35,fade=t=out:st={total-0.6}:d=0.6,"
      f"ass={D}/build/captions.ass,format=yuv420p")
out = f"{D}/{E['out']}"
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", f"{D}/build/raw.mp4", "-i", f"{D}/build/mix.wav",
                "-vf", vf, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-maxrate", "16M", "-bufsize", "32M",
                "-profile:v", "high", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                "-movflags", "+faststart", "-metadata", "title=" + E["title"], "-shortest", out], check=True)
print("wrote", out, total, "s")
