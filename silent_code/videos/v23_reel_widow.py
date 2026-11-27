from engine import *
from reel_lib import *

TITLE = "Reel 3 - The Rich Man Who Refused the Poor Widow's Food"
OUTDIR = os.path.join(ROOT, "out_reels")
HOOK = "HE REFUSED HER FOOD… THEN HE REMEMBERED"
KEYWORD = 'TYPE "KINDNESS"'
MUSIC = dict(kind="pad+piano", root=130.8, prog=[0, -3, 5, 7], qual=["M", "m", "M", "M"], bar=6, step=0.75, pat=[0, 1, 2, 3, 2, 1], vol=0.1)
GAP = 1.1
POST = dict(title="The Rich Man Who Refused the Poor Widow's Food",
            caption="He forgot where he came from. She reminded him with one sentence. 😢\nComment KINDNESS if you believe no good deed is ever forgotten — share this with someone who once fed you. #Kindness #Gratitude #LifeLessons #MoralStory",
            pinned="Who fed you when you had nothing — have you thanked them? 👇")

CAST = dict(
    martha=dict(skin=SKIN["deep"], hair=hx("bdb6ab"), hair_style="bun", top=hx("3f6f8a"), bottom=hx("2f4f62"), skirt=True, leg=SKIN["deep"],
                shoes=hx("3a2a22"), age=74, h=860, collar=hx("efe6d6")),
    martha_young=dict(skin=SKIN["deep"], hair=hx("2a1d16"), hair_style="bun", top=hx("3f6f8a"), bottom=hx("2f4f62"), skirt=True, leg=SKIN["deep"],
                      shoes=hx("3a2a22"), age=34, h=880, collar=hx("efe6d6")),
    henry=dict(skin=SKIN["light"], hair=hx("e3e0da"), hair_style="short", top=hx("3a3f4a"), bottom=hx("2c3038"), shoes=hx("111111"), age=50, h=960,
               collar=hx("ffffff")),
    boy=dict(skin=SKIN["light"], hair=hx("6a4a2a"), hair_style="short", top=hx("9a8a70"), bottom=hx("6a5a48"), shoes=SKIN["light"], age=9, h=560),
    guest1=dict(skin=SKIN["brown"], hair=hx("2a1d16"), hair_style="bob", top=hx("c98a3a"), bottom=hx("5a4a3a"), skirt=True, leg=SKIN["brown"], age=40, h=820),
    guest2=dict(skin=SKIN["fair"], hair=hx("8a6a44"), hair_style="short", top=hx("6a8a5a"), bottom=hx("3a3a40"), age=45, h=880),
)
HALL = dict(wall=(hx("fff6e6"), hx("efd9b5")), floor=hx("a8805a"), sky=(hx("fffbe8"), hx("dff0ff")), trim=hx("ffffff"), grade=(255, 236, 200), grade_s=0.06)
BGS = dict(
    hall=("hall", HALL),
    porch=("porch", dict(sky=(hx("e8c48a"), hx("f6e2bc")), ground=hx("a08a5a"), trees=hx("8a7a4a"), house=hx("d9c4a0"), grade=(200, 150, 90), grade_s=0.25)),
    kitchen=("kitchen", dict(wall=(hx("f6d9a8"), hx("d9a66a")), floor=hx("7a5236"), sky=(hx("ffd27a"), hx("ffb05a")), curtain=hx("8a5a3a"),
                             cab=hx("c9a87a"), win=(70, 330, 430, 900), grade=(255, 200, 120), grade_s=0.1)),
)
NARRATION = """
At the church feast, everyone brought a dish.
Widow Martha brought a small pot of rice and beans — all she had.
When she offered it to Mr. Henry, the richest man in town, he looked at the worn pot and waved it away. 'No, thank you,' he said — loud enough for others to hear.
Martha lowered her eyes… and smiled sadly. 'You ate from this pot before, Henry.'
He froze.
Forty years earlier, a homeless boy with no shoes used to knock on a poor woman's door — and she fed him from that same pot, though she barely had enough for her own children.
That boy was him.
Henry took the pot with both hands, in tears, and ate every grain.
Moral of the story: never look down on the hand that once fed you.
"""
FEAST = [("table", 540, 1080, 1.5, hx("ffffff")), ("food", 340, 1050, 1.0, hx("c9603a")), ("food", 540, 1045, 1.1, hx("e8b43a")),
         ("food", 740, 1050, 1.0, hx("8ab35a"))]
SCENES = [
    dict(bg="hall", back=FEAST, actors=[dict(who="guest1", x=230, f=1, m="smile", h=760), dict(who="guest2", x=860, f=-1, m="talk", h=800),
                                       dict(who="martha", x=540, f=1, p="carry", m="soft", hold="pot", **{"from": -150}, walk=4.0)], fx=["dust"]),
    dict(bg="hall", actors=[dict(who="martha", x=540, f=1, p="hold", m="smile", e="open", hold="pot")], fx=["dust"]),
    dict(bg="hall", back=[("table", 540, 1180, 1.5, hx("ffffff"))],
         actors=[dict(who="guest1", x=120, f=1, m="open", h=740, delay=4), dict(who="martha", x=330, f=1, p="give", m="smile", m2="sad", e2="sad", hold="pot", at=0.35),
                 dict(who="henry", x=780, f=-1, p="stand", p2="refuse", at=0.35, m="soft", m2="talk")]),
    dict(bg="hall", actors=[dict(who="martha", x=330, f=1, p="hold", e="sad", m="smile", hold="pot"), dict(who="henry", x=780, f=-1, p="cross", m="soft")]),
    dict(bg="hall", actors=[dict(who="martha", x=330, f=1, p="hold", e="sad", m="smile", hold="pot"), dict(who="henry", x=780, f=-1, p="stand", e="open", m="open")],
         fx=["flash"]),
    dict(bg="porch", actors=[dict(who="boy", x=330, f=1, p="stand", e="sad", m="sad", **{"from": 120}, walk=2.5),
                             dict(who="martha_young", x=760, f=-1, p="give", m="smile", hold="pot", delay=3.5)]),
    dict(bg="porch", back=[("chair", 420, GYR, 0.75)], actors=[dict(who="boy", x=420, f=1, p="sit_eat", m="smile", hold="bowl", h=580), dict(who="martha_young", x=780, f=-1, p="stand", m="smile")],
         fx=["flash"]),
    dict(bg="hall", actors=[dict(who="martha", x=300, f=1, p="stand", m="smile", tears=0.6),
                            dict(who="henry", x=720, f=-1, p="hold", e="closed", m="sad", tears=1.0, hold="pot")]),
    dict(bg="kitchen", back=[("chair", 280, GYR), ("chair_l", 800, GYR)],
         actors=[dict(who="martha", x=280, p="sit", f=1, m="smile"), dict(who="henry", x=800, p="sit_eat", f=-1, m="smile")],
         props=[("table", 540, 1150, 1.0, hx("e8dcc0")), ("pot", 540, 1120, 0.9), ("food", 700, 1115)], fx=["glow", "dust"]),
]
BEATS = make_beats(NARRATION, SCENES)


class Style(DataReel):
    pass
