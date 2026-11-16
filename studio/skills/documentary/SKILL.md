---
name: documentary
description: Produce documentary videos locally - historical documentaries, biographies, nature, science, true stories, "history of X" - with researched narration, chapter cards, date lower-thirds, archival-style or realistic imagery, depth-parallax Ken Burns moves, measured narration and an understated score. Use when the user asks for a documentary, history video, biography or explainer of real events. Builds on video-creator (rea-studio CLI).
---

# documentary

Follow **video-creator**; documentary specifics:

## Style choice
- `style: documentary` - modern/real-world topics (natural grade, grain 4, dissolves, -16 LUFS).
- `style: historical` - pre-photography eras (painting-realism look, desaturated warm grade, taiko/strings
  `historical` score). For B&W archive feel: `style_overrides: {grade: bw, grain: 10}`.

## Research & accuracy (non-negotiable)
- Use facts you are confident about; date every claim you can. If unsure, say so in narration
  ("historians still debate...") rather than inventing. Never invent quotes - paraphrase.
- Period accuracy in prompts: clothing, architecture, weapons, technology of the era; add anachronisms to
  `negative` (e.g. `modern clothing, cars, electricity poles, plastic`).
- Do not generate fake "photographs" of real people presented as authentic archive. Prefer `historical`
  painting style for real historical figures, and say on screen "illustration" if it could mislead
  (`lower_third: "Illustration"`). Use the user's own archive photos via `image:` when available.

## Structure (3-minute example: ~22 scenes on `historical`)
1. Cold open (hook question / striking image) - 2 scenes
2. Title card (`title_card: true`)
3. Chapters with `title: "Chapter I - 1791"` + `transition: fadeblack` on the chapter's first scene
4. Each chapter: context -> event -> consequence; `lower_third: "Cap-Français, 1791"` for place/date
5. Closing reflection + legacy today - slow `pull_out`
Narration: documentary delivery, 130-150 wpm; `[pause 0.8]` before key reveals.

## Example: `studio/examples/haiti_history_ht.yaml` (Haitian Creole, historical).
