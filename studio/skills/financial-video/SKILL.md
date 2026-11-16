---
name: financial-video
description: Create financial-education videos locally - personal finance, investing basics, budgeting, crypto explainers, economics, money tips - with clean modern visuals, number callouts, charts-as-images, confident narration and a disclaimer. Use when the user asks for finance, money, investing, budgeting or economics videos in any format. Builds on video-creator (rea-studio CLI).
---

# financial-video

```yaml
style: financial          # clean cool grade, smooth transitions, light corporate score, conversational voice
# shorts: style: short + subtitles {style: karaoke}
```

## Content rules
- Educational, not advice: include near the end a scene with
  `lower_third: "Educational content - not financial advice"` (localise it).
- Show the numbers: put key figures in `top_text:` / `title:` ("$100/month x 30 years = $150,000 at 7%") and
  **compute them correctly** (state assumptions: rate, compounding, period). Double-check arithmetic.
- Concrete examples with relatable amounts in the audience's currency (HTG, EUR, BRL, USD...).
- Visual prompts: `clean desk with notebook and coins, soft window light`, `stylized bar chart made of gold coins
  rising`, `family at kitchen table reviewing a budget`. No real logos/brands; no fake screenshots of real apps.
- For a real chart: make it with matplotlib to a PNG and use `image: chart.png` (generated images cannot draw
  accurate charts).
