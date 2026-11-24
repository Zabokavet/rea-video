from engine import *

TITLE = "Your Heart vs Your Mind - Who Should Win"
VOICES = {"h": ("af_bella", 0.86), "m": ("bm_daniel", 0.88)}
GAP = 0.6
CAP_WORDS = 6
MUSIC = dict(kind="pad+piano", root=116.5, prog=[0, 5, -3, 2], qual=["M", "M", "m", "M"], bar=6, step=0.75, pat=[0, 1, 2, 3, 2, 1], vol=0.1)


def Ht(say, note="", **kw):
    return dict(say=say, who="h", v=dict(k="talk", note=note, **kw))


def Mi(say, note="", **kw):
    return dict(say=say, who="m", v=dict(k="talk", note=note, **kw))


BEATS = [
    Ht("Wait. Before you decide anything, listen to me. I'm the one who actually knows what you want.", "I know what you want.", sfx=[("ding", 0, 0.4)]),
    Mi("And I'm the one who stops you from wrecking your life over a feeling. Hello. I'm your mind.", "Hello. I'm your mind."),
    Ht("Your mind loves to pretend it's in charge. But here's a fact. Neuroscientist Antonio Damasio studied a man with damage to the brain area that links emotion to decisions. His logic was perfect. And he couldn't make even simple choices.",
      "Damasio: no emotion, no decisions", fact=True),
    Mi("Fair. Emotions carry information. But you exaggerate. You told them he was the one. Three times. About three different people.", "\"the one\" × 3", tally=3),
    Ht("I was in love!", "I was in love!", gap=0.3),
    Mi("You were intense. Research shows people are poor at predicting how future events will make them feel. We overestimate how happy good things will make us, and how long bad things will hurt. It's called the impact bias. That one's your department.",
       "IMPACT BIAS", graph=True),
    Ht("And you overthink. You make spreadsheets for things that need courage. You kept them in a job they hated for four years, because it was the safe choice.", "Four years of 'safe'."),
    Mi("Safe is not a crime.", "Safe ≠ crime", gap=0.3),
    Ht("Safe is not a life, either.", "Safe ≠ a life", gap=0.5),
    Mi("Fine. Then give me one example where you were right.", "One example."),
    Ht("The friend you almost didn't call back. You were exhausted. I said, call. That call got them through a very bad night.", "\"Call them.\""),
    Mi("I'll allow that one.", "...allowed.", gap=0.6),
    Mi("Then let's be honest. When you flood the system with anger, panic, heartbreak, I go offline. Heart rate goes up, judgment goes down. That's when they send the text they regret at two in the morning.",
       "pulse up, judgment down", gauge=True),
    Ht("So what do you want? To silence me?", "Silence me?"),
    Mi("No. I want you to speak first. Then I want a minute. Psychologist Matthew Lieberman found that simply naming an emotion, putting the feeling into words, calms the brain's alarm system. Name it, and I can work with it.",
       "NAME IT TO TAME IT", label=True),
    Ht("That sounds suspiciously reasonable.", "suspiciously reasonable"),
    Mi("It's my best quality.", "best quality", gap=0.5),
    Ht("So I tell you what matters.", "what matters"),
    Mi("And I work out how to get there safely.", "how to get there"),
    Ht("The heart picks the destination.", "the destination", gap=0.3),
    Mi("The mind plans the route.", "the route", gap=0.7),
    dict(say="So tell us. Which one usually wins for you, your heart or your mind? And did it work out?", who="h", v=dict(k="question")),
    dict(say="The comments are below. I'll be reading them very carefully.", who="m", v=dict(k="question")),
    dict(say="And I'll be feeling every single one.", who="h", v=dict(k="question"), gap=0.6),
]

PINK = hx("ff5d8f")
CREAM = hx("fff1ea")
ROSE = hx("ffd3dc")
NAVY = hx("0b2545")
CYAN = hx("62d6ff")
WINE = hx("5b1530")


class Style(Base):
    xfade = 0
    cap = dict(font="kalam", size=48, y=1010, fill=WINE, hl=PINK, maxw=1500)

    def setup(self):
        hb = gradient(hx("fff5ef"), hx("ffd9e0"))
        hb = texture(hb, 6, 4, blur=3)
        d = D(hb)
        rnd = random.Random(3)
        for i in range(26):
            x, y, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(60, 260)
            d.ellipse((x - r, y - r, x + r, y + r), fill=A(rnd.choice([PINK, hx("ffb3c7"), hx("ffc9a8")]), 0.06))
        self.HB = hb
        mb = Image.new("RGB", (W, H), NAVY)
        d = D(mb)
        for x in range(0, W, 40):
            d.line([(x, 0), (x, H)], fill=A(CYAN, 0.12 if x % 200 else 0.25), width=1)
        for y in range(0, H, 40):
            d.line([(0, y), (W, y)], fill=A(CYAN, 0.12 if y % 200 else 0.25), width=1)
        self.MB = vignette(mb, 0.4)
        self.BG = self.MB
        self.split = []
        for b in self.beats:
            self.split.append(1300 if b.who == "h" else 620)

    def split_at(self, b, lt):
        if b.v["k"] == "question":
            return W / 2
        prev = self.split[b.i - 1] if b.i > 0 else W / 2
        return lerp(prev, self.split[b.i], eio(lt / 0.55))

    def heart_char(self, d, cx, cy, s, t, talking, face="smile"):
        bob = math.sin(t * 3) * s * 0.04
        sq = 1 + (0.04 * math.sin(t * 14) if talking else 0)
        heart(d, cx, cy + bob, s * sq, A(PINK, 1))
        for k in (-1, 1):
            ex, ey = cx + k * s * 0.2, cy - s * 0.12 + bob
            d.ellipse((ex - s * 0.07, ey - s * 0.09, ex + s * 0.07, ey + s * 0.09), fill=A((255, 255, 255), 1))
            d.ellipse((ex - s * 0.035, ey - s * 0.03, ex + s * 0.035, ey + s * 0.05), fill=A(WINE, 1))
        mo = s * (0.06 + (0.05 * abs(math.sin(t * 11)) if talking else 0))
        d.chord((cx - s * 0.12, cy + s * 0.05 + bob - mo, cx + s * 0.12, cy + s * 0.05 + bob + mo), 0, 180, fill=A(WINE, 1))
        for k in (-1, 1):
            d.ellipse((cx + k * s * 0.33 - s * 0.06, cy + s * 0.02 + bob, cx + k * s * 0.33 + s * 0.06, cy + s * 0.08 + bob), fill=A(hx("ff9ab5"), 1))

    def mind_char(self, d, cx, cy, s, t, talking):
        bob = math.sin(t * 2) * s * 0.02
        c = A(CYAN, 1)
        lw = max(3, int(s * 0.025))
        for (dx, dy, r) in ((-0.22, -0.05, 0.3), (0.2, -0.08, 0.32), (0, -0.25, 0.3), (-0.05, 0.15, 0.3), (0.25, 0.15, 0.22)):
            d.ellipse((cx + (dx - r) * s, cy + (dy - r) * s + bob, cx + (dx + r) * s, cy + (dy + r) * s + bob), fill=A(hx("16406e"), 1))
        for (dx, dy, r) in ((-0.22, -0.05, 0.3), (0.2, -0.08, 0.32), (0, -0.25, 0.3), (-0.05, 0.15, 0.3), (0.25, 0.15, 0.22)):
            d.arc((cx + (dx - r) * s, cy + (dy - r) * s + bob, cx + (dx + r) * s, cy + (dy + r) * s + bob), 200, 340, fill=c, width=lw)
        d.line([(cx, cy - s * 0.5 + bob), (cx, cy + s * 0.4 + bob)], fill=A(CYAN, 0.5), width=lw)
        gy = cy + s * 0.02 + bob
        for k in (-1, 1):
            d.ellipse((cx + k * s * 0.2 - s * 0.12, gy - s * 0.1, cx + k * s * 0.2 + s * 0.12, gy + s * 0.1), outline=A((255, 255, 255), 1), width=lw)
            d.ellipse((cx + k * s * 0.2 - s * 0.03, gy - s * 0.03, cx + k * s * 0.2 + s * 0.03, gy + s * 0.03), fill=A((255, 255, 255), 1))
        d.line([(cx - s * 0.08, gy), (cx + s * 0.08, gy)], fill=A((255, 255, 255), 1), width=lw)
        mw = s * 0.12
        mh = s * (0.015 + (0.04 * abs(math.sin(t * 12)) if talking else 0))
        d.rectangle((cx - mw, gy + s * 0.22 - mh, cx + mw, gy + s * 0.22 + mh), fill=A((255, 255, 255), 1))

    def draw(self, img, b, lt, t):
        sx = int(self.split_at(b, lt))
        img.paste(self.HB.crop((0, 0, sx, H)), (0, 0))
        img.paste(self.MB.crop((sx, 0, W, H)), (sx, 0))
        d = D(img)
        d.line([(sx, 0), (sx, H)], fill=A((255, 255, 255), 1), width=6)
        v = b.v
        hcx, mcx = sx / 2, sx + (W - sx) / 2
        h_on = b.who == "h"
        hs = 300 if h_on else 170
        ms = 330 if not h_on else 190
        if v["k"] == "question":
            hs, ms = 220, 240
        self.heart_char(d, hcx, 560 if h_on else 620, hs, t, h_on and lt < b.dur)
        self.mind_char(d, mcx, 560 if not h_on else 620, ms, t, (not h_on) and lt < b.dur)
        text(d, (hcx, 80), "HEART", F("kalam", 56), PINK, alpha=0.9)
        text(d, (mcx, 80), "MIND", F("robotoslab", 50, 700), CYAN, alpha=0.9)
        if v["k"] == "talk":
            a = ease((lt - 0.3) / 0.4)
            if h_on:
                para(d, hcx, 260, v["note"], F("kalam", 64), WINE, sx - 160, alpha=a)
                if v.get("fact"):
                    text(d, (hcx, 870), "Antonio Damasio, Descartes' Error (1994)", F("kalam", 34), WINE, alpha=ease((lt - 3) / 0.5))
            else:
                para(d, mcx, 260, v["note"], F("robotoslab", 56, 700), (235, 248, 255), W - sx - 160, alpha=a)
                if v.get("tally"):
                    for j in range(3):
                        aj = ease((lt - 3 - j * 0.9) / 0.3)
                        figure(d, mcx - 150 + j * 150, 960, 120, "stand", CYAN, t, face="smile", head_fill=NAVY, alpha=aj)
                if v.get("graph"):
                    gx, gy = mcx - 300, 960
                    d.line([(gx, gy), (gx + 600, gy)], fill=A(CYAN, 1), width=3)
                    d.line([(gx, gy), (gx, gy - 130)], fill=A(CYAN, 1), width=3)
                    pts1 = [(gx + i * 30, gy - 110 * math.exp(-i / 18)) for i in range(21)]
                    pts2 = [(gx + i * 30, gy - 110 * math.exp(-i / 5)) for i in range(21)]
                    n = int(21 * ease((lt - 3) / 2)) + 1
                    if n > 1:
                        d.line(pts1[:n], fill=A(hx("ff9ab5"), 1), width=4)
                        d.line(pts2[:n], fill=A((255, 255, 255), 1), width=4)
                    text(d, (gx + 610, gy - 60), "predicted", F("robotoslab", 24), hx("ff9ab5"), "lm", alpha=ease((lt - 5) / 0.4))
                    text(d, (gx + 610, gy - 10), "actual", F("robotoslab", 24), (255, 255, 255), "lm", alpha=ease((lt - 5) / 0.4))
                if v.get("gauge"):
                    for j, (lab, val) in enumerate((("pulse", 0.9), ("judgment", 0.2))):
                        x = mcx - 140 + j * 280
                        d.rectangle((x - 30, 830, x + 30, 980), outline=A(CYAN, 1), width=3)
                        hh = 146 * ease((lt - 3) / 1.5) * val
                        d.rectangle((x - 27, 978 - hh, x + 27, 978), fill=A(hx("ff5d8f") if j == 0 else CYAN, 1))
                        text(d, (x, 1010 - 0), "", F("robotoslab", 1), CYAN)
                if v.get("label"):
                    text(d, (mcx, 900), "Lieberman et al., Psychological Science (2007)", F("robotoslab", 26), CYAN, alpha=ease((lt - 3) / 0.5))
        else:
            a = ease(lt / 0.5)
            rrect(d, (W / 2 - 640, 160, W / 2 + 640, 330), 30, fill=A((255, 255, 255), 0.92 * a))
            para(d, W / 2, 245, "Heart or mind — which one usually wins for you? Did it work out?", F("robotoslab", 50, 700), NAVY, 1180, alpha=a)
            text(d, (hcx, 860), "Team Heart ♥" if False else "TEAM HEART", F("kalam", 54), PINK, alpha=a)
            text(d, (mcx, 860), "TEAM MIND", F("robotoslab", 48, 700), CYAN, alpha=a)

    def cap_style(self, ch):
        if ch[0]["who"] == "h":
            return dict(font="kalam", size=50, y=1015, fill=WINE, hl=PINK, maxw=max(600, self._sx - 120), cx=self._sx / 2, bar=CREAM + (210,))
        return dict(font="robotoslab", size=42, w=600, y=1015, fill=(220, 240, 255), hl=CYAN, maxw=max(600, W - self._sx - 120),
                    cx=self._sx + (W - self._sx) / 2, bar=NAVY + (210,))

    def frame(self, t):
        b = self.tl.beat_at(t)
        self._sx = self.split_at(b, t - b.t0)
        return Base.frame(self, t)

    def show_cap(self, b):
        return b.v["k"] != "question"
