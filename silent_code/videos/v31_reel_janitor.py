from engine import *
from reel_lib import *

TITLE = "Reel 11 - The Janitor at the Graduation"
OUTDIR = os.path.join(ROOT, "out_reels")
HOOK = "NOBODY KNEW THE JANITOR WAS HER FATHER"
KEYWORD = 'TYPE "RESPECT"'
GAP = 0.95
MUSIC = dict(kind="pad+piano", root=110.0, prog=[0, -4, 3, 5], qual=["m", "M", "M", "M"], bar=6, step=0.75, pat=[0, 2, 1, 3], vol=0.1)
POST = dict(title="The Janitor at the Graduation",
            caption="For twelve years, nobody noticed him. Then his daughter said six words. 🎓\nComment RESPECT if you honor every honest job — share this with someone whose parent worked hard for them. #Respect #Fathers #LifeLessons #MoralStory",
            pinned="What job did your parents do so you could have more? 👇")
CAST = dict(
    joseph=dict(skin=SKIN["deep"], hair=hx("6a6660"), hair_style="short", top=hx("4a6a8a"), bottom=hx("4a6a8a"), shoes=hx("2a2a2a"), age=52, h=930),
    amara=dict(skin=SKIN["deep"], hair=hx("1a1210"), hair_style="long", top=hx("1c1c22"), bottom=hx("1c1c22"), age=18, h=880),
    kid1=dict(skin=SKIN["light"], hair=hx("c9893a"), hair_style="short", top=hx("d9534f"), bottom=hx("3a3a50"), age=16, h=860),
    kid2=dict(skin=SKIN["tan"], hair=hx("2a1d16"), hair_style="bob", top=hx("6ab4a4"), bottom=hx("3a3a50"), age=16, h=840),
)
BGS = dict(
    hall=("classroom", dict(wall=(hx("6a9a9a"), hx("2a4a52")), floor=hx("4a6a6a"), grade=(140, 200, 200), grade_s=0.08)),
    day=("classroom", dict(wall=(hx("e8f0ea"), hx("b8ccc0")), floor=hx("9aa89a"))),
    stage=("stage", dict(wall=(hx("2a2a44"), hx("14141e")), floor=hx("4a3a2a"), curtain=hx("7a1f2a"))),
)
NARRATION = """
For twelve years, Mr. Joseph mopped the floors of the school where his daughter studied.
He wore his uniform and kept his head down. Some students laughed at him. Some never even saw him.
His daughter, Amara, never told anyone he was her father. Not because she was ashamed, but because he asked her not to. 'Let them know you for you,' he said.
At graduation, Amara was named top of her class. She walked up to the podium and looked out at the crowd.
'Everything I am, I owe to the man who cleaned these halls every night,' she said. 'Dad, please stand up.'
In the back of the hall, a man in a janitor's uniform slowly stood. And the whole room rose with him.
Moral of the story: there is no small job when it is done out of love.
"""
SCENES = [
    dict(bg="hall", actors=[dict(who="joseph", x=540, p="carry", f=1, e="sad", m="soft", hold="broom")], props=[("mopbucket", 820, GYR)]),
    dict(bg="day", actors=[dict(who="joseph", x=300, p="carry", f=1, e="sad", m="soft", hold="broom"), dict(who="kid1", x=640, p="point_l" if False else "talk", f=-1, m="talk"),
                           dict(who="kid2", x=880, p="stand", f=-1, m="smile")]),
    dict(bg="hall", actors=[dict(who="amara", x=380, p="stand", f=1, m="soft", e="sad"), dict(who="joseph", x=720, p="talk", f=-1, m="talk", m2="smile")]),
    dict(bg="stage", back=[("podium", 540, GYR)], actors=[dict(who="amara", x=540, p="stand", f=1, m="smile", gy=GYR - 10)], props=[("podium", 540, GYR),
                                                                                                                    ("audience", 0, 1560, 1.0)]),
    dict(bg="stage", actors=[dict(who="amara", x=540, p="talk", f=1, m="talk", tears="4")], props=[("podium", 540, GYR), ("audience", 0, 1560, 1.0)]),
    dict(bg="stage", actors=[dict(who="joseph", x=540, p="stand", f=1, e="sad", m="open", tears="2", delay=0.5)],
         props=[("audience", 0, 1560, 1.0, hx("3a3040"))], fx=["glow"]),
    dict(bg="day", actors=[dict(who="amara", x=420, p="hug", f=1, m="smile", tears=0.6), dict(who="joseph", x=660, p="hug", f=-1, m="smile", tears=1.0)],
         fx=["glow", "dust"]),
]
BEATS = make_beats(NARRATION, SCENES)


class Style(DataReel):
    pass
