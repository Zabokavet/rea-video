---
name: video-creator
description: Produce a complete, finished MP4 video locally from a one-line request ("Create a 3-minute cinematic documentary in Haitian Creole about the history of Haiti", "make a 45s TikTok in Spanish about saving money"). Writes the concept and script, splits it into scenes, writes visual prompts with a consistent look, generates images and moving shots, narration (English, French, Spanish, Brazilian Portuguese, Haitian Creole and more), music, sound effects, synced subtitles, transitions, colour grade, mastered audio and a thumbnail - all with free, open-source local models via the `rea-studio` CLI. Use for any request to create, generate, produce or render a video; other video skills (documentary, short-video, news-video...) refine this one.
---

# video-creator: local end-to-end video production

You are the director, writer and editor. `rea-studio` is your crew: it runs open-source models locally
(Kokoro / Piper / MMS-TTS voices, Stable Diffusion keyframes, camera-move / depth-parallax / AnimateDiff motion,
procedural score, faster-whisper subtitles, ffmpeg edit + master). No paid APIs, no uploads.

**Deliverable = a playable MP4 on disk** (plus thumbnail, SRT, credits). Never stop at a script or a pile of images.

## 0. Check the studio (once per session)

```bash
rea-studio doctor            # hardware tier, engines, missing tools
rea-studio voices --lang ht  # what voices really exist for the language
rea-studio styles            # style presets
```
If `rea-studio` is missing: `bash studio/install.sh` in the rea-video repo (see `studio/README.md`).
Respect the tier: on `cpu` a keyframe costs ~60-90 s and AI motion (`motion: animate`) ~3-5 min per scene;
camera / parallax moves are seconds. Tell the user the expected render time before a long job.

## 1. Parse the request

Extract: **topic, language, duration, format** (16:9 YouTube / 9:16 Shorts-TikTok-Reels / 1:1 / 4:5), **style**
(documentary, cinematic, historical, news, financial, explainer, youtube, faceless, short, storytelling, animated,
2d, commercial, ugc, inspirational, sports, interview), gender of narrator, commercial use.
Defaults: 16:9, documentary, male narrator, 60 s. If the user plans to monetise, pass `--commercial`
(this refuses non-commercial models - see licences below).

## 2. Plan

```bash
rea-studio new "History of Haiti" --lang ht --duration 180 --style historical -o projects/haiti-history
```
It prints the scene count and **words per scene** for the target runtime. Respect that word budget - runtime
comes from narration length.

## 3. Write project.yaml (the creative work)

Edit `projects/<slug>/project.yaml`. Rules:
- **Script**: hook in the first 5 s (question, surprising fact, or stakes); one idea per scene; concrete images;
  end with a payoff / call to action. Write *natively* in the target language (not translated word-for-word).
  Numbers as words in Haitian Creole. Use `[pause 0.6]` for dramatic beats.
- **visual**: one shot per scene, written like a cinematographer: *shot size + subject + action + setting + light +
  lens*. E.g. `low-angle wide shot of a mountaintop stone fortress, storm clouds parting, golden rim light, 24mm`.
  Under ~50 words (CLIP truncates at 77 tokens: most important words first). No text/logos in images - add text
  with `title:` / `lower_third:` instead.
- **Consistency** (see the character-consistency skill): define `characters:` and `locations:` once with
  fixed descriptions + `seed`, reference them by name in scenes; keep one `visual_style`.
- **camera** per scene to vary rhythm: push_in, pull_out, pan_left/right, tilt_up/down, drift, orbit, handheld,
  push_in_fast, parallax_in, parallax_left/right (depth 2.5D). Wide establishing -> medium -> detail.
- **motion: animate** only for shots where movement sells it (water, fire, crowds, clouds) - it is slow on CPU.
- **sfx**: `[wind]`, `[whoosh@0, impact@0.4]`, `ambience:ocean`. Names: `rea-studio sfx --help` / the list in
  `rea_studio/audio.py` (whoosh impact boom hit riser click pop ding cash shutter typewriter heartbeat glitch
  wind rain crowd fire ocean city room_tone jungle).
- **Text on screen**: `title:` (chapter card), `lower_third:` (names/dates), `top_text:` (hooks for shorts).
- Real material: `image: assets/photo.jpg` or `video: assets/clip.mp4` per scene; `voice_file:` for a human
  recording (auto-cleaned); `music: {file: track.mp3}`.

Full schema + a worked example: `references/project-schema.md` and `studio/examples/*.yaml`.

## 4. Render: draft, review, final

```bash
rea-studio make projects/<slug>/project.yaml --until voice      # check narration length/timing (seconds)
rea-studio make projects/<slug>/project.yaml --until keyframes  # generate images, then LOOK at work/frames/*.png
rea-studio make projects/<slug>/project.yaml --preview          # 720p draft, camera moves only
rea-studio make projects/<slug>/project.yaml                    # final 1080p (cached stages are reused)
```
**Review keyframes yourself** (open the PNGs): wrong era, extra fingers, text artifacts, a character who
changed face -> edit that scene's `visual`, `seed` or `negative` and re-run; only changed scenes regenerate.

## 5. Deliver

Report: path to MP4, duration, voice used (engine + licence), thumbnail and SRT paths, loudness, any warnings
from the JSON summary (placeholders, non-commercial components, timing mismatches). Be honest about
limitations (e.g. Kreyòl voice quality). Outputs live in `projects/<slug>/output/`.

## Licences (tell the user when relevant)
- Commercial-safe: Kokoro voices, eSpeak, procedural score/SFX, SD1.5 DreamShaper + LCM (OpenRAIL-M),
  AnimateDiff-Lightning (OpenRAIL), Real-ESRGAN, Depth-Anything-V2-Small, Wan2.2 (Apache-2.0).
- **Non-commercial**: MMS-TTS (the neural Haitian Creole voice), MusicGen. Piper voices: check each voice's
  MODEL_CARD. `--commercial` enforces this automatically.

## Troubleshooting
- `image generation failed` -> `rea-studio doctor`; first run downloads ~2 GB from Hugging Face.
- Out of memory on CPU -> close other apps; keep `motion: camera`; use `--preview`.
- Wrong pronunciation of a name -> respell phonetically in the narration (e.g. "Toussaint" -> "Too-san").
- Runtime off target -> the warning says by how much; add/remove words, not scenes.
