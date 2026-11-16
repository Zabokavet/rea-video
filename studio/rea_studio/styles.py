"""Video style presets: the "director's look book" for each kind of video.

A preset sets visual-prompt suffix, colour grade, captions, transitions, camera language, music mood,
narration delivery, pacing and loudness target. Every key can be overridden in project.yaml.
"""
from __future__ import annotations

GRADES = {
    "neutral": "eq=contrast=1.04:saturation=1.02",
    "documentary": "eq=contrast=1.06:saturation=0.94:gamma=0.98,colorbalance=rm=0.02:bm=-0.02:rh=0.03:bh=-0.03",
    "teal_orange": "colorbalance=rs=-0.05:gs=-0.01:bs=0.07:rm=0.02:bm=-0.02:rh=0.07:gh=0.02:bh=-0.07,eq=contrast=1.09:saturation=1.08",
    "warm_film": "colorbalance=rm=0.05:gm=0.01:bm=-0.05:rh=0.04:bh=-0.04,curves=preset=medium_contrast,eq=saturation=0.95",
    "historical": "eq=saturation=0.55:contrast=1.12:gamma=0.97,colorbalance=rs=0.04:rm=0.06:gm=0.02:bm=-0.07:bh=-0.05",
    "bw": "hue=s=0,eq=contrast=1.22:gamma=0.95",
    "news": "eq=contrast=1.03:saturation=1.05",
    "vibrant": "eq=contrast=1.07:saturation=1.22,unsharp=5:5:0.4",
    "moody": "eq=brightness=-0.03:contrast=1.14:saturation=0.82,colorbalance=bs=0.06:bm=0.03:rh=0.03",
    "financial": "colorbalance=bs=0.03:bm=0.02:rh=0.02,eq=contrast=1.06:saturation=1.0",
    "dreamy": "eq=contrast=0.96:saturation=1.05:brightness=0.02,gblur=sigma=0.6,colorbalance=rh=0.04:bh=0.02",
}

XFADES = ["fade", "dissolve", "fadeblack", "fadewhite", "wipeleft", "wiperight", "wipeup", "slideleft", "slideright",
          "slideup", "smoothleft", "smoothright", "smoothup", "circleopen", "circleclose", "zoomin", "radial",
          "hblur", "pixelize", "distance", "diagtl", "squeezeh", "cut"]

BASE = dict(
    aspect="16:9", grade="neutral", grain=0, vignette=False, letterbox=False, captions="clean",
    transitions=["dissolve"], transition_duration=0.7, moves=["push_in", "drift", "pan_right", "pull_out"],
    music="documentary", music_db=-19, sfx_db=-9, delivery="neutral", lufs=-14,
    visual_suffix="highly detailed, sharp focus, professional photography",
    scene_seconds=(5, 9), wpm_factor=1.0, motion="camera",
)

PRESETS: dict[str, dict] = {
    "documentary": dict(grade="documentary", grain=4, vignette=True, captions="documentary",
                        transitions=["dissolve", "fadeblack", "dissolve"], transition_duration=0.9,
                        moves=["push_in", "parallax_in", "pan_right", "drift", "pull_out", "parallax_left"],
                        music="documentary", delivery="documentary", lufs=-16,
                        visual_suffix="cinematic documentary photograph, natural light, 35mm film, rich detail, "
                                      "realistic, award-winning photojournalism"),
    "cinematic": dict(grade="teal_orange", grain=4, vignette=True, letterbox=True, captions="cinematic",
                      transitions=["fadeblack", "dissolve"], transition_duration=1.0,
                      moves=["parallax_in", "orbit", "push_in", "parallax_right", "drift"],
                      music="epic", delivery="cinematic", lufs=-16, scene_seconds=(6, 10),
                      visual_suffix="cinematic film still, anamorphic lens, dramatic lighting, volumetric light, "
                                    "shallow depth of field, color graded, 8k"),
    "historical": dict(grade="historical", grain=5, vignette=True, captions="documentary",
                       transitions=["fadeblack", "dissolve"], transition_duration=1.0,
                       moves=["push_in", "parallax_in", "pan_left", "drift"], music="historical",
                       delivery="documentary", lufs=-16,
                       visual_suffix="painterly historical realism, period accurate costumes and architecture, "
                                     "dramatic natural light, cinematic composition, full bleed, detailed"),
    "news": dict(grade="news", captions="news", transitions=["slideleft", "wipeleft"], transition_duration=0.45,
                 moves=["push_in", "pan_right", "static"], music="news", music_db=-24, delivery="news",
                 visual_suffix="news photography, realistic, editorial photo, natural light", scene_seconds=(4, 7)),
    "financial": dict(grade="financial", captions="clean", transitions=["smoothleft", "dissolve"],
                      transition_duration=0.55, moves=["push_in", "pan_right", "drift"], music="financial",
                      music_db=-21, delivery="conversational",
                      visual_suffix="clean modern photography, business, finance, soft light, high detail"),
    "explainer": dict(grade="vibrant", captions="clean", transitions=["smoothleft", "zoomin"], transition_duration=0.5,
                      moves=["push_in", "drift", "pan_right"], music="corporate", music_db=-21,
                      delivery="conversational", visual_suffix="clean illustration, bright, modern, high detail"),
    "youtube": dict(grade="teal_orange", grain=2, vignette=True, captions="clean",
                    transitions=["dissolve", "smoothleft", "fadeblack"], transition_duration=0.6,
                    moves=["push_in", "parallax_in", "pan_right", "drift"], music="inspirational", music_db=-20,
                    delivery="conversational"),
    "faceless": dict(grade="teal_orange", grain=3, vignette=True, captions="clean",
                     transitions=["dissolve", "fadeblack"], transition_duration=0.7,
                     moves=["push_in", "parallax_in", "drift", "pan_left"], music="mystery", delivery="documentary"),
    "short": dict(aspect="9:16", grade="vibrant", captions="karaoke", transitions=["zoomin", "slideup", "cut"],
                  transition_duration=0.3, moves=["push_in_fast", "push_in", "handheld", "pan_right"],
                  music="energetic", music_db=-20, delivery="energetic", lufs=-14, scene_seconds=(2, 4),
                  visual_suffix="vertical composition, vivid, high contrast, eye-catching, high detail"),
    "storytelling": dict(grade="warm_film", grain=5, vignette=True, captions="cinematic",
                         transitions=["dissolve", "fadeblack"], transition_duration=0.9,
                         moves=["parallax_in", "push_in", "drift", "pan_right"], music="emotional",
                         delivery="calm", lufs=-16,
                         visual_suffix="cinematic still, emotional storytelling, warm light, realistic, detailed"),
    "animated": dict(grade="vibrant", captions="clean", transitions=["dissolve", "circleopen"], transition_duration=0.7,
                     moves=["push_in", "drift", "pan_right"], music="uplifting", delivery="conversational",
                     visual_suffix="stylized 3D animated film still, soft global illumination, expressive, "
                                   "vibrant colors, family animation style"),
    "2d": dict(grade="vibrant", captions="clean", transitions=["slideleft", "circleopen"], transition_duration=0.5,
               moves=["drift", "push_in"], music="uplifting", delivery="conversational",
               visual_suffix="flat 2D vector illustration, clean shapes, bold colors, motion graphics style"),
    "commercial": dict(grade="vibrant", vignette=True, captions="bold", transitions=["zoomin", "smoothleft", "fadewhite"],
                       transition_duration=0.4, moves=["push_in_fast", "orbit", "push_in"], music="corporate",
                       delivery="energetic", scene_seconds=(2.5, 4.5),
                       visual_suffix="premium product photography, studio lighting, commercial, glossy, sharp"),
    "ugc": dict(aspect="9:16", grade="neutral", captions="karaoke", transitions=["cut"], transition_duration=0.1,
                moves=["handheld"], music="lofi", music_db=-24, delivery="conversational", scene_seconds=(2, 4),
                visual_suffix="smartphone photo, authentic, natural light, casual, realistic"),
    "inspirational": dict(grade="warm_film", grain=3, vignette=True, captions="cinematic",
                          transitions=["dissolve", "fadewhite"], transition_duration=0.9,
                          moves=["parallax_in", "pull_out", "drift"], music="inspirational", delivery="calm",
                          visual_suffix="golden hour, cinematic, hopeful, lens flare, epic landscape, detailed"),
    "sports": dict(grade="vibrant", vignette=True, captions="bold", transitions=["zoomin", "slideleft", "cut"],
                   transition_duration=0.3, moves=["push_in_fast", "handheld", "pan_right"], music="energetic",
                   delivery="energetic", scene_seconds=(2, 4),
                   visual_suffix="sports photography, action shot, motion, stadium lights, high shutter speed"),
    "interview": dict(grade="neutral", captions="clean", transitions=["cut", "dissolve"], transition_duration=0.3,
                      moves=["static", "drift"], music="calm", music_db=-26, delivery="conversational",
                      visual_suffix="interview setup, soft key light, shallow depth of field, realistic portrait"),
}
ALIASES = {"doc": "documentary", "history": "historical", "historical_documentary": "historical", "finance": "financial",
           "education": "explainer", "educational": "explainer", "tiktok": "short", "reels": "short", "shorts": "short",
           "youtube_shorts": "short", "faceless_youtube": "faceless", "story": "storytelling", "ad": "commercial",
           "product": "commercial", "promo": "commercial", "presenter": "interview", "motivational": "inspirational",
           "3d": "animated", "animation": "animated", "realistic_story": "storytelling"}


def get(name: str) -> dict:
    key = ALIASES.get(name, name)
    out = dict(BASE)
    out.update(PRESETS.get(key, {}))
    out["name"] = key if key in PRESETS else "custom"
    return out


def grade_chain(style: dict, W: int, H: int) -> str:
    f = [GRADES.get(style["grade"], style["grade"])]  # allow raw ffmpeg filter strings too
    if style.get("vignette"):
        f.append("vignette=angle=PI/5:mode=forward")
    if style.get("grain"):
        f.append(f"noise=alls={int(style['grain'])}:allf=t")
    if style.get("letterbox") and W > H:
        bar = int((H - W / 2.39) / 2)
        if bar > 0:
            f.append(f"drawbox=x=0:y=0:w=iw:h={bar}:color=black:t=fill,drawbox=x=0:y=ih-{bar}:w=iw:h={bar}:color=black:t=fill")
    return ",".join(f)
