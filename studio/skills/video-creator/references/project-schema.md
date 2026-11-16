# project.yaml reference

```yaml
title: "Istwa Ayiti"            # also the opening title card and default thumbnail text
language: ht                    # en | fr | es | pt-br | ht | it | de | hi (rea-studio voices)
format: "16:9"                  # 16:9 | 9:16 | 1:1 | 4:5 | 21:9
style: historical               # rea-studio styles
duration: 180                   # target seconds (only used for a warning; narration sets real runtime)
fps: 24                         # default 30 (24 for cinematic / storytelling)
seed: 1804                      # global seed
commercial: false               # true = refuse non-commercial models
image_model: sd15-lcm           # sd15-lcm (CPU) | sd15 | sdxl-lightning (GPU 8GB+) | flux-schnell (GPU 16GB+)
motion: camera                  # default for all scenes: camera | animate | wan
upscale: auto                   # auto (Real-ESRGAN if present) | esrgan | lanczos
title_card: true
lufs: -16                       # override loudness target

voice:
  voice: auto                   # or an id from `rea-studio voices`: af_heart, am_michael, ff_siwis,
                                #   fr_FR-tom-medium, pm_alex, em_alex, hat (MMS Kreyòl), ht (eSpeak Kreyòl)
                                #   Kokoro blends: "af_heart+af_bella"; Piper multi-speaker: "fr_FR-upmc-medium:1"
  gender: male                  # used when voice is auto
  delivery: documentary         # documentary | cinematic | conversational | news | energetic | calm | neutral
  speed: 1.0                    # multiplies the delivery's speed
  engine: auto                  # kokoro | piper | mms | espeak

music:
  engine: score                 # score (procedural, royalty-free) | musicgen (CC-BY-NC) | none
  mood: historical              # epic historical documentary inspirational emotional tension mystery calm
                                #   corporate news lofi energetic uplifting financial (+ aliases)
  prompt: "..."                 # musicgen only
  file: assets/track.mp3        # use your own track instead
  volume_db: -19                # music bed level under voice (before ducking)
  duck_db: 11                   # extra attenuation while narration plays

subtitles:
  style: documentary            # clean | documentary | cinematic | news | bold | karaoke (word highlight)
  align: auto                   # auto (whisper when reliable) | whisper | script
  burn: true                    # false = soft subtitles only (titles still burned)

thumbnail:
  text: "1804: LIBÈTE"
  accent_words: ["1804"]
  accent: yellow                # yellow red cyan green orange white
  scene: 3                      # which scene's keyframe to use

style_overrides:                # any style key: grade, grain, vignette, letterbox, transitions,
  letterbox: true               #   transition_duration, moves, music_db, sfx_db, captions, lufs ...
  grade: teal_orange            # or a raw ffmpeg filter string

visual_style: "oil painting realism, period accurate, dramatic chiaroscuro"
negative: "text, watermark, modern clothing, cars"   # optional global negative prompt

consistency:
  ip_adapter: true              # condition frames on a generated (or given) reference portrait per character

characters:
  dessalines:
    description: "Black Haitian general in his 40s, short beard, stern eyes, dark blue 1800s military coat with gold epaulettes, bicorne hat"
    seed: 4242
    voice: am_michael           # for dialogue scenes (speaker: dessalines)
    reference: assets/dessalines.png   # optional: your own reference image

locations:
  citadel:
    description: "massive stone fortress atop a green mountain, northern Haiti, tropical forest"

scenes:
  - id: s01                               # optional
    narration: "Text spoken in this scene. [pause 0.6] More text."
    visual: "aerial wide shot of ..."     # keyframe prompt (or image: / video:)
    characters: [dessalines]
    location: citadel
    lighting: "golden hour, low sun"
    camera: parallax_in
    focus: [0.5, 0.4]                     # where push-ins head (x, y in 0-1)
    motion: animate                       # this scene only
    motion_strength: 0.55                 # animate: 0.4 subtle .. 0.7 strong (less faithful to keyframe)
    transition: fadeblack                 # transition INTO this scene (see styles.XFADES)
    transition_duration: 1.0
    duration: 8                           # minimum seconds (extended if narration is longer)
    pause_after: 0.6
    title: "Chapter I - 1791"             # Chapter card; or lower_third: / top_text:
    title_style: Chapter                  # Title | Chapter | Lower | Top
    sfx: [wind, "impact@0.3", "ambience:ocean"]
    speaker: dessalines                   # use the character's voice
    seed: 77                              # pin a keyframe you liked
    negative: "..."
    image: assets/photo.jpg               # use your own picture instead of generating
    video: assets/clip.mp4                # or your own footage (looped/trimmed to fit)
    voice_file: assets/vo_s01.wav         # human recording instead of TTS (denoised + levelled)
```

## Outputs (`<project>/output/`)
- `<slug>.mp4` - H.264 high profile, yuv420p, AAC 256k, loudness normalised, faststart
- `<slug>-thumbnail.jpg`, `<slug>.srt`, `<slug>.ass`
- `<slug>.report.json` (timings, voices, loudness, warnings), `<slug>.CREDITS.txt` (licences)
- `work/` caches every stage: `vo/`, `frames/`, `clips/`, `music.wav`, `stem_voice.wav`, `mix_master.wav`
