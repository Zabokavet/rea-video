---
name: youtube-video
description: Produce long-form horizontal YouTube videos locally (16:9, 1080p) - explainers, essays, top lists, tutorials-with-visuals, channel episodes - optimised for retention, with chapters, captions, -14 LUFS audio, a click-worthy thumbnail plus title, description and chapter timestamps. Use when the user asks for a YouTube video or episode. Builds on video-creator (rea-studio CLI).
---

# youtube-video

```yaml
style: youtube            # or documentary / explainer / financial / faceless
format: "16:9"
lufs: -14                 # YouTube normalises to -14 LUFS
subtitles: {style: clean, burn: false}   # upload the SRT as captions (better for SEO), keep video clean
```
Burn captions (`burn: true`) only if the user wants them baked in.

## Retention structure
0-15 s hook + payoff promise -> context -> 3-5 sections with `title:` chapter cards -> pattern interrupts every
45-90 s (new location, `camera: push_in_fast`, sfx `whoosh`/`pop`, on-screen `top_text`) -> recap -> CTA.

## After rendering, write `output/youtube.md` with
- 3 title options (<= 60 chars, keyword first)
- Description: 2-line summary, then **chapters** built from scene start times in `report.json`
  (`0:00 Intro`, ...; first chapter at 0:00, >= 3 chapters, each >= 10 s)
- 10-15 tags, and note the SRT file for upload.
- Thumbnail: `output/<slug>-thumbnail.jpg` (1280x720) - see thumbnail-generator.
