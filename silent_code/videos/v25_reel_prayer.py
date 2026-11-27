from engine import *
from reel_lib import *

TITLE = "Reel 5 - The Prayer She Wanted to Take Back"
OUTDIR = os.path.join(ROOT, "out_reels")
HOOK = "SHE BEGGED GOD FOR WEALTH FOR 10 YEARS"
KEYWORD = 'TYPE "GOD KNOWS"'
GAP = 1.2
MUSIC = dict(kind="pad+piano", root=103.8, prog=[0, -4, 3, 5], qual=["m", "M", "M", "M"], bar=8, step=1.0, pat=[0, 2, 1, 3], vol=0.11)
POST = dict(title="The Prayer She Wanted to Take Back",
            caption="She begged God for wealth for 10 years. When it came, she begged Him to take it back. 🙏 Comment GOD KNOWS if you trust His timing — share this with someone still waiting on a prayer. #Faith #TrustGod #GodsTiming #LifeLessons",
            pinned="What prayer are you still waiting on — and could the delay be protecting you? 👇")

CAST = dict(
    anna=dict(skin=SKIN["fair"], hair=hx("8a3a22"), hair_style="long", top=hx("5a7a6a"), bottom=hx("3a4a44"), shoes=hx("2e2420"), age=38, h=900),
    husband=dict(skin=SKIN["fair"], hair=hx("3a2a20"), hair_style="short", top=hx("6a6a7a"), bottom=hx("2c3038"), age=42, h=950),
    girl=dict(skin=SKIN["fair"], hair=hx("8a3a22"), hair_style="long", top=hx("e8a4b8"), bottom=hx("4a4a6a"), age=12, h=640),
    boy=dict(skin=SKIN["fair"], hair=hx("3a2a20"), hair_style="short", top=hx("4a7ad9"), bottom=hx("3a3a40"), age=9, h=580),
)
BGS = dict(
    small=("bedroom", dict(wall=(hx("4a4060"), hx("221c33")), floor=hx("3a2e2a"), night=True, sky=(hx("0c1026"), hx("2a2a50")), curtain=hx("5a3a4a"),
                           win=(80, 360, 400, 860), bed=hx("b8a8c8"), grade=(255, 190, 130), grade_s=0.06)),
    office=("office", dict(wall=(hx("f4f1ea"), hx("d8d2c6")), floor=hx("8a7a6a"), sky=(hx("dff0ff"), hx("bcd8f0")), win=(80, 330, 470, 900))),
    big=("mansion", dict(wall=(hx("eef2f6"), hx("b8c4d2")), floor=hx("9aa4b2"), sky=(hx("e6f0fa"), hx("c4d4e6")), trim=hx("ffffff"), grade=(190, 210, 240), grade_s=0.1)),
    bignight=("mansion", dict(wall=(hx("5a6478"), hx("232a3a")), floor=hx("3a4250"), night=True, sky=(hx("0c1226"), hx("232a45")), trim=hx("8a94a8"))),
    warm=("kitchen", dict(wall=(hx("f6d9a8"), hx("d99a5a")), floor=hx("7a5236"), night=True, sky=(hx("1a1830"), hx("4a3a5a")), curtain=hx("9a4a3a"),
                          cab=hx("d9b88a"), win=(70, 330, 430, 900), grade=(255, 190, 120), grade_s=0.12)),
)
NARRATION = """
For ten years, Anna prayed the same prayer: 'Lord, make me rich.'
And for ten years, heaven was silent. She cried. She doubted. She almost stopped believing.
Then, in one year, everything came at once — the business, the money, the big house.
And slowly, the money began to eat her family. No more dinners together. Her husband became a stranger. Her children learned prices, not values.
One night, Anna knelt in her big empty house and prayed a new prayer: 'Lord… take it back. Give me my family instead.'
She understood at last: God was never saying no. He was saying, 'Not yet — you are not ready to carry it.'
Moral of the story: sometimes the delay is not the denial. The delay is the protection.
"""
SCENES = [
    dict(bg="small", back=[("candle", 300, GYR - 10, 0.8)], actors=[dict(who="anna", x=560, p="kneel_pray", f=-1, e="closed", m="sad", tears="1.5")]),
    dict(bg="small", back=[("candle", 300, GYR - 10, 0.8)], actors=[dict(who="anna", x=600, p="sit_hands_face", f=-1, e="closed", m="sad", tears=1.0,
                                                                          gy=GYR - 20)]),
    dict(bg="office", back=[("chair", 440, GYR)], actors=[dict(who="anna", x=440, p="sit_talk", f=1, m="smile")],
         props=[("papers", 720, 1030, 0.9), ("money", 840, 1020, 1.0), ("money", 900, 990, 0.8)], fx=["flash"]),
    dict(bg="big", back=[("table", 540, 1260, 1.5, hx("ffffff"))],
         actors=[dict(who="husband", x=150, p="phone", f=1, m="soft", h=920), dict(who="girl", x=520, p="hold", f=1, m="soft", hold="phone"),
                 dict(who="boy", x=760, p="hold", f=-1, m="soft", hold="phone"), dict(who="anna", x=960, p="stand", f=-1, e="sad", m="sad")]),
    dict(bg="bignight", actors=[dict(who="anna", x=540, p="kneel_pray", f=1, e="closed", m="sad", tears=1.0)], fx=["dark"]),
    dict(bg="bignight", actors=[dict(who="anna", x=540, p="kneel", f=1, e="open", m="soft", m2="smile", tears=0.8)], fx=["glow"]),
    dict(bg="warm", back=[("chair", 200, GYR, 0.9), ("chair_l", 880, GYR)],
         actors=[dict(who="husband", x=200, p="sit_talk", f=1, m="smile"), dict(who="anna", x=880, p="sit_talk", f=-1, m="smile"),
                 dict(who="girl", x=430, p="stand", f=1, m="smile", gy=GYR - 10), dict(who="boy", x=640, p="wave", f=-1, m="smile", gy=GYR - 10)],
         props=[("table", 545, 1200, 1.1, hx("f3ead8")), ("food", 420, 1170), ("food", 560, 1160, 1.2), ("food", 690, 1170)], fx=["glow", "dust"]),
]
BEATS = make_beats(NARRATION, SCENES)


class Style(DataReel):
    pass
