"""Subtitles and on-screen text: SRT + styled ASS (libass), word-level timing.

Timing sources, best first:
 1. faster-whisper word timestamps on the final narration, aligned back to *our* script text with difflib
    (so spelling/diacritics come from the script, timing from the audio). Used when Whisper knows the language
    well (en, fr, es, pt, it, de...).
 2. Script timing: we synthesised every sentence separately, so sentence boundaries are exact; words inside a
    sentence are spread by syllable-ish weight. This is what Haitian Creole uses (Whisper 'ht' is unreliable).
Also works for any existing video: `rea-studio subtitles video.mp4 --lang fr` transcribes it.
"""
from __future__ import annotations

import difflib
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from .util import find_font, font_family, log


def load_16k(media: str | Path):
    """Decode any audio/video to 16 kHz mono float32 with ffmpeg (avoids PyAV version clashes in faster-whisper)."""
    import numpy as np

    from .util import run
    p = run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(media), "-vn", "-ac", "1", "-ar", "16000",
             "-f", "f32le", "-"])
    return np.frombuffer(p.stdout, dtype=np.float32).copy()


@dataclass
class Word:
    text: str
    start: float
    end: float


# ------------------------------------------------------------------ timing
def _weight(w: str) -> float:
    vowels = len(re.findall(r"[aeiouyàâäéèêëîïôöùûüœæãõáíóúòìAEIOUY]+", w, re.I))
    pause = 1.2 if re.search(r"[,;:]$", w) else (1.8 if re.search(r"[.!?…]$", w) else 0)
    return max(1, vowels) + pause + 0.15 * len(w)


def words_from_sentences(sentences: list[tuple[float, float, str]]) -> list[Word]:
    out = []
    for s, e, text in sentences:
        toks = text.split()
        if not toks:
            continue
        ws = [_weight(t) for t in toks]
        tot = sum(ws)
        t = s
        for tok, w in zip(toks, ws):
            d = (e - s) * w / tot
            out.append(Word(tok, round(t, 3), round(t + d, 3)))
            t += d
    return out


def _norm(w: str) -> str:
    w = unicodedata.normalize("NFKD", w.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in w if not unicodedata.combining(c)))


def refine_with_whisper(words: list[Word], audio: Path, lang: str, model: str = "small") -> tuple[list[Word], float]:
    """Return (words with whisper timing where matched, match ratio)."""
    from faster_whisper import WhisperModel
    from .hardware import torch_device
    dev = "cuda" if torch_device() == "cuda" else "cpu"
    wm = WhisperModel(model, device=dev, compute_type="float16" if dev == "cuda" else "int8")
    segs, _ = wm.transcribe(load_16k(audio), language=lang, word_timestamps=True, vad_filter=False, beam_size=5)
    hyp = [Word(w.word.strip(), w.start, w.end) for s in segs for w in (s.words or [])]
    a = [_norm(w.text) for w in words]
    b = [_norm(w.text) for w in hyp]
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    matched = 0
    out = [Word(w.text, w.start, w.end) for w in words]
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            ow, hw = out[blk.a + k], hyp[blk.b + k]
            # only accept whisper timing if it stays near the script timing (guards against misalignment)
            if abs(hw.start - ow.start) < 1.5:
                ow.start, ow.end = hw.start, hw.end
                matched += 1
    ratio = matched / max(1, len(words))
    # keep monotonic
    for i in range(1, len(out)):
        if out[i].start < out[i - 1].end:
            out[i].start = out[i - 1].end
        if out[i].end <= out[i].start:
            out[i].end = out[i].start + 0.08
    return out, ratio


def transcribe(media: Path, lang: str | None = None, model: str = "small") -> list[Word]:
    from faster_whisper import WhisperModel
    wm = WhisperModel(model, device="cpu", compute_type="int8")
    segs, info = wm.transcribe(load_16k(media), language=lang, word_timestamps=True, vad_filter=True)
    words = [Word(w.word.strip(), w.start, w.end) for s in segs for w in (s.words or [])]
    log(f"transcribed {len(words)} words, language={info.language} (p={info.language_probability:.2f})")
    return words


# ------------------------------------------------------------------ chunking
def chunk(words: list[Word], max_chars: int = 42, max_lines: int = 2, max_dur: float = 6.0,
          max_words: int | None = None) -> list[list[Word]]:
    cues, cur = [], []
    limit = max_chars * max_lines
    for w in words:
        text_len = len(" ".join(x.text for x in cur + [w]))
        too_long = cur and (text_len > limit or (w.end - cur[0].start) > max_dur or
                            (max_words and len(cur) >= max_words))
        if too_long:
            cues.append(cur)
            cur = []
        cur.append(w)
        if re.search(r"[.!?…]$", w.text) and len(" ".join(x.text for x in cur)) > max_chars * 0.5:
            cues.append(cur)
            cur = []
    if cur:
        cues.append(cur)
    return cues


def _wrap(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    words = text.split()
    best, best_diff = text, 1e9
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        d = abs(len(a) - len(b)) + (0 if len(a) <= max_chars and len(b) <= max_chars else 100)
        if d < best_diff:
            best, best_diff = a + "\n" + b, d
    return best


def _ts(t: float, sep: str = ",") -> str:
    h, rem = divmod(max(0, t), 3600)
    m, s = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d}{sep}{int(round((s % 1) * 1000)):03d}"


def write_srt(cues: list[list[Word]], path: Path, max_chars: int = 42) -> Path:
    lines = []
    for i, c in enumerate(cues, 1):
        lines += [str(i), f"{_ts(c[0].start)} --> {_ts(c[-1].end + 0.15)}", _wrap(" ".join(w.text for w in c), max_chars), ""]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


# ------------------------------------------------------------------ ASS
CAPTION_STYLES = {
    # name: (font role, size as % of height, primary, outline colour, outline, shadow, bold, border style, margin_v %, upper)
    "clean":       ("body", 4.6, "&H00FFFFFF", "&H00000000", 2.6, 0.8, 1, 1, 6.5, False),
    "documentary": ("body", 4.2, "&H00F0F0F0", "&H64000000", 1.6, 1.4, 0, 1, 7.0, False),
    "cinematic":   ("serif", 4.0, "&H00EAF2F6", "&H78000000", 1.2, 1.6, 0, 1, 8.5, False),
    "news":        ("body", 4.4, "&H00FFFFFF", "&H00602B10", 0.0, 0.0, 1, 3, 9.0, False),
    "bold":        ("title", 6.2, "&H00FFFFFF", "&H00000000", 4.0, 1.5, 1, 1, 30.0, True),  # shorts/reels
    "karaoke":     ("title", 6.2, "&H00FFFFFF", "&H00000000", 4.0, 1.5, 1, 1, 30.0, True),
}
HIGHLIGHT = "&H0000E5FF"  # ASS BGR: yellow


def _ass_header(W: int, H: int, style: str) -> str:
    role, size, prim, outc, outline, shadow, bold, bstyle, mv, _ = CAPTION_STYLES[style]
    fs = int(H * size / 100)
    font = font_family(find_font(role))
    tfont = font_family(find_font("title"))
    sfont = font_family(find_font("serif"))
    mvp = int(H * mv / 100)
    back = "&H96000000" if bstyle == 3 else "&H80000000"
    return f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,{font},{fs},{prim},{HIGHLIGHT},{outc if bstyle != 3 else back},{back},{-1 if bold else 0},0,0,0,100,100,0,0,{bstyle},{outline if bstyle != 3 else 8},{shadow},2,{int(W*0.06)},{int(W*0.06)},{mvp},1
Style: Title,{tfont},{int(H*0.085)},&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,2,0,1,3,2,5,{int(W*0.08)},{int(W*0.08)},0,1
Style: Chapter,{sfont},{int(H*0.06)},&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,4,0,1,1.5,2.5,5,{int(W*0.08)},{int(W*0.08)},0,1
Style: Lower,{font},{int(H*0.04)},&H00FFFFFF,&H00FFFFFF,&H00B06A1E,&HC8000000,-1,0,0,0,100,100,0,0,3,10,0,1,{int(W*0.05)},{int(W*0.05)},{int(H*0.16)},1
Style: Top,{tfont},{int(H*0.055)},&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,1,0,1,3,1.5,8,{int(W*0.06)},{int(W*0.06)},{int(H*0.08)},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def _ass_ts(t: float) -> str:
    h, rem = divmod(max(0, t), 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def _esc(t: str) -> str:
    return t.replace("\\", "\\\\").replace("{", "(").replace("}", ")").replace("\n", "\\N")


def write_ass(cues: list[list[Word]], path: Path, W: int, H: int, style: str = "clean",
              overlays: list[dict] | None = None, max_chars: int = 42) -> Path:
    style = style if style in CAPTION_STYLES else "clean"
    upper = CAPTION_STYLES[style][9]
    ev = []
    for c in cues:
        st, en = c[0].start, c[-1].end + 0.12
        if style in ("bold", "karaoke"):
            # one event per active word: whole group visible, current word highlighted + popped
            for i, w in enumerate(c):
                ws, we = w.start, (c[i + 1].start if i + 1 < len(c) else en)
                parts = []
                for j, x in enumerate(c):
                    t = _esc(x.text.upper() if upper else x.text)
                    parts.append("{\\c" + HIGHLIGHT + "\\fscx112\\fscy112}" + t + "{\\r}" if j == i else t)
                pop = "{\\fad(60,0)}" if i == 0 else ""
                ev.append(f"Dialogue: 0,{_ass_ts(ws)},{_ass_ts(we)},Sub,,0,0,0,,{pop}{' '.join(parts)}")
        else:
            txt = _esc(_wrap(" ".join(w.text for w in c), max_chars))
            ev.append(f"Dialogue: 0,{_ass_ts(st)},{_ass_ts(en)},Sub,,0,0,0,,{{\\fad(120,120)}}{txt}")
    for o in overlays or []:
        kind = o.get("style", "Title")
        fade = "{\\fad(500,500)}" if kind in ("Title", "Chapter") else "{\\fad(250,250)}"
        if kind == "Title":
            fade = "{\\fad(600,600)\\t(0,1500,\\fscx104\\fscy104)}"
        ev.append(f"Dialogue: 1,{_ass_ts(o['start'])},{_ass_ts(o['end'])},{kind},,0,0,0,,{fade}{_esc(o['text'])}")
    path.write_text(_ass_header(W, H, style) + "\n".join(ev) + "\n", encoding="utf-8-sig")
    return path


def caption_params(aspect: str, style: str) -> dict:
    if style in ("bold", "karaoke"):
        return dict(max_chars=16, max_lines=2, max_dur=2.2, max_words=4)
    if aspect in ("9:16", "4:5"):
        return dict(max_chars=24, max_lines=2, max_dur=4.0, max_words=None)
    return dict(max_chars=42, max_lines=2, max_dur=6.0, max_words=None)
