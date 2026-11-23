"""Narration (one fixed voice for all 5 videos) + shared ambient pad + timeline."""
import json, os, subprocess, sys, wave
import numpy as np

SR = 48000
TARGET = 65.0
LEAD = 0.9      # silence before first line
TAIL = 2.2      # hold after last line
PMIN, PMAX = 0.55, 1.15
VERIFY = True

def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def read_wav(p):
    out = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(out, dtype=np.float32).copy()

def write_wav(p, x, ch=1):
    x = np.clip(x, -1, 1)
    pcm = (x * 32767).astype(np.int16)
    with wave.open(p, "wb") as w:
        w.setnchannels(ch); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())

# pronunciation helpers (only affect what the TTS engine reads, never the on-screen text)
TTS_FIX = {
    "soulmate": "soul mate",
    "Love that is real can wait.": "Love, that is real, can wait.",
}


def tts_text(line):
    for k, v in TTS_FIX.items():
        line = line.replace(k, v)
    return line.replace(" — ", ", ").replace("—", ", ")


_ASR = None
NUMS = {"1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six", "7": "seven",
        "8": "eight", "9": "nine", "10": "ten"}


def _norm(s):
    import re
    s = s.lower().replace("soul mate", "soulmate").replace("soul-mate", "soulmate")
    toks = re.findall(r"[a-z0-9']+", s)
    return [NUMS.get(t, t) for t in toks]


def asr_score(x, ref):
    """Word-level similarity between what a speech recognizer hears and the script line."""
    global _ASR
    import difflib
    if _ASR is None:
        from faster_whisper import WhisperModel
        _ASR = WhisperModel("small.en", device="cpu", compute_type="int8")
    y = x[::3].astype(np.float32)  # 48k -> 16k
    segs, _ = _ASR.transcribe(y, beam_size=5, language="en")
    hyp = " ".join(s.text for s in segs)
    return difflib.SequenceMatcher(None, _norm(ref), _norm(hyp)).ratio(), hyp

def trim(x, thr=0.004):
    idx = np.where(np.abs(x) > thr)[0]
    if len(idx) == 0:
        return x
    a = max(0, idx[0] - int(0.03 * SR)); b = min(len(x), idx[-1] + int(0.08 * SR))
    return x[a:b]

def synth_line(text, out, voice, ls):
    raw = out + ".raw.wav"
    p = subprocess.run([sys.executable, "-m", "piper", "-m", voice, "-f", raw,
                        "--length-scale", str(ls), "--sentence-silence", "0.4",
                        "--noise-scale", "0.55", "--noise-w-scale", "0.7"],
                       input=tts_text(text).encode(), check=True, capture_output=True)
    # deeper, warmer: pitch down ~1.6 semitones with formants preserved, low shelf, gentle comp
    run(["ffmpeg", "-y", "-i", raw, "-af",
         "aresample=48000,rubberband=pitch=0.912:formant=preserved:pitchq=quality,"
         "lowshelf=g=3.5:f=140,equalizer=f=3200:t=q:w=1.2:g=-1.5,highpass=f=60,"
         "acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120",
         "-ac", "1", "-ar", str(SR), out])
    os.remove(raw)
    x = trim(read_wav(out))
    return x

def pad(duration, seed=7):
    """Soft low ambient pad (same for all videos): Dm9-ish chord, slow swells."""
    rng = np.random.default_rng(seed)
    n = int(duration * SR); t = np.arange(n) / SR
    notes = [73.42, 110.0, 146.83, 174.61, 220.0, 164.81]
    L = np.zeros(n); R = np.zeros(n)
    for i, f in enumerate(notes):
        for det in (-0.12, 0.0, 0.13):
            ph = rng.uniform(0, 2 * np.pi)
            amp = (0.9 if f < 150 else 0.5) * (1 + 0.35 * np.sin(2 * np.pi * (0.03 + 0.011 * i) * t + ph))
            s = np.sin(2 * np.pi * (f + det) * t + ph) + 0.18 * np.sin(2 * np.pi * 2 * (f + det) * t + ph)
            pan = 0.5 + 0.35 * np.sin(ph)
            L += amp * s * (1 - pan); R += amp * s * pan
    # airy filtered noise
    noise = rng.standard_normal(n)
    k = np.ones(400) / 400
    nz = np.convolve(noise, k, mode="same") * 6
    L += nz * 0.25; R += np.roll(nz, 900) * 0.25
    env = np.minimum(1, t / 3.0) * np.minimum(1, (duration - t) / 3.5)
    L *= env; R *= env
    m = max(np.abs(L).max(), np.abs(R).max())
    return np.stack([L, R], 1) / m * 0.5

def build(video, outdir, voice):
    os.makedirs(outdir, exist_ok=True)
    lines = video["lines"]
    ls = 1.18
    for attempt in range(6):
        clips = []
        for i, l in enumerate(lines):
            best = None
            for k in range(8):
                c = synth_line(l, os.path.join(outdir, f"line{i:02d}.wav"), voice, ls)
                sc, hyp = asr_score(c, l) if VERIFY else (1.0, "")
                if best is None or sc > best[0]:
                    best = (sc, c, hyp)
                if sc >= 0.999:
                    break
            if best[0] < 0.999:
                print(f"    line {i} best ASR match {best[0]:.3f}: {best[2]!r}", flush=True)
            clips.append(best[1])
        speech = sum(len(c) for c in clips) / SR
        p = (TARGET - LEAD - TAIL - speech) / (len(lines) - 1)
        print(f"  ls={ls:.3f} speech={speech:.2f}s pause={p:.2f}s", flush=True)
        if PMIN <= p <= PMAX:
            break
        # adjust speed so the pause lands mid-range
        want = TARGET - LEAD - TAIL - 0.8 * (len(lines) - 1)
        ls = ls * want / speech
    p = min(max(p, PMIN), PMAX)
    timeline = []
    t = LEAD
    voice_track = np.zeros(int((TARGET + 1) * SR), dtype=np.float32)
    for i, c in enumerate(clips):
        a = int(t * SR)
        voice_track[a:a + len(c)] += c
        timeline.append({"start": round(t, 3), "end": round(t + len(c) / SR, 3), "text": lines[i]})
        t += len(c) / SR + (p if i < len(clips) - 1 else 0)
    total = max(TARGET, t + TAIL)
    voice_track = voice_track[:int(total * SR)]
    write_wav(os.path.join(outdir, "voice.wav"), voice_track)
    write_wav(os.path.join(outdir, "pad.wav"), pad(total).reshape(-1), ch=2)
    # loudness: voice -15 LUFS, pad ~ -36 LUFS (well under voice), final -14 LUFS
    run(["ffmpeg", "-y", "-i", os.path.join(outdir, "voice.wav"), "-i", os.path.join(outdir, "pad.wav"),
         "-filter_complex",
         "[0:a]loudnorm=I=-15:TP=-2:LRA=9,aformat=channel_layouts=stereo[v];"
         "[1:a]loudnorm=I=-24:TP=-6,volume=-12dB,aformat=channel_layouts=stereo[m];"
         "[v][m]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.89",
         "-ar", str(SR), os.path.join(outdir, "mix.wav")])
    meta = {"duration": round(total, 3), "length_scale": ls, "pause": p, "lines": timeline}
    with open(os.path.join(outdir, "timeline.json"), "w") as f:
        json.dump(meta, f, indent=2)
    return meta
