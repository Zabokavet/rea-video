# The Silent Code: 5 Shorts, ready to upload

Companion Shorts to "How a Narcissist Controls You (The 4 Stages)".
All five are vertical **9:16, 1080×1920, 30 fps, H.264 + AAC, about 65 s each**, loudness about -14 LUFS (YouTube's standard).

| # | File | YouTube title | Pinned comment |
|---|------|---------------|----------------|
| 1 | `videos/silent_code_01_idealization.mp4` | Love Bombing Is Not Love: 10 Signs | Which sign did you miss at the beginning? 👇 |
| 2 | `videos/silent_code_02_devaluation.mp4` | When the Praise Turns Cold: 10 Signs of Devaluation | When did you first notice the change? 👇 |
| 3 | `videos/silent_code_03_discard.mp4` | The Discard: Why They Leave So Coldly — 10 Truths | Did the discard come right after you set a boundary? 👇 |
| 4 | `videos/silent_code_04_hoovering.mp4` | Hoovering: When They Come Back — 10 Rules | Did they come back with "I miss you"? 👇 |
| 5 | `videos/silent_code_05_breaking_the_cycle.mp4` | How to Break the Cycle: 10 Rules | Which rule are you starting with today? 👇 |

`videos/thumb_*.jpg` are still frames you can use as custom thumbnails.

## What is in every video (same for all 5)
- One static top-down shot: an aged parchment book on a dark wooden desk, with a gold frame on the page.
- The script appears line by line in gold serif type (Cormorant Garamond), word for word. The page holds no other text: no subtitles, logo or watermark.
- A right hand in a dark suit sleeve, white cuff and gold cufflink. The index finger slides along each line from left to right as it is spoken, and a thin gold underline follows the fingertip. Between lines the finger moves down to the next line. No face is shown, and there are no cuts or camera moves.
- One narrator voice for the whole series: an adult male with an American accent, slowed and pitched down slightly for a deep, calm delivery, with pauses between lines.
- The same quiet, low ambient pad under every video.

## How it was verified
- Every narrated line was run through a speech recognizer (Whisper) and generated again until the recognizer heard it **word for word** as written. This catches mistakes such as "can wait" being heard as "can't wait".
- The length of each video is forced to 65.0 s by adjusting speaking speed and the pauses between lines.

## Rebuilding / editing
```
pip install piper-tts faster-whisper scipy pillow numpy   # plus ffmpeg
# voice: https://huggingface.co/rhasspy/piper-voices  en/en_US/ryan/high (en_US-ryan-high.onnx + .json)
python3 src/build_all.py --voice en_US-ryan-high.onnx            # all 5
python3 src/build_all.py --voice en_US-ryan-high.onnx --only 3   # just one
```
Change the script text in `src/scripts.py`. Pronunciation tweaks that change only the audio, never the text on screen, are in `TTS_FIX` in `src/audio.py`.

Font: Cormorant Garamond (SIL Open Font License, see `assets/fonts/OFL-LICENSE.txt`). Voice: Piper "ryan" (en_US).
