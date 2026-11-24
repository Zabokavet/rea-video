from engine import *

TITLE = "Confessions of a Former People-Pleaser"
VOICES = {"n": ("af_heart", 0.86)}
GAP = 0.9
MUSIC = dict(kind="piano+pad", root=98.0, prog=[0, 3, -4, -2], qual=["m", "M", "M", "M"], bar=8, step=1.0, pat=[0, 1, 2, 1], vol=0.12)


def C(say, label="", line="", **kw):
    return dict(say=say, v=dict(k="room", label=label, line=line, **kw))


BEATS = [
    C("I said yes to things I hated, for twelve years. Not because I was kind. Because I was scared.", line="12 years of yes.", hook=True, gap=1.1),
    C("Confession one. My kindness was a strategy. If everyone liked me, no one could leave me. I didn't help people because I wanted to. I helped them so they'd stay.",
      "confession no. 1", "my kindness was a strategy."),
    C("Confession two. I had no idea what I liked. Ask me where to eat, and I'd say, whatever you want. It sounded easygoing. It was actually empty.",
      "confession no. 2", "\"whatever you want.\""),
    C("Confession three. I was secretly angry, all the time. Every yes I didn't mean became a small resentment, and I smiled right over it.",
      "confession no. 3", "every fake yes became resentment."),
    C("Psychologists describe something called the fawn response. When you feel threatened, instead of fighting or running, you try to please the danger away. It often begins in childhood, in homes where someone's mood decided whether you were safe.",
      "the fawn response", "please the danger away.", fawn=True),
    C("Confession four. I attracted people who take. Of course I did. I was an open door with a welcome sign. The takers found me. The givers found me boring.",
      "confession no. 4", "an open door with a welcome sign."),
    C("Here's what changed. One night a friend asked me to cover her shift, for the fourth time that month. I typed, of course, no problem. And then I deleted it. I wrote, I can't this time. My hands were shaking.",
      "", "", phone=1),
    C("She replied: no worries. That's it. No disaster. Twelve years of fear, and the truth was two words long.", "", "", phone=2),
    C("Confession five. Saying no felt like guilt at first. But that guilt wasn't a sign I was doing something wrong. It was a sign I was doing something new.",
      "confession no. 5", "guilt can mean: new, not wrong.", dawn=0.3),
    C("If you're like I was, start small. Wait three seconds before you answer any request. Say, let me check and get back to you. And notice who gets angry at your boundaries, because that tells you exactly who benefited from you having none.",
      "start small", "three seconds. \"let me check.\"", dawn=0.6),
    C("I'm still kind. But now it's a choice. Not a survival plan.", "", "a choice, not a survival plan.", dawn=1.0, gap=1.2),
    dict(say="What's the one thing you keep saying yes to, that you wish you could say no to? You can confess it here, in the comments. No judgment.",
         v=dict(k="question", dawn=1.0)),
]

WALL = hx("16202a")
SOFT = (238, 230, 222)
PEACH = hx("ffc6a5")
WX0, WY0, WX1, WY1 = 1180, 170, 1640, 640


class Style(Base):
    cap = dict(font="Inter", size=50, w=400, y=1000, fill=(225, 220, 215), hl=PEACH, maxw=1500, stroke=2, sfill=(10, 14, 18))
    xfade = 0.9

    def setup(self):
        wall = gradient(hx("1b2733"), hx("0c1117"))
        wall = texture(wall, 4, 3, blur=1)
        d = D(wall)
        d.rectangle((0, 860, W, H), fill=A(hx("0a0d11"), 1))
        self.BG = vignette(wall, 0.6)
        self.dawn = []
        cur = 0.0
        for b in self.beats:
            cur = b.v.get("dawn", cur)
            self.dawn.append(cur)

    def room(self, d, b, lt, t, img):
        prev = self.dawn[b.i - 1] if b.i else 0
        dawn = lerp(prev, self.dawn[b.i], ease(lt / 3))
        sky_top = mixc(hx("0d1a33"), hx("f2b38a"), dawn)
        sky_bot = mixc(hx("1a2a4a"), hx("ffe0b8"), dawn)
        for i in range(10):
            y0 = WY0 + (WY1 - WY0) * i / 10
            d.rectangle((WX0, y0, WX1, y0 + (WY1 - WY0) / 10 + 1), fill=A(mixc(sky_top, sky_bot, i / 9), 1))
        if dawn < 0.5:
            rain(d, t, (170, 190, 220), n=60, alpha=0.35 * (1 - dawn * 2), speed=700, box=(WX0, WY0, WX1, WY1))
        else:
            r = 50
            d.ellipse((WX0 + 300 - r, WY1 - 80 - r - dawn * 60, WX0 + 300 + r, WY1 - 80 + r - dawn * 60), fill=A((255, 230, 190), dawn))
        d.rectangle((WX0, WY0, WX1, WY1), outline=A(hx("2c3a48"), 1), width=16)
        d.line([((WX0 + WX1) / 2, WY0), ((WX0 + WX1) / 2, WY1)], fill=A(hx("2c3a48"), 1), width=10)
        d.line([(WX0, (WY0 + WY1) / 2), (WX1, (WY0 + WY1) / 2)], fill=A(hx("2c3a48"), 1), width=10)
        # light spill on floor
        d.polygon([(WX0, WY1), (WX1, WY1), (WX1 + 160, 860), (WX0 - 260, 860)], fill=A(mixc((120, 150, 200), (255, 210, 160), dawn), 0.06 + 0.06 * dawn))
        # bed + figure
        d.rectangle((620, 770, 1060, 860), fill=A(hx("2a3644"), 1))
        d.rectangle((600, 700, 640, 860), fill=A(hx("223040"), 1))
        candle(d, 420, 860, 150, hx("d8cfc0"), t=t)
        pose = "sit_sad" if dawn < 0.5 else "sit"
        face = "frown" if dawn < 0.3 else ("flat" if dawn < 0.8 else "smile")
        figure(d, 860, 860, 290, pose, SOFT, t, face=face, head_fill=WALL)

    def draw(self, img, b, lt, t):
        d = D(img)
        v = b.v
        self.room(d, b, lt, t, img)
        if v["k"] == "room":
            if v.get("hook"):
                text(d, (130, 330), v["line"], F("shadows", 110), PEACH, "lm", alpha=ease((lt - 0.5) / 1.0))
                text(d, (135, 440), "confessions of a former people-pleaser", F("shadows", 46), SOFT, "lm", alpha=ease((lt - 2.5) / 1.0))
            else:
                if v.get("label"):
                    text(d, (130, 230), v["label"], F("shadows", 46), hx("8fa3b5"), "lm", alpha=ease((lt - 0.3) / 0.8))
                if v.get("line"):
                    para(d, 130, 290, v["line"], F("shadows", 76), PEACH, 1000, align="l", valign="t", alpha=ease((lt - 1.2) / 1.0))
            if v.get("phone"):
                px, py = 940, 770
                phone(d, px, py, 95, (20, 20, 24), screen=hx("26344a"), glow=0.8)
                if v["phone"] == 1:
                    txt = "of course, no problem!" if 4.5 < lt < 7.5 else ("I can't this time." if lt >= 8.5 else "")
                    if txt:
                        bubble(d, 520, 480, txt, F("Inter", 36, 500), SOFT if lt < 8 else PEACH, WALL, tail=(1, 1))
                    if 7.5 <= lt < 8.5:
                        scribble(d, 400, 650, 480, hx("ff6b6b"), 5, ease((lt - 7.5) / 0.5), amp=2)
                else:
                    bubble(d, 520, 480, "no worries", F("Inter", 40, 600), hx("cde8ff"), WALL, tail=(1, 1), alpha=ease((lt - 0.5) / 0.3))
                    text(d, (130, 300), "two words.", F("shadows", 76), PEACH, "lm", alpha=ease((lt - 5) / 0.8))
            if v.get("fawn"):
                for i, w in enumerate(("fight", "flight", "freeze", "fawn")):
                    aa = ease((lt - 3 - i * 0.6) / 0.5)
                    c = PEACH if w == "fawn" else hx("62788c")
                    text(d, (160 + i * 230, 430), w, F("shadows", 56), c, "lm", alpha=aa)
        elif v["k"] == "question":
            a = ease(lt / 1.0)
            d.rectangle((0, 0, W, H), fill=A((8, 10, 14), 0.55 * a))
            para(d, W / 2, 400, "what do you keep saying yes to, when you mean no?", F("shadows", 84), PEACH, 1400, alpha=a)
            text(d, (W / 2, 600), "confess it in the comments. no judgment.", F("shadows", 50), SOFT, alpha=ease((lt - 2) / 1.0))

    def captions(self, img, t):
        ch = self.tl.chunk_at(t)
        if ch:
            for w in ch:
                pass
        Base.captions(self, img, t)

    def show_cap(self, b):
        return b.v["k"] != "question"
