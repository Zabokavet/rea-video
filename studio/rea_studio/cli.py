"""rea-studio command line."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _doctor(a):
    from . import tts
    from .hardware import detect
    from .images import default_preset
    hw = detect()
    eng = tts.available_engines()
    mods = {}
    for m in ["torch", "diffusers", "transformers", "kokoro", "piper", "faster_whisper", "spandrel", "cv2", "soundfile"]:
        try:
            mod = __import__(m)
            mods[m] = getattr(mod, "__version__", "ok")
        except Exception:
            mods[m] = None
    import shutil
    tools = {t: shutil.which(t) for t in ["ffmpeg", "ffprobe", "espeak-ng", "blender", "kdenlive", "shotcut",
                                          "audacity", "openshot-qt"]}
    if a.json:
        print(json.dumps({"hardware": hw.to_dict(), "tts_engines": sorted(eng), "python_modules": mods,
                          "tools": tools}, indent=2))
        return
    print(f"OS        {hw.os} {hw.os_version} ({hw.arch}), Python {hw.python}")
    print(f"CPU       {hw.cpu} x{hw.cpu_cores}   RAM {hw.ram_gb} GB   free disk {hw.disk_free_gb} GB")
    print(f"GPU       {hw.gpu or 'none'} {f'({hw.vram_gb} GB)' if hw.gpu else ''}  -> tier '{hw.tier}', "
          f"image model '{default_preset(hw.tier)}'")
    print(f"ffmpeg    {hw.ffmpeg or 'MISSING'}")
    print(f"TTS       {', '.join(sorted(eng)) or 'none'}")
    print("Python    " + ", ".join(f"{k}={'✗' if v is None else v}" for k, v in mods.items()))
    print("Tools     " + ", ".join(f"{k}={'✓' if v else '✗'}" for k, v in tools.items()))
    for n in hw.notes:
        print("note      " + n)


def _voices(a):
    from . import tts
    print(tts.describe_voices(a.lang))


def _styles(a):
    from . import styles
    for k in styles.PRESETS:
        s = styles.get(k)
        print(f"{k:14s} {s['aspect']:5s} grade={s['grade']:12s} captions={s['captions']:12s} music={s['music']:13s} "
              f"voice={s['delivery']:14s} transitions={'/'.join(s['transitions'])}")
    print("\naliases: " + ", ".join(f"{k}->{v}" for k, v in styles.ALIASES.items()))


def _new(a):
    from . import project
    d = Path(a.out or project.slug(a.topic))
    d.mkdir(parents=True, exist_ok=True)
    f = d / "project.yaml"
    if f.exists() and not a.force:
        sys.exit(f"{f} exists (use --force)")
    f.write_text(project.skeleton(a.topic, a.lang, a.duration, a.format, a.style), encoding="utf-8")
    n, w = project.plan_scenes(a.duration, a.lang, a.style)
    print(f"{f}\n{n} scenes x ~{w} words. Fill the TODOs, then: rea-studio make {f}")


def _make(a):
    from .pipeline import Build
    b = Build(a.project, preview=a.preview, allow_placeholder=a.allow_placeholder, commercial=a.commercial,
              image_preset=a.image_model, motion_override=a.motion, out_dir=a.out)
    r = b.run(until=a.until)
    print(json.dumps({k: r.get(k) for k in ("output", "thumbnail", "srt", "seconds", "voices", "subtitle_timing",
                                             "loudness", "commercial_safe", "warnings", "build_time_s")},
                     indent=2, ensure_ascii=False, default=str))


def _tts(a):
    from . import tts
    text = Path(a.file).read_text(encoding="utf-8") if a.file else a.text
    sp = tts.synthesize(text, a.lang, a.voice, a.gender, a.delivery, a.speed, a.engine, a.commercial)
    tts.save_wav(a.out, sp.audio)
    if a.master:
        from . import audio
        audio.loudnorm(Path(a.out), Path(a.out).with_suffix(".mastered.wav"), -16, -1.5, 7)
    print(json.dumps({"out": a.out, "voice": f"{sp.voice.engine}:{sp.voice.id}", "seconds": round(sp.duration, 2),
                      "license": sp.license, "sentences": sp.sentences}, indent=2, ensure_ascii=False))


def _image(a):
    from . import images
    from .hardware import detect
    g = images.ImageGenerator(a.model or images.default_preset(detect().tier))
    out = g.generate(a.prompt + (", " + a.style if a.style else ""), Path(a.out), a.aspect, a.seed)
    print(out)


def _animate(a):
    from . import motion, project
    W, H = project.RES[a.aspect] if not a.preview else project.PREVIEW_RES[a.aspect]
    if a.ai:
        motion.animate_clip(Path(a.image), Path(a.out), a.duration, W, H, a.fps, a.prompt or "", a.move)
    else:
        motion.camera_clip(Path(a.image), Path(a.out), a.duration, W, H, a.fps, a.move)
    print(a.out)


def _music(a):
    from . import audio
    x = audio.musicgen(a.duration, a.prompt or f"{a.mood} instrumental background music") if a.engine == "musicgen" \
        else audio.compose(a.duration, a.mood, a.seed)
    audio.save(Path(a.out), x)
    print(a.out)


def _sfx(a):
    from . import audio
    audio.save(Path(a.out), audio.sfx(a.name, a.seed, a.length))
    print(a.out)


def _subs(a):
    from . import subtitles as ST
    from .util import probe_streams
    words = ST.transcribe(Path(a.media), a.lang, a.model)
    st = probe_streams(a.media)
    v = next((s for s in st["streams"] if s["codec_type"] == "video"), None)
    W, H = (int(v["width"]), int(v["height"])) if v else (1920, 1080)
    aspect = "9:16" if H > W else "16:9"
    cp = ST.caption_params(aspect, a.style)
    cues = ST.chunk(words, cp["max_chars"], cp["max_lines"], cp["max_dur"], cp["max_words"])
    base = Path(a.out or Path(a.media).with_suffix(""))
    ST.write_srt(cues, base.with_suffix(".srt"), cp["max_chars"])
    ST.write_ass(cues, base.with_suffix(".ass"), W, H, a.style, max_chars=cp["max_chars"])
    if a.burn and v:
        from .util import ffmpeg
        assp = str(base.with_suffix(".ass")).replace(":", "\\:")
        ffmpeg("-i", a.media, "-vf", f"subtitles='{assp}'", "-c:a", "copy", str(base) + ".subbed.mp4")
    print(base.with_suffix(".srt"))


def _thumb(a):
    from . import thumbnail
    print(thumbnail.make(Path(a.image), a.text, Path(a.out), a.aspect, a.accent, a.accent_words))


def _clean(a):
    from . import tts
    print(tts.clean_recording(a.src, a.dst))


def _selftest(a):
    from .selftest import run
    sys.exit(run(Path(a.out), quick=a.quick))


def main(argv=None):
    ap = argparse.ArgumentParser(prog="rea-studio", description="Local AI video production studio")
    sp = ap.add_subparsers(dest="cmd", required=True)

    p = sp.add_parser("doctor", help="inspect hardware, engines and tools")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=_doctor)

    p = sp.add_parser("voices", help="list local voices per language (with honesty notes)")
    p.add_argument("--lang")
    p.set_defaults(fn=_voices)

    sp.add_parser("styles", help="list video style presets").set_defaults(fn=_styles)

    p = sp.add_parser("new", help="create a project.yaml skeleton sized to the target duration")
    p.add_argument("topic")
    p.add_argument("--lang", default="en")
    p.add_argument("--duration", type=float, default=60)
    p.add_argument("--format", choices=["16:9", "9:16", "1:1", "4:5"])
    p.add_argument("--style", default="documentary")
    p.add_argument("-o", "--out")
    p.add_argument("--force", action="store_true")
    p.set_defaults(fn=_new)

    p = sp.add_parser("make", help="produce the full video from project.yaml")
    p.add_argument("project")
    p.add_argument("--preview", action="store_true", help="720p, camera moves only, no whisper: fast draft")
    p.add_argument("--allow-placeholder", action="store_true", help="use gradient cards if image gen fails")
    p.add_argument("--commercial", action="store_true", help="refuse non-commercial models (MMS-TTS, MusicGen)")
    p.add_argument("--image-model", choices=["sd15-lcm", "sd15", "sdxl-lightning", "flux-schnell"])
    p.add_argument("--motion", choices=["camera", "animate", "wan"], help="override motion engine for all scenes")
    p.add_argument("--until", choices=["voice", "keyframes"], help="stop early to review")
    p.add_argument("-o", "--out", help="output directory (default <project>/output)")
    p.set_defaults(fn=_make)

    p = sp.add_parser("tts", help="narrate text")
    p.add_argument("text", nargs="?")
    p.add_argument("--file")
    p.add_argument("--lang", default="en")
    p.add_argument("--voice", default="auto")
    p.add_argument("--gender", choices=["male", "female"])
    p.add_argument("--engine", default="auto", choices=["auto", "kokoro", "piper", "mms", "espeak"])
    p.add_argument("--delivery", default="neutral")
    p.add_argument("--speed", type=float)
    p.add_argument("--commercial", action="store_true")
    p.add_argument("--master", action="store_true", help="also write a -16 LUFS mastered copy")
    p.add_argument("-o", "--out", default="voice.wav")
    p.set_defaults(fn=_tts)

    p = sp.add_parser("image", help="generate one image")
    p.add_argument("prompt")
    p.add_argument("--aspect", default="16:9")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--model")
    p.add_argument("--style", help="extra style text")
    p.add_argument("-o", "--out", default="image.png")
    p.set_defaults(fn=_image)

    p = sp.add_parser("animate", help="turn an image into a moving shot")
    p.add_argument("image")
    p.add_argument("--move", default="push_in")
    p.add_argument("--duration", type=float, default=5)
    p.add_argument("--aspect", default="16:9")
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--ai", action="store_true", help="AnimateDiff-Lightning motion (slow on CPU)")
    p.add_argument("--prompt")
    p.add_argument("--preview", action="store_true")
    p.add_argument("-o", "--out", default="shot.mp4")
    p.set_defaults(fn=_animate)

    p = sp.add_parser("music", help="generate background music")
    p.add_argument("--mood", default="documentary")
    p.add_argument("--duration", type=float, default=60)
    p.add_argument("--engine", default="score", choices=["score", "musicgen"])
    p.add_argument("--prompt")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("-o", "--out", default="music.wav")
    p.set_defaults(fn=_music)

    p = sp.add_parser("sfx", help="generate a sound effect")
    p.add_argument("name")
    p.add_argument("--length", type=float)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("-o", "--out", default="sfx.wav")
    p.set_defaults(fn=_sfx)

    p = sp.add_parser("subtitles", help="transcribe any video/audio to SRT + ASS (faster-whisper)")
    p.add_argument("media")
    p.add_argument("--lang")
    p.add_argument("--model", default="small")
    p.add_argument("--style", default="clean")
    p.add_argument("--burn", action="store_true")
    p.add_argument("-o", "--out")
    p.set_defaults(fn=_subs)

    p = sp.add_parser("thumbnail", help="make a thumbnail from an image")
    p.add_argument("image")
    p.add_argument("--text", required=True)
    p.add_argument("--aspect", default="16:9")
    p.add_argument("--accent", default="yellow")
    p.add_argument("--accent-words", nargs="*")
    p.add_argument("-o", "--out", default="thumbnail.jpg")
    p.set_defaults(fn=_thumb)

    p = sp.add_parser("clean-audio", help="denoise + level a human voice recording")
    p.add_argument("src")
    p.add_argument("dst")
    p.set_defaults(fn=_clean)

    p = sp.add_parser("selftest", help="run the end-to-end acceptance tests")
    p.add_argument("--out", default=str(Path.home() / ".rea-studio" / "selftest"))
    p.add_argument("--quick", action="store_true", help="skip AI image/video generation")
    p.set_defaults(fn=_selftest)

    a = ap.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
