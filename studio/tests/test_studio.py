"""Fast tests: no model downloads. The end-to-end test uses eSpeak NG + a supplied image (skipped if absent)."""
import json
import shutil
from pathlib import Path

import numpy as np
import pytest
import yaml

from rea_studio import audio as A
from rea_studio import languages as L
from rea_studio import project as P
from rea_studio import styles as S
from rea_studio import subtitles as ST
from rea_studio import textnorm, tts

HAS_FFMPEG = shutil.which("ffmpeg") is not None
HAS_ESPEAK = shutil.which("espeak-ng") is not None


def test_haitian_numbers():
    assert textnorm.ht_number(1804) == "mil uisan kat"
    assert textnorm.ht_number(1791) == "mil sètsan katrevenonz"
    assert textnorm.ht_number(1492) == "mil katsan katrevendouz"
    assert textnorm.ht_number(21) == "vennteyen"
    assert textnorm.ht_number(75) == "swasannkenz"
    assert textnorm.normalize("99%", "ht") == "katrevendiznèf pousan"
    assert textnorm.normalize("1804", "fr") == "1804"  # only Kreyòl is normalised here


def test_split_script_pauses():
    parts = tts.split_script("Hello there. How are you? [pause 1.2] Fine! [paragraph] Bye.")
    assert [p[0] for p in parts] == ["Hello there.", "How are you?", "Fine!", "Bye."]
    assert parts[1][1] == 1.2 and parts[2][1] == -2.0 and parts[0][1] == -1.0


def test_language_registry_is_honest():
    ht = L.get("kreyol")
    assert ht.code == "ht"
    assert {v.engine for v in ht.voices} == {"mms", "espeak"}  # no fake Kokoro/Piper Kreyòl voice
    assert L.pick_voice(ht, commercial=True).engine == "espeak"
    assert L.pick_voice(L.get("fr"), gender="male").engine == "piper"
    assert L.pick_voice(L.get("en"), gender="female").id == "af_heart"
    with pytest.raises(RuntimeError):
        L.pick_voice(ht, commercial=True, available={"kokoro"})


def test_subtitle_chunking_and_files(tmp_path):
    words = ST.words_from_sentences([(0.0, 3.0, "This is the first sentence of the video."),
                                     (3.5, 6.0, "And a second one, a bit shorter.")])
    assert words[0].start == 0.0 and abs(words[-1].end - 6.0) < 1e-6
    assert all(w.end > w.start for w in words)
    cues = ST.chunk(words, 42)
    srt = ST.write_srt(cues, tmp_path / "a.srt")
    assert "00:00:00,000 -->" in srt.read_text()
    ass = ST.write_ass(ST.chunk(words, 16, 2, 2.2, 4), tmp_path / "a.ass", 1080, 1920, "karaoke",
                       [{"start": 0, "end": 2, "text": "HOOK", "style": "Top"}])
    txt = ass.read_text(encoding="utf-8-sig")
    assert "PlayResY: 1920" in txt and ST.HIGHLIGHT in txt and ",Top,," in txt


def test_styles_and_grade():
    st = S.get("tiktok")
    assert st["name"] == "short" and st["aspect"] == "9:16"
    g = S.grade_chain(S.get("cinematic"), 1920, 1080)
    assert "drawbox" in g and "noise" in g
    assert "drawbox" not in S.grade_chain(S.get("cinematic"), 1080, 1920)  # no letterbox on vertical


def test_project_skeleton_roundtrip(tmp_path):
    text = P.skeleton("History of Haiti", "ht", 180, None, "historical")
    data = yaml.safe_load(text)
    n, wps = P.plan_scenes(180, "ht", "historical")
    assert len(data["scenes"]) == n and data["language"] == "ht" and wps > 5
    f = tmp_path / "project.yaml"
    f.write_text(text)
    p = P.load(f)
    assert p["format"] == "16:9" and p["_style"]["name"] == "historical"


def test_project_validation(tmp_path):
    f = tmp_path / "p.yaml"
    f.write_text(yaml.safe_dump({"scenes": [{"narration": "x", "visual": "y", "characters": ["ghost"]}]}))
    with pytest.raises(P.ProjectError):
        P.load(f)


def test_music_and_sfx():
    x = A.compose(6, "epic", seed=1)
    assert x.shape == (6 * A.SR, 2) and np.abs(x).max() <= 0.81
    for name in A.SFX_NAMES:
        s = A.sfx(name)
        assert s.ndim == 2 and s.shape[1] == 2 and np.isfinite(s).all()


def test_ducking_reduces_music_under_voice():
    n = A.SR * 4
    music = np.full((n, 2), 0.5, np.float32)
    voice = np.zeros(n, np.float32)
    voice[A.SR:2 * A.SR] = 0.5
    d = A.duck(music, voice, 12)
    assert d[int(1.8 * A.SR), 0] < 0.2 and d[int(0.5 * A.SR), 0] > 0.45


@pytest.mark.skipif(not HAS_FFMPEG, reason="ffmpeg missing")
def test_camera_clip(tmp_path):
    from PIL import Image

    from rea_studio import motion
    img = tmp_path / "k.png"
    Image.fromarray((np.random.default_rng(0).random((288, 512, 3)) * 255).astype(np.uint8)).save(img)
    out = motion.camera_clip(img, tmp_path / "c.mp4", 1.0, 320, 180, 24, "orbit", upscale_method="lanczos")
    from rea_studio.util import probe_duration
    assert abs(probe_duration(out) - 1.0) < 0.15


@pytest.mark.skipif(not (HAS_FFMPEG and HAS_ESPEAK), reason="needs ffmpeg + espeak-ng")
def test_full_pipeline_espeak(tmp_path):
    from PIL import Image

    from rea_studio.pipeline import Build
    img = tmp_path / "frame.png"
    Image.new("RGB", (512, 288), (40, 90, 140)).save(img)
    proj = tmp_path / "project.yaml"
    proj.write_text(yaml.safe_dump({
        "title": "Tès", "language": "ht", "style": "news", "voice": {"voice": "ht", "engine": "espeak"},
        "scenes": [{"narration": "Bonjou tout moun. An 1804, Ayiti te vin lib.", "image": str(img), "sfx": ["ding"],
                    "lower_third": "Pòtoprens"},
                   {"narration": "Mèsi.", "image": str(img), "transition": "wipeleft"}]}, allow_unicode=True))
    r = Build(proj, preview=True).run()
    assert Path(r["output"]).exists() and Path(r["thumbnail"]).exists()
    assert r["voices"] == ["espeak:ht"] and r["commercial_safe"] is True
    assert -16 < r["loudness"]["lufs"] < -12
    rep = json.loads(Path(r["output"]).with_suffix(".report.json").read_text())
    assert rep["subtitle_timing"] == "script"
