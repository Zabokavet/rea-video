---
name: ugc-video
description: Make UGC-style (user-generated-content look) vertical ads and testimonials locally - authentic phone-camera aesthetic, handheld moves, casual conversational voice, karaoke captions, product hooks and CTA. Use for "UGC ad", "TikTok ad", "testimonial style", "influencer style" or native-looking product videos. Builds on video-creator and short-video (rea-studio CLI).
---

# ugc-video

```yaml
style: ugc               # 9:16, neutral grade, handheld, hard cuts, lofi bed at -24 dB, karaoke captions
voice: {voice: af_bella, delivery: conversational}   # EN; pick a natural conversational voice per language
```

## Script pattern (20-40 s)
1. Hook (problem / bold claim): "I didn't believe this $15 thing would fix my mornings..."
2. Problem agitation (1-2 scenes)  3. Product reveal (`image:` the **real product photo**, `camera: push_in_fast`)
4. 2-3 benefits shown, not told  5. Social proof line  6. CTA with `top_text: "Link in bio"`.

## Honesty rules
- Use the user's real product images (`image:`), never invent product features, prices or results.
- Do not imply a real customer said it if it is AI narration; no fake testimonials or reviews presented as
  genuine. Label as "dramatization" (`lower_third:`) when a scene acts out a customer story.
- Never clone a real creator's voice or face. Authorised recordings can be used via `voice_file:`.
- Talking-head (a person speaking to camera, lip-synced) is not generated locally by this studio; offer
  product B-roll + voice, or the user's own phone clips via `video:`.
