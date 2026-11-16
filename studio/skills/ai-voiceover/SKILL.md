---
name: ai-voiceover
description: Generate professional voice-overs and narration locally - natural male/female voices in English (US/UK), French, Spanish, Brazilian Portuguese, Italian, Hindi, Haitian Creole and more - with control of speed, delivery style, pauses, emphasis, per-scene audio files, denoising and broadcast mastering; also clean up human recordings. Use for any TTS, narration, voice-over, audio book, podcast-voice or "read this text" request. Uses rea-studio (Kokoro, Piper, MMS-TTS, eSpeak NG).
---

# ai-voiceover

## Pick the voice honestly
`rea-studio voices --lang <code>` lists every local voice with gender, accent, quality and licence.
Quality ranking: **Kokoro** (most natural) > **Piper** > **MMS-TTS** > **eSpeak** (robotic).
| Language | Best female | Best male | Notes |
|---|---|---|---|
| English | af_heart, bf_emma (UK) | am_michael, am_fenrir, bm_george (UK) | many more |
| French | ff_siwis | fr_FR-tom-medium (Piper) | Kokoro has one FR voice |
| Spanish | ef_dora | em_alex / es_ES-davefx-medium (Spain) | |
| Brazilian Portuguese | pf_dora | pm_alex | |
| Haitian Creole | - (none exists) | hat (MMS, neural, **non-commercial**) / ht (eSpeak, robotic) | see multilingual-video |

## Commands
```bash
rea-studio tts "Text..." --lang en --voice am_michael --delivery documentary -o vo.wav --master
rea-studio tts --file script.txt --lang fr --gender male --delivery conversational -o vo_fr.wav
rea-studio clean-audio raw_recording.wav clean.wav     # denoise + de-ess + compress + -16 LUFS
```
- `--delivery`: documentary (0.92x, long pauses) | cinematic | conversational | news | energetic | calm | neutral
- `--speed 1.1` multiplies the delivery speed. Markup: `[pause 0.8]`, `[breath]`, `[paragraph]`; `...` = hesitation.
- Emotion: there is no emotion slider in these engines - it comes from **writing** (short sentences, punctuation,
  pauses), delivery preset, voice choice (af_nicole is soft, am_fenrir is deep) and Kokoro blends
  (`"af_heart+af_bella"`).
- Per-scene files: inside a project, each scene is rendered to `work/vo/<scene>.wav` with exact sentence timings
  (`.json`); the full narration stem is `work/stem_voice.wav`.
- Every file is polished (high-pass, presence, warmth, 3:1 compression); `--master` adds EBU R128 -16 LUFS.

## Voice cloning (authorised voices only)
**Not installed and not tested by this studio.** If the user owns the voice or has written consent, the vetted
local options are **OpenVoice v2** (MIT, runs on CPU) and **F5-TTS** (code MIT, weights CC-BY-NC); install them in
their own venv following their READMEs, render narration to WAV, then use it via `voice_file:` per scene.
Refuse to clone celebrities, politicians or anyone without consent.
