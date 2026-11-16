---
name: video-editor
description: Edit and post-produce videos locally with ffmpeg - cut, trim, join, reorder, transitions, speed ramps, colour grading, LUTs, letterbox, upscaling/enhancement, stabilisation, audio cleanup, music ducking, loudness mastering, resize/reframe 16:9 <-> 9:16, export presets for YouTube/TikTok/Instagram. Use for any edit of existing footage or a rendered rea-studio video. Also how to re-edit a rea-studio project.
---

# video-editor

## Re-editing a rea-studio project (preferred)
Change project.yaml (order of scenes, `transition`, `camera`, `duration`, `style_overrides`, music) and re-run
`rea-studio make` - only changed stages re-render. Cached pieces: `work/clips/*.mp4` (graded later),
`work/stem_voice.wav`, `work/music.wav`.

## ffmpeg recipes (any footage)
```bash
# trim (re-encode for frame accuracy)
ffmpeg -ss 00:00:05 -to 00:00:20 -i in.mp4 -c:v libx264 -crf 18 -c:a aac out.mp4
# join same-format clips
printf "file 'a.mp4'\nfile 'b.mp4'\n" > list.txt && ffmpeg -f concat -safe 0 -i list.txt -c copy joined.mp4
# crossfade two clips (A is 8 s long)
ffmpeg -i a.mp4 -i b.mp4 -filter_complex "[0:v][1:v]xfade=transition=dissolve:duration=1:offset=7[v];[0:a][1:a]acrossfade=d=1[a]" -map "[v]" -map "[a]" out.mp4
# grade with a preset from rea_studio/styles.py GRADES, e.g. teal-orange + grain + vignette
ffmpeg -i in.mp4 -vf "colorbalance=rs=-0.05:bs=0.07:rh=0.07:bh=-0.07,eq=contrast=1.09:saturation=1.08,vignette=PI/5,noise=alls=5:allf=t" -c:a copy graded.mp4
# apply a .cube LUT
ffmpeg -i in.mp4 -vf lut3d=film.cube -c:a copy out.mp4
# 16:9 -> 9:16 blurred-background reframe
ffmpeg -i in.mp4 -vf "split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=30[bg];[b]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2" -c:a copy vertical.mp4
# speed ramp 2x / slow motion with interpolation
ffmpeg -i in.mp4 -vf "setpts=0.5*PTS" -af atempo=2 fast.mp4
ffmpeg -i in.mp4 -vf "minterpolate=fps=60:mi_mode=mci,setpts=2*PTS" -an slowmo.mp4
# stabilise (two pass, vidstab if your ffmpeg has it) else deshake
ffmpeg -i in.mp4 -vf deshake stab.mp4
# upscale 720p -> 1080p
ffmpeg -i in.mp4 -vf "scale=1920:1080:flags=lanczos,unsharp=5:5:0.5" -c:a copy up.mp4
```
- AI upscaling of stills/keyframes: Real-ESRGAN x4 runs automatically in rea-studio (`upscale: esrgan`).
- Audio: `rea-studio clean-audio in.wav out.wav` (denoise, de-ess, compress, -16 LUFS);
  mastering for platforms: `-af loudnorm=I=-14:TP=-1.5:LRA=11` (YouTube/TikTok/IG), -16 for podcasts/docs.
- Music ducking under voice: `[music][voice]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400`.

## Export presets
- YouTube 1080p: `-c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -c:a aac -b:a 256k -movflags +faststart`
- TikTok/Reels/Shorts: 1080x1920, 30 fps, same codec, file < 287 MB (TikTok) / < 4 GB (IG)
- Optional desktop editors (manual fine-tuning): Kdenlive or Shotcut (GPL, free); Audacity for audio.
