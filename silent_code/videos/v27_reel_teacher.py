from engine import *
from reel_lib import *

TITLE = "Reel 7 - The Teacher Who Always Made Too Much Lunch"
OUTDIR = os.path.join(ROOT, "out_reels")
HOOK = "SHE SHARED HER LUNCH WITH ONE BOY FOR A YEAR"
KEYWORD = 'TYPE "TEACHER"'
MUSIC = dict(kind="pad+piano", root=146.8, prog=[0, 5, 7, 4], qual=["M", "M", "M", "m"], bar=6, step=0.5, pat=[0, 1, 2, 3, 2, 1], vol=0.09)
POST = dict(title="The Teacher Who Always Made Too Much Lunch",
            caption="She never told anyone. Twenty-five years later, he never forgot. 🍎\nComment TEACHER if a teacher once changed your life — share this with a teacher who deserves to hear it. #Teachers #Kindness #LifeLessons #Gratitude",
            pinned="Which teacher saw you when nobody else did? Tag them 👇")
CAST = dict(
    grace=dict(skin=SKIN["tan"], hair=hx("4a2e1e"), hair_style="bun", top=hx("e8b43a"), bottom=hx("5a4a6a"), skirt=True, leg=SKIN["tan"], age=40, h=900),
    grace_old=dict(skin=SKIN["tan"], hair=hx("cfc9bf"), hair_style="bun", top=hx("cfe0e8"), bottom=hx("cfe0e8"), skirt=True, leg=SKIN["tan"], age=66, h=870),
    eli=dict(skin=SKIN["deep"], hair=hx("1a1210"), hair_style="short", top=hx("8a9aa8"), bottom=hx("4a4a50"), age=9, h=560),
    eli_dr=dict(skin=SKIN["deep"], hair=hx("1a1210"), hair_style="short", top=hx("4aa89a"), bottom=hx("4aa89a"), shoes=hx("e8eef5"), age=34, h=960),
)
BGS = dict(
    class_=("classroom", dict(wall=(hx("fff0c4"), hx("f2cf7a")), floor=hx("b08a5a"), grade=(255, 220, 150), grade_s=0.06)),
    hosp=("hospital", dict(wall=(hx("e4f2ec"), hx("b8d8cc")), floor=hx("9ab4aa"), sky=(hx("e8f4ff"), hx("c4dcf0")), win=(70, 340, 430, 860))),
)
NARRATION = """
Every day at noon, Mrs. Grace noticed one boy who never ate.
Leo said he wasn't hungry. But his hands shook, and he couldn't focus in class.
So Mrs. Grace started bringing two sandwiches. 'I made too much,' she would say, and slide one across her desk.
She did it every school day, for a whole year. She never told anyone.
Twenty-five years later, Mrs. Grace lay in a hospital bed, waiting for a heart surgery she was afraid she couldn't afford.
The surgeon walked in, read her name on the chart, and stopped.
'You won't remember me,' he said softly. 'You always made too much.'
He performed the surgery himself. The bill came back marked: paid in full, twenty-five years ago.
Moral of the story: a small kindness to a child can grow into a life you will never see coming.
"""
DESK = [("table", 540, 1200, 0.7, hx("a8805a"))]
SCENES = [
    dict(bg="class_", back=[("chair", 760, GYR, 0.75)], actors=[dict(who="eli", x=760, p="sit_sad", f=-1, e="sad", m="sad"),
                                                            dict(who="grace", x=260, p="stand", f=1, m="soft", e="sad")]),
    dict(bg="class_", back=[("chair", 540, GYR, 0.75)], actors=[dict(who="eli", x=540, p="sit_hands_face", f=1, e="sad", m="sad")]),
    dict(bg="class_", actors=[dict(who="grace", x=330, p="give", f=1, m="talk", m2="smile", hold="bread"), dict(who="eli", x=760, p="stand", f=-1, e="open", m="open", m2="smile")],
         props=DESK),
    dict(bg="class_", back=[("chair", 330, GYR), ("chair_l", 760, GYR, 0.75)],
         actors=[dict(who="grace", x=330, p="sit_eat", f=1, m="smile"), dict(who="eli", x=760, p="sit_eat", f=-1, m="smile")], props=DESK, fx=["glow", "dust"]),
    dict(bg="hosp", back=[("bed", 620, GYR, 1.0, hx("e8eef0"))], actors=[dict(who="grace_old", x=560, p="sit_hold", f=1, e="sad", m="sad", gy=GYR - 70)]),
    dict(bg="hosp", back=[("bed", 380, GYR, 0.9, hx("e8eef0"))], actors=[dict(who="grace_old", x=330, p="sit", f=1, e="open", m="soft", gy=GYR - 60),
                                                                     dict(who="eli_dr", x=820, p="hold", f=-1, e="open", m="open", hold="papers", **{"from": 1200}, walk=2)]),
    dict(bg="hosp", back=[("bed", 380, GYR, 0.9, hx("e8eef0"))], actors=[dict(who="grace_old", x=330, p="sit", f=1, e="open", m="open", m2="smile", tears="3", gy=GYR - 60),
                                                                     dict(who="eli_dr", x=760, p="talk", f=-1, m="talk", tears=0.6)]),
    dict(bg="hosp", back=[("bed", 380, GYR, 0.9, hx("e8eef0"))], actors=[dict(who="grace_old", x=330, p="sit_hold", f=1, e="sad", m="smile", tears=1.0, hold="papers",
                                                                          gy=GYR - 60)], fx=["glow"]),
    dict(bg="hosp", actors=[dict(who="grace_old", x=420, p="hug", f=1, m="smile", tears=0.8), dict(who="eli_dr", x=680, p="hug", f=-1, m="smile", tears=0.6)],
         fx=["glow", "dust"]),
]
BEATS = make_beats(NARRATION, SCENES)


class Style(DataReel):
    pass
