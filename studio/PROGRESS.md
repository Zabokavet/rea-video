# rea-studio progress report

Keep this file current so any later session can continue without redoing work.

## Phase 1: infrastructure (done, 2026-11-16)

Build/test machine: cloud Linux VM, Intel Xeon 4 vCPU, 15.7 GB RAM, **no GPU**, Python 3.12 venv
(`~/.rea-studio/venv`), ffmpeg 6.1 (libass, xfade, loudnorm), espeak-ng 1.51. That machine is the *worst case*
(CPU only), so everything below is proven to run without a GPU.

| Item | State | Evidence |
|---|---|---|
| Installer `studio/install.sh` (no sudo, hardware-aware torch, fonts, skills, `--models core/full`) | done | run on the build machine |
| CLI `rea-studio` (doctor, voices, styles, new, make, tts, image, animate, music, sfx, subtitles, thumbnail, clean-audio, selftest) | done | |
| 16 skills in `studio/skills/` linked to `~/.claude/skills`, `~/.agents/skills`, repo `.claude/skills` | done | discovered by Claude Code |
| Unit tests `studio/tests` (11, no downloads, includes an eSpeak Kreyòl end-to-end render) | 11/11 pass | `pytest -q` |
| Hugging Face downloads | working | needs hosts huggingface.co + *.hf.co CDN |

## Test results (requirement 12)

Voice intelligibility = synthesise -> faster-whisper `small` transcription -> character error rate vs the script.

| # | Test | Result |
|---|---|---|
| 1 | Generate an image locally | PASS: DreamShaper 8 + LCM-LoRA, 864x480, ~60 s (idle CPU) to ~120 s (busy) |
| 2 | Generate a short video locally | PASS: camera/parallax clips; AnimateDiff-Lightning v2v 4 s clip in 5 min (selftest) |
| 3 | English voice-over | PASS: Kokoro af_heart CER 0.0, am_michael CER 0.0 |
| 4 | French voice-over | PASS: Kokoro ff_siwis (F) CER 0.018; Piper fr_FR-tom (M) CER 0.0 |
| 4b | Spanish / Brazilian Portuguese | PASS: Kokoro em_alex CER 0.0; pf_dora CER 0.0 |
| 5 | Haitian Creole narration | PASS with limits: MMS-TTS `hat` CER 0.30 (was 0.40 before clause-level pauses + number spelling), eSpeak `ht` CER 0.33 (Whisper's Kreyòl ASR is weak, so these numbers overstate errors; transcripts are phonetically close, e.g. "Bye vin nina esti diyo" for "Byenvini nan estidyo") |
| 6 | Subtitles | PASS: SRT + ASS, whisper word alignment (en) / script timing (ht) |
| 7-8 | Narration + visuals + music -> MP4 | PASS: see demo renders below |

### Demo renders (in `studio/projects/`, git-ignored)
- `haiti-history/`: **Istwa Ayiti**, 2:02 historical documentary in Haitian Creole, 1080p30, 12 scenes,
  MMS-TTS narration, procedural historical score, SFX, Kreyòl subtitles, chapter cards, AnimateDiff on 2 scenes.
  Keyframe review loop used for real: 6 frames regenerated (picture frames/signatures from "oil painting" wording,
  anachronistic flags, missing fortress) -> the `historical` preset and default negative prompt were fixed.
  Final build: 12 min from cache (51 min for the first full build on CPU); -16.0 LUFS, -4.4 dBTP.
- `haiti-history-fr/`: **Histoire d'Haïti**, the same film in French (Piper fr_FR-tom male voice), reusing the
  Kreyòl keyframes (no image generation); 1:51, Whisper word-aligned subtitles (72% of words matched), -16.0 LUFS.
- `compound-short/`: **The 8th Wonder of the World**, 28 s 1080x1920 TikTok/Reels/Shorts in English (Kokoro
  am_michael, energetic), karaoke captions, hook text, procedural financial score, -14.1 LUFS; 21 min on CPU.

### Bugs found by watching the first full render, now fixed
- AnimateDiff video-to-video defaulted to 512x512 output while the writer expected 512x288, so the raw
  frames went out of alignment (rolling, blocky shots). Size is now passed explicitly and every frame is
  resized defensively; motion-compensated interpolation was replaced by frame blending.
- Subtitle cues split mid-phrase and could span two scenes. Cues now break at sentence ends, pauses longer
  than 0.6 s, and commas or colons when full, and never overlap (regression test added).
- Historical grain was too heavy (file was 279 MB for 2 minutes). Grain is lower now, and the final encode
  uses x264 medium/film at CRF 18 with an 8 Mbit/s cap (YouTube 1080p recommendation); assembly dropped from 21 to 4.7 minutes (measured).

## Known limitations / honest notes
- **Haitian Creole voice**: only MMS-TTS (neural, one voice, 16 kHz source, CC-BY-NC) and eSpeak (robotic)
  exist locally. No female neural Kreyòl voice exists. For commercial Kreyòl videos: eSpeak or a human narrator
  (`voice_file:`).
- SD1.5 cannot draw accurate flags, text or specific real faces; avoid them in prompts (use `title:` overlays).
- On CPU, Wan/LTX/CogVideoX image-to-video is not feasible (text encoders alone need >10 GB RAM, generation would
  take hours). The `wan` motion engine is implemented for NVIDIA GPUs but **untested** (no GPU here).
- IP-Adapter character conditioning and SDXL-Lightning / FLUX presets are implemented but **untested** here
  (IP-Adapter adds ~2.5 GB of downloads; SDXL/FLUX need a GPU).
- MusicGen integration is implemented but was not exercised in this session (non-commercial; procedural score is default).
- PyTorch in the build venv is the CUDA wheel (works on CPU); the installer picks the CPU wheel on GPU-less Linux.

## Next phases
1. On a GPU machine: `rea-studio doctor`, then test `--image-model sdxl-lightning`, `motion: wan`, `consistency.ip_adapter`.
2. Optional: ComfyUI bridge for custom GPU workflows (FLUX + PuLID for identity, Wan 2.2 14B).
3. Talking-head/presenter: evaluate LivePortrait (MIT code; check weights licence) + lip-sync for the interview style.
4. Kreyòl: re-evaluate when a new open Kreyòl TTS appears; consider fine-tuning Piper on an openly licensed Kreyòl corpus.

Full acceptance run: `rea-studio selftest` -> **12/12 passed** (2026-11-16, CPU-only machine).
