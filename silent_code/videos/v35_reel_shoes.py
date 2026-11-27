from engine import *
from reel_lib import *

TITLE = "Reel 15 - The Girl With the Worn Shoes"
OUTDIR = os.path.join(ROOT, "out_reels")
HOOK = "THEY LAUGHED AT HER SHOES… UNTIL ONE GIRL SAW WHY"
KEYWORD = 'TYPE "EMPATHY"'
GAP = 1.5
VOICES = {"n": ("af_heart", 0.75)}
MUSIC = dict(kind="pad+piano", root=123.5, prog=[0, -4, 3, -2], qual=["m", "M", "M", "M"], bar=6, step=0.75, pat=[0, 2, 1, 3], vol=0.1)
POST = dict(title="The Girl With the Worn Shoes",
            caption="They laughed at her shoes. Then one girl saw how far she walked in them. 👟💙\nComment EMPATHY if you believe kindness should be taught — share this with a parent or a teacher. #Kindness #Empathy #LifeLessons #MoralStory",
            pinned="Were you ever the kid who got laughed at — or the one who stood up? 👇")
CAST = dict(
    mia=dict(skin=SKIN["tan"], hair=hx("2a1d16"), hair_style="long", top=hx("9aa8b8"), bottom=hx("4a4a5a"), shoes=hx("6a5242"), age=11, h=640),
    chloe=dict(skin=SKIN["fair"], hair=hx("e0b860"), hair_style="long", top=hx("f28fa8"), bottom=hx("5a5a8a"), shoes=hx("e8eef5"), age=11, h=640),
    kid=dict(skin=SKIN["brown"], hair=hx("1a1210"), hair_style="short", top=hx("6ab46a"), bottom=hx("3a3a50"), age=11, h=640),
    mom=dict(skin=SKIN["fair"], hair=hx("c9a05a"), hair_style="bob", top=hx("4a6a8a"), bottom=hx("3a3a40"), age=40, h=900),
)
BGS = dict(
    yard=("street", dict(sky=(hx("a8dcf4"), hx("f0faff")), bld=hx("f2c890"), seed=21)),
    dawn=("road", dict(sky=(hx("1a2a4a"), hx("e89a7a")), trees=hx("2a3646"), ground=hx("3a4a4a"))),
    car=("car", dict(sky=(hx("1a2a4a"), hx("e89a7a")))),
)
NARRATION = """
Every morning, Mia came to school in the same worn-out shoes, and every morning, the other kids laughed.
Chloe laughed the loudest.
One day, Chloe's mother was driving her to school early, before sunrise, and Chloe saw someone walking alone on the side of the highway.
It was Mia. Walking five kilometers, in the dark, in those shoes.
Chloe stayed quiet the whole way to school.
That afternoon, she found Mia by the gate and held out a box. 'I have two pairs,' she said. 'And I'm sorry.'
From that day on, nobody laughed at Mia's shoes. Chloe made sure of it.
Moral of the story: you never know how far someone walked to stand next to you.
"""
SCENES = [
    dict(bg="yard", actors=[dict(who="mia", x=330, p="sit_sad" if False else "stand", f=1, e="sad", m="sad"), dict(who="kid", x=640, p="talk", f=-1, m="talk"),
                            dict(who="chloe", x=860, p="talk", f=-1, m="open")], props=[("shoes_old", 260, GYR - 2, 0.0)]),
    dict(bg="yard", actors=[dict(who="chloe", x=540, p="talk", f=-1, m="talk", m2="smile")]),
    dict(bg="car", actors=[dict(who="chloe", x=560, gy=1500, h=760, p="stand", f=1, e="open", m="soft")], props=[("dash", 780, 1000)]),
    dict(bg="dawn", actors=[dict(who="mia", x=900, p="carry", f=1, e="sad", m="soft", **{"from": 200}, walk=9)]),
    dict(bg="car", actors=[dict(who="chloe", x=560, gy=1500, h=760, p="stand", f=1, e="sad", m="sad", tears="2")], props=[("dash", 780, 1000)]),
    dict(bg="yard", actors=[dict(who="mia", x=330, p="stand", f=1, e="open", m="open", m2="smile", tears="5"), dict(who="chloe", x=720, p="give", f=-1, m="talk", hold="box")]),
    dict(bg="yard", actors=[dict(who="mia", x=360, p="hug", f=1, m="smile"), dict(who="chloe", x=600, p="hug", f=-1, m="smile"), dict(who="kid", x=880, p="wave", f=-1, m="smile")],
         props=[("shoes_new", 300, GYR - 2, 0.7)], fx=["glow"]),
    dict(bg="yard", actors=[dict(who="mia", x=400, p="wave", f=1, m="smile"), dict(who="chloe", x=680, p="wave", f=-1, m="smile")], fx=["glow", "dust"]),
]
BEATS = make_beats(NARRATION, SCENES)


class Style(DataReel):
    pass
