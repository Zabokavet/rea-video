# rea-studio: a local AI video production studio

Turn a one-line request into a finished, edited MP4: script, scenes, AI images, camera moves and AI motion,
natural narration in many languages (including **Haitian Creole**), music, sound effects, synced subtitles,
colour grade, mastered audio and a thumbnail. Everything runs on your computer with free, open-source models:
no API keys, subscriptions, credits or uploads.

```
"Create a 2-minute historical documentary in Haitian Creole about the history of Haiti, 16:9."
          │  Claude Code + skills (video-creator, documentary, multilingual-video ...)
          ▼
 project.yaml ──► voice ──► timeline ──► keyframes ──► clips ──► subtitles ──► edit + grade ──► mix + master ──► MP4 + thumbnail
                 Kokoro     narration     SD1.5+LCM     camera /    whisper /    ffmpeg xfade,     score/MusicGen,
                 Piper      drives        (SDXL/FLUX    parallax /  script       libass,           SFX, ducking,
                 MMS-TTS    scene         on GPU)       AnimateDiff timing       LUT-style grade   -14/-16 LUFS
                 eSpeak     lengths       Real-ESRGAN   (Wan on GPU)
```

## Install

Requirements: ffmpeg, Python 3.10–3.12 (or [uv](https://docs.astral.sh/uv/)), ~15 GB of disk, 8 GB of RAM (16 GB recommended).
Optional: espeak-ng (needed for Kokoro's non-English voices and the eSpeak Kreyòl voice).

```bash
# Ubuntu/Debian: sudo apt install ffmpeg espeak-ng      macOS: brew install ffmpeg espeak-ng
bash studio/install.sh --models core     # CLI + engines + fonts + skills + model pre-download (~6 GB)
rea-studio doctor                        # what your machine can run
rea-studio selftest                      # end-to-end acceptance test (~10 min on CPU)
```
The installer never uses sudo. It creates `~/.rea-studio/venv`, links `rea-studio` into `~/.local/bin`, and links
the 16 skills into `~/.claude/skills` (Claude Code) and `~/.agents/skills`. Inside this repo, the skills are also
available through `.claude/skills/`. Windows: use WSL2 (Ubuntu).

## Use it with Claude Code

Ask in plain words, for example:

> Create a video about **the Citadelle Laferrière** in **Haitian Creole**, lasting **2 minutes**, in **16:9**.
> Make a 45-second TikTok in Spanish about saving money.
> Turn this script into a French news report with subtitles.

Claude loads the **video-creator** skill (plus the matching style skill), writes `projects/<slug>/project.yaml`,
renders a draft, checks the keyframes, and renders the final MP4 to `projects/<slug>/output/`.

## Use it directly

```bash
rea-studio new "History of Haiti" --lang ht --duration 120 --style historical -o projects/haiti
# edit projects/haiti/project.yaml (narration + visual per scene)
rea-studio make projects/haiti/project.yaml --preview   # fast 720p draft
rea-studio make projects/haiti/project.yaml             # final 1080p
```
Building blocks: `rea-studio tts | image | animate | music | sfx | subtitles | thumbnail | clean-audio`;
`rea-studio voices --lang <code>` and `rea-studio styles` list the options. See
[`skills/video-creator/references/project-schema.md`](skills/video-creator/references/project-schema.md) for
every project.yaml option, and [`examples/`](examples/) for complete projects.

## What is inside (all local, all free)

| Job | Engine | License | Status |
|---|---|---|---|
| Narration, English/French/Spanish/PT-BR/Italian/Hindi | **Kokoro-82M** | Apache-2.0 | installed, tested |
| More voices (male French, es-ES, de…) | **Piper** (piper-tts 1.x) | GPL-3.0 engine; per-voice data licence | installed, tested |
| Haitian Creole neural voice (+1,100 languages) | **Meta MMS-TTS** `facebook/mms-tts-hat` | CC-BY-NC-4.0 (**non-commercial**) | installed, tested |
| Haitian Creole commercial-safe voice | **eSpeak NG** `ht` | GPL-3.0 | installed, tested (robotic) |
| Keyframes (CPU) | DreamShaper 8 (SD1.5) + **LCM-LoRA**, 6 steps | CreativeML OpenRAIL-M | installed, tested |
| Keyframes (GPU) | SDXL-Lightning / FLUX.1-schnell | OpenRAIL++ / Apache-2.0 | code path, needs GPU |
| Character consistency | seeds + bibles + **IP-Adapter** (h94) | Apache-2.0 | code path (downloads on first use) |
| Camera moves, 2.5D parallax | OpenCV + **Depth-Anything-V2-Small** | Apache-2.0 | installed, tested |
| AI motion (CPU-capable) | **AnimateDiff-Lightning** video-to-video | CreativeML OpenRAIL-M | installed, tested |
| AI image-to-video (GPU) | **Wan2.2-TI2V-5B** via diffusers | Apache-2.0 | code path, needs NVIDIA ≥12 GB |
| Upscaling | **Real-ESRGAN x4plus** via spandrel | BSD-3 | installed, tested |
| Music | built-in procedural composer (14 moods) | original output, royalty-free | tested |
| Music (prompted) | MusicGen-small | CC-BY-NC-4.0 (**non-commercial**) | optional |
| Sound effects | built-in procedural SFX (21 types) | original output | tested |
| Subtitles | **faster-whisper** (small) + script timing; SRT/ASS, karaoke | MIT | installed, tested |
| Edit, grade, transitions, master | **FFmpeg** (xfade, libass, loudnorm) | LGPL/GPL | system, tested |

`--commercial` (or `commercial: true`) refuses the non-commercial components; every render writes a
`*.CREDITS.txt` listing the licence of each component used.

### Evaluated and not installed (and why)
- **ComfyUI** (GPL-3): excellent node UI for GPU users, but it duplicates what rea-studio drives directly through
  diffusers, and adds a server to babysit. Recommended as an optional add-on on GPU machines for hand-tuned
  workflows (Wan, FLUX, PuLID).
- **LTX-Video / CogVideoX**: the useful sizes need a ≥12–24 GB GPU. Newer LTX releases use a custom open-weights
  licence that should be read before commercial use. Wan2.2 (Apache-2.0) covers this slot.
- **Coqui XTTS-v2**: Coqui Public Model License (non-commercial); the company closed in 2024; no Kreyòl; Kokoro
  sounds better for the supported languages.
- **Remotion**: source-available, needs a paid company licence for companies with 4+ people, so it isn't free
  open source. FFmpeg + libass cover motion graphics here.
- **Blender, Kdenlive, Shotcut, OpenShot, Audacity**: free (GPL) desktop apps for manual work; not needed by the
  automated pipeline. Install from your OS package manager if you want to hand-edit (`*.srt`, `work/clips`, and
  stems in `work/` import cleanly).
- **MoviePy**: not used; direct FFmpeg filter graphs are faster and more precise.

## Hardware tiers (chosen automatically by `rea-studio doctor`)

| Tier | Keyframe | Motion | 2-min video |
|---|---|---|---|
| CPU only (4 cores, 16 GB) | SD1.5+LCM, ~60–120 s | camera/parallax ~1–2 min per 1080p shot (incl. Real-ESRGAN), AnimateDiff ~4–6 min per shot | ~60–75 min (measured: 2-min, 12-scene film); `--preview` ~20 min |
| GPU ≤8 GB | SD1.5+LCM, ~2 s | AnimateDiff ~20 s per shot | ~5 min |
| GPU 12–16 GB | SDXL-Lightning | + Wan2.2-TI2V-5B | ~10–20 min with Wan |
| GPU ≥24 GB | FLUX.1-schnell | + Wan2.2 at 720p | ~15–30 min with Wan |

## Languages

`rea-studio voices` prints the live list. Summary: **en, fr, es, pt-BR, it, hi** have natural Kokoro voices;
**fr** male, **de** and extra accents come from Piper; **Haitian Creole** has no Kokoro/Piper/XTTS voice anywhere
(checked November 2026). Its best local voice is Meta's MMS-TTS (neural, single male-ish voice, non-commercial),
with eSpeak NG as the commercial-safe robotic fallback. Kreyòl numbers are spelled out automatically (1804 → *mil
uisan kat*). Subtitles for Kreyòl are timed from the script, because Whisper's Kreyòl recognition is weak.

## Files
```
studio/
  install.sh               installer (no sudo)
  rea_studio/              CLI + pipeline (tts, images, motion, audio, subtitles, styles, thumbnail, pipeline)
  skills/<16 skills>/      Claude Code skills (SKILL.md + references)
  examples/*.yaml          complete projects (Kreyòl documentary, English TikTok)
  tests/                   pytest (no model downloads)
  PROGRESS.md              build/test log and the next steps
```
