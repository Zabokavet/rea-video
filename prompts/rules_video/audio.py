"""Build the soundtrack: narration on the timeline, dark music bed (ducked under the voice),
pen-scratch + page-turn foley, an opening low hit. Output: mix.wav (48k stereo, -14 LUFS)."""
import json, subprocess, sys
import numpy as np
from scipy.signal import butter, sosfilt

WD = sys.argv[1]
SR = 48000
TL = json.load(open(f"{WD}/timeline.json"))
END = TL["end"]
n = int(END * SR) + SR
r = np.random.default_rng(3)


def load(f):
    raw = subprocess.run(["ffmpeg", "-v", "quiet", "-i", f, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], "bandpass", fs=SR, output="sos"), x)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, "lowpass", fs=SR, output="sos"), x)


# ---------------------------------------------------------------- voice
voice = np.zeros(n, np.float32)
active = np.zeros(n, np.float32)
for s in TL["sent"]:
    a = load(s["file"])
    i = int(s["t0"] * SR)
    voice[i:i + len(a)] += a
    active[i:i + len(a)] = 1
# processing: rumble cut, gentle chest + presence lift, light compression via ffmpeg
np.asarray(voice, np.float32).tofile(f"{WD}/voice_raw.f32")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", f"{WD}/voice_raw.f32",
                "-af", "highpass=f=70,equalizer=f=130:t=q:w=1:g=2.5,equalizer=f=3200:t=q:w=1.2:g=2,"
                       "acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=2,alimiter=limit=0.9",
                "-f", "f32le", f"{WD}/voice_proc.f32"], check=True)
voice = np.fromfile(f"{WD}/voice_proc.f32", np.float32)[:n]
voice = np.pad(voice, (0, n - len(voice)))
voice /= np.abs(voice).max() + 1e-9
voice *= 0.85

# ---------------------------------------------------------------- music (D minor, slow, dark)
t = np.arange(n) / SR
f = lambda m: 440 * 2 ** ((m - 69) / 12)
music = np.zeros((n, 2), np.float32)


def saw(freq, det):
    ph = (t * freq * (1 + det)) % 1.0
    return 2 * ph - 1


# sub drone D1/D2 with slow swell
drone = 0.55 * np.sin(2 * np.pi * f(26) * t) + 0.35 * np.sin(2 * np.pi * f(38) * t + 0.3)
drone *= 0.75 + 0.25 * np.sin(2 * np.pi * t / 11.0)
music += drone[:, None] * 0.20
# pad chords every 8 s: Dm - Bb - Gm - A
chords = [[50, 53, 57], [46, 50, 53], [43, 46, 50], [45, 49, 52]]
CH = 8.0
pad = np.zeros((n, 2), np.float32)
for k in range(int(END / CH) + 2):
    notes = chords[k % 4]
    s0 = int(k * CH * SR); s1 = min(n, int((k + 1) * CH * SR + 2.0 * SR))
    if s0 >= n:
        break
    seg = slice(s0, s1)
    tt = t[seg] - k * CH
    env = np.clip(tt / 2.0, 0, 1) * np.clip((CH + 2.0 - tt) / 2.0, 0, 1)
    for ch, det in ((0, -0.003), (1, 0.003)):
        x = sum(saw(f(m), det)[seg] + saw(f(m), -det * 0.6)[seg] for m in notes)
        pad[seg, ch] += x * env * 0.06
for ch in range(2):
    pad[:, ch] = lp(pad[:, ch], 650, 4)
music += pad
# sparse dark piano motif (bell-like additive tone), one note every 2 s
motif = [74, 69, 65, 69, 70, 65, 62, 65, 67, 62, 58, 62, 69, 64, 61, 64]
for k in range(int(END / 2.0) + 1):
    m = motif[k % len(motif)]
    i0 = int((k * 2.0 + 0.05) * SR)
    L = int(3.2 * SR)
    if i0 >= n:
        break
    tt = np.arange(min(L, n - i0)) / SR
    tone = sum(a * np.sin(2 * np.pi * f(m) * h * (1 + 0.0004 * h * h) * tt) * np.exp(-tt * (1.6 + 1.1 * h))
               for h, a in ((1, 1.0), (2, 0.42), (3, 0.18), (4, 0.08)))
    tone *= np.clip(tt / 0.004, 0, 1)
    pan = 0.5 + 0.18 * np.sin(k)
    music[i0:i0 + len(tt), 0] += tone * 0.055 * (1 - pan) * 2
    music[i0:i0 + len(tt), 1] += tone * 0.055 * pan * 2
# slow heartbeat pulse (lub-dub) every 1.8 s, very low
for k in range(int(END / 1.8)):
    for off, amp in ((0.0, 1.0), (0.22, 0.6)):
        i0 = int((k * 1.8 + 0.9 + off) * SR); L = int(0.25 * SR)
        if i0 + L >= n:
            continue
        tt = np.arange(L) / SR
        thump = np.sin(2 * np.pi * (58 - 60 * tt) * tt) * np.exp(-tt * 22) * amp
        music[i0:i0 + L] += (thump * 0.16)[:, None]
# air
air = bp(r.standard_normal(n), 1800, 6000) * (0.004 + 0.003 * np.sin(2 * np.pi * t / 7))
music += np.stack([air, np.roll(air, 999)], 1)
# fade in/out
music *= np.clip(t / 0.6, 0, 1)[:, None] * np.clip((END - t) / 2.0, 0, 1)[:, None]

# duck under the voice (smooth envelope, ~-7 dB while talking)
k = int(0.12 * SR)
env = np.convolve(active, np.ones(k) / k, mode="same")
env = np.convolve(env, np.ones(k) / k, mode="same")
music *= (1 - 0.55 * env)[:, None]

# ---------------------------------------------------------------- foley
fx = np.zeros((n, 2), np.float32)
# opening low hit under the hook
L = int(2.2 * SR); tt = np.arange(L) / SR
hit = np.sin(2 * np.pi * (48 - 14 * tt) * tt) * np.exp(-tt * 2.2) * 0.55 + lp(r.standard_normal(L), 160) * np.exp(-tt * 9) * 0.5
fx[:L] += hit[:, None] * 0.9
# page turns: two swishes (lift + flip), panned right -> left
for tr in TL["turns"]:
    i0 = int((tr["t0"] - 0.05) * SR); L = int(0.95 * SR); tt = np.arange(L) / SR
    nz = bp(r.standard_normal(L), 700, 5500)
    e = 0.6 * np.exp(-((tt - 0.12) / 0.06) ** 2) + 1.0 * np.exp(-((tt - 0.45) / 0.13) ** 2) + 0.25 * np.exp(-((tt - 0.72) / 0.05) ** 2)
    pan = np.clip(1 - tt / 0.9, 0, 1)
    sw = nz * e * 0.22
    fx[i0:i0 + L, 0] += sw * (1 - pan * 0.6)
    fx[i0:i0 + L, 1] += sw * (0.4 + pan * 0.6)
# pen scratch while underlining (soft ballpoint friction, follows each spoken word)
scr = bp(r.standard_normal(n), 2500, 7500, 2)
grain = 0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 37 * t + 3 * np.sin(2 * np.pi * 3 * t)))
pen_env = np.zeros(n, np.float32)
for s in TL["sent"]:
    for w in s["words"]:
        a, b = int((s["t0"] + w["s"]) * SR), int((s["t0"] + w["e"]) * SR)
        pen_env[a:b] = 1
k = int(0.03 * SR)
pen_env = np.convolve(pen_env, np.ones(k) / k, mode="same")
fx += (scr * grain * pen_env * 0.016)[:, None]

# ---------------------------------------------------------------- mix + loudness
mix = voice[:, None] * 1.0 + music * 0.55 + fx
mix = mix[: int(END * SR)]
mix.astype(np.float32).tofile(f"{WD}/mix_raw.f32")
for name, sig in (("voice_only", voice[: int(END * SR), None] * np.ones((1, 2))), ("music_only", music[: int(END * SR)] * 0.55)):
    sig.astype(np.float32).tofile(f"{WD}/{name}.f32")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", f"{WD}/{name}.f32", f"{WD}/{name}.wav"], check=True)
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", f"{WD}/mix_raw.f32",
                "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", str(SR), f"{WD}/mix.wav"], check=True)
print("mix.wav written", END)
