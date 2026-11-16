---
name: multilingual-video
description: Produce the same video in several languages, or a video in a specific non-English language - Haitian Creole (Kreyòl Ayisyen), French, Spanish, Brazilian Portuguese, Italian, German, Hindi and more - with native scripts, the right local voice, translated on-screen text and subtitles, reusing the same visuals. Use for translation/localisation/dubbing requests or any video not in English. Builds on video-creator (rea-studio CLI).
---

# multilingual-video

## Language support (truthful, as installed)
| Code | Voice (natural -> fallback) | Subtitle timing |
|---|---|---|
| en | Kokoro (many) / Piper | Whisper word-aligned |
| fr | Kokoro ff_siwis (F), Piper fr_FR-tom (M) | Whisper |
| es | Kokoro ef_dora / em_alex, Piper es_ES / es_MX | Whisper |
| pt-br | Kokoro pf_dora / pm_alex, Piper pt_BR-faber | Whisper |
| it, hi | Kokoro | Whisper |
| de | Piper thorsten (M), eva_k (F) | Whisper |
| **ht** | **MMS-TTS `hat`** (neural, single voice, CC-BY-NC) -> eSpeak `ht` (robotic, commercial-safe) | from script |
| other | MMS-TTS (1,100+ languages, verify `facebook/mms-tts-<iso3>` exists) -> eSpeak | from script |

## Haitian Creole specifics
- No Kokoro / Piper / XTTS / F5 voice exists for Kreyòl (checked 2026-11). MMS-TTS is the best local option:
  intelligible, somewhat flat, 16 kHz (we upsample and master it). It is **non-commercial**. For monetised
  videos: eSpeak `ht` (robotic) or the user's own Kreyòl narrator via `voice_file:` - say this plainly.
- Never fake Kreyòl with a French voice: French voices mispronounce Kreyòl orthography.
- Write in standard orthography (IPN): *mwen, ou, li, nou, yo; è ò à*. Numbers are converted to words
  automatically (1804 -> "mil uisan kat"), but writing them as words is safer.
- Short sentences help MMS prosody; commas become real pauses.

## Localising one video into N languages
1. Finish and approve the master project (e.g. `en`).
2. Copy the folder per language: `cp -r projects/topic projects/topic-fr`.
3. In the copy: set `language`, translate `narration`, `title`, `lower_third`, `top_text`, `thumbnail.text`
   (adapt idioms, units, currency; keep names). **Keep `visual`, seeds and `image:` paths** - point `image:` at the
   master's `work/frames/<id>.png` to reuse keyframes and skip generation.
4. Render each. Runtime differs per language (fr/es/pt ~10-20% longer than en) - scene timing follows narration.
5. Check each SRT against the script.
