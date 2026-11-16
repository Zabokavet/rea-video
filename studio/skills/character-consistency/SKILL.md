---
name: character-consistency
description: Keep characters, faces, clothing, locations, lighting, visual style and voices consistent across every scene of a multi-scene AI video made with rea-studio - character bibles, location bibles, style bible, fixed seeds, IP-Adapter reference portraits, per-character voices and a continuity review loop. Use whenever a video has recurring characters or places, or the user asks for consistency/continuity.
---

# character-consistency

Diffusion models have no memory between images; consistency comes from **repeating identical information** and
**conditioning on references**. rea-studio does the plumbing; you must write the bibles.

## 1. Bibles in project.yaml
```yaml
visual_style: "cinematic realism, warm Caribbean light, 35mm film, muted greens and ochres"   # style bible
characters:
  marie:
    description: "Haitian woman, early 30s, dark skin, short natural hair with a red headwrap, small gold hoop earrings, white linen blouse, oval face, high cheekbones"
    seed: 3141
    gender: female
    voice: af_heart                  # or ff_siwis / pf_dora ... same voice every time she speaks
    reference: assets/marie.png      # optional real/approved reference image
locations:
  market:
    description: "busy open-air market in Port-au-Prince, colourful umbrellas, crates of mangoes, dusty street"
consistency: {ip_adapter: true}
```
- Descriptions: **fixed, specific, visual**: age, skin tone, face shape, hair, 1-2 signature items (headwrap,
  scar, glasses), outfit with colours. Copy-paste, never paraphrase. Changes of outfit = a new character entry
  (`marie_night`).
- Scenes reference `characters: [marie]`, `location: market`; the description + style are injected verbatim.
- `seed` per character makes their scenes start from related noise; pin any scene you like with `seed:`.
- `ip_adapter: true` (SD1.5 presets): generates a neutral portrait per character (`work/refs/`) - or uses
  `reference:` - and conditions every frame containing that character on it (scale 0.55). Approve the portrait
  first (`rea-studio make ... --until keyframes`, look at `work/refs/*.png`); delete it to regenerate.
- Lighting continuity: set `lighting:` per scene to follow time of day logically.

## 2. Review loop (do it, don't skip)
After `--until keyframes`, view all `work/frames/*.png` side by side. For each mismatch: tweak that scene's
`visual` (put the character first), change `seed`, or add `negative: "beard, glasses"`; re-run - only that frame
regenerates. Two characters in one frame drift most: prefer one character per shot, or a wide shot.

## 3. Limits (be honest)
SD1.5 + IP-Adapter gives *strong resemblance*, not identical faces. For production-grade identity on a GPU:
train a character LoRA (kohya_ss, ~15 images) or use FLUX + PuLID/InstantID in ComfyUI. Voices are exactly
consistent (same voice id + delivery).
