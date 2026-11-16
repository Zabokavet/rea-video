---
name: storytelling
description: Write and produce story-driven videos locally - short stories, fables, bedtime stories, animated stories, realistic narrative films, screenplays turned into narrated videos - with story structure, recurring characters, consistent look and emotional score. Use when the user asks for a story, tale, screenplay, script with characters, animated story or narrative video. Builds on video-creator and character-consistency (rea-studio CLI).
---

# storytelling

## 1. Story first (write before any prompt)
- Logline: *[character] wants [goal] but [obstacle], so [action] - or else [stakes].*
- Structure for 1-3 min: **Setup** (world + want, 20%) -> **Inciting incident** -> **Rising conflict** (2-3 beats)
  -> **Climax** (darkest moment / choice) -> **Resolution + image that mirrors the opening**.
- Show, don't tell: narration states what the image cannot (thoughts, time jumps); visuals carry action.
- Dialogue: give characters a `voice:` in `characters:` and set `speaker:` on lines they say.
- For screenplay format requests: also save `script.md` (Fountain-style: scene headings, action, dialogue)
  next to project.yaml, then derive scenes from it.

## 2. Production settings
```yaml
style: storytelling        # warm film grade, dissolves, emotional score, calm delivery
# animated look:  style: animated  (stylized 3D)  |  style: 2d (flat vector)
characters: {...}          # REQUIRED for recurring people - see character-consistency
consistency: {ip_adapter: true}
```
- Kids/bedtime: `voice: af_heart`, delivery `calm`, `music: {mood: calm}`, `style: animated`.
- Emotional peaks: `camera: push_in`, `[pause 1.0]`, `music_db` unchanged (ducking handles it).

## 3. Visual continuity checklist
Same character description string every time; same location id for the same place; time of day progresses
logically (`lighting:`); props introduced before they matter. Review `work/frames/` and re-seed outliers.
