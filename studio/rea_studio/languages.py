"""Language registry: which local voice engines really support which language.

Quality ranking we use (best first), all local / offline after the first model download:
  kokoro  Kokoro-82M (Apache-2.0). Most natural. en-US/en-GB/fr/es/pt-BR/it/hi (+ja/zh with extras).
  piper   Piper VITS voices (engine GPL-3.0; per-voice dataset licences, see MODEL_CARD of each voice).
          Good quality, very fast, gives us *male* French and more accents.
  mms     Meta MMS-TTS VITS (CC-BY-NC-4.0: NON-COMMERCIAL). 1,100+ languages incl. Haitian Creole (hat).
  espeak  eSpeak NG (GPL-3.0). Robotic formant synth, but supports Haitian Creole ('ht') and is
          licence-clean for commercial use. Last resort.

Nothing here claims support that does not exist: a language that has no entry for an engine is
simply not offered by that engine.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Voice:
    engine: str
    id: str
    gender: str  # female | male
    accent: str = ""
    quality: str = "good"  # best | good | fair | robotic
    note: str = ""


@dataclass
class Language:
    code: str
    name: str
    whisper: str | None  # faster-whisper language code (None = whisper does not know it)
    voices: list[Voice] = field(default_factory=list)
    kokoro_lang: str | None = None
    mms: str | None = None  # facebook/mms-tts-<iso639-3>
    espeak: str | None = None
    words_per_minute: int = 140
    notes: str = ""


def _k(i, g, a="", q="best", note=""):
    return Voice("kokoro", i, g, a, q, note)


def _p(i, g, a="", q="good", note=""):
    return Voice("piper", i, g, a, q, note)


LANGUAGES: dict[str, Language] = {}


def _add(lang: Language):
    LANGUAGES[lang.code] = lang


_add(Language("en", "English", "en", kokoro_lang="a", mms="eng", espeak="en-us", words_per_minute=150, voices=[
    _k("af_heart", "female", "US"), _k("af_bella", "female", "US"), _k("af_nicole", "female", "US", note="soft/whisper-like"),
    _k("am_michael", "male", "US"), _k("am_fenrir", "male", "US"), _k("am_puck", "male", "US"),
    _k("bf_emma", "female", "UK"), _k("bf_isabella", "female", "UK"), _k("bm_george", "male", "UK"),
    _k("bm_fable", "male", "UK"), _k("bm_lewis", "male", "UK"),
    _p("en_US-ryan-high", "male", "US"), _p("en_US-lessac-high", "female", "US"), _p("en_GB-alan-medium", "male", "UK"),
]))
_add(Language("fr", "French", "fr", kokoro_lang="f", mms="fra", espeak="fr-fr", words_per_minute=150, voices=[
    _k("ff_siwis", "female", "France"),
    _p("fr_FR-tom-medium", "male", "France"), _p("fr_FR-siwis-medium", "female", "France"),
    _p("fr_FR-gilles-low", "male", "France", q="fair"), _p("fr_FR-upmc-medium", "male", "France", note="multi-speaker: speaker 0=female, 1=male"),
], notes="Kokoro has only one French voice (female); male French uses Piper."))
_add(Language("es", "Spanish", "es", kokoro_lang="e", mms="spa", espeak="es-419", words_per_minute=160, voices=[
    _k("ef_dora", "female", "neutral/LatAm"), _k("em_alex", "male", "neutral/LatAm"),
    _p("es_ES-davefx-medium", "male", "Spain"), _p("es_MX-claude-high", "female", "Mexico"), _p("es_MX-ald-medium", "male", "Mexico"),
]))
_add(Language("pt-br", "Brazilian Portuguese", "pt", kokoro_lang="p", mms="por", espeak="pt-br", words_per_minute=150, voices=[
    _k("pf_dora", "female", "Brazil"), _k("pm_alex", "male", "Brazil"), _k("pm_santa", "male", "Brazil"),
    _p("pt_BR-faber-medium", "male", "Brazil"),
]))
_add(Language("ht", "Haitian Creole (Kreyòl Ayisyen)", "ht", mms="hat", espeak="ht", words_per_minute=140, voices=[
    Voice("mms", "hat", "male", "Haiti", "fair",
          "Meta MMS-TTS Haitian Creole: the only real neural Kreyòl voice that runs locally. Single voice, "
          "16 kHz, CC-BY-NC-4.0 (non-commercial). We upsample + master it."),
    Voice("espeak", "ht", "male", "Haiti", "robotic", "eSpeak NG Haitian Creole rules: intelligible, robotic, commercial-safe."),
    Voice("espeak", "ht+f3", "female", "Haiti", "robotic", "eSpeak NG female variant."),
], notes="No Kokoro, Piper, XTTS or F5 model supports Haitian Creole as of 2026-11. MMS-TTS is best local option; "
         "it is non-commercial. For monetised videos use espeak (robotic) or record a human narrator and let the "
         "studio handle cleanup, subtitles and sync. Whisper 'ht' ASR is weak, so Kreyòl subtitles are timed from the "
         "script, not transcribed."))
_add(Language("it", "Italian", "it", kokoro_lang="i", mms="ita", espeak="it", voices=[
    _k("if_sara", "female", "Italy"), _k("im_nicola", "male", "Italy"), _p("it_IT-riccardo-x_low", "male", "Italy", q="fair")]))
_add(Language("de", "German", "de", mms="deu", espeak="de", voices=[
    _p("de_DE-thorsten-high", "male", "Germany"), _p("de_DE-eva_k-x_low", "female", "Germany", q="fair")]))
_add(Language("hi", "Hindi", "hi", kokoro_lang="h", mms="hin", espeak="hi", voices=[
    _k("hf_alpha", "female", "India"), _k("hm_omega", "male", "India")]))


def get(code: str) -> Language:
    c = code.lower().replace("_", "-")
    alias = {"english": "en", "en-us": "en", "en-gb": "en", "french": "fr", "fr-fr": "fr", "francais": "fr",
             "spanish": "es", "espanol": "es", "pt": "pt-br", "portuguese": "pt-br", "pt-pt": "pt-br",
             "haitian": "ht", "haitian creole": "ht", "kreyol": "ht", "kreyòl": "ht", "creole": "ht", "hat": "ht",
             "italian": "it", "german": "de", "hindi": "hi"}
    c = alias.get(c, c)
    if c in LANGUAGES:
        return LANGUAGES[c]
    # Unknown language: MMS-TTS covers ~1,100 ISO-639-3 codes. We do not pretend: caller gets an MMS-only entry
    # and must verify that facebook/mms-tts-<code> exists.
    return Language(c, c, None, mms=c if len(c) == 3 else None, espeak=c,
                    voices=[Voice("mms", c, "male", "", "fair", "unverified: requires facebook/mms-tts-" + c),
                            Voice("espeak", c, "male", "", "robotic", "only if espeak-ng --voices lists it")],
                    notes="Not in the curated registry; MMS/espeak availability is checked at synthesis time.")


def pick_voice(lang: Language, gender: str | None = None, engine: str | None = None,
               commercial: bool = False, available: set[str] | None = None) -> Voice:
    """Best available voice for the request. `available` = engines importable on this machine."""
    cands = list(lang.voices)
    if engine and engine != "auto":
        cands = [v for v in cands if v.engine == engine]
    if commercial:
        cands = [v for v in cands if v.engine != "mms"]
    if available is not None:
        cands = [v for v in cands if v.engine in available]
    if gender:
        g = [v for v in cands if v.gender == gender]
        cands = g or cands
    if not cands:
        raise RuntimeError(f"No usable local voice for {lang.name} (engine={engine}, commercial={commercial}). {lang.notes}")
    order = {"best": 0, "good": 1, "fair": 2, "robotic": 3}
    return sorted(cands, key=lambda v: order.get(v.quality, 9))[0]


def find_voice(voice_id: str) -> Voice | None:
    for lang in LANGUAGES.values():
        for v in lang.voices:
            if v.id == voice_id:
                return v
    return None
