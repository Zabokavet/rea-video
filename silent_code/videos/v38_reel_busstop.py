from engine import *
from reel_lib import *

TITLE = "Reel 18 - The Stranger at the Bus Stop"
OUTDIR = os.path.join(ROOT, "out_reels")
HOOK = "SHE WAS READY TO GIVE UP… THEN A STRANGER SAT DOWN"
KEYWORD = 'TYPE "HOPE"'
GAP = 1.4
MUSIC = dict(kind="pad+piano", root=110.0, prog=[0, 3, -2, 5], qual=["m", "M", "M", "M"], bar=6, step=0.75, pat=[0, 2, 1, 3], vol=0.1)
POST = dict(title="The Stranger at the Bus Stop",
            caption="Five rejections. One rainy night. One stranger with an umbrella. ☂️\nComment HOPE if you're still knocking on doors — share this with someone who is about to give up. #Hope #NeverGiveUp #LifeLessons #Motivation",
            pinned="How many doors closed before the right one opened for you? 👇")
CAST = dict(
    emma=dict(skin=SKIN["light"], hair=hx("6a4a3a"), hair_style="long", top=hx("6a7a8a"), bottom=hx("2a3038"), age=26, h=880),
    old=dict(skin=SKIN["tan"], hair=hx("e3e0da"), hair_style="bun", top=hx("c0392b"), bottom=hx("3a2a2a"), skirt=True, leg=SKIN["tan"], age=78, h=830, glasses=True),
)
NIGHTRAIN = dict(night=True, sky=(hx("0a1020"), hx("1e2a44")), bld=hx("10141e"), seed=7)
BGS = dict(stop=("busstop", NIGHTRAIN), day=("busstop", dict(sky=(hx("a8dcf4"), hx("f0faff")), bld=hx("b8c4d0"), seed=7)))
NARRATION = """
It was raining, and Emma sat at the bus stop, soaked, holding a rejection letter. The fifth one that month.
She had decided this was the last time she would try.
An old woman sat down beside her and held her umbrella over both of them.
'Bad day?' she asked.
Emma showed her the letter. The old woman read it, folded it, and handed it back. 'Do you know how many times I was rejected before I became a teacher? Thirty-one.'
'Why didn't you quit?'
'Because the thirty-second door was the one that opened.'
The bus came, and the old woman was gone.
Emma applied one more time. That door opened.
Moral of the story: sometimes you are only one more try away from everything.
"""
BENCH_GY = GYR - 40
E = lambda **k: dict(who="emma", x=640, p=k.pop("p", "sit_hold"), f=-1, gy=BENCH_GY, **k)
O = lambda **k: dict(who="old", x=880, p=k.pop("p", "sit"), f=-1, gy=BENCH_GY, **k)
SCENES = [
    dict(bg="stop", actors=[E(e="sad", m="sad", hold="letter", tears="3")], fx=["rain"]),
    dict(bg="stop", actors=[E(p="sit_hands_face", e="closed", m="sad", tears=1.0)], fx=["rain"]),
    dict(bg="stop", actors=[E(p="sit_sad", e="sad", m="sad"), dict(who="old", x=880, p="carry", f=-1, m="smile", gy=BENCH_GY, **{"from": 1250}, walk=2.5)],
         props=[("umbrella", 770, 560, 1.0)], fx=["rain"]),
    dict(bg="stop", actors=[E(p="sit_sad", e="sad", m="soft"), O(m="talk")], props=[("umbrella", 770, 560, 1.0)], fx=["rain"]),
    dict(bg="stop", actors=[E(p="sit", e="sad", m="soft", m2="open"), O(p="sit_talk", m="talk", hold="letter")], props=[("umbrella", 770, 560, 1.0)], fx=["rain"]),
    dict(bg="stop", actors=[E(p="sit_talk", e="open", m="talk"), O(m="smile")], props=[("umbrella", 770, 560, 1.0)], fx=["rain"]),
    dict(bg="stop", actors=[E(p="sit", e="open", m="soft", m2="smile"), O(p="sit_talk", m="talk", m2="smile")], props=[("umbrella", 770, 560, 1.0)], fx=["rain", "glow"]),
    dict(bg="stop", back=[], actors=[E(p="sit", e="open", m="open")], props=[("bus", 540, GYR + 120, 1.0, hx("e8b43a"))], fx=["rain"]),
    dict(bg="day", actors=[dict(who="emma", x=540, p="arms_up" if False else "wave", f=1, m="smile", hold=None)], props=[("envelope", 720, 900, 1.2)], fx=["glow"]),
    dict(bg="day", actors=[dict(who="emma", x=540, p="stand", f=1, m="smile")], fx=["glow", "dust"]),
]
BEATS = make_beats(NARRATION, SCENES)


class Style(DataReel):
    pass
