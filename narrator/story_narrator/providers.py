"""AI voice providers. Every narration is synthesized by one of these; nothing is recorded.

Each provider can return either lossless PCM (kept as the WAV master) or MP3. The app
asks for PCM first and falls back to MP3 only if the provider or plan refuses it.
"""
from __future__ import annotations

import random
import time
from dataclasses import dataclass, field

import httpx

from .config import Settings
from .languages import LANGUAGES, language as lang_info


class ProviderError(RuntimeError):
    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.status = status


@dataclass
class Audio:
    data: bytes
    kind: str  # "pcm" (signed 16-bit little-endian) or "mp3"
    sample_rate: int = 0
    channels: int = 1


@dataclass
class VoiceProvider:
    name: str = ""
    label: str = ""
    chunk_chars: int = 4000
    models: list[str] = field(default_factory=list)
    default_model: str = ""
    # language code -> "native" (a voice trained on that language) or "prompted" (a
    # multilingual voice that reads the text; accent and accuracy are not guaranteed)
    languages: dict[str, str] = field(default_factory=dict)
    note: str = ""

    def voices(self) -> list[dict]:
        raise NotImplementedError

    def synthesize(self, text: str, voice: str, model: str, lossless: bool, language: str = "ht") -> Audio:
        raise NotImplementedError


_RETRY_STATUSES = {408, 409, 425, 429, 500, 502, 503, 504}


def _post_with_retry(client: httpx.Client, url: str, *, attempts: int = 6, **kw) -> httpx.Response:
    """Retry the provider's own rate limits and transient errors with backoff (Retry-After honored)."""
    delay = 1.0
    for i in range(attempts):
        try:
            r = client.post(url, **kw)
        except (httpx.TimeoutException, httpx.TransportError) as e:
            if i == attempts - 1:
                raise ProviderError(f"Network error talking to the voice provider: {e}") from e
        else:
            if r.status_code < 400:
                return r
            if r.status_code not in _RETRY_STATUSES or i == attempts - 1:
                raise ProviderError(_describe(r), r.status_code)
            ra = r.headers.get("retry-after")
            if ra and ra.replace(".", "", 1).isdigit():
                delay = max(delay, float(ra))
        time.sleep(delay + random.random() * 0.5)
        delay = min(delay * 2, 60)
    raise ProviderError("Voice provider did not respond")


def _describe(r: httpx.Response) -> str:
    msg = r.text
    try:
        body = r.json()
    except ValueError:
        body = None
    if isinstance(body, dict):
        for key in ("error", "detail"):
            val = body.get(key)
            if isinstance(val, dict) and val.get("message"):
                msg = val["message"]
                break
            if isinstance(val, str) and val:
                msg = val
                break
    return f"Voice provider returned HTTP {r.status_code}: {str(msg)[:400]}"


def _client() -> httpx.Client:
    # Long chunks can take a while to synthesize; never cut a response short.
    return httpx.Client(timeout=httpx.Timeout(connect=20, read=600, write=60, pool=60))


class OpenAIProvider(VoiceProvider):
    VOICES = ["alloy", "ash", "ballad", "coral", "echo", "fable", "nova", "onyx", "sage", "shimmer", "verse"]

    def __init__(self, s: Settings):
        super().__init__(name="openai", label="OpenAI TTS", chunk_chars=4000,
                         models=list(dict.fromkeys([s.openai_model, "gpt-4o-mini-tts", "tts-1-hd", "tts-1"])),
                         default_model=s.openai_model, languages={c: "prompted" for c in LANGUAGES})
        self._key, self._base = s.openai_api_key, s.openai_base_url

    def voices(self) -> list[dict]:
        return [{"id": v, "name": v.capitalize()} for v in self.VOICES]

    def synthesize(self, text, voice, model, lossless, language="ht"):
        fmt = "pcm" if lossless else "mp3"  # OpenAI pcm = 24 kHz, 16-bit, mono, little-endian
        model = model or self.default_model
        body = {"model": model, "voice": voice, "input": text, "response_format": fmt}
        if model.startswith("gpt-"):  # tts-1 models don't take instructions
            body["instructions"] = lang_info(language)["instructions"]
        with _client() as c:
            r = _post_with_retry(c, f"{self._base}/audio/speech",
                                 headers={"Authorization": f"Bearer {self._key}"}, json=body)
        return Audio(r.content, fmt, 24000 if lossless else 0)


class ElevenLabsProvider(VoiceProvider):
    BASE = "https://api.elevenlabs.io/v1"

    def __init__(self, s: Settings):
        super().__init__(name="elevenlabs", label="ElevenLabs", chunk_chars=s.elevenlabs_chunk_chars,
                         models=list(dict.fromkeys([s.elevenlabs_model, "eleven_multilingual_v2",
                                                    "eleven_turbo_v2_5", "eleven_flash_v2_5"])),
                         default_model=s.elevenlabs_model, languages={c: "prompted" for c in LANGUAGES})
        self._key = s.elevenlabs_api_key
        self._pcm, self._mp3 = s.elevenlabs_pcm_format, s.elevenlabs_mp3_format
        self._voice_cache: tuple[float, list[dict]] | None = None

    def voices(self) -> list[dict]:
        if self._voice_cache and time.time() - self._voice_cache[0] < 600:
            return self._voice_cache[1]
        with _client() as c:
            r = c.get(f"{self.BASE}/voices", headers={"xi-api-key": self._key})
        if r.status_code >= 400:
            raise ProviderError(_describe(r), r.status_code)
        voices = [{"id": v["voice_id"], "name": v.get("name") or v["voice_id"]} for v in r.json().get("voices", [])]
        self._voice_cache = (time.time(), voices)
        return voices

    def synthesize(self, text, voice, model, lossless, language="ht"):
        fmt = self._pcm if lossless else self._mp3
        with _client() as c:
            r = _post_with_retry(c, f"{self.BASE}/text-to-speech/{voice}", params={"output_format": fmt},
                                 headers={"xi-api-key": self._key},
                                 json={"text": text, "model_id": model or self.default_model})
        if lossless:
            return Audio(r.content, "pcm", int(fmt.split("_", 1)[1]))
        return Audio(r.content, "mp3")


def configured_providers(s: Settings) -> dict[str, VoiceProvider]:
    out: dict[str, VoiceProvider] = {}
    from .local_mms import MMSProvider, mms_installed
    if s.local_tts == "on" or (s.local_tts == "auto" and mms_installed()):
        out["mms"] = MMSProvider(s)
    if s.openai_api_key:
        out["openai"] = OpenAIProvider(s)
    if s.elevenlabs_api_key:
        out["elevenlabs"] = ElevenLabsProvider(s)
    return out
