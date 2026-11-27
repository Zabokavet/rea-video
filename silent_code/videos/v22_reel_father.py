from engine import *
from reel_lib import *

TITLE = "Reel 2 - Five Things Your Father Did That You Only Understand When He Is Gone"
OUTDIR = os.path.join(ROOT, "out_reels")
HOOK = "5 THINGS YOUR FATHER HID FROM YOU"
KEYWORD = 'TYPE "THANK YOU DAD"'
MUSIC = dict(kind="pad+piano", root=98.0, prog=[0, 5, -3, 3], qual=["M", "M", "m", "M"], bar=6, step=1.0, pat=[0, 2, 1, 3], vol=0.11)
GAP = 1.1
POST = dict(title="Five Things Your Father Did That You Only Understand When He Is Gone",
            caption="He never told you any of this. He just carried it. 🥺\nComment THANK YOU DAD if yours carried it too — share this with your father while he can still read it. #FathersLove #FamilyFirst #LifeLessons #Parents",
            pinned="Which of the five did YOUR father do? 👇")

CAST = dict(
    dad=dict(skin=SKIN["tan"], hair=hx("3a2a20"), hair_style="short", top=hx("8a5a3a"), bottom=hx("3e4452"), shoes=hx("4a3428"), age=40, h=930),
    dad_old=dict(skin=SKIN["tan"], hair=hx("a9a49c"), hair_style="short", top=hx("8a5a3a"), bottom=hx("3e4452"), shoes=hx("4a3428"), age=66, h=910),
    kid=dict(skin=SKIN["tan"], hair=hx("3a2a20"), hair_style="short", top=hx("d9534f"), bottom=hx("3a5a8a"), shoes=hx("e8eef5"), age=8, h=560),
)
EVE = dict(wall=(hx("f0cfa4"), hx("c98f5e")), floor=hx("7a4a2e"), sky=(hx("ffb27a"), hx("e87a5a")), curtain=hx("5a6e4a"), hills=hx("7a6a4a"),
           grade=(255, 190, 130), grade_s=0.1)
BGS = dict(
    home=("room", EVE),
    kitchen=("kitchen", dict(EVE, cab=hx("e2d2b4"), win=(70, 330, 430, 900))),
    dawn=("street", dict(night=True, sky=(hx("1a2240"), hx("6a5a7a")))),
    car=("car", dict(sky=(hx("05070e"), hx("1a1f33")))),
    old=("room", dict(EVE, sky=(hx("ffcf8a"), hx("f29a6a")), curtain=hx("8a4a3a"))),
)
NARRATION = """
There are five things your father did that you will only understand when he is gone.
One: he wore the same shoes for six years — so yours could be new every September.
Two: he said 'I'm not hungry' at the table — when there wasn't enough for everyone.
Three: he stayed at the job he hated, in silence, for thirty years — because rent does not accept excuses.
Four: he apologized to you, even the times he was right — because your heart mattered more than his pride.
And five — the one that breaks everyone who hears it: he cried where you could never see him.
In the car. In the dark. Alone. So that in your memory, he would always be strong.
Moral of the story: a father's love is not loud. It is the weight he carried so you never had to feel it.
"""
SCENES = [
    dict(bg="home", actors=[dict(who="dad", x=440, f=1, m="smile"), dict(who="kid", x=720, f=-1, m="smile")], fx=["dust"]),
    dict(bg="home", actors=[dict(who="kid", x=780, f=-1, m="open", m2="smile"), dict(who="dad", x=380, p="kneel", f=1, m="smile", hold="shoes_new")],
         props=[("shoes_old", 170, GYR - 4, 1.0)], fx=["dust"]),
    dict(bg="kitchen", back=[("chair", 300, GYR, 1), ("chair_l", 800, GYR)],
         actors=[dict(who="dad", x=300, p="sit", f=1, m="smile"), dict(who="kid", x=790, p="sit_eat", f=-1, m="smile", h=600)],
         props=[("table", 545, 1150, 1.0), ("plate", 400, 1120), ("food", 690, 1120), ("food", 545, 1110, 1.2)]),
    dict(bg="dawn", actors=[dict(who="dad", x=520, from_=None, p="carry", f=1, e="sad", m="soft", hold="papers")]),
    dict(bg="home", actors=[dict(who="dad", x=420, p="kneel", f=1, e="sad", m="talk", m2="soft"), dict(who="kid", x=760, p="cross", f=-1, e="sad", m="sad", p2="hug", m2="smile")]),
    dict(bg="car", actors=[dict(who="dad", x=560, gy=1500, h=1050, p="stand", f=1, e="sad", m="sad", p2="hands_face", at=0.55, tears="2.5")],
         props=[("dash", 780, 1000)], fx=["dark"]),
    dict(bg="car", actors=[dict(who="dad", x=560, gy=1500, h=1050, p="hands_face", f=1, e="closed", m="sad", tears=1.0)], props=[("dash", 780, 1000)], fx=["dark"]),
    dict(bg="old", back=[("armchair", 600, GYR)], actors=[dict(who="dad_old", x=600, p="sit", f=-1, e="closed", e2="open", m="smile")], fx=["dust", "glow"]),
]
for s in SCENES:
    for a in s.get("actors", []):
        a.pop("from_", None)
BEATS = make_beats(NARRATION, SCENES)


class Style(DataReel):
    pass
