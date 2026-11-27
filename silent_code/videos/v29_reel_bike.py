from engine import *
from reel_lib import *

TITLE = "Reel 9 - The Boy Who Sold His Bike"
OUTDIR = os.path.join(ROOT, "out_reels")
HOOK = "HE SOLD HIS BIKE TO SAVE HIS MOTHER"
KEYWORD = 'TYPE "BLESS"'
GAP = 1.15
MUSIC = dict(kind="pad+piano+hats", root=130.8, prog=[0, 7, 9, 5], qual=["M", "M", "m", "M"], bar=4, step=0.5, pat=[0, 2, 1, 3], bpm=76, vol=0.08)
POST = dict(title="The Boy Who Sold His Bike",
            caption="He gave up the thing he loved most. A week later, it came back. 🚲❤️\nComment BLESS if this touched your heart — share it with someone who gives without counting. #Kindness #MothersLove #LifeLessons #MoralStory",
            pinned="What's the most selfless thing a child has ever done for you? 👇")
CAST = dict(
    sam=dict(skin=SKIN["brown"], hair=hx("1a1210"), hair_style="short", top=hx("f2c84a"), bottom=hx("3a6a9a"), shoes=hx("e8eef5"), age=10, h=600),
    mom=dict(skin=SKIN["brown"], hair=hx("1a1210"), hair_style="bun", top=hx("e8eef0"), bottom=hx("7a8a9a"), skirt=True, leg=SKIN["brown"], age=40, h=880),
    lewis=dict(skin=SKIN["fair"], hair=hx("a9a49c"), hair_style="short", top=hx("3a7a6a"), bottom=hx("4a4036"), age=60, h=930, glasses=True),
)
SUM = dict(sky=(hx("8ad0f0"), hx("e8f6ff")), bld=hx("e8b48a"), seed=11)
BGS = dict(
    street=("street", SUM),
    shop=("street", dict(SUM, bld=hx("6ab4a4"), seed=5)),
    home=("bedroom", dict(wall=(hx("dff2f0"), hx("a8d4cc")), floor=hx("8a7a6a"), sky=(hx("e8f6ff"), hx("bce4f4")), win=(80, 360, 420, 860), bed=hx("f4e2c8"))),
    porch=("porch", dict(sky=(hx("8ad0f0"), hx("e8f6ff")), ground=hx("7aa85a"), trees=hx("5a8a4a"), house=hx("f4e2c8"))),
)
NARRATION = """
Ten-year-old Sam loved his red bike more than anything he owned.
But his mother was sick, and the medicine cost more than they had.
One morning, Sam wheeled his bike to the shop on the corner and asked the owner, Mr. Lewis, to buy it.
Mr. Lewis looked at the boy, then at the bike. 'Why are you selling it, son?'
'My mom needs medicine,' Sam said. 'She'll get better. I don't need a bike.'
Mr. Lewis paid him, and Sam ran to the pharmacy without looking back.
A week later, his mother was feeling better. And there, leaning against their front door, was the red bike, with a note: 'A boy who gives up his treasure for his mother should never walk.'
Moral of the story: a selfless heart always finds its way back to its treasure.
"""
SCENES = [
    dict(bg="street", actors=[dict(who="sam", x=380, p="wave", f=1, m="smile")], props=[("bike", 700, GYR, 1.1)]),
    dict(bg="home", back=[("medicine", 330, 1040, 1.0)], actors=[dict(who="mom", x=760, p="sit_sad", f=-1, e="sad", m="sad", gy=GYR - 20),
                                                              dict(who="sam", x=420, p="stand", f=1, e="sad", m="sad")]),
    dict(bg="shop", actors=[dict(who="lewis", x=840, p="cross", f=-1, m="soft"), dict(who="sam", x=420, p="hold", f=1, e="sad", m="soft", **{"from": 120}, walk=2.5)],
         props=[("bike", 600, GYR, 0.9)]),
    dict(bg="shop", actors=[dict(who="lewis", x=840, p="talk", f=-1, m="talk", e="sad"), dict(who="sam", x=380, p="stand", f=1, e="sad", m="soft")],
         props=[("bike", 600, GYR, 0.9)]),
    dict(bg="shop", actors=[dict(who="lewis", x=840, p="stand", f=-1, e="sad", m="soft", tears="3"), dict(who="sam", x=380, p="talk", f=1, e="sad", m="talk", tears=0.4)],
         props=[("bike", 600, GYR, 0.9)]),
    dict(bg="street", actors=[dict(who="sam", x=900, p="carry", f=1, m="smile", hold="medicine", **{"from": 150}, walk=4.5),
                              dict(who="lewis", x=180, p="hold", f=1, e="sad", m="smile", h=900)], props=[("bike", 330, GYR, 0.8)]),
    dict(bg="porch", actors=[dict(who="mom", x=300, p="stand", f=1, m="smile"), dict(who="sam", x=520, p="arms_up" if False else "wave", f=1, e="open", m="open", m2="smile",
                                                                                     tears="6")],
         props=[("bike", 860, GYR, 0.9), ("envelope", 860, 1160, 0.8)], fx=["glow"]),
    dict(bg="street", actors=[dict(who="sam", x=540, p="wave", f=1, m="smile")], props=[("bike", 760, GYR, 1.1)], fx=["glow", "dust"]),
]
BEATS = make_beats(NARRATION, SCENES)


class Style(DataReel):
    pass
