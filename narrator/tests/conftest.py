import math
import struct
import subprocess
import time

import pytest
from fastapi.testclient import TestClient

from story_narrator.app import create_app
from story_narrator.config import Settings
from story_narrator.providers import Audio, ProviderError, VoiceProvider

RATE = 24000


def tone(text: str) -> bytes:
    """Fake 'speech': 10 ms of a 440 Hz tone per character, as 16-bit PCM."""
    n = int(RATE * 0.01 * len(text))
    return b"".join(struct.pack("<h", int(8000 * math.sin(2 * math.pi * 440 * i / RATE))) for i in range(n))


def pcm_to_mp3(pcm: bytes) -> bytes:
    p = subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "s16le", "-ar", str(RATE), "-ac", "1",
                        "-i", "pipe:0", "-codec:a", "libmp3lame", "-b:a", "64k", "-f", "mp3", "pipe:1"],
                       input=pcm, capture_output=True, check=True)
    return p.stdout


class FakeProvider(VoiceProvider):
    def __init__(self, chunk_chars=100, pcm=True, fail=None):
        super().__init__(name="fake", label="Fake", chunk_chars=chunk_chars, models=["m1"], default_model="m1")
        self.pcm, self.fail, self.calls = pcm, fail, []

    def voices(self):
        return [{"id": "v1", "name": "Voice One"}]

    def synthesize(self, text, voice, model, lossless):
        self.calls.append((text, lossless))
        if self.fail:
            raise ProviderError(self.fail, 401)
        if lossless and not self.pcm:
            raise ProviderError("PCM needs a higher plan", 403)
        data = tone(text)
        return Audio(data, "pcm", RATE) if lossless else Audio(pcm_to_mp3(data), "mp3")


def settings(tmp_path):
    s = Settings.from_env()
    return Settings(**{**s.__dict__, "data_dir": tmp_path, "workers": 2})


@pytest.fixture
def make_client(tmp_path):
    def make(provider):
        return TestClient(create_app(settings(tmp_path), {"fake": provider}))
    return make


def wait_done(client, nid, timeout=60):
    end = time.time() + timeout
    while time.time() < end:
        rec = client.get(f"/api/narrations/{nid}").json()
        if rec["status"] in ("ready", "failed"):
            return rec
        time.sleep(0.05)
    raise AssertionError("narration did not finish")
