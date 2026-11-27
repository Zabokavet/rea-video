from engine import *
from reel_lib import *

TITLE = "Reel 6 - The Old Man Who Ordered Two Coffees"
OUTDIR = os.path.join(ROOT, "out_reels")
HOOK = "HE ORDERED TWO COFFEES EVERY DAY FOR 3 YEARS"
KEYWORD = 'TYPE "SIT WITH THEM"'
MUSIC = dict(kind="pad+piano", root=110.0, prog=[0, 5, 3, -2], qual=["m", "M", "M", "M"], bar=6, step=0.75, pat=[0, 2, 1, 3], vol=0.1)
POST = dict(title="The Old Man Who Ordered Two Coffees",
            caption="Everyone thought he was confused. One question changed everything. ☕💔\nComment SIT WITH THEM if you'd have sat down too — share this with someone who never lets anyone feel alone. #Kindness #Love #LifeLessons #MoralStory",
            pinned="Who in your life is drinking their coffee alone right now? 👇")
CAST = dict(
    walter=dict(skin=SKIN["fair"], hair=hx("e3e0da"), hair_style="short", top=hx("8a6a4a"), bottom=hx("4a4036"), shoes=hx("3a2a20"), age=80, h=880, glasses=True,
                collar=hx("f0ece4")),
    lily=dict(skin=SKIN["brown"], hair=hx("1e1612"), hair_style="long", top=hx("f4f1ea"), bottom=hx("2a2a30"), shoes=hx("1e1e1e"), age=24, h=880),
    staff=dict(skin=SKIN["light"], hair=hx("c9893a"), hair_style="bob", top=hx("f4f1ea"), bottom=hx("2a2a30"), age=30, h=860),
)
CAFE = dict(wall=(hx("4a3a3a"), hx("2a2024")), floor=hx("5a3a2a"), sky=(hx("8a9aaa"), hx("c4ccd4")), trim=hx("2a1e1a"), win=(60, 360, 520, 1000),
            grade=(255, 200, 140), grade_s=0.08)
BGS = dict(cafe=("restaurant", CAFE), cafe_rain=("restaurant", dict(CAFE, sky=(hx("5a6a7a"), hx("8a98a6")))))
NARRATION = """
Every morning at eight, old Walter ordered two coffees at the same little café.
He drank one. The other went cold across the table, untouched.
The new waitress, Lily, thought he was confused. The others just rolled their eyes.
One rainy morning, she finally asked him, 'Who is the second coffee for?'
Walter smiled. 'My wife, Ellen. Fifty-one years, we had coffee here together. She passed three years ago. I'm not ready to drink alone.'
Lily said nothing. She took off her apron, sat down in the empty chair, and drank the cold coffee with him.
From that day on, she joined him every morning at eight.
When Walter passed away a year later, he left her a note: 'Thank you for not letting me drink alone.'
Moral of the story: you never know what someone is carrying. Sit with them anyway.
"""
T = [("chair", 300, GYR), ("chair_l", 800, GYR)]
TB = [("table", 550, 1170, 0.75, hx("e8dcc8")), ("cup", 450, 1140), ("cup", 660, 1140)]
SCENES = [
    dict(bg="cafe", back=T[:1], actors=[dict(who="walter", x=300, p="sit", f=1, m="smile")], props=TB + [("steam", 450, 1090), ("steam", 660, 1090)], fx=["dust"]),
    dict(bg="cafe", back=T[:1] + [("chair_l", 800, GYR)], actors=[dict(who="walter", x=300, p="sit_eat", f=1, m="soft", e="sad")], props=TB + [("steam", 450, 1090)]),
    dict(bg="cafe", actors=[dict(who="lily", x=360, p="cross", f=1, e="open", m="soft"), dict(who="staff", x=760, p="talk", f=-1, m="smirk" if False else "talk")]),
    dict(bg="cafe_rain", back=T[:1], actors=[dict(who="walter", x=300, p="sit", f=1, m="soft"), dict(who="lily", x=780, p="talk", f=-1, m="talk", m2="soft")],
         props=TB, fx=["rain"]),
    dict(bg="cafe_rain", back=T[:1], actors=[dict(who="walter", x=300, p="sit_talk", f=1, m="talk", e="sad", tears="6"), dict(who="lily", x=780, p="stand", f=-1, e="sad", m="sad")],
         props=TB + [("photo", 550, 1060, 0.6)], fx=["rain"]),
    dict(bg="cafe", back=T, actors=[dict(who="walter", x=300, p="sit", f=1, m="smile", tears=0.7), dict(who="lily", x=800, p="sit_eat", f=-1, m="smile",
                                                                                                    **{"from": 980}, walk=1.5)], props=TB),
    dict(bg="cafe", back=T, actors=[dict(who="walter", x=300, p="sit_talk", f=1, m="talk"), dict(who="lily", x=800, p="sit_talk", f=-1, m="smile")],
         props=TB + [("steam", 450, 1090), ("steam", 660, 1090)], fx=["glow", "dust"]),
    dict(bg="cafe", back=T, actors=[dict(who="lily", x=800, p="sit_hold", f=-1, e="sad", m="sad", tears="2", hold="letter")],
         props=TB),
    dict(bg="cafe", back=T, actors=[dict(who="lily", x=800, p="sit", f=-1, m="smile")], props=TB + [("steam", 450, 1090), ("steam", 660, 1090)],
         fx=["glow", "dust"]),
]
BEATS = make_beats(NARRATION, SCENES)


class Style(DataReel):
    pass
