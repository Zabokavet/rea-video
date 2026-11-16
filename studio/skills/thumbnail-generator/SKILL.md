---
name: thumbnail-generator
description: Create click-worthy video thumbnails locally - YouTube 1280x720, Shorts/TikTok covers 1080x1920 - from a generated or supplied image, with punchy grade, big readable headline, accent-coloured keyword, legibility scrim, and optionally a dedicated AI-generated hero image. Use for thumbnail, cover image or poster requests.
---

# thumbnail-generator

Projects make one automatically (`output/<slug>-thumbnail.jpg`) from `thumbnail:` settings:
```yaml
thumbnail: {text: "THE FORTRESS THAT NEVER FELL", accent_words: ["NEVER"], accent: yellow, scene: 3}
```
Standalone:
```bash
rea-studio image "dramatic close-up of an ancient stone fortress, storm clouds, lightning, high contrast, cinematic" --seed 5 -o hero.png
rea-studio thumbnail hero.png --text "THE FORTRESS THAT NEVER FELL" --accent-words NEVER --accent yellow -o thumb.jpg
rea-studio thumbnail hero.png --text "1804" --aspect 9:16 -o cover.jpg
```

## What makes thumbnails work
- 2-5 words, never the full title; one emotional/curiosity keyword in the accent colour.
- One clear subject, big, high contrast; empty area for the text (the scrim darkens the left side on 16:9,
  bottom on 9:16). For a dedicated hero image, prompt for `negative space on the left`.
- Faces with strong emotion work best for people topics; for history/places, scale and drama.
- Check readability at 160 px wide. Avoid text that repeats the title; avoid clutter, logos and misleading imagery.
- Make 2-3 variants (different `--seed`, accent words) for A/B testing.
