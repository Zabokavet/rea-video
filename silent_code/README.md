# The Silent Code: 20-video generator

This folder holds a procedural pipeline that builds the 20 horizontal (1920×1080, 24 fps) videos for the channel
"The Silent Code". Each video uses a different format, visual style and voice.

## How it works

- `engine.py` handles text-to-speech (local Kokoro TTS), word timing, karaoke captions, procedural music and sound
  effects, ducking, loudness normalisation (-14 LUFS) and H.264/AAC encoding through ffmpeg.
- `draw.py` holds the shared drawing parts: stick figures with poses and faces, props, a frog, a scorpion, a pointing
  hand, chalk and paper textures, and similar.
- `videos/vNN_*.py`: each file is one video. It contains the script (`BEATS`), the voice(s), the music settings and
  its own `Style` class that defines the look.
- `fonts/`: open-licence fonts (Google Fonts OFL/Apache, plus Inter and JetBrains Mono).

## Rendering

```bash
pip install kokoro-onnx soundfile numpy pillow
# model files: kokoro-v1.0.onnx + voices-v1.0.bin (github.com/thewh1teagle/kokoro-onnx releases)
export KOKORO_DIR=/path/to/model/files
python3 engine.py 1 2 3          # render videos -> out/
python3 engine.py time 5         # print the runtime only
python3 engine.py preview 7 3 20 # write still frames at t=3s and t=20s -> build/
```

## Videos

| # | Format | Title | Voice(s) |
|---|--------|-------|----------|
| 1 | Story | The Friend Who Smiled While I Was Falling | am_michael |
| 2 | Stages | The 5 Stages of Losing Yourself in a Relationship | af_sarah |
| 3 | Mistakes | 7 Mistakes That Make Smart People Look Weak | am_puck |
| 4 | Comparison | Quiet Confidence vs Loud Arrogance | bm_george |
| 5 | Documentary | The Psychology of Revenge: Why It Never Heals You | am_onyx |
| 6 | Letter | A Letter to the Man Who Was Always "Fine" | bf_emma |
| 7 | Q&A | Why Do People Lie When the Truth Is Easier? | af_nova |
| 8 | Timeline | How a Manipulator Takes Over Your Life in 90 Days | am_fenrir |
| 9 | Case study | The Coworker Everyone Trusted — Until the Mask Fell | bf_isabella |
| 10 | Dialogue | Your Heart vs Your Mind: Who Should Win? | af_bella + bm_daniel |
| 11 | Myth vs Truth | 5 Lies About Narcissists Everyone Believes | af_jessica |
| 12 | Checklist | The Self-Respect Checklist: 9 Things to Check Every Morning | am_eric |
| 13 | Confession | Confessions of a Former People-Pleaser | af_heart |
| 14 | Fable | The Scorpion and the Frog: Why People Never Really Change | bm_fable |
| 15 | Countdown | 10 Sentences That End an Argument Instantly | am_liam |
| 16 | Before/After | The Day He Stopped Explaining Himself | am_echo |
| 17 | Board lesson | The 4 Laws of Social Power | bm_lewis |
| 18 | White book | 10 Rules of Emotional Control | af_nicole |
| 19 | Interview | A Psychologist Explains Why They Always Come Back | af_kore + bf_alice |
| 20 | Debate | Is Forgiveness Strength or Weakness? | af_sky + bf_lily + am_adam |

The psychologist in video 19 is a fictional, dramatized character and is labelled that way on screen.
