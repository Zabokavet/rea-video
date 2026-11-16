---
name: cinematic-video
description: Make film-look videos locally - cinematic trailers, short films, mood pieces, epic intros - with anamorphic-style framing, letterbox, teal-orange grade, film grain, depth-parallax camera moves, slow dissolves, epic score and dramatic narration. Use when the user asks for something "cinematic", "like a movie", "film look", a trailer, or a short film. Builds on the video-creator skill and the rea-studio CLI.
---

# cinematic-video

Follow **video-creator** for the pipeline; this skill adds the film grammar.

## Settings
```yaml
style: cinematic          # teal_orange grade, grain 6, vignette, 2.39 letterbox, 24 fps, -16 LUFS, epic score
voice: {gender: male, delivery: cinematic}    # slow, long pauses (bm_george / am_fenrir / am_michael in EN)
music: {mood: epic}       # or tension / emotional / mystery
```

## Shot design (write `visual:` like a DP)
- Open on an **establishing extreme wide** (landscape, skyline), then wide -> medium -> close-up -> detail insert.
- Name the lens & light: `24mm wide`, `85mm portrait, shallow depth of field`, `backlit silhouette`,
  `volumetric god rays through dust`, `rim light`, `blue hour`, `practical lights`, `fog`.
- Camera per scene: `parallax_in` (depth push), `orbit` (reveal), `pull_out` (ending/loneliness),
  `push_in` (tension), `drift` (contemplative). Avoid repeating the same move twice in a row.
- Use `motion: animate` on 1-3 hero shots with natural motion (waves, fire, smoke, clouds, rain, crowds).
- Silence is cinematic: scenes with no narration + `ambience:wind` / `riser` / `impact@0` before a title.
- Trailer structure: hook (2 shots) -> world -> conflict (faster cuts, `transition_duration: 0.4`) ->
  `riser` -> black frame + `impact` + title card -> button line.

## Example scene
```yaml
- narration: "Some walls are built to keep enemies out. [pause 0.8] This one was built to keep freedom in."
  visual: "low-angle extreme wide shot of a colossal stone fortress on a mountain peak, storm clouds parting, golden rim light, 24mm, volumetric light"
  camera: parallax_in
  sfx: ["ambience:wind", "impact@4.5"]
  transition: fadeblack
```
Then `rea-studio make project.yaml --preview`, review, final render.
