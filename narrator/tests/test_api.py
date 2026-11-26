import io
import tempfile
import wave
from pathlib import Path

from story_narrator.audio import probe_duration

from conftest import RATE, FakeProvider, tone, wait_done

STORY = ("The lighthouse keeper woke before dawn. " * 30).strip()  # ~1200 chars -> many chunks


def create(client, **kw):
    body = {"title": "The Lighthouse Keeper", "text": STORY, "provider": "fake", "voice": "v1", **kw}
    r = client.post("/api/narrations", json=body)
    assert r.status_code == 202, r.text
    return r.json()


def test_long_story_exports_lossless_wav_and_mp3(make_client):
    provider = FakeProvider(chunk_chars=100)
    with make_client(provider) as c:
        rec = wait_done(c, create(c)["id"])
        assert rec["status"] == "ready", rec
        assert rec["chunks_total"] == rec["chunks_done"] > 10
        assert rec["has_wav"] and rec["has_mp3"]

        wav = c.get(f"/api/narrations/{rec['id']}/audio.wav?download=1")
        assert wav.status_code == 200 and wav.headers["content-type"] == "audio/wav"
        assert 'filename="The-Lighthouse-Keeper_' in wav.headers["content-disposition"]
        assert wav.headers["content-disposition"].startswith("attachment;")
        with wave.open(io.BytesIO(wav.content)) as w:
            frames = w.readframes(w.getnframes())
            assert w.getframerate() == RATE
        # Nothing truncated or altered: the WAV is exactly the provider's samples, in order.
        assert frames == b"".join(tone(text) for text, _ in provider.calls)

        mp3 = c.get(f"/api/narrations/{rec['id']}/audio.mp3?download=1")
        assert mp3.status_code == 200 and mp3.headers["content-type"] == "audio/mpeg"
        assert mp3.headers["content-disposition"].endswith(".mp3")
        assert abs(probe(mp3.content) - rec["duration"]) < 0.2

        inline = c.get(f"/api/narrations/{rec['id']}/audio.mp3")
        assert inline.headers["content-disposition"].startswith("inline;")
        part = c.get(f"/api/narrations/{rec['id']}/audio.wav", headers={"Range": "bytes=0-99"})
        assert part.status_code == 206 and len(part.content) == 100  # seeking works


def test_mp3_only_plan_falls_back_and_hides_wav(make_client):
    provider = FakeProvider(chunk_chars=300, pcm=False)
    with make_client(provider) as c:
        rec = wait_done(c, create(c)["id"])
        assert rec["status"] == "ready", rec
        assert rec["has_mp3"] and not rec["has_wav"]
        assert c.get(f"/api/narrations/{rec['id']}/audio.wav").status_code == 404
        mp3 = c.get(f"/api/narrations/{rec['id']}/audio.mp3").content
        mp3_chunks = [t for t, lossless in provider.calls if not lossless]
        expected = sum(len(t) for t in mp3_chunks) * 0.01
        # Every chunk is in the joined file; each MP3 chunk carries ~0.05 s of encoder padding.
        assert expected - 0.05 < probe(mp3) < expected + 0.1 * len(mp3_chunks)


def test_library_lists_searches_retries_and_deletes(make_client):
    provider = FakeProvider(fail="Invalid API key")
    with make_client(provider) as c:
        bad = wait_done(c, create(c, title="Broken")["id"])
        assert bad["status"] == "failed" and "Invalid API key" in bad["error"]

        provider.fail = None
        assert c.post(f"/api/narrations/{bad['id']}/retry").status_code == 202
        assert wait_done(c, bad["id"])["status"] == "ready"

        other = wait_done(c, create(c, title="Second Tale", text="A short one.")["id"])
        titles = [n["title"] for n in c.get("/api/narrations").json()["narrations"]]
        assert titles == ["Second Tale", "Broken"]
        assert [n["title"] for n in c.get("/api/narrations?q=Second").json()["narrations"]] == ["Second Tale"]

        assert c.delete(f"/api/narrations/{other['id']}").status_code == 204
        assert c.get(f"/api/narrations/{other['id']}/audio.mp3").status_code == 404
        assert len(c.get("/api/narrations").json()["narrations"]) == 1


def test_creole_is_the_default_and_numbers_are_read_in_creole(make_client):
    provider = FakeProvider(chunk_chars=4000)
    with make_client(provider) as c:
        r = c.post("/api/narrations", json={"title": "Twa ti kochon", "provider": "fake", "voice": "v1",
                                            "text": "Te gen 3 ti kochon ki te gen 25 goud."})
        rec = wait_done(c, r.json()["id"])
        assert rec["status"] == "ready" and rec["language"] == "ht"
        assert provider.calls[0][0] == "Te gen twa ti kochon ki te gen vennsenk goud."
        assert provider.languages_used == ["ht"]
        s = c.get("/api/status").json()
        assert s["default_language"] == "ht" and s["languages"][0]["name"] == "Kreyòl ayisyen"
        # other languages are allowed, but only with a provider that has a voice for them
        assert c.post("/api/narrations", json={"title": "x", "text": "y", "provider": "fake", "voice": "v",
                                               "language": "es"}).status_code == 400
        fr = wait_done(c, c.post("/api/narrations", json={"title": "Conte", "text": "Il y a 3 chats.",
                                                          "provider": "fake", "voice": "v", "language": "fr"}).json()["id"])
        assert fr["language"] == "fr" and provider.calls[-1][0] == "Il y a 3 chats."


def test_creole_titles_make_good_filenames(make_client):
    with make_client(FakeProvider()) as c:
        rec = wait_done(c, create(c, title="Bouki ak Ti Malis: lanmè a")["id"])
        h = c.get(f"/api/narrations/{rec['id']}/audio.mp3?download=1").headers["content-disposition"]
        assert 'filename="Bouki-ak-Ti-Malis-lanme-a_' in h  # ASCII fallback
        assert "filename*=UTF-8''Bouki-ak-Ti-Malis-lanm%C3%A8-a_" in h  # keeps the è


def test_validation_and_ui(make_client):
    with make_client(FakeProvider()) as c:
        assert c.post("/api/narrations", json={"title": "x", "text": "y", "provider": "nope", "voice": "v"}).status_code == 400
        assert c.post("/api/narrations", json={"title": "", "text": "y", "provider": "fake", "voice": "v"}).status_code == 422
        s = c.get("/api/status").json()
        assert s["providers"][0]["id"] == "fake"
        assert c.get("/api/providers/fake/voices").json()["voices"][0]["id"] == "v1"
        page = c.get("/").text
        assert 'lang="ht"' in page and "Rakontè Istwa" in page
        js = c.get("/app.js").text
        assert "Telechaje odyo a (MP3)" in js and "Download Audio (MP3)" in js and "Bibliyotèk odyo" in js


def probe(data: bytes) -> float:
    with tempfile.NamedTemporaryFile(suffix=".mp3") as f:
        f.write(data)
        f.flush()
        return probe_duration(Path(f.name))
