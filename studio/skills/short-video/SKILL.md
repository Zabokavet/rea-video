---
name: short-video
description: Create vertical 9:16 short-form videos locally for TikTok, Instagram/Facebook Reels and YouTube Shorts (15-90 s) - fast hook, quick cuts, big word-by-word karaoke captions, energetic voice and music, loud -14 LUFS master. Also cut a long video down into shorts. Use when the user mentions TikTok, Reels, Shorts, vertical video, or a video under ~90 seconds for social media. Builds on video-creator (rea-studio CLI).
---

# short-video

```yaml
style: short              # 9:16, vibrant, karaoke captions, 2-4 s scenes, zoom/slide transitions, energetic
format: "9:16"
duration: 45
voice: {delivery: energetic}        # conversational for calmer niches
subtitles: {style: karaoke}         # word-by-word highlight; "bold" = same without the pop
```

## Rules that matter on short-form
- **First 1.5 s**: visual hook + `top_text:` with the hook as text (many watch muted). No title card:
  `title_card: false`.
- One idea per video. 1-2 sentences per scene; scenes 2-4 s; vary `camera` (push_in_fast, handheld, push_in).
- Keep captions inside safe zones: karaoke captions sit ~30% from bottom, clear of TikTok/Reels UI.
- End with a loop line that flows into the first line, or a one-line CTA.
- Platforms: TikTok <= 10 min (best 21-60 s), Reels <= 90 s for reach, Shorts <= 3 min. Same 1080x1920 file works.

## Cut-down from a long video
Copy the long project's best 6-12 scenes (keep `image:` paths to their `work/frames/*.png` to reuse keyframes),
set `format: "9:16"` and `style: short`, tighten narration, render. Keyframes are re-cropped automatically;
for important subjects set `focus: [x, y]` so the vertical crop keeps them.
