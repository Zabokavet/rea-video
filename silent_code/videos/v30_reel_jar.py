from engine import *
from reel_lib import *

TITLE = "Reel 10 - The Coin Jar Under the Bed"
OUTDIR = os.path.join(ROOT, "out_reels")
HOOK = "SHE FOUND HIS SECRET JAR AFTER 30 YEARS"
KEYWORD = 'TYPE "TRUE LOVE"'
GAP = 1.15
MUSIC = dict(kind="pad+piano", root=123.5, prog=[0, 5, -3, 3], qual=["M", "M", "m", "M"], bar=6, step=0.75, pat=[0, 1, 2, 3, 2, 1], vol=0.1)
POST = dict(title="The Coin Jar Under the Bed",
            caption="She thought he was hiding something. He was — for thirty years. 🌊❤️\nComment TRUE LOVE if you believe in this kind of love — share it with the person who quietly gives things up for you. #TrueLove #Marriage #LifeLessons #MoralStory",
            pinned="What small thing does your partner quietly give up for you? 👇")
CAST = dict(
    rosa=dict(skin=SKIN["tan"], hair=hx("9a948c"), hair_style="bun", top=hx("d96a5a"), bottom=hx("4a3a3a"), skirt=True, leg=SKIN["tan"], age=58, h=880),
    tom=dict(skin=SKIN["tan"], hair=hx("bdb8b0"), hair_style="short", top=hx("4a6a8a"), bottom=hx("5a5048"), age=62, h=940),
)
BGS = dict(
    bed=("bedroom", dict(wall=(hx("fbf1e0"), hx("e6cfaa")), floor=hx("9a7a5a"), sky=(hx("fff6e0"), hx("ffe0b0")), curtain=hx("c98a6a"), win=(80, 360, 420, 860),
                         bed=hx("f4e8d8"))),
    beach=("beach", dict(sky=(hx("ff8a6a"), hx("ffd9a0")), sea=hx("3a6aa0"), sand=hx("e8c890"))),
)
NARRATION = """
After thirty years of marriage, Rosa found a jar hidden under the bed, full of coins and little folded notes.
Her heart sank. What had her husband, Tom, been hiding?
She opened the first note. 'Skipped my coffee today. One dollar for the sea.'
The next one: 'Walked home instead of the bus. Two dollars for the sea.'
There were hundreds of them.
On their first date, Rosa had told Tom that her dream was to see the ocean. She had never seen it. She had forgotten she ever said it.
He hadn't.
That summer, Tom took her hand at the edge of the water, and Rosa cried like a girl of twenty.
Moral of the story: real love is not in grand gestures. It is in the small things someone quietly gives up for you.
"""
SCENES = [
    dict(bg="bed", actors=[dict(who="rosa", x=380, p="kneel", f=1, e="open", m="open")], props=[("jar", 720, GYR - 10, 1.1)], fx=["dust"]),
    dict(bg="bed", actors=[dict(who="rosa", x=480, p="hold", f=1, e="sad", m="sad", hold="jar")]),
    dict(bg="bed", actors=[dict(who="rosa", x=480, p="hold", f=1, e="open", m="soft", hold="letter")], props=[("jar", 820, GYR - 10, 0.9)]),
    dict(bg="bed", actors=[dict(who="rosa", x=480, p="hold", f=1, e="sad", m="soft", tears="2", hold="letter")], props=[("jar", 820, GYR - 10, 0.9)]),
    dict(bg="bed", actors=[dict(who="rosa", x=380, p="kneel", f=1, e="sad", m="open", tears=0.6)],
         props=[("jar", 720, GYR - 10, 1.1)] + [("envelope", 520 + (i % 5) * 110, GYR - 20 - (i // 5) * 40, 0.6) for i in range(10)]),
    dict(bg="beach", actors=[dict(who="rosa", x=380, p="talk", f=1, m="talk"), dict(who="tom", x=700, p="stand", f=-1, m="smile")], fx=["flash"]),
    dict(bg="bed", actors=[dict(who="tom", x=540, p="stand", f=1, m="smile")], props=[("jar", 820, GYR - 10, 0.9)], fx=["glow"]),
    dict(bg="beach", actors=[dict(who="rosa", x=440, p="hug", f=1, e="closed", m="smile", tears=1.0), dict(who="tom", x=660, p="hug", f=-1, m="smile")], fx=["glow"]),
    dict(bg="beach", actors=[dict(who="rosa", x=440, p="stand", f=1, m="smile"), dict(who="tom", x=650, p="stand", f=-1, m="smile")], fx=["glow", "dust"]),
]
BEATS = make_beats(NARRATION, SCENES)


class Style(DataReel):
    pass
