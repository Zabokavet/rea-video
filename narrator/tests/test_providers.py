import json

import httpx
import pytest

from conftest import FakeProvider, settings
from story_narrator import providers
from story_narrator.jobs import JobRunner
from story_narrator.library import Library
from story_narrator.providers import ElevenLabsProvider, OpenAIProvider, ProviderError


@pytest.fixture
def transport(monkeypatch):
    calls, replies = [], []

    def handler(req: httpx.Request):
        calls.append(req)
        return replies.pop(0) if replies else httpx.Response(200, content=b"\x01\x00" * 10)

    monkeypatch.setattr(providers, "_client", lambda: httpx.Client(transport=httpx.MockTransport(handler)))
    monkeypatch.setattr(providers.time, "sleep", lambda s: None)
    return calls, replies


def test_openai_requests_pcm_and_retries_rate_limits(tmp_path, transport):
    calls, replies = transport
    s = settings(tmp_path).__class__(**{**settings(tmp_path).__dict__, "openai_api_key": "sk-test"})
    replies.append(httpx.Response(429, headers={"retry-after": "1"}, json={"error": {"message": "slow down"}}))
    out = OpenAIProvider(s).synthesize("Hello.", "nova", "", lossless=True)
    assert (out.kind, out.sample_rate) == ("pcm", 24000)
    assert len(calls) == 2  # retried after the provider's 429
    body = json.loads(calls[-1].content)
    assert body == {"model": "gpt-4o-mini-tts", "voice": "nova", "input": "Hello.", "response_format": "pcm"}
    assert calls[-1].headers["authorization"] == "Bearer sk-test"


def test_elevenlabs_formats_and_errors(tmp_path, transport):
    calls, replies = transport
    s = settings(tmp_path).__class__(**{**settings(tmp_path).__dict__, "elevenlabs_api_key": "xi"})
    p = ElevenLabsProvider(s)
    assert p.synthesize("Hi.", "VOICE", "", lossless=True).sample_rate == 24000
    assert calls[-1].url.params["output_format"] == "pcm_24000"
    assert calls[-1].url.path == "/v1/text-to-speech/VOICE"
    assert p.synthesize("Hi.", "VOICE", "", lossless=False).kind == "mp3"
    replies.append(httpx.Response(401, json={"detail": {"message": "invalid api key"}}))
    with pytest.raises(ProviderError, match="invalid api key") as e:
        p.synthesize("Hi.", "VOICE", "", lossless=False)
    assert e.value.status == 401


def test_auth_errors_do_not_fall_back_to_mp3(tmp_path):
    provider = FakeProvider(fail="bad key")
    lib = Library(tmp_path)
    rec = lib.create("T", "Hello there.", "fake", "v1", "m1")
    with pytest.raises(ProviderError):
        JobRunner(settings(tmp_path), lib, {"fake": provider}).run(rec["id"])
    assert provider.calls == [("Hello there.", True)]
