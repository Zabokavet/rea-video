from engine import *
from reel_lib import *

TITLE = "Reel 4 - Why the Quiet Sibling Holds the Whole Family Together"
OUTDIR = os.path.join(ROOT, "out_reels")
HOOK = "THE SIBLING NOBODY THANKS"
KEYWORD = "TAG YOUR QUIET SIBLING"
GAP = 1.2
VOICES = {"n": ("af_heart", 0.77)}
MUSIC = dict(kind="pad+piano", root=116.5, prog=[0, -4, -2, 3], qual=["m", "M", "M", "M"], bar=6, step=0.75, pat=[0, 2, 3, 1], vol=0.1)
POST = dict(title="Why the Quiet Sibling Holds the Whole Family Together",
            caption="Every family has one. Most families never thank her. 💙\nShare this to the quiet sibling in your family — today, not someday.\n#Family #Siblings #LifeLessons #ThankYou",
            pinned="Are YOU the quiet sibling in your family? 👇")

CAST = dict(
    sis=dict(skin=SKIN["light"], hair=hx("3a2a20"), hair_style="bob", top=hx("8fa6c4"), bottom=hx("3e4a5e"), shoes=hx("2e2a2a"), age=31, h=880),
    bro=dict(skin=SKIN["light"], hair=hx("6a4a2a"), hair_style="short", top=hx("2c3038"), bottom=hx("22262e"), shoes=hx("111111"), age=36, h=950, collar=hx("ffffff")),
    loud=dict(skin=SKIN["light"], hair=hx("c9893a"), hair_style="long", top=hx("e05a6a"), bottom=hx("3a3a50"), shoes=hx("e8eef5"), age=27, h=870),
    mom=dict(skin=SKIN["light"], hair=hx("cfc9bf"), hair_style="bun", top=hx("b08aa8"), bottom=hx("4a4250"), skirt=True, leg=SKIN["light"], age=68, h=840, glasses=True),
    dad=dict(skin=SKIN["light"], hair=hx("bdb8b0"), hair_style="short", top=hx("5a6e5a"), bottom=hx("3a3a40"), age=70, h=900),
)
BLUE = dict(wall=(hx("c6d3e6"), hx("7d8fb0")), floor=hx("4e5670"), night=True, sky=(hx("1d2a4a"), hx("5a6a9a")), curtain=hx("3a4a6e"), trim=hx("e6ecf5"),
            grade=(150, 175, 230), grade_s=0.12)
BGS = dict(
    dinner=("room", dict(BLUE, win=(620, 330, 1010, 900))),
    flat=("room", dict(BLUE, wall=(hx("d6dcea"), hx("8d97b8")), curtain=None, win=(80, 360, 420, 900))),
    car=("car", dict(sky=(hx("0b1226"), hx("2a3a66")))),
    dark=("bedroom", dict(BLUE, wall=(hx("4a5675"), hx("1c2238")), floor=hx("262a3a"), win=(80, 360, 420, 900), bed=hx("8a96b4"))),
    door=("porch", dict(night=True, sky=(hx("0e1430"), hx("3a4a7a")), ground=hx("3a4a52"), trees=hx("2a3646"), house=hx("8a96b0"))),
)
NARRATION = """
In every family, there is one sibling nobody talks about.
Not the successful one. Not the loud one. The quiet one.
She is the one who calls your parents every day — so you don't have to feel guilty.
She pays the bill nobody sees. She drives four hours and says it was nothing.
After every family fight, she is the first to forgive — so the family does not break.
Then one evening, she didn't answer her phone.
In one night, the whole family saw it: the calls stopped, the peace stopped, the glue was gone. She had been carrying everyone — silently — for years, and nobody had ever carried her.
Moral of the story: thank the quiet one before their silence becomes permanent.
"""
TABLE = [("chair", 230, GYR, 0.9), ("chair_l", 860, GYR)]
SCENES = [
    dict(bg="dinner", back=TABLE, actors=[dict(who="bro", x=230, p="sit_talk", f=1, m="talk"), dict(who="loud", x=860, p="sit_talk", f=-1, m="talk"),
                                          dict(who="sis", x=540, p="hold", f=1, m="soft", hold="food", gy=GYR - 30)],
         props=[("table", 545, 1180, 1.0, hx("e6ecf5")), ("food", 380, 1150), ("food", 700, 1150)]),
    dict(bg="dinner", actors=[dict(who="bro", x=220, p="talk", f=1, m="talk", h=980), dict(who="loud", x=520, p="wave", f=-1, m="talk"),
                              dict(who="sis", x=860, p="stand", f=-1, m="soft", e="sad", h=840)]),
    dict(bg="flat", back=[("lamp", 900, GYR), ("armchair", 520, GYR)], actors=[dict(who="sis", x=520, p="sit_phone", f=1, m="talk", m2="smile")],
         props=[("phone", 640, 760, 0.8)]),
    dict(bg="car", actors=[dict(who="sis", x=560, gy=1500, h=1000, p="stand", f=1, e="open", m="soft")], props=[("dash", 780, 1000), ("papers", 300, 990, 0.8)]),
    dict(bg="dinner", actors=[dict(who="bro", x=220, p="refuse", f=1, m="open", e="sad"), dict(who="loud", x=860, p="cross", f=-1, m="sad"),
                              dict(who="sis", x=540, p="stand", p2="hug", f=-1, m="soft", m2="smile")]),
    dict(bg="dark", props=[("ringing", 760, 1060, 1.0)], fx=["dark"]),
    dict(bg="door", actors=[dict(who="mom", x=200, f=1, e="sad", m="sad", tears=0.8, h=800), dict(who="bro", x=420, f=1, e="sad", m="sad"),
                            dict(who="loud", x=620, f=1, e="sad", m="sad", tears="1.0", p2="hug"),
                            dict(who="sis", x=860, f=-1, e="sad", m="soft", p="stand", p2="hug", m2="smile", tears=0.6, delay=2.0)]),
    dict(bg="flat", back=[("lamp", 960, GYR)], actors=[dict(who="sis", x=380, f=1, m="smile", p="stand", p2="hug"), dict(who="mom", x=700, f=-1, m="smile", p="give",
                                                                                                                      hold="bouquet")], fx=["glow"]),
]
BEATS = make_beats(NARRATION, SCENES)


class Style(DataReel):
    pass
