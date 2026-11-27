from engine import *
from reel_lib import *

TITLE = "Reel 19 - The Wooden Bowl"
OUTDIR = os.path.join(ROOT, "out_reels")
HOOK = "THEY MADE GRANDPA EAT ALONE FROM A WOODEN BOWL"
KEYWORD = 'TYPE "RESPECT ELDERS"'
GAP = 1.35
MUSIC = dict(kind="pad+piano", root=98.0, prog=[0, -2, -4, 3], qual=["m", "M", "M", "M"], bar=8, step=1.0, pat=[0, 2, 1, 3], vol=0.11)
POST = dict(title="The Wooden Bowl",
            caption="They made Grandpa eat alone. Their little boy was watching. 🥣\nComment RESPECT ELDERS if you believe our parents deserve a place at the table — share this with your family. #Family #RespectElders #LifeLessons #MoralStory",
            pinned="How do you want to be treated when you are old? 👇")
CAST = dict(
    frank=dict(skin=SKIN["fair"], hair=hx("e3e0da"), hair_style="short", top=hx("7a6a5a"), bottom=hx("4a4036"), age=84, h=850, glasses=True),
    son=dict(skin=SKIN["fair"], hair=hx("6a4a2a"), hair_style="short", top=hx("3a5a7a"), bottom=hx("2c3038"), age=42, h=950),
    wife=dict(skin=SKIN["fair"], hair=hx("c9893a"), hair_style="long", top=hx("a8445a"), bottom=hx("3a3040"), age=40, h=880),
    kid=dict(skin=SKIN["fair"], hair=hx("6a4a2a"), hair_style="short", top=hx("e8b43a"), bottom=hx("3a5a8a"), age=7, h=540),
)
BGS = dict(kitchen=("kitchen", dict(wall=(hx("e8c898"), hx("a8783a")), floor=hx("5a3a24"), night=True, sky=(hx("10101e"), hx("2a2240")), curtain=hx("7a3a2a"),
                                    cab=hx("b88a5a"), win=(70, 330, 430, 900), grade=(255, 190, 120), grade_s=0.12)))
NARRATION = """
Old Frank's hands shook so much that he kept breaking plates at dinner.
So his son and daughter-in-law gave him a wooden bowl, and made him eat alone in the corner of the kitchen.
Sometimes, there were tears in the old man's eyes. Nobody noticed.
One evening, they saw their little boy sitting on the floor, carving a piece of wood.
'What are you making?' his father asked.
The boy smiled. 'Two little bowls. For you and Mom, when I grow up.'
The parents looked at each other, and couldn't say a word.
That night, they led the old man back to the family table. And from then on, nobody said a thing when he spilled his food.
Moral of the story: children watch how you treat your parents. One day, they will treat you the same way.
"""
TABLE = [("chair_l", 900, GYR)]
TOP = [("table", 680, 1200, 0.75, hx("e8dcc0")), ("food", 560, 1170), ("food", 800, 1170)]
SCENES = [
    dict(bg="kitchen", back=[("chair", 460, GYR)], actors=[dict(who="frank", x=460, p="sit_eat", f=1, e="sad", m="open")], props=TOP + [("plate", 900, GYR - 10, 0.8)],
         fx=["flash"]),
    dict(bg="kitchen", back=[("chair", 150, GYR, 0.8)] + TABLE, actors=[dict(who="frank", x=150, p="sit_hold", f=1, e="sad", m="sad", hold="bowl", h=800),
                                                                    dict(who="son", x=900, p="sit_talk", f=-1, m="talk"), dict(who="wife", x=540, p="stand", f=-1, m="soft")],
         props=TOP),
    dict(bg="kitchen", back=[("chair", 300, GYR, 0.8)], actors=[dict(who="frank", x=300, p="sit_hold", f=1, e="sad", m="sad", hold="bowl", tears="1.5")]),
    dict(bg="kitchen", actors=[dict(who="kid", x=420, p="kneel", f=1, m="smile", h=520), dict(who="son", x=820, p="stand", f=-1, m="soft", delay=2)],
         props=[("bowl", 560, GYR - 10, 0.6)]),
    dict(bg="kitchen", actors=[dict(who="kid", x=420, p="kneel", f=1, m="smile", h=520), dict(who="son", x=780, p="kneel", f=-1, m="talk")],
         props=[("bowl", 560, GYR - 10, 0.6)]),
    dict(bg="kitchen", actors=[dict(who="kid", x=420, p="kneel", f=1, m="talk", m2="smile", h=520), dict(who="son", x=780, p="kneel", f=-1, e="open", m="open")],
         props=[("bowl", 540, GYR - 10, 0.6), ("bowl", 600, GYR - 10, 0.6)]),
    dict(bg="kitchen", actors=[dict(who="son", x=360, p="stand", f=1, e="sad", m="sad"), dict(who="wife", x=720, p="hands_face", f=-1, e="closed", m="sad", tears="2")]),
    dict(bg="kitchen", back=[("chair", 300, GYR), ("chair_l", 1000, GYR)],
         actors=[dict(who="frank", x=300, p="sit_eat", f=1, m="smile", tears=0.6), dict(who="kid", x=560, p="stand", f=-1, m="smile", gy=GYR - 10),
                 dict(who="son", x=1000, p="sit_talk", f=-1, m="smile")], props=[("table", 650, 1200, 0.9, hx("e8dcc0")), ("food", 470, 1170), ("food", 800, 1170)], fx=["glow"]),
    dict(bg="kitchen", back=[("chair", 300, GYR), ("chair_l", 1000, GYR)],
         actors=[dict(who="frank", x=300, p="sit_talk", f=1, m="smile"), dict(who="wife", x=650, p="stand", f=-1, m="smile", gy=GYR - 10),
                 dict(who="son", x=1000, p="sit", f=-1, m="smile")], props=[("table", 650, 1200, 0.9, hx("e8dcc0")), ("food", 470, 1170)], fx=["glow", "dust"]),
]
BEATS = make_beats(NARRATION, SCENES)


class Style(DataReel):
    pass
