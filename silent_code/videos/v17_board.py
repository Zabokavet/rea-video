from engine import *

TITLE = "The 4 Laws of Social Power"
VOICES = {"n": ("bm_lewis", 0.84)}
GAP = 0.95
MUSIC = dict(kind="pad+piano", root=87.3, prog=[0, 5, 3, -2], qual=["m", "M", "M", "M"], bar=8, step=1.0, pat=[0, 2, 1, 3], vol=0.07)

LAWS = ["Value, not volume", "Least interest", "Emotions are contagious", "Reciprocity binds"]


def L(n, say):
    return dict(say=say, v=dict(k="law", n=n), sfx=[("chalk", 0.2, 1.0), ("chalk", 1.4, 0.8)])


BEATS = [
    dict(say="Power isn't taken by the loudest person in the room. It's given, by everyone else, according to four laws. Let's put them on the board.",
         v=dict(k="hook"), sfx=[("chalk", 0.3, 1.0), ("chalk", 1.5, 1.0)], gap=0.8),
    L(1, "Law one: power follows value, not volume. Researchers describe two routes to status. Dominance, which is power through fear and force. And prestige, which is power through skill, knowledge and generosity. Dominance gets obedience while you're watching. Prestige gets loyalty when you're not. People willingly hand influence to those who make them better. Think of the colleague everyone goes to for help. They never demand respect. They don't have to."),
    L(2, "Law two: the principle of least interest. Sociologist Willard Waller noticed that in any relationship, the person who is less invested holds more power. This isn't a reason to play cold games. It's a reason to build a full life, so that no single person, job or group holds all of your interest."),
    L(3, "Law three: emotions are contagious. Psychologists call it emotional contagion: we unconsciously mirror the moods around us. In a tense room, the calmest person becomes the anchor everyone else syncs to. If you can regulate yourself, you can quietly steer the room. That's why panicking leaders lose a room, and steady ones win it."),
    L(4, "Law four: reciprocity binds. Research popularized by Robert Cialdini shows that when someone gives us something, even something small we never asked for, we feel pressure to repay it. Give generously, and you build lasting goodwill. But watch for gifts with hooks: the favor nobody asked for, that's later used as leverage."),
    dict(say="Notice that none of these laws are about control. Each one can be used to manipulate, or to protect yourself from manipulation. Knowing them is the protection.",
         v=dict(k="sum"), sfx=[("chalk", 0.5, 0.8)]),
    dict(say="Which law have you seen used against you? Write the number in the comments: one, two, three, or four.",
         v=dict(k="question"), sfx=[("chalk", 0.3, 1.0)]),
]

CH = (236, 240, 232)
YEL = hx("f7e27a")
PINK = hx("f5a3b5")
BLUE = hx("9fd3f2")
BOARD = hx("1f2b24")


class Style(Base):
    cap = dict(font="kalam", size=46, y=1000, fill=CH, hl=YEL, bar=(0, 0, 0, 110), maxw=1500, barr=10)
    xfade = 0

    def setup(self):
        b = Image.new("RGB", (W, H), BOARD)
        b = texture(b, 7, 3, blur=2, seed=11)
        d = D(b)
        rnd = random.Random(4)
        for i in range(40):
            x, y = rnd.uniform(100, W - 100), rnd.uniform(100, H - 100)
            r = rnd.uniform(60, 200)
            d.ellipse((x - r, y - r * 0.4, x + r, y + r * 0.4), fill=A(CH, 0.012))
        wood = hx("6b4423")
        d.rectangle((0, 0, W, 34), fill=A(wood, 1))
        d.rectangle((0, H - 34, W, H), fill=A(wood, 1))
        d.rectangle((0, 0, 34, H), fill=A(wood, 1))
        d.rectangle((W - 34, 0, W, H), fill=A(wood, 1))
        d.rectangle((0, H - 50, W, H - 34), fill=A(hx("8a5a30"), 1))
        self.BG = vignette(b, 0.4)
        self.f = F("gloria", 44)
        self.law_t = {}
        for b_ in self.beats:
            if b_.v.get("k") == "law":
                self.law_t[b_.v["n"]] = b_.t0

    def chalk(self, d, xy, s, font, col, anchor="lm", reveal=1.0, alpha=0.93):
        s2 = s[:int(len(s) * clamp01(reveal) + 0.5)]
        if s2:
            d.text(xy, s2, font=font, fill=A(col, alpha), anchor=anchor)

    def pointer(self, d, tip, t):
        x, y = tip[0] + math.sin(t * 1.5) * 6, tip[1] + math.cos(t * 1.3) * 4
        d.line([(x, y), (x + 420, y + 380)], fill=A(hx("a0703c"), 1), width=12)
        d.line([(x, y), (x + 30, y + 27)], fill=A(hx("e8d8b0"), 1), width=12)

    def index(self, d, now, cur):
        self.chalk(d, (90, 110), "THE 4 LAWS OF", F("gloria", 40), YEL)
        self.chalk(d, (90, 165), "SOCIAL POWER", F("gloria", 52), YEL)
        d.line([(90, 205), (560, 210)], fill=A(YEL, 0.8), width=4)
        for n in range(1, 5):
            if n in self.law_t and now >= self.law_t[n]:
                r = (now - self.law_t[n]) / 1.4
                y = 300 + (n - 1) * 140
                col = CH if n != cur else YEL
                self.chalk(d, (90, y), f"{n}.", F("gloria", 52), PINK, reveal=r * 3)
                para(d, 150, y - 30, LAWS[n - 1], F("gloria", 44), col, 480, align="l", valign="t", reveal=r, alpha=0.93)
        d.line([(650, 100), (655, 940)], fill=A(CH, 0.35), width=4)

    def diagram(self, d, n, lt, dur, t):
        cx = 1250
        p = lambda a: ease((lt - a * dur) / 1.2)
        if n == 1:
            self.chalk(d, (cx, 140), "Two routes to status", F("gloria", 54), CH, "mm", reveal=p(0.05) * 1.5)
            figure(d, cx, 470, 170, "stand", CH, t, face="flat", head_fill=BOARD, alpha=p(0.08))
            for side, (lab, a, b_, col, ta) in ((-1, ("DOMINANCE", "fear, force", "obedience (while watched)", PINK, 0.15)),
                                               (1, ("PRESTIGE", "skill, generosity", "loyalty (when you're not)", BLUE, 0.3))):
                x = cx + side * 300
                arrow(d, (cx + side * 40, 470), (x, 560), col, 5, 20, p(ta))
                self.chalk(d, (x, 610), lab, F("gloria", 50), col, "mm", reveal=p(ta) * 2)
                self.chalk(d, (x, 680), a, F("gloria", 36), CH, "mm", reveal=p(ta + 0.05) * 2)
                self.chalk(d, (x, 790), "→ " + b_ if False else b_, F("gloria", 34), CH, "mm", reveal=p(ta + 0.25) * 2)
            if lt > 0.6 * dur:
                d.ellipse((cx + 300 - 230, 560, cx + 300 + 230, 850), outline=A(YEL, 0.9), width=5)
            return (cx + 300, 610)
        if n == 2:
            self.chalk(d, (cx, 140), "Principle of least interest", F("gloria", 54), CH, "mm", reveal=p(0.05) * 1.5)
            tilt = ease((lt - 0.3 * dur) / 1.5)
            L_, R_ = balance(d, cx, 330, 330, CH, tiltv=-1.2 * tilt, lc=PINK, rc=BLUE)
            self.chalk(d, (L_[0], L_[1] + 230), "more invested", F("gloria", 38), PINK, "mm", reveal=p(0.2) * 2)
            self.chalk(d, (R_[0] + 60, R_[1] - 70), "less invested = more power", F("gloria", 38), BLUE, "mm", reveal=p(0.3) * 2)
            self.chalk(d, (cx, 840), "fix: build a FULL life", F("gloria", 52), YEL, "mm", reveal=p(0.65) * 1.6)
            if lt > 0.7 * dur:
                for i, s in enumerate(("friends", "work", "hobbies", "health")):
                    self.chalk(d, (cx - 420 + i * 280, 920), s, F("gloria", 34), CH, "mm", reveal=p(0.72 + i * 0.04) * 2)
            return (cx, 840)
        if n == 3:
            self.chalk(d, (cx, 140), "Emotional contagion", F("gloria", 54), CH, "mm", reveal=p(0.05) * 1.5)
            calm = ease((lt - 0.5 * dur) / 2)
            for i in range(6):
                ang = i / 6 * 2 * math.pi
                x = cx + math.cos(ang) * 330
                y = 560 + math.sin(ang) * 230
                face = "angry" if calm < 0.5 else "flat"
                figure(d, x, y + 70, 120, "stand", mixc(PINK, CH, calm), t + i, face=face, head_fill=BOARD, alpha=p(0.1))
                for k in range(3):
                    wx = lerp(cx, x, 0.25 + k * 0.18)
                    wy = lerp(560, y, 0.25 + k * 0.18)
                    if calm > 0:
                        d.arc((wx - 12, wy - 12, wx + 12, wy + 12), 0, 180, fill=A(BLUE, calm * 0.8), width=3)
            figure(d, cx, 640, 150, "stand", BLUE, t, face="smile", head_fill=BOARD, alpha=p(0.35))
            self.chalk(d, (cx, 870), "the calmest person = the anchor", F("gloria", 46), YEL, "mm", reveal=p(0.55) * 1.6)
            return (cx, 600)
        if n == 4:
            self.chalk(d, (cx, 140), "Reciprocity", F("gloria", 54), CH, "mm", reveal=p(0.05) * 1.5)
            figure(d, cx - 330, 600, 200, "hold", CH, t, face="smile", head_fill=BOARD, alpha=p(0.1))
            figure(d, cx + 330, 600, 200, "stand", CH, t, face="flat", head_fill=BOARD, flip=True, alpha=p(0.1))
            arrow(d, (cx - 200, 380), (cx + 200, 380), BLUE, 5, 22, p(0.15))
            self.chalk(d, (cx, 340), "a gift", F("gloria", 40), BLUE, "mm", reveal=p(0.15) * 2)
            arrow(d, (cx + 200, 480), (cx - 200, 480), PINK, 5, 22, p(0.3))
            self.chalk(d, (cx, 530), "\"I owe them\"", F("gloria", 40), PINK, "mm", reveal=p(0.3) * 2)
            if lt > 0.62 * dur:
                hx_, hy_ = cx, 700
                a = ease((lt - 0.62 * dur) / 1)
                d.arc((hx_ - 50, hy_ - 10, hx_ + 50, hy_ + 90), 0, 180, fill=A(YEL, a), width=6)
                d.line([(hx_ + 50, hy_ + 40), (hx_ + 50, hy_ - 120)], fill=A(YEL, a), width=6)
                d.line([(hx_ - 50, hy_ + 40), (hx_ - 30, hy_ + 20)], fill=A(YEL, a), width=6)
                self.chalk(d, (cx, 860), "watch for gifts with hooks", F("gloria", 48), YEL, "mm", reveal=p(0.65) * 2)
            return (cx, 700)

    def draw(self, img, b, lt, t):
        d = D(img)
        v = b.v
        k = v["k"]
        now = b.t0 + lt
        if k == "hook":
            self.chalk(d, (W / 2, 380), "POWER IS GIVEN,", F("gloria", 110), CH, "mm", reveal=lt / 1.5)
            self.chalk(d, (W / 2, 540), "not taken.", F("gloria", 110), YEL, "mm", reveal=(lt - 2.5) / 1.2)
            self.chalk(d, (W / 2, 720), "4 laws", F("gloria", 70), PINK, "mm", reveal=(lt - 5) / 0.8)
            if lt > 5.5:
                d.ellipse((W / 2 - 160, 660, W / 2 + 160, 780), outline=A(PINK, 0.85), width=5)
            return
        cur = v.get("n")
        self.index(d, now, cur)
        if k == "law":
            if lt < 0.5 and v["n"] > 1:
                pass
            tip = self.diagram(d, v["n"], lt, b.dur, t)
            if lt < 2.5:
                tip = (560, 300 + (v["n"] - 1) * 140)
            self.pointer(d, tip, t)
        elif k == "sum":
            self.chalk(d, (1250, 300), "not about control.", F("gloria", 70), CH, "mm", reveal=lt / 1.5)
            self.chalk(d, (1250, 450), "manipulate  OR  protect", F("gloria", 62), PINK, "mm", reveal=(lt - 4) / 1.5)
            self.chalk(d, (1250, 620), "Knowing them IS the protection.", F("gloria", 58), YEL, "mm", reveal=(lt - 7) / 1.5)
            if lt > 9:
                d.line([(860, 670), (1650, 675)], fill=A(YEL, 0.8), width=5)
        elif k == "question":
            self.chalk(d, (1250, 280), "QUIZ:", F("gloria", 70), PINK, "mm", reveal=lt / 0.6)
            para(d, 1250, 430, "Which law has been used against you?", F("gloria", 64), CH, 1050, reveal=(lt - 0.5) / 2)
            for i in range(4):
                x = 950 + i * 200
                self.chalk(d, (x, 640), str(i + 1), F("gloria", 90), YEL, "mm", reveal=(lt - 3 - i * 0.3) / 0.3)
                if lt > 3.2 + i * 0.3:
                    d.ellipse((x - 60, 580, x + 60, 700), outline=A(CH, 0.6), width=4)
            self.chalk(d, (1250, 800), "answer in the comments", F("gloria", 46), CH, "mm", reveal=(lt - 5) / 1)

    def show_cap(self, b):
        return b.v["k"] not in ("question", "hook")
