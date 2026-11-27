from engine import *
from reel_lib import *

TITLE = "Reel 16 - The Nurse Who Sings"
OUTDIR = os.path.join(ROOT, "out_reels")
HOOK = "SHE SINGS TO STRANGERS IN THEIR LAST HOUR"
KEYWORD = 'TYPE "NO ONE ALONE"'
GAP = 1.35
VOICES = {"n": ("af_heart", 0.78)}
MUSIC = dict(kind="pad+piano", root=103.8, prog=[0, 5, 3, -2], qual=["m", "M", "M", "M"], bar=8, step=1.0, pat=[0, 2, 3, 1], vol=0.1)
POST = dict(title="The Nurse Who Sings",
            caption="Every night shift, she does something that isn't in her job description. 🕯️\nComment NO ONE ALONE if you believe no one should leave this world alone — share this with a nurse you love. #Nurses #Kindness #LifeLessons #Compassion",
            pinned="Who held your hand when you needed it most? 👇")
CAST = dict(
    hannah=dict(skin=SKIN["brown"], hair=hx("1a1210"), hair_style="bun", top=hx("5a8ab4"), bottom=hx("5a8ab4"), shoes=hx("e8eef5"), age=36, h=900),
    doc=dict(skin=SKIN["light"], hair=hx("8a5a3a"), hair_style="short", top=hx("f4f6f8"), bottom=hx("3a4a5a"), age=28, h=950),
    nurse2=dict(skin=SKIN["tan"], hair=hx("6a4a2a"), hair_style="bob", top=hx("5a8ab4"), bottom=hx("5a8ab4"), shoes=hx("e8eef5"), age=30, h=880),
    dad=dict(skin=SKIN["brown"], hair=hx("bdb8b0"), hair_style="short", top=hx("cfe0e8"), bottom=hx("cfe0e8"), age=70, h=880),
)
NIGHT = dict(wall=(hx("2a4a4a"), hx("12222a")), floor=hx("1e2e30"), night=True, sky=(hx("0a1020"), hx("1a2440")), win=(70, 340, 430, 860))
BGS = dict(ward=("hospital", NIGHT), past=("hospital", dict(NIGHT, wall=(hx("5a5a5a"), hx("2a2a2a")), grade=(200, 200, 200), grade_s=0.3)))
BED = [("bed", 640, GYR, 1.0, hx("cfe0e8")), ("patient", 640, GYR, 1.0)]
NARRATION = """
Every night shift, nurse Hannah does something that isn't in her job description.
When a patient is close to the end and has no family left to come, she pulls up a chair, holds their hand, and softly sings.
Her coworkers used to think it was strange.
Then one night, a young doctor asked her why.
Hannah was quiet for a moment. 'My father died in a hospital like this one. I was on a plane, trying to get to him. He died alone, in a room full of machines.'
She looked at the patient beside her. 'I couldn't be there for him. So I'm here for them.'
The young doctor pulled up a chair on the other side of the bed, and stayed.
Moral of the story: no one should leave this world alone. Be someone's hand to hold.
"""
SCENES = [
    dict(bg="ward", actors=[dict(who="hannah", x=560, p="carry", f=1, m="soft", hold="papers", **{"from": 200}, walk=3)], props=[("lamp", 960, GYR)]),
    dict(bg="ward", back=BED + [("chair", 260, GYR)], actors=[dict(who="hannah", x=260, p="sit_talk", f=1, e="closed", m="talk")], props=[("lamp", 960, GYR)], fx=["glow"]),
    dict(bg="ward", actors=[dict(who="nurse2", x=380, p="talk", f=1, m="talk"), dict(who="doc", x=720, p="cross", f=-1, m="soft")]),
    dict(bg="ward", back=BED + [("chair", 260, GYR)], actors=[dict(who="hannah", x=260, p="sit", f=1, m="soft"), dict(who="doc", x=960, p="talk", f=-1, m="talk", h=920)]),
    dict(bg="past", back=[("bed", 640, GYR, 1.0, hx("d8d8d8")), ("patient", 640, GYR, 1.0, hx("b8b8b8"))], fx=["dark"]),
    dict(bg="ward", back=BED + [("chair", 260, GYR)], actors=[dict(who="hannah", x=260, p="sit_talk", f=1, e="sad", m="talk", tears=0.8)], props=[("lamp", 960, GYR)]),
    dict(bg="ward", back=BED + [("chair", 260, GYR), ("chair_l", 980, GYR)], actors=[dict(who="hannah", x=260, p="sit_talk", f=1, e="closed", m="talk"),
                                                                              dict(who="doc", x=980, p="sit", f=-1, m="soft", **{"from": 1300}, walk=2)], fx=["glow"]),
    dict(bg="ward", back=BED + [("chair", 260, GYR), ("chair_l", 980, GYR)], actors=[dict(who="hannah", x=260, p="sit", f=1, m="smile"),
                                                                              dict(who="doc", x=980, p="sit", f=-1, m="smile")], props=[("candle", 640, 1110, 0.6)],
         fx=["glow", "dust"]),
]
BEATS = make_beats(NARRATION, SCENES)


class Style(DataReel):
    pass
