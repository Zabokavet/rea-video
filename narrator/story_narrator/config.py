"""Settings, read from the environment (and an optional .env file)."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def load_env_file(path: str | os.PathLike | None) -> None:
    """Load KEY=VALUE lines into os.environ without overriding variables already set."""
    if not path:
        return
    p = Path(path)
    if not p.is_file():
        return
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip().removeprefix("export ").strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    workers: int
    openai_api_key: str
    openai_model: str
    openai_base_url: str
    elevenlabs_api_key: str
    elevenlabs_model: str
    elevenlabs_pcm_format: str
    elevenlabs_mp3_format: str
    elevenlabs_chunk_chars: int
    mp3_vbr_quality: int
    local_tts: str
    hf_cache_dir: str

    @classmethod
    def from_env(cls) -> "Settings":
        env = os.environ.get
        return cls(
            data_dir=Path(env("NARRATOR_DATA_DIR", "data")).resolve(),
            # Jobs beyond this many run in a queue; nothing is ever rejected.
            workers=max(1, int(env("NARRATOR_WORKERS", "2"))),
            openai_api_key=env("OPENAI_API_KEY", ""),
            openai_model=env("OPENAI_TTS_MODEL", "gpt-4o-mini-tts"),
            openai_base_url=env("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/"),
            elevenlabs_api_key=env("ELEVENLABS_API_KEY", ""),
            elevenlabs_model=env("ELEVENLABS_MODEL", "eleven_multilingual_v2"),
            # pcm_44100 needs an ElevenLabs Pro plan; pcm_24000 works on every plan.
            elevenlabs_pcm_format=env("ELEVENLABS_PCM_FORMAT", "pcm_24000"),
            elevenlabs_mp3_format=env("ELEVENLABS_MP3_FORMAT", "mp3_44100_128"),
            elevenlabs_chunk_chars=int(env("ELEVENLABS_CHUNK_CHARS", "4500")),
            # LAME VBR quality used when encoding MP3 from the lossless master: 0 = best.
            mp3_vbr_quality=int(env("NARRATOR_MP3_QUALITY", "0")),
            # Native Haitian Creole voice (Meta MMS) running on this computer: auto | on | off.
            # "auto" turns it on when the optional [kreyol] dependencies are installed.
            local_tts=env("NARRATOR_LOCAL_TTS", "auto").lower(),
            hf_cache_dir=env("NARRATOR_MODEL_DIR", ""),
        )
