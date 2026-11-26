"""Cartoon-style lip-sync for the narrator avatar.

usage: python3 talk.py <dir>      (dir = a1; needs avatar_audio.wav, avatar_spans.json, words.json, talk.json)
talk.json: {"base": "kf/avatar_501.png", "small": "mouths/small_1.png", "open": "mouths/open_1.png",
            "oh": "mouths/oh_1.png", "ee": "mouths/ee_1.png", "blink": "mouths/blink_1.png",
            "mask_mouth": "mouths/mask_mouth.png", "mask_eyes": "mouths/mask_eyes.png", "pivot": [384, 1000]}
Mouth opening follows the voice loudness frame by frame; the mouth SHAPE follows the letters of the word
being spoken (o/u/w -> "oh", e/i/y -> "ee", a -> "open", m/b/p -> closed). Adds blinks, head tilt/nods, breathing.
Writes <dir>/talk/avatar.mp4 (25 fps, same size as the avatar image), matching the concatenated avatar audio.
"""
import json, math, re, subprocess, sys
import cv2, numpy as np, soundfile as sf

D = sys.argv[1]; FPS = 25
C = json.load(open(f"{D}/talk.json"))
rd = lambda p: cv2.cvtColor(cv2.imread(f"{D}/{p}"), cv2.COLOR_BGR2RGB).astype(np.float32)
base = rd(C["base"]); H, W = base.shape[:2]
shape = {k: rd(C[k]) for k in ("small", "open", "oh", "ee")}
blink = rd(C["blink"])
mm = cv2.imread(f"{D}/{C['mask_mouth']}", 0).astype(np.float32)[..., None] / 255
me = cv2.imread(f"{D}/{C['mask_eyes']}", 0).astype(np.float32)[..., None] / 255

audio, sr = sf.read(f"{D}/avatar_audio.wav")
if audio.ndim > 1: audio = audio.mean(1)
dur = len(audio) / sr; N = int(dur * FPS)
# loudness envelope per frame (40 ms window), normalised
env = np.array([np.sqrt(np.mean(audio[int(i / FPS * sr): int(i / FPS * sr) + int(0.04 * sr)] ** 2) + 1e-12) for i in range(N)])
env = env / (np.percentile(env, 95) + 1e-9)
sm = np.zeros(N); a = 0
for i in range(N):  # fast attack, slower release = natural jaw
    a = a + (env[i] - a) * (0.75 if env[i] > a else 0.45); sm[i] = a

# word timings mapped into the concatenated avatar timeline
spans = json.load(open(f"{D}/avatar_spans.json")); words = json.load(open(f"{D}/words.json"))
tl = []; off = 0.0
for s0, s1 in spans:
    for w in words:
        if w["s"] >= s0 - 0.05 and w["e"] <= s1 + 0.05:
            tl.append((off + w["s"] - s0, off + w["e"] - s0, re.sub(r"[^a-z]", "", w["w"].lower())))
    off += s1 - s0
def letter_at(t):
    for s, e, w in tl:
        if s <= t <= e and w:
            return w[min(int((t - s) / max(e - s, 1e-3) * len(w)), len(w) - 1)], w
    return None, None

rng = np.random.default_rng(4)
blinks = []; t = 1.2
while t < dur: blinks.append(t); t += rng.uniform(2.4, 4.6)
def blink_amt(t):
    for b in blinks:
        d = t - b
        if 0 <= d < 0.16: return [0.55, 1.0, 1.0, 0.55][min(int(d / 0.04), 3)]
    return 0.0

kx = np.linspace(0, dur, N)
tilt = 1.1 * np.sin(kx * 0.9 + 1.3) + 0.5 * np.sin(kx * 2.1)           # degrees
dx = 6 * np.sin(kx * 0.7 + 0.4); dy = 4 * np.sin(kx * 1.1 + 2.0)        # pixels
breath = 1 + 0.006 * np.sin(kx * 2 * math.pi / 3.6)
# nods: small downward dip at the start of loud syllables
nod = np.zeros(N)
peaks = [i for i in range(2, N - 2) if sm[i] > 0.9 and sm[i] >= sm[i - 1] and sm[i] >= sm[i + 1]]
last = -99
for p in peaks:
    if p - last < 12: continue
    last = p
    for j in range(p, min(p + 10, N)): nod[j] += 5 * math.sin(math.pi * (j - p) / 10)
px, py = C.get("pivot", [W / 2, H * 0.75])

ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                       "-i", "-", "-c:v", "libx264", "-crf", "12", "-preset", "medium", "-pix_fmt", "yuv420p",
                       f"{D}/talk/avatar.mp4"], stdin=subprocess.PIPE)
prev = None
for i in range(N):
    t = i / FPS
    o = sm[i]; ch, w = letter_at(t)
    if o < 0.18 or ch in ("m", "b", "p"): m = None
    elif o < 0.5: m = "small"
    elif ch in ("o", "u", "w"): m = "oh"
    elif ch in ("e", "i", "y"): m = "ee"
    else: m = "open"
    fr = base.copy()
    if m:
        fr = fr * (1 - mm) + shape[m] * mm
    if prev is not None and prev != m:   # one-frame soften between mouth shapes
        pv = base if prev is None else (base * (1 - mm) + shape[prev] * mm)
        fr = fr * 0.7 + (pv if prev else base) * 0.3
    prev = m
    b = blink_amt(t)
    if b: fr = fr * (1 - me * b) + blink * (me * b)
    M = cv2.getRotationMatrix2D((px, py), tilt[i], breath[i])
    M[0, 2] += dx[i]; M[1, 2] += dy[i] + nod[i]
    fr = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    ff.stdin.write(np.clip(fr, 0, 255).astype(np.uint8).tobytes())
ff.stdin.close(); ff.wait()
open_frac = np.mean([1 if x >= 0.18 else 0 for x in sm])
print(f"wrote {D}/talk/avatar.mp4  {N} frames  mouth-open {open_frac:.0%} of frames  blinks {len(blinks)}")
