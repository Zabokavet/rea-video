from engine import *
from reel_lib import *

TITLE = "Reel 8 - The Daughter Who Was Ashamed of Her Mother's Hands"
OUTDIR = os.path.join(ROOT, "out_reels")
HOOK = "SHE WAS ASHAMED OF HER MOTHER'S HANDS"
KEYWORD = 'TYPE "MOM"'
MUSIC = dict(kind="pad+piano", root=98.0, prog=[0, -4, 3, -2], qual=["m", "M", "M", "M"], bar=8, step=1.0, pat=[0, 2, 3, 1], vol=0.11)
GAP = 1.3
VOICES = {"n": ("af_heart", 0.77)}
POST = dict(title="The Daughter Who Was Ashamed of Her Mother's Hands",
            caption="She hid her mother's scars for years. Then she learned where they came from. 💔\nComment MOM if your mother sacrificed more than you'll ever know — share this with her today. #MothersLove #Family #LifeLessons #MoralStory",
            pinned="What did your mother sacrifice that you only understood later? 👇")
SCAR = hx("c98a7a")
CAST = dict(
    mom=dict(skin=SKIN["light"], hair=hx("6a4a3a"), hair_style="bob", top=hx("b88aa8"), bottom=hx("4a3a4a"), skirt=True, leg=SKIN["light"], age=48, h=880,
             hand=SCAR),
    sophie=dict(skin=SKIN["light"], hair=hx("c9a05a"), hair_style="long", top=hx("8ab4d9"), bottom=hx("3a4a6a"), age=18, h=880),
    friend=dict(skin=SKIN["tan"], hair=hx("2a1d16"), hair_style="bob", top=hx("e8a43a"), bottom=hx("3a3a40"), age=18, h=860),
    aunt=dict(skin=SKIN["light"], hair=hx("8a6a4a"), hair_style="bun", top=hx("7a8a5a"), bottom=hx("3a3a30"), skirt=True, leg=SKIN["light"], age=55, h=860),
    baby=dict(skin=SKIN["light"], hair=hx("c9a05a"), hair_style="short", top=hx("f4e2ea"), bottom=hx("f4e2ea"), age=1, h=300),
)
BGS = dict(
    home=("room", dict(wall=(hx("f6e2ea"), hx("dcb4c4")), floor=hx("8a6a6a"), sky=(hx("fff4f4"), hx("f4c8d4")), curtain=hx("b07a9a"), grade=(255, 220, 230),
                       grade_s=0.06)),
    lawn=("stage", dict(wall=(hx("f4f8ff"), hx("c8d8f0")), floor=hx("6a8a5a"), curtain=hx("3a4a8a"))),
    night=("kitchen", dict(wall=(hx("6a5a7a"), hx("2a2236")), floor=hx("3a3036"), night=True, sky=(hx("0e1026"), hx("2a2a4a")), cab=hx("8a7a8a"),
                           win=(70, 330, 430, 900))),
    fire=("bedroom", dict(wall=(hx("ff9a4a"), hx("8a2a1a")), floor=hx("3a2020"), night=True, sky=(hx("2a0a0a"), hx("6a2a1a")), bed=hx("c8a8a0"),
                          win=(80, 360, 420, 860))),
)
NARRATION = """
Sophie loved her mother. But she was ashamed of her hands.
They were scarred and twisted, and when her friends came over, Sophie asked her mother to wear gloves.
At her graduation, she asked her mother to sit in the back.
Her mother just nodded. 'Of course, sweetheart.'
That night, Sophie's aunt found her and said quietly, 'Do you know how your mother got those scars?'
Sophie shook her head.
'When you were one year old, your crib caught fire. Your mother pulled you out with her bare hands. She never told you, because she didn't want you to carry it.'
Sophie ran to her mother, took those scarred hands, and kissed them, again and again.
Moral of the story: never be ashamed of the scars someone earned protecting you.
"""
SCENES = [
    dict(bg="home", actors=[dict(who="sophie", x=700, p="cross", f=-1, e="sad", m="soft"), dict(who="mom", x=330, p="hold", f=1, m="smile", hold="cup")], fx=["dust"]),
    dict(bg="home", actors=[dict(who="friend", x=820, p="wave", f=-1, m="smile"), dict(who="sophie", x=560, p="talk", f=-1, m="talk"),
                            dict(who="mom", x=230, p="stand", f=1, e="sad", m="soft")]),
    dict(bg="lawn", back=[("audience", 0, 1480, 1.0, hx("3a3a5a"))], actors=[dict(who="sophie", x=540, p="stand", f=1, m="smile")], props=[("cap_gown", 540, 470, 1.0)]),
    dict(bg="lawn", actors=[dict(who="mom", x=540, p="hold", f=1, e="sad", m="smile")], props=[("audience", 0, 1480, 1.0, hx("3a3a5a"))]),
    dict(bg="night", actors=[dict(who="sophie", x=760, p="sit_sad", f=-1, e="sad", m="soft", gy=GYR), dict(who="aunt", x=320, p="talk", f=1, m="talk")],
         back=[("chair_l", 760, GYR)]),
    dict(bg="night", back=[("chair_l", 760, GYR)], actors=[dict(who="sophie", x=760, p="sit", f=-1, e="sad", m="sad"), dict(who="aunt", x=320, p="stand", f=1, e="sad", m="soft")]),
    dict(bg="fire", actors=[dict(who="mom", x=540, p="hold", f=1, e="sad", m="open", hold="gift")], fx=["flash"]),
    dict(bg="home", actors=[dict(who="mom", x=380, p="hug", f=1, m="smile", tears=0.8), dict(who="sophie", x=660, p="hug", f=-1, e="closed", m="sad", tears=1.0)],
         fx=["glow"]),
    dict(bg="home", actors=[dict(who="mom", x=380, p="hug", f=1, m="smile"), dict(who="sophie", x=660, p="hug", f=-1, m="smile", tears=0.5)], fx=["glow", "dust"]),
]
BEATS = make_beats(NARRATION, SCENES)


class Style(DataReel):
    pass
