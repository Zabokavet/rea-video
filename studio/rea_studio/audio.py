"""Music, sound effects, mixing and mastering - all local.

Music engines
  score     Built-in procedural composer (this file). Chord progressions, pads, piano arpeggios, bass, drums,
            convolution reverb, intro/build/outro arrangement matched to video length. 100% original output,
            no licence restrictions - safe for monetised videos.
  musicgen  Meta MusicGen-small via transformers (weights CC-BY-NC-4.0: NON-COMMERCIAL). Text-prompted, more
            "produced" sound. ~3-5 min of CPU per 30 s; looped with crossfades to length.
SFX
  Procedural one-shots and beds: whoosh, impact, boom, riser, hit, click, pop, ding, shutter, typewriter,
  heartbeat, glitch, wind, rain, crowd, fire, ocean, city. Generated per render (no stock library needed).
Mix
  Voice-keyed ducking of music, SFX bus, stereo widening of music, EBU R128 two-pass loudness normalisation
  (-14 LUFS for YouTube/Shorts/TikTok, -16 for documentaries/podcasts), true-peak limiting at -1.5 dBTP.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

from .util import log, run

SR = 48000
NOTE = {n: i for i, n in enumerate(["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"])}


def midi_hz(m: float) -> float:
    return 440.0 * 2 ** ((m - 69) / 12)


# ------------------------------------------------------------------------- moods
# progression = scale degrees (1-based) of chord roots; quality from scale. drums: none|soft|pulse|epic|lofi|four
MOODS = {
    "epic":          dict(bpm=84, key="D", minor=True, prog=[1, 6, 3, 7], drums="epic", arp=True, bright=0.6),
    "historical":    dict(bpm=72, key="D", minor=True, prog=[1, 4, 6, 5], drums="taiko", arp=False, bright=0.45),
    "documentary":   dict(bpm=70, key="C", minor=False, prog=[6, 4, 1, 5], drums="none", arp=True, bright=0.45),
    "inspirational": dict(bpm=96, key="G", minor=False, prog=[1, 5, 6, 4], drums="soft", arp=True, bright=0.7),
    "emotional":     dict(bpm=66, key="A", minor=True, prog=[1, 6, 3, 7], drums="none", arp=True, bright=0.4),
    "tension":       dict(bpm=90, key="E", minor=True, prog=[1, 1, 6, 5], drums="pulse", arp=False, bright=0.35),
    "mystery":       dict(bpm=76, key="F#", minor=True, prog=[1, 6, 4, 5], drums="none", arp=True, bright=0.3),
    "calm":          dict(bpm=68, key="F", minor=False, prog=[1, 3, 4, 1], drums="none", arp=True, bright=0.5),
    "corporate":     dict(bpm=110, key="C", minor=False, prog=[1, 5, 6, 4], drums="four", arp=True, bright=0.8),
    "news":          dict(bpm=120, key="A", minor=True, prog=[1, 1, 6, 7], drums="pulse", arp=True, bright=0.75),
    "lofi":          dict(bpm=82, key="D#", minor=False, prog=[2, 5, 1, 6], drums="lofi", arp=True, bright=0.35),
    "energetic":     dict(bpm=128, key="B", minor=True, prog=[1, 6, 3, 7], drums="four", arp=True, bright=0.85),
    "uplifting":     dict(bpm=100, key="D", minor=False, prog=[4, 1, 5, 6], drums="soft", arp=True, bright=0.75),
    "financial":     dict(bpm=104, key="A", minor=False, prog=[1, 5, 6, 4], drums="soft", arp=True, bright=0.7),
}
MOOD_ALIASES = {"cinematic": "epic", "sad": "emotional", "suspense": "tension", "dark": "tension", "happy": "uplifting",
                "sports": "energetic", "ambient": "calm", "tech": "corporate", "money": "financial", "history": "historical",
                "motivational": "inspirational", "ad": "corporate", "commercial": "corporate", "horror": "mystery"}

_MAJ, _MIN = [0, 2, 4, 5, 7, 9, 11], [0, 2, 3, 5, 7, 8, 10]


def _chord(deg: int, root_midi: int, minor: bool) -> list[int]:
    sc = _MIN if minor else _MAJ
    i = deg - 1
    return [root_midi + sc[(i + k) % 7] + 12 * ((i + k) // 7) for k in (0, 2, 4, 6)]  # 7th chord


def _adsr(n: int, a: float, r: float, sus: float = 1.0) -> np.ndarray:
    env = np.full(n, sus, np.float32)
    na, nr = min(n, int(a * SR)), min(n, int(r * SR))
    if na:
        env[:na] = np.linspace(0, sus, na)
    if nr:
        env[-nr:] *= np.linspace(1, 0, nr)
    return env


def _saw(f: float, n: int, detune: float = 0.0, max_h: int = 24) -> np.ndarray:
    t = np.arange(n) / SR
    out = np.zeros(n, np.float32)
    ff = f * (1 + detune)
    for h in range(1, min(max_h, int(9000 / ff)) + 1):
        out += np.sin(2 * np.pi * ff * h * t + h * 0.7).astype(np.float32) / h
    return out


def _lp(x, fc, order=2):
    return sosfilt(butter(order, min(fc, SR / 2 - 100), "lowpass", fs=SR, output="sos"), x)


def _hp(x, fc, order=2):
    return sosfilt(butter(order, fc, "highpass", fs=SR, output="sos"), x)


def _pad(chord: list[int], n: int, bright: float) -> np.ndarray:
    x = np.zeros(n, np.float32)
    for m in chord:
        f = midi_hz(m)
        for d in (-0.006, 0.0, 0.0065):
            x += _saw(f, n, d, 12)
    x = _lp(x, 600 + 2200 * bright)
    return (x * _adsr(n, 0.6, 0.8, 1.0) / (len(chord) * 3)).astype(np.float32)


def _pluck(f: float, n: int, decay: float = 1.2) -> np.ndarray:
    t = np.arange(n) / SR
    x = sum(np.sin(2 * np.pi * f * h * t) * (0.6 ** (h - 1)) * np.exp(-t * decay * h) for h in range(1, 6))
    return (x * np.minimum(1, t / 0.004)).astype(np.float32)


def _kick(n, f0=110, f1=42, dec=7):
    t = np.arange(n) / SR
    ph = 2 * np.pi * (f1 * t + (f0 - f1) * (1 - np.exp(-t * 30)) / 30)
    return (np.sin(ph) * np.exp(-t * dec)).astype(np.float32)


def _noise_hit(n, dec, hp=6000, rng=None):
    rng = rng or np.random.default_rng(0)
    t = np.arange(n) / SR
    return (_hp(rng.standard_normal(n), hp) * np.exp(-t * dec)).astype(np.float32)


def _reverb(x: np.ndarray, seconds=2.6, wet=0.32, seed=1) -> np.ndarray:
    """Stereo convolution reverb from decaying filtered noise. x: (n,) or (n,2) -> (n,2)."""
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    irs = []
    for _ in range(2):
        ir = rng.standard_normal(n) * np.exp(-t * 6.9 / seconds)
        irs.append(_lp(ir, 5000) / math.sqrt(n) * 4)
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    wet_sig = np.stack([fftconvolve(x[:, c], irs[c])[: len(x)] for c in range(2)], 1)
    return ((1 - wet) * x + wet * wet_sig).astype(np.float32)


def compose(duration: float, mood: str = "documentary", seed: int = 0, intensity: float = 1.0) -> np.ndarray:
    """Procedural score, stereo float32 @48k, exactly `duration` seconds, with intro/build/outro."""
    mood = MOOD_ALIASES.get(mood, mood)
    m = MOODS.get(mood, MOODS["documentary"])
    rng = np.random.default_rng(seed)
    root = 48 + NOTE[m["key"]]  # C3-ish
    beat = 60.0 / m["bpm"]
    bar_n = int(4 * beat * SR)
    total = int(duration * SR)
    bars = math.ceil(total / bar_n) + 1
    chords = [_chord(d, root, m["minor"]) for d in m["prog"]]
    # pre-render each chord's parts once
    pads = [_pad([c[0] - 12] + c, bar_n + int(0.8 * SR), m["bright"]) for c in chords]
    L = bars * bar_n + SR * 3
    pad_bus = np.zeros(L, np.float32)
    arp_bus = np.zeros(L, np.float32)
    bass_bus = np.zeros(L, np.float32)
    drum_bus = np.zeros(L, np.float32)
    intro_bars = 2 if bars > 6 else 1
    outro_start = max(intro_bars + 1, bars - 2)
    step = beat / 2  # eighth notes
    pattern = [0, 2, 1, 3, 2, 1, 3, 2] if rng.random() > 0.5 else [0, 1, 2, 3, 2, 3, 1, 2]
    for b in range(bars):
        ci = b % len(chords)
        s = b * bar_n
        p = pads[ci]
        pad_bus[s:s + len(p)] += p
        section = "intro" if b < intro_bars else ("outro" if b >= outro_start else "main")
        if m["arp"] and section != "intro":
            for k in range(8):
                note = chords[ci][pattern[k]] + 12
                if rng.random() < 0.12:
                    continue  # humanised gaps
                n = int(beat * 2 * SR)
                st = s + int(k * step * SR + rng.normal(0, 0.004) * SR)
                st = max(st, 0)
                pl = _pluck(midi_hz(note), n, 2.2 - m["bright"]) * (0.8 + 0.2 * rng.random())
                arp_bus[st:st + n] += pl[: max(0, min(n, L - st))]
        if section != "intro":
            n = bar_n
            t = np.arange(n) / SR
            f = midi_hz(chords[ci][0] - 12)
            bass = (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)) * _adsr(n, 0.02, 0.3, 0.9)
            bass_bus[s:s + n] += np.tanh(bass * 1.5).astype(np.float32) * 0.6
        dr = m["drums"]
        if dr != "none" and section == "main":
            for k in range(4):
                bt = s + int(k * beat * SR)
                if dr in ("four", "epic", "soft", "lofi") and (dr == "four" or k in (0, 2)):
                    kk = _kick(int(0.5 * SR)) * (0.9 if dr != "soft" else 0.5)
                    drum_bus[bt:bt + len(kk)] += kk[: L - bt]
                if dr in ("four", "soft", "lofi") and k in (1, 3):
                    sn = _noise_hit(int(0.3 * SR), 18, 1800, rng) * (0.35 if dr != "soft" else 0.18)
                    drum_bus[bt:bt + len(sn)] += sn[: L - bt]
                if dr in ("four", "pulse", "lofi", "soft"):
                    for h in (0, 0.5):
                        ht = bt + int(h * beat * SR)
                        hh = _noise_hit(int(0.08 * SR), 60, 7000, rng) * 0.12
                        drum_bus[ht:ht + len(hh)] += hh[: L - ht]
                if dr == "pulse":
                    kk = _kick(int(0.3 * SR), 70, 40, 14) * 0.55
                    drum_bus[bt:bt + len(kk)] += kk[: L - bt]
                if dr in ("epic", "taiko") and (k == 0 or (k == 2 and b % 2) or (dr == "taiko" and k == 3 and b % 2)):
                    tk = _kick(int(1.0 * SR), 90, 55, 4.5) * 0.9
                    tk[: int(0.4 * SR)] += _noise_hit(int(0.4 * SR), 9, 300, rng) * 0.3
                    drum_bus[bt:bt + len(tk)] += tk[: L - bt]
    # arrangement fades + build
    env = np.ones(L, np.float32)
    env[: intro_bars * bar_n] = np.linspace(0.35, 1, intro_bars * bar_n)
    mix_mono_pad = pad_bus * 0.55
    music = np.stack([mix_mono_pad, mix_mono_pad], 1)
    # stereo: arp slightly right, bass center, drums center
    music[:, 0] += arp_bus * 0.32
    music[:, 1] += arp_bus * 0.42
    music += (bass_bus * 0.45)[:, None]
    music += (drum_bus * 0.55 * intensity)[:, None]
    music = _reverb(music, 2.8 if mood in ("epic", "historical", "emotional", "documentary") else 1.6, 0.3, seed)
    music *= env[:, None]
    music = music[:total]
    fade = min(int(3 * SR), total // 4)
    music[-fade:] *= np.linspace(1, 0, fade)[:, None] ** 1.5
    music[: int(0.05 * SR)] *= np.linspace(0, 1, int(0.05 * SR))[:, None]
    peak = np.abs(music).max()
    return (music / peak * 0.8).astype(np.float32) if peak else music


_musicgen = None


def musicgen(duration: float, prompt: str, seed: int = 0, segment: float = 30.0) -> np.ndarray:
    """MusicGen-small (CC-BY-NC). Generates <=30 s then loops with 3 s crossfades."""
    global _musicgen
    import torch
    from transformers import AutoProcessor, MusicgenForConditionalGeneration
    if _musicgen is None:
        log("loading MusicGen-small (non-commercial licence; ~1.2 GB)")
        _musicgen = (AutoProcessor.from_pretrained("facebook/musicgen-small"),
                     MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small").eval())
    proc, model = _musicgen
    torch.manual_seed(seed)
    seg = min(segment, duration + 1)
    inputs = proc(text=[prompt], padding=True, return_tensors="pt")
    with torch.no_grad():
        audio = model.generate(**inputs, do_sample=True, guidance_scale=3.0, max_new_tokens=int(seg * 50))
    sr = model.config.audio_encoder.sampling_rate
    from .tts import _resample
    x = _resample(audio[0, 0].numpy(), sr)
    return _loop_to(np.stack([x, x], 1), duration)


def _loop_to(x: np.ndarray, duration: float, xfade: float = 3.0) -> np.ndarray:
    total = int(duration * SR)
    if len(x) >= total:
        out = x[:total].copy()
    else:
        xf = int(min(xfade, len(x) / 4 / SR) * SR)
        out = x.copy()
        while len(out) < total:
            ramp = np.linspace(0, 1, xf)[:, None]
            out[-xf:] = out[-xf:] * (1 - ramp) + x[:xf] * ramp
            out = np.concatenate([out, x[xf:]])
        out = out[:total]
    fade = min(int(3 * SR), total // 4)
    out[-fade:] *= np.linspace(1, 0, fade)[:, None]
    return out.astype(np.float32)


# ------------------------------------------------------------------------- SFX
def sfx(name: str, seed: int = 0, length: float | None = None) -> np.ndarray:
    """Procedural sound effect -> stereo float32 @48k."""
    rng = np.random.default_rng(seed)
    name = name.lower().replace("-", "_")
    def N(s): return int(s * SR)  # noqa: E731
    if name in ("whoosh", "swoosh", "transition"):
        n = N(length or 0.9)
        t = np.linspace(0, 1, n)
        x = rng.standard_normal(n)
        fc = 300 + 5000 * np.sin(np.pi * t) ** 2
        out = np.zeros(n)
        for i in range(0, n, 1024):  # time-varying band-pass
            seg = slice(i, min(n, i + 1024))
            out[seg] = sosfilt(butter(2, [max(80, fc[i] * 0.5), min(20000, fc[i] * 1.5)], "bandpass", fs=SR,
                                      output="sos"), x[max(0, i - 2048):seg.stop])[-(seg.stop - seg.start):]
        env = np.sin(np.pi * t) ** 1.5
        pan = np.linspace(-0.8, 0.8, n)
        y = out * env
        st = np.stack([y * (1 - pan) / 2, y * (1 + pan) / 2], 1)
    elif name in ("impact", "hit", "boom", "trailer_hit"):
        n = N(length or (2.5 if name != "hit" else 0.6))
        y = _kick(n, 80 if name != "hit" else 160, 30, 2.2 if name == "boom" else 4) + \
            _noise_hit(n, 6 if name != "hit" else 25, 200, rng) * 0.5
        st = _reverb(np.tanh(y * 2) * 0.7, 3.0, 0.4, seed)
    elif name == "riser":
        n = N(length or 3.0)
        t = np.arange(n) / SR
        f = 200 * 2 ** (t / t[-1] * 3)
        y = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.4 + _hp(rng.standard_normal(n), 2000) * 0.25 * (t / t[-1])
        y *= (t / t[-1]) ** 2
        st = _reverb(y, 2.0, 0.3, seed)
    elif name in ("click", "ui", "tick"):
        n = N(0.05)
        y = np.sin(2 * np.pi * 2200 * np.arange(n) / SR) * np.exp(-np.arange(n) / SR * 120)
        st = np.stack([y, y], 1)
    elif name in ("pop", "bubble"):
        n = N(0.15)
        t = np.arange(n) / SR
        y = np.sin(2 * np.pi * (300 + 900 * np.exp(-t * 40)) * t) * np.exp(-t * 30)
        st = np.stack([y, y], 1)
    elif name in ("ding", "bell", "cash", "notification"):
        n = N(1.6)
        t = np.arange(n) / SR
        y = sum(np.sin(2 * np.pi * 1318.5 * r * t) * a * np.exp(-t * d) for r, a, d in
                [(1, 1, 3), (2.76, 0.4, 5), (5.4, 0.2, 8), (1.5, 0.3, 4)])
        if name == "cash":
            y += _noise_hit(n, 20, 3000, rng) * 0.3
        st = _reverb(y * 0.5, 1.5, 0.25, seed)
    elif name in ("shutter", "camera"):
        n = N(0.25)
        y = _noise_hit(n, 45, 1500, rng)
        y[N(0.09):] += _noise_hit(n - N(0.09), 60, 2500, rng) * 0.8
        st = np.stack([y, y], 1)
    elif name == "typewriter":
        n = N(length or 2.0)
        y = np.zeros(n)
        tpos = 0
        while tpos < n - N(0.05):
            k = _noise_hit(N(0.04), 120, 1200, rng) * (0.6 + 0.4 * rng.random())
            y[tpos:tpos + len(k)] += k
            tpos += int(N(0.09) * (0.6 + rng.random()))
        st = np.stack([y, y], 1)
    elif name == "heartbeat":
        n = N(length or 3.0)
        y = np.zeros(n)
        for s in np.arange(0, length or 3.0, 0.9):
            for o, a in ((0, 1), (0.22, 0.7)):
                i = N(s + o)
                k = _kick(N(0.25), 60, 35, 18) * a
                y[i:i + len(k)] += k[: max(0, n - i)]
        st = np.stack([y, y], 1)
    elif name == "glitch":
        n = N(length or 0.5)
        y = np.repeat(rng.standard_normal(n // 200 + 1), 200)[:n] * (rng.random(n) > 0.3)
        y = _hp(y, 500) * 0.6
        st = np.stack([y, np.roll(y, 300)], 1)
    elif name in ("wind", "rain", "crowd", "fire", "ocean", "waves", "city", "room_tone", "jungle", "forest"):
        n = N(length or 10)
        t = np.arange(n) / SR
        w = rng.standard_normal((n, 2))
        if name == "wind":
            lfo = 0.5 + 0.5 * np.sin(2 * np.pi * 0.13 * t + rng.random() * 6) * np.sin(2 * np.pi * 0.051 * t)
            st = np.stack([_lp(w[:, c], 500) for c in range(2)], 1) * (0.3 + 0.7 * lfo[:, None])
        elif name == "rain":
            st = np.stack([_hp(_lp(w[:, c], 9000), 900) for c in range(2)], 1) * 0.35
            drops = (rng.random((n, 2)) > 0.9993) * rng.standard_normal((n, 2)) * 3
            st += np.stack([_hp(drops[:, c], 2000) for c in range(2)], 1)
        elif name in ("ocean", "waves"):
            swell = (0.5 + 0.5 * np.sin(2 * np.pi * t / 7.5)) ** 2
            st = np.stack([_lp(w[:, c], 1400) for c in range(2)], 1) * (0.15 + 0.85 * swell[:, None])
        elif name == "fire":
            crack = (rng.random((n, 2)) > 0.9995) * rng.standard_normal((n, 2)) * 4
            st = np.stack([_lp(w[:, c], 350) * 0.6 + _hp(crack[:, c], 1500) for c in range(2)], 1)
        elif name in ("jungle", "forest"):
            st = np.stack([_lp(w[:, c], 2500) * 0.15 for c in range(2)], 1)
            for _ in range(int((length or 10) * 0.8)):  # bird chirps
                i = rng.integers(0, max(1, n - N(0.3)))
                f0 = rng.uniform(2500, 5000)
                tt = np.arange(N(0.12)) / SR
                ch = np.sin(2 * np.pi * (f0 + 1500 * np.sin(2 * np.pi * 30 * tt)) * tt) * np.sin(np.pi * tt / tt[-1]) * 0.3
                st[i:i + len(ch), rng.integers(0, 2)] += ch
        else:  # crowd / city / room_tone: band-limited murmur
            band = {"crowd": (250, 2500), "city": (60, 1200), "room_tone": (60, 400)}[name]
            st = np.stack([sosfilt(butter(2, band, "bandpass", fs=SR, output="sos"), w[:, c]) for c in range(2)], 1)
            st *= (0.7 + 0.3 * np.sin(2 * np.pi * 0.3 * t + rng.random())[:, None])
        f = min(N(1.0), n // 3)
        st[:f] *= np.linspace(0, 1, f)[:, None]
        st[-f:] *= np.linspace(1, 0, f)[:, None]
    else:
        raise ValueError(f"unknown sfx '{name}'. Known: " + ", ".join(SFX_NAMES))
    st = np.asarray(st, np.float32)
    peak = np.abs(st).max()
    return st / peak * 0.8 if peak else st


SFX_NAMES = ["whoosh", "impact", "boom", "hit", "riser", "click", "pop", "ding", "cash", "shutter", "typewriter",
             "heartbeat", "glitch", "wind", "rain", "crowd", "fire", "ocean", "city", "room_tone", "jungle"]
AMBIENCES = {"wind", "rain", "crowd", "fire", "ocean", "waves", "city", "room_tone", "jungle", "forest"}


# ------------------------------------------------------------------------- mixing
def place(bus: np.ndarray, clip: np.ndarray, at: float, gain_db: float = 0.0) -> None:
    i = int(at * SR)
    if clip.ndim == 1:
        clip = np.stack([clip, clip], 1)
    if i >= len(bus):
        return
    n = min(len(clip), len(bus) - i)
    bus[i:i + n] += clip[:n] * (10 ** (gain_db / 20))


def duck(music: np.ndarray, voice: np.ndarray, depth_db: float = 11.0, attack: float = 0.08, release: float = 0.6) -> np.ndarray:
    """Sidechain-style ducking: music drops by depth_db while the narrator speaks."""
    v = np.abs(voice if voice.ndim == 1 else voice.mean(1))
    hop = 480
    frames = np.array([v[i:i + hop].max() if i < len(v) else 0 for i in range(0, len(music), hop)])
    active = (frames > 0.02).astype(float)
    g = np.zeros_like(active)
    a_c, r_c = math.exp(-hop / (attack * SR)), math.exp(-hop / (release * SR))
    s = 0.0
    for i, x in enumerate(active):
        s = (a_c if x > s else r_c) * s + (1 - (a_c if x > s else r_c)) * x
        g[i] = s
    gain = 10 ** (-depth_db * np.repeat(g, hop)[: len(music)] / 20)
    return (music * gain[:, None]).astype(np.float32)


def mixdown(voice: np.ndarray, music: np.ndarray | None, sfx_bus: np.ndarray | None, music_db: float = -18.0,
            sfx_db: float = -8.0, duck_db: float = 11.0) -> np.ndarray:
    n = len(voice)
    out = np.stack([voice, voice], 1).astype(np.float32) if voice.ndim == 1 else voice.copy()
    if music is not None:
        m = np.zeros((n, 2), np.float32)
        m[: min(n, len(music))] = music[:n]
        out += duck(m, voice, duck_db) * 10 ** (music_db / 20)
    if sfx_bus is not None:
        out += sfx_bus[:n] * 10 ** (sfx_db / 20)
    peak = np.abs(out).max()
    if peak > 0.98:
        out = np.tanh(out / peak * 1.2) / np.tanh(1.2) * 0.98  # soft clip safety; loudnorm sets final level
    return out


def loudnorm(src: Path, dst: Path, lufs: float = -14.0, tp: float = -1.5, lra: float = 11.0) -> dict:
    """Two-pass EBU R128 normalisation with ffmpeg. Returns measured stats of the output."""
    flt = f"loudnorm=I={lufs}:TP={tp}:LRA={lra}"
    p = run(["ffmpeg", "-hide_banner", "-i", src, "-af", flt + ":print_format=json", "-f", "null", "-"])
    meas = json.loads(re.findall(r"\{[^{}]+\}", p.stderr.decode())[-1])
    second = (f"{flt}:measured_I={meas['input_i']}:measured_TP={meas['input_tp']}:measured_LRA={meas['input_lra']}"
              f":measured_thresh={meas['input_thresh']}:offset={meas['target_offset']}:linear=true")
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", src, "-af", second + ",alimiter=limit=0.84:level=false",
         "-ar", str(SR), dst])
    return measure(dst)


def measure(path: Path) -> dict:
    p = run(["ffmpeg", "-hide_banner", "-i", path, "-af", "loudnorm=print_format=json", "-f", "null", "-"])
    m = json.loads(re.findall(r"\{[^{}]+\}", p.stderr.decode())[-1])
    return {"lufs": float(m["input_i"]), "true_peak": float(m["input_tp"]), "lra": float(m["input_lra"])}


def save(path: Path, x: np.ndarray, sr: int = SR) -> Path:
    import soundfile as sf
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), x, sr, subtype="PCM_24")
    return path
