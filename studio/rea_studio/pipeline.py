"""End-to-end production: project.yaml -> finished MP4 (+ SRT/ASS, thumbnail, credits, report).

Stages (each cached under <project>/work, so re-running after an edit only redoes what changed):
  voice -> timeline -> keyframes -> clips -> music -> sfx -> subtitles -> assemble -> master -> thumbnail
"""
from __future__ import annotations

import gc
import json
import shutil
import time
from pathlib import Path

import numpy as np

from . import audio as A
from . import images as I
from . import motion as M
from . import project as P
from . import styles as S
from . import subtitles as ST
from . import thumbnail as T
from . import tts
from .hardware import detect
from .util import ffmpeg, log, probe_duration, stable_hash

WHISPER_GOOD = {"en", "fr", "es", "pt", "it", "de", "hi"}


class Build:
    def __init__(self, project_path: str | Path, preview: bool = False, allow_placeholder: bool = False,
                 commercial: bool = False, image_preset: str | None = None, motion_override: str | None = None,
                 out_dir: str | Path | None = None):
        self.p = P.load(project_path)
        self.style = self.p["_style"]
        self.preview = preview
        self.allow_placeholder = allow_placeholder
        self.commercial = commercial or bool(self.p.get("commercial"))
        self.hw = detect()
        self.image_preset = image_preset or self.p.get("image_model") or I.default_preset(self.hw.tier)
        self.motion_override = motion_override
        self.W, self.H = P.resolution(self.p, preview)
        self.fps = int(self.p["fps"])
        self.root = Path(self.p["_dir"])
        self.work = self.root / "work"
        self.out = Path(out_dir) if out_dir else self.root / "output"
        self.name = P.slug(self.p.get("output_name") or self.p["title"]) + ("-preview" if preview else "")
        self.report: dict = {"title": self.p["title"], "language": self.p["language"], "format": self.p["format"],
                             "style": self.style["name"], "resolution": f"{self.W}x{self.H}", "fps": self.fps,
                             "hardware": self.hw.to_dict(), "stages": {}, "licenses": set(), "warnings": []}
        self._imggen = None

    # ------------------------------------------------------------------ helpers
    def _cached(self, path: Path, key: str) -> bool:
        k = path.with_name(path.name + ".key")
        return path.exists() and k.exists() and k.read_text() == key

    def _mark(self, path: Path, key: str):
        path.with_name(path.name + ".key").write_text(key)

    def _stage(self, name: str, t0: float):
        self.report["stages"][name] = round(time.time() - t0, 1)
        log(f"✓ {name} ({self.report['stages'][name]} s)")

    # ------------------------------------------------------------------ 1. voice
    def voice(self):
        t0 = time.time()
        vcfg = self.p["voice"]
        (self.work / "vo").mkdir(parents=True, exist_ok=True)
        self.vo = []
        for s in self.p["scenes"]:
            wav = self.work / "vo" / f"{s['id']}.wav"
            meta = wav.with_suffix(".json")
            if s.get("voice_file"):  # human / authorised recording
                key = stable_hash("file", s["voice_file"], Path(s["voice_file"]).stat().st_mtime)
                if not self._cached(wav, key):
                    tts.clean_recording(s["voice_file"], wav)
                    d = probe_duration(wav)
                    meta.write_text(json.dumps({"sentences": [[0, d, s.get("narration", "")]], "voice": "recording",
                                                "license": "user recording"}))
                    self._mark(wav, key)
            elif s["narration"].strip():
                speaker = s.get("speaker")
                cv = (self.p["characters"].get(speaker) or {}) if speaker else {}
                voice = s.get("voice") or cv.get("voice") or vcfg.get("voice", "auto")
                gender = cv.get("gender") or vcfg.get("gender")
                delivery = s.get("delivery") or vcfg.get("delivery") or self.style["delivery"]
                speed = float(s.get("speed") or vcfg.get("speed") or 1.0)
                engine = vcfg.get("engine", "auto")
                key = stable_hash(s["narration"], voice, gender, delivery, speed, engine, self.p["language"],
                                  self.commercial, 3)
                if not self._cached(wav, key):
                    sp = tts.synthesize(s["narration"], self.p["language"], voice, gender, delivery, speed, engine,
                                        self.commercial)
                    tts.save_wav(wav, sp.audio)
                    meta.write_text(json.dumps({"sentences": sp.sentences, "voice": f"{sp.voice.engine}:{sp.voice.id}",
                                                "license": sp.license}, ensure_ascii=False))
                    self._mark(wav, key)
            else:
                self.vo.append(None)
                continue
            m = json.loads(meta.read_text())
            import soundfile as sf
            a, sr = sf.read(str(wav), dtype="float32")
            if a.ndim > 1:
                a = a.mean(1)
            self.vo.append({"audio": a, "sentences": m["sentences"], "voice": m["voice"]})
            self.report["licenses"].add(m["license"])
        voices = sorted({v["voice"] for v in self.vo if v})
        self.report["voices"] = voices
        if any(v.startswith("mms:") for v in voices):
            self.report["warnings"].append("Narration uses Meta MMS-TTS (CC-BY-NC-4.0): non-commercial use only.")
        if any(v.startswith("espeak:") for v in voices):
            self.report["warnings"].append("Narration uses eSpeak NG (robotic formant voice).")
        self._stage("voice", t0)

    # ------------------------------------------------------------------ 2. timeline
    def timeline(self):
        st = self.style
        td_default = float(st["transition_duration"])
        lo, hi = st["scene_seconds"]
        t = 0.0
        self.tl = []
        n = len(self.p["scenes"])
        for i, s in enumerate(self.p["scenes"]):
            tr = s.get("transition") or st["transitions"][i % len(st["transitions"])]
            td = 0.04 if tr == "cut" else float(s.get("transition_duration", td_default))
            lead = float(s.get("lead_in", max(0.3, td * 0.6)))
            vo = self.vo[i]
            vo_len = len(vo["audio"]) / tts.SR if vo else 0.0
            tail = float(s.get("pause_after", 0.55 if st["delivery"] not in ("energetic",) else 0.25))
            dur = max(vo_len + lead + tail, float(s.get("duration", 0)) or (lo if vo else hi))
            if s.get("duration") and float(s["duration"]) < vo_len + lead:
                self.report["warnings"].append(f"{s['id']}: duration {s['duration']} < narration {vo_len:.1f}s; extended")
            if i == n - 1:
                dur += 1.2  # let the last image breathe under the music fade
            self.tl.append({"id": s["id"], "start": round(t, 3), "dur": round(dur, 3), "lead": lead,
                            "transition": tr, "td": td if i < n - 1 else 0.0})
            t += dur
        self.total = round(t, 3)
        target = self.p.get("duration")
        if target and abs(self.total - float(target)) / float(target) > 0.15:
            self.report["warnings"].append(
                f"runtime {self.total:.0f}s vs requested {float(target):.0f}s: adjust narration length "
                f"(~{languages_wpm(self.p['language'])} words/min)")
        self.report["duration"] = self.total
        log(f"timeline: {len(self.tl)} scenes, {self.total:.1f}s")

    # ------------------------------------------------------------------ 3. keyframes
    def _gen(self) -> I.ImageGenerator:
        if self._imggen is None:
            ip = bool((self.p.get("consistency") or {}).get("ip_adapter")) and bool(self.p["characters"])
            self._imggen = I.ImageGenerator(self.image_preset, ip_adapter=ip)
        return self._imggen

    def character_refs(self):
        """Reference portrait per character (used by IP-Adapter and shown in the report)."""
        refs = {}
        for name, c in self.p["characters"].items():
            if c.get("reference"):
                refs[name] = Path(c["reference"]) if Path(c["reference"]).is_absolute() else self.root / c["reference"]
                continue
            if not (self.p.get("consistency") or {}).get("ip_adapter"):
                continue
            out = self.work / "refs" / f"{name}.png"
            prompt = f"portrait of {c['description']}, neutral background, front view, {self.p['visual_style']}"
            key = stable_hash(prompt, c.get("seed", 0), self.image_preset)
            if not self._cached(out, key):
                self._gen().generate(prompt, out, "1:1", int(c.get("seed", 1)))  # IP scale 0: no reference yet
                self._mark(out, key)
            refs[name] = out
        self.refs = refs

    def keyframes(self):
        t0 = time.time()
        self.character_refs()
        (self.work / "frames").mkdir(parents=True, exist_ok=True)
        self.frames = []
        aspect = self.p["format"]
        for i, s in enumerate(self.p["scenes"]):
            if s.get("image"):
                self.frames.append(Path(s["image"]))
                self.report["licenses"].add("user-supplied images (your rights)")
                continue
            if s.get("video"):
                self.frames.append(None)
                continue
            out = self.work / "frames" / f"{s['id']}.png"
            prompt = I.build_prompt(s, self.p)
            seed = I.scene_seed(s, self.p, i)
            ref = next((self.refs[c] for c in s.get("characters", []) or [] if c in getattr(self, "refs", {})), None)
            neg = s.get("negative") or self.p.get("negative") or I.NEGATIVE
            key = stable_hash(prompt, seed, neg, self.image_preset, aspect, str(ref), 2)
            if not self._cached(out, key):
                try:
                    log(f"keyframe {s['id']} ({i + 1}/{len(self.p['scenes'])}): {prompt[:90]}...")
                    self._gen().generate(prompt, out, aspect, seed, neg, ref)
                except Exception as e:
                    if not self.allow_placeholder:
                        raise RuntimeError(f"image generation failed for {s['id']}: {e}\n"
                                           "Fix the model install (rea-studio doctor) or pass --allow-placeholder.") from e
                    I.placeholder(s["visual"], out, aspect, seed)
                    self.report["warnings"].append(f"{s['id']}: PLACEHOLDER image ({type(e).__name__})")
                self._mark(out, key)
            self.frames.append(out)
        self.report["licenses"].add(f"images: {self.image_preset} - {I.PRESETS[self.image_preset]['license']}")
        self._imggen = None
        gc.collect()
        self._stage("keyframes", t0)

    # ------------------------------------------------------------------ 4. clips
    def clips(self):
        t0 = time.time()
        (self.work / "clips").mkdir(parents=True, exist_ok=True)
        self.clip_paths = []
        moves = self.style["moves"]
        for i, s in enumerate(self.p["scenes"]):
            seg = self.tl[i]
            length = seg["dur"] + seg["td"]
            out = self.work / "clips" / f"{s['id']}_{self.W}x{self.H}.mp4"
            if s.get("video"):
                key = stable_hash("video", s["video"], length, self.W, self.H, self.fps)
                if not self._cached(out, key):
                    ffmpeg("-stream_loop", "-1", "-i", s["video"], "-t", f"{length:.3f}", "-an", "-vf",
                           f"scale={self.W}:{self.H}:force_original_aspect_ratio=increase,crop={self.W}:{self.H},fps={self.fps}",
                           "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", out)
                    self._mark(out, key)
                self.clip_paths.append(out)
                continue
            move = s.get("camera") or moves[i % len(moves)]
            mode = self.motion_override or s.get("motion") or self.p.get("motion") or self.style["motion"]
            if self.preview and mode in ("animate", "wan"):
                mode = "camera"
            focus = tuple(s.get("focus", (0.5, 0.45)))
            key = stable_hash(str(self.frames[i]), self.frames[i].stat().st_mtime, move, mode, length, self.W, self.H,
                              self.fps, focus, 3)
            if not self._cached(out, key):
                log(f"clip {s['id']}: {mode}/{move} {length:.1f}s")
                if mode == "animate":
                    try:
                        M.animate_clip(self.frames[i], out, length, self.W, self.H, self.fps,
                                       prompt=I.build_prompt(s, self.p), move=move,
                                       strength=float(s.get("motion_strength", 0.55)), seed=I.scene_seed(s, self.p, i))
                        self.report["licenses"].add("AnimateDiff-Lightning (CreativeML OpenRAIL-M)")
                    except Exception as e:
                        self.report["warnings"].append(f"{s['id']}: AI animation failed ({e}); camera move used")
                        M.camera_clip(self.frames[i], out, length, self.W, self.H, self.fps, move, focus)
                elif mode == "wan":
                    M.wan_clip(self.frames[i], out, length, self.W, self.H, self.fps, I.build_prompt(s, self.p),
                               I.scene_seed(s, self.p, i))
                    self.report["licenses"].add("Wan2.2 (Apache-2.0)")
                else:
                    M.camera_clip(self.frames[i], out, length, self.W, self.H, self.fps, move, focus,
                                  "lanczos" if self.preview else self.p.get("upscale", "auto"))
                self._mark(out, key)
            self.clip_paths.append(out)
        gc.collect()
        self._stage("clips", t0)

    # ------------------------------------------------------------------ 5. audio beds
    def voice_bus(self) -> np.ndarray:
        bus = np.zeros(int(self.total * A.SR) + A.SR, np.float32)
        for seg, vo in zip(self.tl, self.vo):
            if vo:
                i = int((seg["start"] + seg["lead"]) * A.SR)
                bus[i:i + len(vo["audio"])] += vo["audio"][: len(bus) - i]
        return bus

    def music(self) -> np.ndarray | None:
        t0 = time.time()
        mc = self.p["music"]
        if mc.get("enabled") is False or mc.get("engine") == "none":
            return None
        n = len(self.voice_bus_)
        out = self.work / "music.wav"
        mood = mc.get("mood") or self.style["music"]
        engine = mc.get("engine", "score")
        if self.commercial and engine == "musicgen":
            self.report["warnings"].append("--commercial: MusicGen (CC-BY-NC) replaced by the procedural score")
            engine = "score"
        key = stable_hash(engine, mood, mc.get("prompt"), mc.get("file"), round(self.total, 2), self.p["seed"], 2)
        import soundfile as sf
        if not self._cached(out, key):
            if mc.get("file"):
                f = Path(mc["file"]) if Path(mc["file"]).is_absolute() else self.root / mc["file"]
                tmp = self.work / "music_src.wav"
                ffmpeg("-i", f, "-ar", str(A.SR), "-ac", "2", tmp)
                x, _ = sf.read(str(tmp), dtype="float32")
                x = A._loop_to(x, self.total)
                lic = "user-supplied music (your rights)"
            elif engine == "musicgen":
                prompt = mc.get("prompt") or f"{mood} cinematic background music, instrumental, no vocals"
                x = A.musicgen(self.total, prompt, int(self.p["seed"]))
                lic = "MusicGen-small (CC-BY-NC-4.0: non-commercial)"
            else:
                x = A.compose(self.total, mood, int(self.p["seed"]))
                lic = "procedural score by rea-studio (original, royalty-free)"
            A.save(out, x)
            out.with_suffix(".lic").write_text(lic)
            self._mark(out, key)
        self.report["licenses"].add(out.with_suffix(".lic").read_text())
        x, _ = sf.read(str(out), dtype="float32")
        m = np.zeros((n, 2), np.float32)
        m[: min(n, len(x))] = x[:n]
        self._stage("music", t0)
        return m

    def sfx_bus(self) -> np.ndarray:
        n = len(self.voice_bus_)
        bus = np.zeros((n, 2), np.float32)
        auto_whoosh = self.style["transitions"][0] in ("slideleft", "smoothleft", "zoomin", "wipeleft", "slideup")
        for i, (s, seg) in enumerate(zip(self.p["scenes"], self.tl)):
            items = list(s.get("sfx", []) or [])
            if auto_whoosh and i > 0 and seg["transition"] != "cut" and not s.get("no_auto_sfx"):
                items.append(f"whoosh@{-0.35}")
            for it in items:
                name, _, at = str(it).partition("@")
                gain = 0.0
                if ":" in name:  # e.g. ambience:ocean or ocean:-6
                    a, b = name.split(":", 1)
                    name, gain = (b, -10.0) if a == "ambience" else (a, float(b))
                start = seg["start"] + (float(at) if at else 0.0)
                if name in A.AMBIENCES:
                    clip = A.sfx(name, i, seg["dur"] + seg["td"])
                    gain += -12.0
                else:
                    clip = A.sfx(name, i)
                A.place(bus, clip, max(0.0, start), gain)
        return bus

    # ------------------------------------------------------------------ 6. subtitles
    def subtitles(self):
        t0 = time.time()
        words: list[ST.Word] = []
        for seg, vo in zip(self.tl, self.vo):
            if not vo:
                continue
            off = seg["start"] + seg["lead"]
            words += ST.words_from_sentences([(a + off, b + off, t) for a, b, t in vo["sentences"]])
        lang = self.p["language"]
        wl = {"pt-br": "pt"}.get(lang, lang)
        mode = (self.p.get("subtitles") or {}).get("align", "auto")
        self.report["subtitle_timing"] = "script"
        if mode in ("auto", "whisper") and wl in WHISPER_GOOD and words and not self.preview:
            try:
                vo_path = self.work / "voice_bus.wav"
                A.save(vo_path, self.voice_bus_)
                refined, ratio = ST.refine_with_whisper(words, vo_path, wl)
                if ratio >= 0.6:
                    words = refined
                    self.report["subtitle_timing"] = f"whisper word-aligned ({ratio:.0%} words matched)"
                else:
                    self.report["subtitle_timing"] = f"script (whisper matched only {ratio:.0%})"
            except Exception as e:
                self.report["warnings"].append(f"whisper alignment skipped: {type(e).__name__}: {e}")
        cs = (self.p.get("subtitles") or {}).get("style") or self.style["captions"]
        cp = ST.caption_params(self.p["format"], cs)
        cues = ST.chunk(words, cp["max_chars"], cp["max_lines"], cp["max_dur"], cp["max_words"])
        overlays = []
        title_end = 0.0
        if self.p.get("title_card", True) and self.tl:
            title_end = min(self.tl[0]["dur"] * 0.6, 4.0)
            overlays.append({"start": 0.25, "end": title_end, "text": self.p["title"], "style": "Title"})
        for i, (s, seg) in enumerate(zip(self.p["scenes"], self.tl)):
            for key, default in (("title", "Chapter"), ("lower_third", "Lower"), ("top_text", "Top")):
                if s.get(key):
                    style = s.get("title_style", default)
                    start = seg["start"] + 0.2 + (self.tl[i - 1]["td"] * 0.5 if i else 0)
                    if style in ("Title", "Chapter"):
                        start = max(start, title_end + 0.3)  # never stack on the opening title card
                    end = seg["start"] + seg["dur"] - 0.2
                    end = min(end, start + float(s.get("text_duration", 4.0)))
                    if end - start > 0.8:
                        overlays.append({"start": start, "end": end, "text": str(s[key]), "style": style})
        self.out.mkdir(parents=True, exist_ok=True)
        self.srt = ST.write_srt(cues, self.out / f"{self.name}.srt", cp["max_chars"])
        self.ass = ST.write_ass(cues, self.work / "captions.ass", self.W, self.H, cs, overlays, cp["max_chars"])
        shutil.copy(self.ass, self.out / f"{self.name}.ass")
        self.burn_subs = (self.p.get("subtitles") or {}).get("burn", True)
        if not self.burn_subs:  # still burn titles; captions stay soft
            self.ass = ST.write_ass([], self.work / "titles.ass", self.W, self.H, cs, overlays)
        self._stage("subtitles", t0)

    # ------------------------------------------------------------------ 7. assemble
    def assemble(self) -> Path:
        t0 = time.time()
        inputs, chain = [], []
        for c in self.clip_paths:
            inputs += ["-i", str(c)]
        prev = "[0:v]"
        for i in range(1, len(self.clip_paths)):
            seg_prev = self.tl[i - 1]
            tr = self.tl[i]["transition"]
            name = "fade" if tr == "cut" else tr
            off = self.tl[i]["start"]
            lbl = f"[x{i}]"
            chain.append(f"{prev}[{i}:v]xfade=transition={name}:duration={seg_prev['td']:.3f}:offset={off:.3f}{lbl}")
            prev = lbl
        grade = S.grade_chain(self.style, self.W, self.H)
        ass = str(self.ass).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
        from .util import font_dirs_for_libass
        fd = next(iter(font_dirs_for_libass()), None)
        fontsdir = f":fontsdir='{str(fd)}'" if fd else ""
        chain.append(f"{prev}{grade},subtitles='{ass}'{fontsdir},format=yuv420p[v]")
        silent = self.work / f"video_{self.W}x{self.H}.mp4"
        crf = "21" if self.preview else str(self.p.get("crf", 18))
        ffmpeg(*inputs, "-filter_complex", ";".join(chain), "-map", "[v]", "-t", f"{self.total:.3f}", "-r", str(self.fps),
               "-c:v", "libx264", "-preset", "fast" if self.preview else "medium", "-tune", "film", "-crf", crf,
               "-maxrate", "8M" if self.H >= 1080 or self.W >= 1080 else "5M", "-bufsize", "16M", "-profile:v", "high",
               "-pix_fmt", "yuv420p", silent)
        self.silent = silent
        self._stage("assemble", t0)
        return silent

    # ------------------------------------------------------------------ 8. mix + master + mux
    def master(self) -> Path:
        t0 = time.time()
        music = self.music()
        sfx = self.sfx_bus()
        mc = self.p["music"]
        mix = A.mixdown(self.voice_bus_, music, sfx, float(mc.get("volume_db", self.style["music_db"])),
                        float(self.style["sfx_db"]), float(mc.get("duck_db", 11)))
        raw = self.work / "mix_raw.wav"
        A.save(raw, mix)
        mastered = self.work / "mix_master.wav"
        self.report["loudness"] = A.loudnorm(raw, mastered, float(self.p.get("lufs", self.style["lufs"])))
        A.save(self.work / "stem_voice.wav", self.voice_bus_)
        final = self.out / f"{self.name}.mp4"
        ffmpeg("-i", self.silent, "-i", mastered, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac",
               "-b:a", "256k", "-ar", "48000", "-shortest", "-movflags", "+faststart",
               "-metadata", f"title={self.p['title']}", "-metadata", f"language={self.p['language']}", final)
        self.final = final
        self._stage("master", t0)
        return final

    def thumb(self) -> Path:
        tcfg = self.p.get("thumbnail") or {}
        idx = int(tcfg.get("scene", 1)) - 1
        frames = [f for f in self.frames if f]
        frame = self.frames[idx] if 0 <= idx < len(self.frames) and self.frames[idx] else (frames[0] if frames else None)
        if frame is None:
            frame = self.work / "thumb_src.png"
            ffmpeg("-ss", "1", "-i", self.final, "-frames:v", "1", frame)
        out = self.out / f"{self.name}-thumbnail.jpg"
        T.make(frame, tcfg.get("text", self.p["title"]), out, self.p["format"], tcfg.get("accent", "yellow"),
               tcfg.get("accent_words"))
        return out

    # ------------------------------------------------------------------ run
    def run(self, until: str | None = None) -> dict:
        t_all = time.time()
        log(f"producing '{self.p['title']}' [{self.p['language']}, {self.p['format']}, {self.style['name']}] "
            f"{self.W}x{self.H}@{self.fps} on {self.hw.tier}")
        self.voice()
        self.timeline()
        self.voice_bus_ = self.voice_bus()
        if until == "voice":
            return self.report
        self.keyframes()
        if until == "keyframes":
            return self.report
        self.clips()
        self.subtitles()
        self.assemble()
        final = self.master()
        th = self.thumb()
        info = probe_duration(final)
        self.report.update(output=str(final), thumbnail=str(th), srt=str(self.srt), seconds=round(info, 2),
                           build_time_s=round(time.time() - t_all, 1),
                           commercial_safe=not any("NON-COMMERCIAL" in lic.upper() or "NC-" in lic.upper()
                                                   for lic in self.report["licenses"]))
        self.report["licenses"] = sorted(self.report["licenses"])
        (self.out / f"{self.name}.report.json").write_text(json.dumps(self.report, indent=2, ensure_ascii=False))
        credits = ["Produced locally with rea-studio.", "", "Components and licences:"] + \
                  [f"  - {x}" for x in self.report["licenses"]] + [""] + [f"WARNING: {w}" for w in self.report["warnings"]]
        (self.out / f"{self.name}.CREDITS.txt").write_text("\n".join(credits))
        log(f"done: {final} ({info:.1f}s) in {self.report['build_time_s']}s")
        for w in self.report["warnings"]:
            log("warning: " + w)
        return self.report


def languages_wpm(code: str) -> int:
    from . import languages
    return languages.get(code).words_per_minute
