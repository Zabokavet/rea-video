from engine import *
from reel_lib import *

TITLE = "Reel 17 - The Bread Thief"
OUTDIR = os.path.join(ROOT, "out_reels")
HOOK = "HE CAUGHT A BOY STEALING BREAD"
KEYWORD = 'TYPE "MERCY"'
GAP = 1.4
VOICES = {"n": ("af_heart", 0.77)}
MUSIC = dict(kind="pad+piano", root=116.5, prog=[0, -4, 3, 5], qual=["m", "M", "M", "M"], bar=6, step=0.75, pat=[0, 1, 2, 3, 2, 1], vol=0.1)
POST = dict(title="The Bread Thief",
            caption="He caught a hungry boy stealing. What he did next changed a whole life. 🍞\nComment MERCY if you believe one second chance can change everything — share this with someone who gave you yours. #Mercy #Kindness #SecondChances #LifeLessons",
            pinned="Who gave you a second chance when you didn't deserve one? 👇")
CAST = dict(
    baker=dict(skin=SKIN["fair"], hair=hx("bdb8b0"), hair_style="short", top=hx("f6f1e8"), bottom=hx("5a4a3a"), age=58, h=950, collar=hx("e8c890")),
    boy=dict(skin=SKIN["brown"], hair=hx("1a1210"), hair_style="short", top=hx("7a6a5a"), bottom=hx("4a4036"), shoes=SKIN["brown"], age=11, h=600),
    man=dict(skin=SKIN["brown"], hair=hx("1a1210"), hair_style="short", top=hx("f6f1e8"), bottom=hx("3a3a40"), age=32, h=950, collar=hx("e8c890")),
)
BGS = dict(
    bakery=("bakery", dict(wall=(hx("f4d8a8"), hx("c98a4a")), floor=hx("7a4a2a"), sky=(hx("ffd890"), hx("ff9a5a")), win=(60, 330, 440, 900), trim=hx("6a3a1a"),
                           grade=(255, 190, 110), grade_s=0.1)),
    dawn=("bakery", dict(wall=(hx("e8c890"), hx("a86a3a")), floor=hx("6a4028"), night=True, sky=(hx("2a2a4a"), hx("e8905a")), win=(60, 330, 440, 900),
                         trim=hx("6a3a1a"))),
    street=("street", dict(sky=(hx("ffcf9a"), hx("fff2dc")), bld=hx("c98a5a"), seed=14)),
)
NARRATION = """
The baker caught the boy with a loaf of bread hidden under his shirt.
The boy froze, waiting to be beaten, or dragged to the police.
Instead, the baker asked, 'When did you last eat?'
'Two days ago,' the boy whispered.
The baker put a second loaf in his hands. 'Come back tomorrow at five. I need someone to sweep the floors. I'll pay you in bread and in money.'
The boy came back the next day. And the next. For ten years.
Today, he owns six bakeries. And by the door of every single one is a basket of free bread, with a sign: 'If you are hungry, take one. Someone once did this for me.'
Moral of the story: mercy can change the whole direction of a life.
"""
SCENES = [
    dict(bg="bakery", actors=[dict(who="boy", x=380, p="hold", f=1, e="open", m="open", hold="bread"), dict(who="baker", x=780, p="point_l" if False else "give", f=-1, m="open")],
         fx=["flash"]),
    dict(bg="bakery", actors=[dict(who="boy", x=380, p="hands_face", f=1, e="closed", m="sad"), dict(who="baker", x=780, p="hips" if False else "cross", f=-1, m="soft")]),
    dict(bg="bakery", actors=[dict(who="boy", x=380, p="stand", f=1, e="sad", m="sad"), dict(who="baker", x=760, p="kneel", f=-1, e="sad", m="talk")]),
    dict(bg="bakery", actors=[dict(who="boy", x=380, p="stand", f=1, e="sad", m="talk", tears="0.5"), dict(who="baker", x=760, p="kneel", f=-1, e="sad", m="sad")]),
    dict(bg="bakery", actors=[dict(who="boy", x=380, p="hold", f=1, e="open", m="smile", tears=0.6, hold="bread"), dict(who="baker", x=760, p="give", f=-1, m="smile", hold="bread")]),
    dict(bg="dawn", actors=[dict(who="boy", x=540, p="carry", f=1, m="smile", hold="broom")], props=[("basket", 860, 1060, 0.7)]),
    dict(bg="street", actors=[dict(who="man", x=420, p="give", f=1, m="smile", hold="bread"), dict(who="boy", x=780, p="hold", f=-1, m="smile", hold="bread", delay=2)],
         props=[("basket", 200, GYR - 10, 1.0)], fx=["glow"]),
    dict(bg="bakery", actors=[dict(who="man", x=420, p="hug", f=1, m="smile", tears=0.6), dict(who="baker", x=660, p="hug", f=-1, m="smile", tears=0.6)],
         props=[("basket", 900, GYR - 10, 0.8)], fx=["glow", "dust"]),
]
BEATS = make_beats(NARRATION, SCENES)


class Style(DataReel):
    pass
