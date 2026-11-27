from engine import *
from reel_lib import *

TITLE = "Reel 12 - Did You Eat Today"
OUTDIR = os.path.join(ROOT, "out_reels")
HOOK = "HE ASKED HIS SON THE SAME QUESTION 5 TIMES"
KEYWORD = 'TYPE "DID YOU EAT"'
GAP = 1.05
MUSIC = dict(kind="pad+piano", root=98.0, prog=[0, 3, -2, -4], qual=["m", "M", "M", "M"], bar=8, step=1.0, pat=[0, 2, 1, 3], vol=0.11)
POST = dict(title="Did You Eat Today?",
            caption="He thought his father was just forgetting. He was actually saying I love you. 🍲\nComment DID YOU EAT if your parents said I love you this way — share this with them. #Parents #Family #LifeLessons #MoralStory",
            pinned="What's the sentence your parents used instead of I love you? 👇")
CAST = dict(
    peter=dict(skin=SKIN["light"], hair=hx("e3e0da"), hair_style="short", top=hx("8a7a5a"), bottom=hx("4a4036"), age=82, h=860, glasses=True, collar=hx("efe9de")),
    peter_young=dict(skin=SKIN["light"], hair=hx("5a4030"), hair_style="short", top=hx("5a6a7a"), bottom=hx("3a3a40"), age=38, h=930),
    mark=dict(skin=SKIN["light"], hair=hx("5a4030"), hair_style="short", top=hx("2c4a6a"), bottom=hx("2a2e36"), age=45, h=940),
    mark_kid=dict(skin=SKIN["light"], hair=hx("5a4030"), hair_style="short", top=hx("e8b43a"), bottom=hx("3a5a8a"), age=7, h=540),
    helen=dict(skin=SKIN["light"], hair=hx("cfc9bf"), hair_style="bun", top=hx("9a7aa8"), bottom=hx("4a3a4a"), skirt=True, leg=SKIN["light"], age=78, h=840),
)
BGS = dict(
    living=("room", dict(wall=(hx("e6ecd8"), hx("b4c09a")), floor=hx("7a6a4a"), sky=(hx("ffe8b0"), hx("ffc08a")), curtain=hx("7a8a5a"),
                         grade=(255, 220, 160), grade_s=0.06)),
    door=("porch", dict(sky=(hx("f6b07a"), hx("ffe0b8")), ground=hx("7a8a5a"), trees=hx("5a6a4a"), house=hx("e8dcc0"))),
    past=("kitchen", dict(wall=(hx("d9c4a0"), hx("a88a5a")), floor=hx("6a5038"), night=True, sky=(hx("10101e"), hx("2a2a40")), cab=hx("c9b08a"),
                          win=(70, 330, 430, 900), grade=(200, 160, 100), grade_s=0.25)),
)
NARRATION = """
Every visit, old Peter asked his son the same question. 'Did you eat today?'
Mark would answer, 'Yes, Dad.' Five minutes later: 'Did you eat today?'
His memory was fading, and Mark's patience was fading with it.
One evening he snapped. 'Dad, I told you! I ate! Stop asking!'
His father went quiet, and looked down at his hands.
On the way out, his mother stopped him at the door. 'When you were small, your father worked two jobs.
Some nights he came home and there was only enough food for you. So every night he asked, did you eat today? Because if you had, he could go to bed hungry and happy.'
Mark walked back inside, sat beside his father, and said, 'Yes, Dad. I ate. Did you?'
Moral of the story: some people only know one way to say I love you. Learn to hear it.
"""
SOFA = [("armchair", 330, GYR)]
SCENES = [
    dict(bg="living", back=SOFA, actors=[dict(who="peter", x=330, p="sit_talk", f=1, m="talk", m2="smile"), dict(who="mark", x=780, p="stand", f=-1, m="soft")], fx=["dust"]),
    dict(bg="living", back=SOFA, actors=[dict(who="peter", x=330, p="sit_talk", f=1, m="smile", m2="talk"), dict(who="mark", x=780, p="hold", f=-1, m="talk", m2="soft",
                                                                                                          hold="phone")]),
    dict(bg="living", back=SOFA, actors=[dict(who="peter", x=330, p="sit", f=1, m="smile"), dict(who="mark", x=780, p="cross", f=-1, e="sad", m="soft")]),
    dict(bg="living", back=SOFA, actors=[dict(who="peter", x=330, p="sit", f=1, e="open", m="open"), dict(who="mark", x=760, p="refuse", f=-1, m="open")]),
    dict(bg="living", back=SOFA, actors=[dict(who="peter", x=330, p="sit_sad", f=1, e="sad", m="sad"), dict(who="mark", x=800, p="stand", f=-1, e="sad", m="soft")]),
    dict(bg="door", actors=[dict(who="helen", x=380, p="talk", f=1, m="talk", e="sad"), dict(who="mark", x=720, p="stand", f=-1, e="sad", m="sad", tears="12")]),
    dict(bg="past", back=[("chair_l", 760, GYR, 0.75)], actors=[dict(who="mark_kid", x=760, p="sit_eat", f=-1, m="smile"),
                                                             dict(who="peter_young", x=330, p="stand", f=1, e="sad", m="smile")],
         props=[("table", 640, 1220, 0.5, hx("c9b08a")), ("food", 680, 1190)]),
    dict(bg="living", back=SOFA + [("chair_l", 720, GYR)], actors=[dict(who="peter", x=330, p="sit", f=1, m="smile", tears=0.6),
                                                                 dict(who="mark", x=720, p="sit_talk", f=-1, m="talk", m2="smile", tears=0.8)], fx=["glow"]),
    dict(bg="living", back=SOFA + [("chair_l", 720, GYR)], actors=[dict(who="peter", x=330, p="sit_eat", f=1, m="smile"), dict(who="mark", x=720, p="sit_eat", f=-1, m="smile")],
         props=[("table", 530, 1230, 0.5, hx("f3ead8")), ("food", 480, 1200), ("food", 590, 1200)], fx=["glow", "dust"]),
]
BEATS = make_beats(NARRATION, SCENES)


class Style(DataReel):
    pass
