"""Local text-to-speech with sentence-level timing.

Every engine returns mono float32 at 48 kHz plus per-sentence (start, end, text) timings, which is
what lets us sync subtitles and scene cuts exactly to the narration without guessing.

Script markup understood in narration text:
  [pause 0.8]   insert 0.8 s of silence (also [pause=0.8], [breath])
  *word*        emphasis marker (stripped; Kokoro/Piper have no SSML, so emphasis comes from punctuation)
  ...           is kept: engines render it as a hesitation
"""
from __future__ import annotations

import re
import tempfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from . import languages as L
from .util import log, run, which

SR = 48000

# Delivery presets: speed multiplier, gap between sentences, gap at [paragraph]
DELIVERY = {
    "documentary": dict(speed=0.92, gap=0.42, para=0.9),
    "cinematic": dict(speed=0.88, gap=0.55, para=1.1),
    "conversational": dict(speed=1.04, gap=0.22, para=0.5),
    "news": dict(speed=1.02, gap=0.25, para=0.55),
    "energetic": dict(speed=1.12, gap=0.12, para=0.3),
    "calm": dict(speed=0.9, gap=0.5, para=1.0),
    "neutral": dict(speed=1.0, gap=0.3, para=0.7),
}


@dataclass
class Speech:
    audio: np.ndarray  # float32 mono @ SR
    sentences: list[tuple[float, float, str]]
    voice: L.Voice
    license: str

    @property
    def duration(self) -> float:
        return len(self.audio) / SR


LICENSES = {
    "kokoro": "Kokoro-82M, Apache-2.0 (commercial OK)",
    "piper": "Piper (GPL-3.0 engine); voice dataset licence per MODEL_CARD - check before commercial use",
    "mms": "Meta MMS-TTS, CC-BY-NC-4.0 (NON-COMMERCIAL ONLY)",
    "espeak": "eSpeak NG, GPL-3.0 (output audio is yours)",
}


def available_engines() -> set[str]:
    eng = set()
    try:
        import kokoro  # noqa: F401
        eng.add("kokoro")
    except Exception:
        pass
    try:
        import piper  # noqa: F401
        eng.add("piper")
    except Exception:
        pass
    try:
        import transformers  # noqa: F401
        import torch  # noqa: F401
        eng.add("mms")
    except Exception:
        pass
    if which("espeak-ng") or which("espeak"):
        eng.add("espeak")
    return eng


# ------------------------------------------------------------------ text handling
_PAUSE = re.compile(r"\[(?:pause[ =]?(\d+(?:\.\d+)?)|breath|paragraph)\]", re.I)
_SENT = re.compile(r"(?<=[.!?…»”\"])\s+(?=[^\s])|(?<=[.!?…])(?=[A-ZÀ-ÖØ-Þ¿¡«“\"])")


def split_script(text: str) -> list[tuple[str, float]]:
    """-> [(sentence, pause_after_seconds_or_-1_for_default)]"""
    out: list[tuple[str, float]] = []
    pos = 0
    for m in list(_PAUSE.finditer(text)) + [None]:
        chunk = text[pos:m.start()] if m else text[pos:]
        for s in _SENT.split(chunk.strip()):
            s = re.sub(r"\*(.+?)\*", r"\1", s).strip()
            if s:
                out.append((s, -1.0))
        if m:
            secs = float(m.group(1)) if m.group(1) else (0.35 if "breath" in m.group(0).lower() else -2.0)
            if out:
                out[-1] = (out[-1][0], secs)
            pos = m.end()
    return out


def _resample(x: np.ndarray, sr: int) -> np.ndarray:
    if sr == SR:
        return x.astype(np.float32)
    from math import gcd

    from scipy.signal import resample_poly
    g = gcd(SR, sr)
    return resample_poly(x, SR // g, sr // g).astype(np.float32)


def _trim(x: np.ndarray, thresh: float = 0.004) -> np.ndarray:
    idx = np.where(np.abs(x) > thresh)[0]
    if len(idx) == 0:
        return x
    a = max(0, idx[0] - int(0.02 * SR))
    b = min(len(x), idx[-1] + int(0.06 * SR))
    return x[a:b]


# ------------------------------------------------------------------ engines
_kokoro_cache: dict = {}
_piper_cache: dict = {}
_mms_cache: dict = {}


def _kokoro(text: str, voice: str, lang: L.Language, speed: float) -> np.ndarray:
    from kokoro import KPipeline
    lc = lang.kokoro_lang or "a"
    if voice.startswith("b"):
        lc = "b"
    if lc not in _kokoro_cache:
        _kokoro_cache[lc] = KPipeline(lang_code=lc, repo_id="hexgrad/Kokoro-82M")
    pipe = _kokoro_cache[lc]
    v = voice.replace("+", ",")  # "af_heart+af_bella" = averaged blend
    parts = [np.asarray(r.audio, dtype=np.float32) for r in pipe(text, voice=v, speed=speed, split_pattern=None)
             if r.audio is not None]
    return _resample(np.concatenate(parts) if parts else np.zeros(1, np.float32), 24000)


def _piper_model(voice_id: str) -> Path:
    from huggingface_hub import hf_hub_download
    code, name, quality = voice_id.rsplit("-", 2)[0], voice_id.split("-")[1], voice_id.split("-")[-1]
    fam = code.split("_")[0]
    base = f"{fam}/{code}/{name}/{quality}/{voice_id}"
    onnx = hf_hub_download("rhasspy/piper-voices", base + ".onnx")
    hf_hub_download("rhasspy/piper-voices", base + ".onnx.json")
    return Path(onnx)


def _piper(text: str, voice_id: str, speed: float, speaker: int | None = None) -> np.ndarray:
    from piper import PiperVoice
    if voice_id not in _piper_cache:
        _piper_cache[voice_id] = PiperVoice.load(str(_piper_model(voice_id)))
    pv = _piper_cache[voice_id]
    try:  # piper-tts >= 1.3
        from piper import SynthesisConfig
        cfg = SynthesisConfig(length_scale=1.0 / max(speed, 0.3), speaker_id=speaker)
        chunks = list(pv.synthesize(text, syn_config=cfg))
        sr = chunks[0].sample_rate if chunks else 22050
        audio = np.concatenate([c.audio_float_array for c in chunks]) if chunks else np.zeros(1, np.float32)
    except ImportError:  # older API: raw int16 stream
        sr = pv.config.sample_rate
        raw = b"".join(pv.synthesize_stream_raw(text, length_scale=1.0 / speed, speaker_id=speaker))
        audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
    return _resample(audio, sr)


def _mms(text: str, code: str, speed: float) -> np.ndarray:
    import torch
    from transformers import AutoTokenizer, VitsModel
    repo = f"facebook/mms-tts-{code}"
    if repo not in _mms_cache:
        _mms_cache[repo] = (VitsModel.from_pretrained(repo).eval(), AutoTokenizer.from_pretrained(repo))
    model, tok = _mms_cache[repo]
    model.speaking_rate = speed
    model.noise_scale = 0.6  # a little less "wobble" than default 0.667
    torch.manual_seed(0)
    # MMS vocab is lower-case letters only (Haitian keeps à è ò). Digits are spelled out first; commas are not in
    # the vocab, so we synthesise clause by clause and put the pauses back ourselves.
    from .textnorm import normalize
    clean = normalize(text, "ht" if code == "hat" else code).lower().replace("’", "'")
    sr = model.config.sampling_rate
    parts = []
    for clause in [c.strip() for c in re.split(r"[,;:—–()]", clean) if c.strip()]:
        with torch.no_grad():
            inp = tok(clause, return_tensors="pt")
            if inp["input_ids"].shape[-1] == 0:
                continue
            parts.append(_trim(model(**inp).waveform[0].numpy()))
        parts.append(np.zeros(int(0.16 * sr), np.float32))
    wav = np.concatenate(parts[:-1]) if parts else np.zeros(sr // 4, np.float32)
    return _resample(wav, sr)


def _espeak(text: str, voice: str, speed: float) -> np.ndarray:
    import soundfile as sf
    exe = which("espeak-ng") or which("espeak")
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "e.wav"
        run([exe, "-v", voice, "-s", str(int(150 * speed)), "-p", "45", "-w", out, text])
        a, sr = sf.read(out, dtype="float32")
    return _resample(a, sr)


def _synth_sentence(text: str, voice: L.Voice, lang: L.Language, speed: float) -> np.ndarray:
    if voice.engine == "kokoro":
        return _kokoro(text, voice.id, lang, speed)
    if voice.engine == "piper":
        spk = None
        vid = voice.id
        if ":" in vid:
            vid, s = vid.split(":")
            spk = int(s)
        return _piper(text, vid, speed, spk)
    if voice.engine == "mms":
        return _mms(text, voice.id, speed)
    if voice.engine == "espeak":
        return _espeak(text, voice.id, speed)
    raise ValueError(f"unknown TTS engine {voice.engine}")


def resolve_voice(lang_code: str, voice: str | None = "auto", gender: str | None = None,
                  engine: str | None = "auto", commercial: bool = False) -> tuple[L.Language, L.Voice]:
    lang = L.get(lang_code)
    avail = available_engines()
    if voice and voice != "auto":
        v = L.find_voice(voice.split(":")[0].split("+")[0])
        if v is None:  # free-form id, e.g. a piper voice not in the registry
            eng = engine if engine and engine != "auto" else ("piper" if "-" in voice else "kokoro")
            v = L.Voice(eng, voice, gender or "?")
        else:
            v = L.Voice(v.engine, voice, v.gender, v.accent, v.quality, v.note)
        if v.engine not in avail:
            raise RuntimeError(f"voice {voice} needs engine '{v.engine}', which is not installed")
        if commercial and v.engine == "mms":
            raise RuntimeError("MMS-TTS is CC-BY-NC (non-commercial); pick another voice or drop --commercial")
        return lang, v
    return lang, L.pick_voice(lang, gender, engine, commercial, avail)


def synthesize(text: str, lang_code: str = "en", voice: str | None = "auto", gender: str | None = None,
               delivery: str = "neutral", speed: float | None = None, engine: str | None = "auto",
               commercial: bool = False) -> Speech:
    lang, v = resolve_voice(lang_code, voice, gender, engine, commercial)
    d = DELIVERY.get(delivery, DELIVERY["neutral"])
    spd = (speed or 1.0) * d["speed"]
    pieces: list[np.ndarray] = []
    timings = []
    t = 0.0
    for sent, pause in split_script(text):
        a = _trim(_synth_sentence(sent, v, lang, spd))
        a = a / max(1e-6, np.abs(a).max()) * 0.89  # peak-normalise each sentence so engines are consistent
        pieces.append(a)
        dur = len(a) / SR
        timings.append((round(t, 3), round(t + dur, 3), sent))
        gap = d["gap"] if pause == -1.0 else (d["para"] if pause == -2.0 else pause)
        pieces.append(np.zeros(int(gap * SR), np.float32))
        t += dur + gap
    if pieces:  # drop trailing gap
        pieces.pop()
    audio = np.concatenate(pieces) if pieces else np.zeros(SR // 2, np.float32)
    audio = polish_voice(audio)
    return Speech(audio, timings, v, LICENSES[v.engine])


# ------------------------------------------------------------------ voice processing
def polish_voice(x: np.ndarray, sr: int = SR) -> np.ndarray:
    """Broadcast-style voice chain in numpy: rumble high-pass, gentle presence lift, soft compression."""
    from scipy.signal import butter, sosfilt
    x = sosfilt(butter(2, 70, "highpass", fs=sr, output="sos"), x)
    # presence: add a bit of 2.5-5 kHz band
    pres = sosfilt(butter(2, [2500, 5000], "bandpass", fs=sr, output="sos"), x)
    x = x + 0.18 * pres
    # warmth: small low-mid lift
    warm = sosfilt(butter(2, [120, 300], "bandpass", fs=sr, output="sos"), x)
    x = x + 0.08 * warm
    # soft-knee RMS compressor (3:1 above -20 dBFS)
    env = np.sqrt(np.convolve(x * x, np.ones(int(0.02 * sr)) / int(0.02 * sr), mode="same") + 1e-12)
    db = 20 * np.log10(env)
    gain_db = np.where(db > -20, (-20 - db) * (1 - 1 / 3), 0.0)
    x = x * 10 ** (gain_db / 20)
    peak = np.abs(x).max()
    return (x / peak * 0.89).astype(np.float32) if peak > 0 else x.astype(np.float32)


def clean_recording(src: str | Path, dst: str | Path) -> Path:
    """For human / cloned recordings: denoise + de-ess + level. Uses ffmpeg's FFT denoiser."""
    from .util import ffmpeg
    ffmpeg("-i", src, "-af",
           "highpass=f=70,afftdn=nf=-25:tn=1,deesser=i=0.4,"
           "acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=2,"
           "loudnorm=I=-16:TP=-1.5:LRA=7", "-ar", str(SR), "-ac", "1", dst)
    return Path(dst)


def save_wav(path: str | Path, audio: np.ndarray, sr: int = SR) -> Path:
    import soundfile as sf
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), audio, sr, subtype="PCM_16")
    return Path(path)


def describe_voices(lang_code: str | None = None) -> str:
    avail = available_engines()
    rows = []
    for code, lang in L.LANGUAGES.items():
        if lang_code and L.get(lang_code).code != code:
            continue
        rows.append(f"\n{lang.name} [{code}]  (subtitles ASR: {'whisper:' + lang.whisper if lang.whisper else 'none'})")
        for v in lang.voices:
            ok = "✓" if v.engine in avail else "✗ (engine not installed)"
            rows.append(f"  {ok} {v.engine:7s} {v.id:24s} {v.gender:6s} {v.accent:14s} {v.quality:8s} {v.note}")
        if lang.notes:
            rows.append(f"  note: {lang.notes}")
    return "\n".join(rows)


if __name__ == "__main__":
    log(describe_voices())
