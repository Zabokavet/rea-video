from engine import *
from reel_lib import *

TITLE = "Reel 14 - The Old Man Who Planted a Tree"
OUTDIR = os.path.join(ROOT, "out_reels")
HOOK = "HE PLANTED A TREE HE WOULD NEVER SIT UNDER"
KEYWORD = 'TYPE "LEGACY"'
GAP = 1.4
VOICES = {"n": ("af_heart", 0.76)}
MUSIC = dict(kind="pad+piano", root=146.8, prog=[0, 5, 9, 7], qual=["M", "M", "m", "M"], bar=6, step=0.75, pat=[0, 1, 2, 3, 2, 1], vol=0.09)
POST = dict(title="The Old Man Who Planted a Tree",
            caption="Everyone laughed at the old man. Thirty years later, they understood. 🌳\nComment LEGACY if you're building something for people you'll never meet — share this with someone who plants for others. #Legacy #Wisdom #LifeLessons #MoralStory",
            pinned="What are you planting today that someone else will enjoy? 👇")
CAST = dict(
    abel=dict(skin=SKIN["deep"], hair=hx("e3e0da"), hair_style="short", top=hx("e8dcc0"), bottom=hx("6a5a48"), shoes=hx("4a3428"), age=80, h=860),
    young=dict(skin=SKIN["tan"], hair=hx("2a1d16"), hair_style="short", top=hx("4a8ad9"), bottom=hx("3a3a40"), age=25, h=950),
    old_young=dict(skin=SKIN["tan"], hair=hx("bdb8b0"), hair_style="short", top=hx("4a8ad9"), bottom=hx("3a3a40"), age=55, h=930),
    gk1=dict(skin=SKIN["tan"], hair=hx("2a1d16"), hair_style="long", top=hx("f2a6c0"), bottom=hx("4a4a6a"), age=8, h=540),
    gk2=dict(skin=SKIN["tan"], hair=hx("2a1d16"), hair_style="short", top=hx("f2c84a"), bottom=hx("3a5a8a"), age=6, h=500),
)
BGS = dict(
    farm=("farm", dict(sky=(hx("ffd27a"), hx("fff2c8")), ground=hx("7a9a4a"), trees=hx("4a7a3a"))),
    later=("farm", dict(sky=(hx("8ad0f0"), hx("eaf8ff")), ground=hx("6a9a4a"), trees=hx("3a6a3a"))),
    memory=("farm", dict(sky=(hx("e8c48a"), hx("f6e2bc")), ground=hx("a08a5a"), trees=hx("8a7a4a"), grade=(200, 150, 90), grade_s=0.25)),
)
NARRATION = """
Eighty-year-old Abel was planting a tiny mango tree when a young man walked by and laughed.
'Old man, that tree takes years to grow fruit. You'll never eat from it.'
Abel kept digging. 'I know.'
'Then why waste your time?'
Abel wiped his hands. 'When I was a boy, I ate mangoes from a tree I didn't plant. Someone I never met planted it for me. Now it's my turn.'
The young man shook his head and left.
Thirty years later, that same man stood in the shade of a huge mango tree, watching his grandchildren laugh and eat its fruit. He finally understood.
Moral of the story: the best things we do are for people we will never meet.
"""
SAP = [("sapling", 600, GYR, 1.2)]
SCENES = [
    dict(bg="farm", actors=[dict(who="abel", x=420, p="kneel", f=1, m="smile"), dict(who="young", x=880, p="stand", f=-1, m="smile", delay=2.5)], props=SAP),
    dict(bg="farm", actors=[dict(who="abel", x=380, p="kneel", f=1, m="soft"), dict(who="young", x=820, p="talk", f=-1, m="talk")], props=SAP),
    dict(bg="farm", actors=[dict(who="abel", x=380, p="kneel", f=1, m="talk", m2="smile"), dict(who="young", x=820, p="cross", f=-1, m="soft")], props=SAP),
    dict(bg="farm", actors=[dict(who="abel", x=380, p="kneel", f=1, m="smile"), dict(who="young", x=820, p="shrug" if False else "refuse", f=-1, m="talk")], props=SAP),
    dict(bg="memory", back=[("tree", 600, GYR, 1.0)], actors=[dict(who="abel", x=380, p="talk", f=1, m="talk"), dict(who="young", x=820, p="stand", f=-1, m="soft")]),
    dict(bg="farm", actors=[dict(who="abel", x=380, p="kneel", f=1, m="smile"), dict(who="young", x=1300, p="stand", f=1, m="soft", **{"from": 820}, walk=4)], props=SAP),
    dict(bg="later", back=[("tree", 540, GYR, 1.2)], actors=[dict(who="old_young", x=860, p="stand", f=-1, m="smile", tears="5"),
                                                         dict(who="gk1", x=380, p="wave", f=1, m="smile"), dict(who="gk2", x=560, p="arms_up", f=-1, m="smile")]),
    dict(bg="later", back=[("tree", 540, GYR, 1.2)], actors=[dict(who="old_young", x=420, p="kneel", f=1, m="smile"), dict(who="gk2", x=700, p="stand", f=-1, m="smile")],
         props=[("sapling", 860, GYR, 1.0)], fx=["glow", "dust"]),
]
BEATS = make_beats(NARRATION, SCENES)


class Style(DataReel):
    pass
