---
name: faceless-video
description: Create faceless YouTube videos locally - top-10 lists, mysteries, facts, history, motivation, finance, "did you know" channels - with AI narration, AI visuals, captions and music; no presenter or camera needed. Use when the user wants faceless content, a YouTube automation channel video, or narration-over-visuals videos. Builds on video-creator (rea-studio CLI).
---

# faceless-video

Follow **video-creator** with these defaults:
```yaml
style: faceless            # teal-orange, parallax moves, mystery score; or youtube / documentary / financial
format: "16:9"             # make a 9:16 cut-down with the short-video skill
voice: {voice: am_michael, delivery: documentary}   # consistent channel voice: always reuse the same voice id
subtitles: {style: clean}
```

## Formula
- **Hook (0-5 s)**: a curiosity gap - "In 1902, a whole city vanished in 90 seconds." Show the most striking image first.
- **Promise (5-15 s)**: what the viewer will learn.
- **Body**: numbered segments (`title: "#3"` with `title_style: Chapter`) or story beats; change the image every
  4-7 s (one scene each); re-hook every ~60 s ("but the strangest part came next...").
- **Payoff + CTA**: answer the hook; one line asking to subscribe / comment.

## Channel consistency
Keep the same `voice`, `visual_style`, `style`, music mood and thumbnail accent colour across videos
(save them in a template project and copy it). Thumbnail: 3-5 words, one accent word (thumbnail-generator skill).

## Avoid
Reusing other channels' footage or music, cloned voices of real people, misleading claims. All generated
assets here are original; MusicGen output is non-commercial - keep `music.engine: score` for monetised channels.
