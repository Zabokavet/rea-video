from engine import *
from reel_lib import *

TITLE = "Reel 13 - The Brother Who Left School"
OUTDIR = os.path.join(ROOT, "out_reels")
HOOK = "HE QUIT SCHOOL SO HIS BROTHER WOULDN'T HAVE TO"
KEYWORD = 'TYPE "BROTHER"'
GAP = 1.15
MUSIC = dict(kind="pad+piano", root=87.3, prog=[0, -4, 3, 5], qual=["m", "M", "M", "M"], bar=6, step=0.75, pat=[0, 2, 1, 3], vol=0.11)
POST = dict(title="The Brother Who Left School",
            caption="He carried bricks for twelve years so his brother could carry books. 🧱🎓\nComment BROTHER if someone sacrificed for your success — share this with them. #Brothers #Family #Sacrifice #LifeLessons",
            pinned="Who carried something for you that you never saw? 👇")
CAST = dict(
    samuel=dict(skin=SKIN["brown"], hair=hx("1a1210"), hair_style="short", top=hx("b07a4a"), bottom=hx("5a4a3a"), shoes=hx("4a3428"), age=16, h=900),
    samuel_man=dict(skin=SKIN["brown"], hair=hx("1a1210"), hair_style="short", top=hx("b07a4a"), bottom=hx("5a4a3a"), shoes=hx("4a3428"), age=28, h=940,
                    hand=hx("b8a080")),
    david=dict(skin=SKIN["brown"], hair=hx("1a1210"), hair_style="short", top=hx("e8eef5"), bottom=hx("3a4a6a"), age=10, h=600),
    david_dr=dict(skin=SKIN["brown"], hair=hx("1a1210"), hair_style="short", top=hx("1c1c22"), bottom=hx("1c1c22"), age=22, h=930),
)
BGS = dict(
    home=("room", dict(wall=(hx("e8d4b8"), hx("b8946a")), floor=hx("6a4a30"), sky=(hx("c8c0b8"), hx("a8a098")), curtain=hx("6a5a4a"))),
    yard=("farm", dict(sky=(hx("ff9a4a"), hx("ffd08a")), ground=hx("c08a5a"), trees=hx("a86a3a"))),
    stage=("stage", dict(wall=(hx("2a2a44"), hx("14141e")), floor=hx("4a3a2a"), curtain=hx("2a3a7a"))),
)
NARRATION = """
When their father died, Samuel was sixteen, and his little brother David was ten.
There was only enough money for one of them to stay in school.
Samuel didn't even let David choose. He packed his books into a box, and the next morning he went to work at the brickyard.
For twelve years, he carried bricks in the heat, and sent every spare coin to his brother's school.
David became a doctor.
At his graduation, they handed him his diploma, and he walked straight past the stage, down to the back row, where Samuel sat in his work clothes with dusty hands.
He placed the diploma in his brother's hands and said, 'This one is yours. I only carried it.'
Moral of the story: behind every success is someone who carried what you never saw.
"""
SCENES = [
    dict(bg="home", actors=[dict(who="samuel", x=380, p="hug", f=1, e="sad", m="sad", tears=0.6), dict(who="david", x=620, p="hands_face", f=-1, e="closed", m="sad", tears=1.0)],
         props=[("photo", 820, 900, 0.8)]),
    dict(bg="home", actors=[dict(who="samuel", x=380, p="stand", f=1, e="sad", m="soft"), dict(who="david", x=700, p="stand", f=-1, e="sad", m="soft")],
         props=[("money", 540, 1190, 0.8), ("table", 540, 1220, 0.5, hx("8a6a4a"))]),
    dict(bg="home", actors=[dict(who="samuel", x=420, p="hold", f=1, m="smile", hold="box"), dict(who="david", x=760, p="stand", f=-1, e="open", m="open")]),
    dict(bg="yard", back=[("bricks", 840, GYR, 1.6)], actors=[dict(who="samuel_man", x=420, p="hold", f=1, e="sad", m="soft", hold="box", tears=0)], fx=["dust"]),
    dict(bg="stage", actors=[dict(who="david_dr", x=540, p="stand", f=1, m="smile")], props=[("cap_gown", 540, 470, 1.0), ("podium", 840, GYR)]),
    dict(bg="stage", actors=[dict(who="david_dr", x=320, p="hold", f=1, m="soft", hold="diploma", **{"from": 120}, walk=3),
                             dict(who="samuel_man", x=800, p="sit", f=-1, e="open", m="soft", gy=GYR + 40)], back=[("chair_l", 800, GYR + 40)],
         props=[("audience", 0, 1560, 1.0)]),
    dict(bg="stage", back=[("chair_l", 760, GYR + 40)], actors=[dict(who="david_dr", x=420, p="give", f=1, m="talk", tears=0.8, hold="diploma"),
                                                            dict(who="samuel_man", x=760, p="sit_hold", f=-1, e="sad", m="smile", tears=1.0, gy=GYR + 40)],
         props=[("audience", 0, 1560, 1.0)], fx=["glow"]),
    dict(bg="stage", actors=[dict(who="david_dr", x=430, p="hug", f=1, m="smile", tears=0.6), dict(who="samuel_man", x=650, p="hug", f=-1, m="smile", tears=0.8)],
         fx=["glow", "dust"]),
]
BEATS = make_beats(NARRATION, SCENES)


class Style(DataReel):
    pass
