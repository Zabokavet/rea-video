---
name: subtitle-generator
description: Generate accurate subtitles and captions locally - SRT and styled ASS, word-level timing, karaoke word highlight for shorts, burned-in or soft - for rea-studio projects or for ANY existing video/audio file via faster-whisper (99 languages). Use for "add subtitles", "captions", "transcribe", "SRT", "burn captions", or caption styling requests.
---

# subtitle-generator

## Existing video or audio
```bash
rea-studio subtitles input.mp4 --lang fr                  # -> input.srt + input.ass
rea-studio subtitles input.mp4 --lang en --style karaoke --burn   # -> input.subbed.mp4 with burned captions
rea-studio subtitles podcast.mp3 --model medium           # better accuracy, slower (small is the default)
```
Models: tiny/base (fast), small (default, good), medium / large-v3 (best, slow on CPU). Omit `--lang` to
auto-detect. Haitian Creole ASR in Whisper is weak: for Kreyòl, prefer subtitles from a known script.

## Inside a project (automatic)
Sentence timing is exact (each sentence is synthesised separately); word timing is refined with faster-whisper
when the language is reliable (en fr es pt it de hi), otherwise distributed by syllables. Configure:
```yaml
subtitles: {style: karaoke, align: auto, burn: true}
```
Styles: `clean` (white + outline), `documentary`, `cinematic` (serif, lives in the letterbox bar), `news` (boxed),
`bold` (big uppercase, shorts), `karaoke` (bold + current word highlighted yellow and popped).
Line rules: <= 42 chars x 2 lines (16:9), <= 24 (9:16), 2-4 words per caption for karaoke, <= 6 s per cue.

## Editing
Fix text in the generated `.srt`/`.ass` and re-burn:
`ffmpeg -i video.mp4 -vf "subtitles=file.ass" -c:a copy out.mp4`. To change narration itself, edit
project.yaml and re-run `rea-studio make` (subtitles regenerate).
