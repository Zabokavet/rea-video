"""Acceptance tests: prove each capability works on *this* machine, with measurements rather than claims.

Voice tests do a round trip: synthesise -> transcribe with faster-whisper -> character error rate (CER) against
the input text. Low CER = intelligible pronunciation. (Whisper's Haitian Creole ASR is itself weak, so a higher
'ht' CER partly reflects the recogniser; we report it for comparison between voices, not as an absolute score.)
"""
from __future__ import annotations

import json
import time
import traceback
from pathlib import Path

TEXTS = {
    "en": "Welcome to your local film studio. Every frame, every voice and every note is made on this computer.",
    "fr": "Bienvenue dans votre studio de cinéma local. Chaque image, chaque voix et chaque note est créée sur cet ordinateur.",
    "es": "Bienvenido a tu estudio de cine local. Cada imagen, cada voz y cada nota se crea en esta computadora.",
    "pt-br": "Bem-vindo ao seu estúdio de cinema local. Cada imagem, cada voz e cada nota é criada neste computador.",
    "ht": "Byenvini nan estidyo sinema lokal ou a. Chak imaj, chak vwa ak chak nòt fèt sou òdinatè sa a.",
}


def cer(ref: str, hyp: str) -> float:
    import difflib
    import re
    import unicodedata

    def n(s):
        s = unicodedata.normalize("NFKD", s.lower())
        s = "".join(c for c in s if not unicodedata.combining(c))
        return re.sub(r"[^a-z0-9 ]", "", re.sub(r"\s+", " ", s)).strip()
    a, b = n(ref), n(hyp)
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    edits = sum(max(i2 - i1, j2 - j1) for op, i1, i2, j1, j2 in sm.get_opcodes() if op != "equal")
    return round(edits / max(1, len(a)), 3)


_wm = None


def asr(path: Path, lang: str) -> str:
    global _wm
    from faster_whisper import WhisperModel
    if _wm is None:
        _wm = WhisperModel("small", device="cpu", compute_type="int8")
    from .subtitles import load_16k
    segs, _ = _wm.transcribe(load_16k(path), language=lang, beam_size=5)
    return " ".join(s.text.strip() for s in segs)


def run(out: Path, quick: bool = False) -> int:
    from . import images, motion, tts
    from .util import probe_streams
    out.mkdir(parents=True, exist_ok=True)
    results: dict = {}

    def test(name, fn):
        t = time.time()
        try:
            r = fn()
            results[name] = {"ok": True, "seconds": round(time.time() - t, 1), **(r or {})}
            print(f"PASS {name} ({results[name]['seconds']} s) {json.dumps(r or {}, ensure_ascii=False)[:300]}", flush=True)
        except Exception as e:
            results[name] = {"ok": False, "error": f"{type(e).__name__}: {e}", "trace": traceback.format_exc()[-1500:]}
            print(f"FAIL {name}: {type(e).__name__}: {e}", flush=True)

    # 1 image
    img = out / "01_image.png"
    if not quick:
        def t_image():
            from .hardware import detect
            pre = images.default_preset(detect().tier)
            images.ImageGenerator(pre).generate(
                "cinematic film still, colonial-era stone fortress on a lush green Caribbean mountain at golden hour, "
                "dramatic clouds, 35mm, volumetric light, highly detailed", img, "16:9", 7)
            from PIL import Image
            im = Image.open(img)
            return {"file": str(img), "size": im.size, "model": pre}
        test("1_image_generation", t_image)

    # 2 video
    def t_video():
        src = img if img.exists() else images.placeholder("selftest", out / "01_placeholder.png", "16:9", 1)
        clip = motion.camera_clip(src, out / "02_camera_move.mp4", 5, 1280, 720, 30, "parallax_in")
        r = {"camera_clip": str(clip)}
        if not quick:
            ai = motion.animate_clip(src, out / "02_ai_motion.mp4", 4, 1280, 720, 24,
                                     "ocean breeze, moving clouds, swaying trees, cinematic", "drift", 0.55)
            r["ai_clip"] = str(ai)
        return r
    test("2_video_generation", t_video)

    # 3-5 voices with intelligibility round trip
    def voice_test(lang, voice=None, engine="auto", gender=None, tag=""):
        def f():
            sp = tts.synthesize(TEXTS[lang], lang, voice or "auto", gender, "documentary", engine=engine)
            p = out / f"03_voice_{lang}{tag}_{sp.voice.engine}_{sp.voice.id}.wav"
            tts.save_wav(p, sp.audio)
            r = {"file": str(p), "voice": f"{sp.voice.engine}:{sp.voice.id}", "seconds": round(sp.duration, 2),
                 "license": sp.license}
            try:
                hyp = asr(p, {"pt-br": "pt"}.get(lang, lang))
                r.update(asr_text=hyp, cer=cer(TEXTS[lang], hyp))
            except Exception as e:
                r["asr"] = f"skipped: {e}"
            return r
        return f
    test("3_voice_en_female", voice_test("en", "af_heart"))
    test("3_voice_en_male", voice_test("en", "am_michael", tag="_m"))
    test("4_voice_fr_female", voice_test("fr", "ff_siwis"))
    test("4_voice_fr_male", voice_test("fr", "fr_FR-tom-medium", tag="_m"))
    test("4b_voice_es", voice_test("es", "em_alex"))
    test("4b_voice_pt_br", voice_test("pt-br", "pf_dora"))
    test("5_voice_ht_mms", voice_test("ht", "hat", "mms"))
    test("5_voice_ht_espeak", voice_test("ht", "ht", "espeak", tag="_e"))

    # 6 subtitles
    def t_subs():
        from . import subtitles as ST
        sp = tts.synthesize(TEXTS["en"], "en", "af_heart")
        p = out / "06_sub_src.wav"
        tts.save_wav(p, sp.audio)
        words = ST.words_from_sentences(sp.sentences)
        refined, ratio = ST.refine_with_whisper(words, p, "en")
        cues = ST.chunk(refined)
        ST.write_srt(cues, out / "06_subtitles.srt")
        ST.write_ass(cues, out / "06_subtitles.ass", 1920, 1080, "clean")
        return {"srt": str(out / "06_subtitles.srt"), "cues": len(cues), "whisper_word_match": round(ratio, 2)}
    test("6_subtitles", t_subs)

    # 7-8 combine + export
    def t_full():
        proj = out / "mini" / "project.yaml"
        proj.parent.mkdir(parents=True, exist_ok=True)
        frames = [str(img)] if img.exists() else []
        import yaml
        scenes = [
            {"narration": "High above the northern coast, a fortress watches over the sea.",
             "visual": "stone fortress on a mountain at golden hour", "title": "Chapter One", "sfx": ["wind"]},
            {"narration": "Built by thousands of hands, it was meant to never fall. [pause 0.5] It never did.",
             "visual": "close up of ancient stone walls with cannons, warm light"},
        ]
        if not frames and quick:
            frames = [str(images.placeholder("selftest", out / "01_placeholder.png", "16:9", 1))]
        if frames:
            for s in scenes:
                s["image"] = frames[0]
        doc = {"title": "Selftest", "language": "en", "format": "16:9", "style": "documentary", "scenes": scenes,
               "voice": {"voice": "am_michael"}, "music": {"engine": "score", "mood": "historical"}}
        proj.write_text(yaml.safe_dump(doc, allow_unicode=True))
        from .pipeline import Build
        b = Build(proj, preview=True, allow_placeholder=quick)
        r = b.run()
        info = probe_streams(r["output"])
        kinds = sorted(s["codec_type"] for s in info["streams"])
        assert kinds == ["audio", "video"], kinds
        return {"mp4": r["output"], "seconds": r["seconds"], "loudness": r["loudness"], "streams": kinds,
                "thumbnail": r["thumbnail"]}
    test("7_8_full_pipeline_mp4", t_full)

    (out / "selftest.json").write_text(json.dumps(results, indent=2, ensure_ascii=False))
    failed = [k for k, v in results.items() if not v["ok"]]
    print(f"\n{len(results) - len(failed)}/{len(results)} passed. Details: {out / 'selftest.json'}")
    return 1 if failed else 0
