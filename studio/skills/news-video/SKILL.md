---
name: news-video
description: Produce news-report and news-recap videos locally - headline open, anchor-style narration, lower-thirds with places/dates/sources, boxed captions, news bed music, slide transitions - in any supported language. Use when the user asks for a news report, news recap, bulletin, breaking-news style or current-events video. Builds on video-creator (rea-studio CLI).
---

# news-video

```yaml
style: news              # clean grade, boxed captions, slide/wipe transitions, pulsing news bed at -24 dB
voice: {delivery: news}  # e.g. en: am_michael / af_heart, fr: ff_siwis / fr_FR-tom-medium, es: em_alex
```

## Format
- Open: `top_text: "BREAKING"` or headline card; first line = the 5 W's in one sentence.
- Each story: 2-4 scenes; `lower_third: "PORT-AU-PRINCE · 16 NOV 2026"`; attribute claims ("according to ...").
- Close with "what happens next".

## Accuracy & ethics (strict)
- Only report facts the user provided or you are certain of; your knowledge has a cutoff - ask the user for
  sources on current events and cite them in narration or lower-thirds.
- Use generic, clearly illustrative imagery for events (no fabricated photos of real people at real events).
  Add `lower_third: "Illustration"` when an image depicts a specific real event.
- Never imitate a real network's branding, logo, anchors or name.
