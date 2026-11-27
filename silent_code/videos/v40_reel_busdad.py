from engine import *
from reel_lib import *

TITLE = "Reel 20 - The Father Who Watched the Bus"
OUTDIR = os.path.join(ROOT, "out_reels")
HOOK = "HE WATCHED HER BUS EVERY MORNING FOR YEARS"
KEYWORD = 'TYPE "DADDY"'
GAP = 1.1
MUSIC = dict(kind="pad+piano", root=103.8, prog=[0, 5, -3, 3], qual=["M", "M", "m", "M"], bar=6, step=0.75, pat=[0, 1, 2, 3, 2, 1], vol=0.1)
POST = dict(title="The Father Who Watched the Bus",
            caption="She asked him to stop walking her to the bus. He never really stopped. 🍂\nComment DADDY if your father loved you in ways you only saw later — share this with him today. #FathersLove #Family #LifeLessons #MoralStory",
            pinned="What did your father do quietly that you only understood later? 👇")
CAST = dict(
    dad=dict(skin=SKIN["tan"], hair=hx("3a2a20"), hair_style="short", top=hx("8a4a2a"), bottom=hx("3a3a40"), age=42, h=950),
    lucy=dict(skin=SKIN["tan"], hair=hx("3a2a20"), hair_style="long", top=hx("e8a43a"), bottom=hx("4a4a6a"), age=8, h=560),
    lucy_teen=dict(skin=SKIN["tan"], hair=hx("3a2a20"), hair_style="long", top=hx("5a8ab4"), bottom=hx("3a3a50"), age=13, h=780),
    lucy_adult=dict(skin=SKIN["tan"], hair=hx("3a2a20"), hair_style="long", top=hx("2a2a30"), bottom=hx("2a2a30"), age=30, h=880),
    mom=dict(skin=SKIN["tan"], hair=hx("bdb8b0"), hair_style="bun", top=hx("2a2a30"), bottom=hx("2a2a30"), skirt=True, leg=SKIN["tan"], age=68, h=840),
)
FALL = dict(sky=(hx("ffb06a"), hx("ffe4c0")), bld=hx("c9885a"), seed=4)
BGS = dict(
    street=("street", FALL),
    gray=("street", dict(sky=(hx("b8b8c0"), hx("e0e0e6")), bld=hx("8a8a94"), seed=4)),
    home=("room", dict(wall=(hx("e8d0b0"), hx("b08a64")), floor=hx("6a4a30"), sky=(hx("c8c0b8"), hx("a8a098")), curtain=hx("5a4a3a"))),
)
OAK = [("tree", 900, GYR, 0.9, hx("c96a2a"))]
NARRATION = """
Every morning, Lucy's father walked her to the bus stop, and waved until the bus turned the corner.
When she turned thirteen, she told him, 'Dad, stop. It's embarrassing. I can walk alone.'
He nodded, and the next day he stayed home.
Lucy grew up, moved away, and got busy, like everyone does.
Years later, after his funeral, her mother handed her a small notebook. Inside, in her father's handwriting, there was a line for every school day: 'Bus came at 7:42. She got on safely.'
He had never stopped. He had just stood further back, behind the old oak tree, where she couldn't see him.
Lucy held the notebook to her chest and cried.
Moral of the story: some love never leaves. It just learns to stand where you can't see it.
"""
SCENES = [
    dict(bg="street", back=OAK, actors=[dict(who="dad", x=380, p="wave", f=1, m="smile"), dict(who="lucy", x=620, p="wave", f=-1, m="smile")], fx=["dust"]),
    dict(bg="street", back=OAK, actors=[dict(who="dad", x=380, p="stand", f=1, m="smile", m2="soft", e2="sad"), dict(who="lucy_teen", x=660, p="refuse", f=-1, m="talk")]),
    dict(bg="home", actors=[dict(who="dad", x=540, p="stand", f=1, e="sad", m="soft")]),
    dict(bg="gray", actors=[dict(who="lucy_adult", x=540, p="phone", f=1, m="talk")], props=[("suitcase", 800, GYR, 1.0)]),
    dict(bg="home", actors=[dict(who="mom", x=360, p="give", f=1, e="sad", m="sad", tears=0.6, hold="book"), dict(who="lucy_adult", x=720, p="hold", f=-1, e="sad", m="open",
                                                                                                           hold="book", delay=6)]),
    dict(bg="street", back=OAK, actors=[dict(who="lucy", x=300, p="stand", f=1, m="smile", h=560), dict(who="dad", x=960, p="stand", f=-1, m="smile", e="sad")],
         props=[("tree", 900, GYR, 0.9, hx("c96a2a")), ("bus", 330, GYR + 120, 0.6)]),
    dict(bg="home", actors=[dict(who="lucy_adult", x=540, p="hold", f=1, e="closed", m="sad", tears=1.0, hold="book")], fx=["glow"]),
    dict(bg="street", back=OAK, actors=[dict(who="lucy_adult", x=420, p="hold", f=1, e="closed", m="smile", hold="book")], fx=["glow", "dust"]),
]
BEATS = make_beats(NARRATION, SCENES)


class Style(DataReel):
    pass
