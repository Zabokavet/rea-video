from engine import *

TITLE = "Why Do People Lie When the Truth Is Easier"
VOICES = {"n": ("af_nova", 0.86)}
GAP = 0.75
MUSIC = dict(kind="pad+hats+piano", root=123.5, prog=[0, -3, 5, 2], qual=["m", "M", "M", "m"], bar=4, step=0.25, pat=[0, 2, 1, 3], bpm=90, vol=0.08)


def Q(n, q):
    return dict(say=q, v=dict(k="q", n=n, q=q), sfx=[("whoosh", 0, 0.4)], gap=0.5)


def Ans(n, say, chips):
    return dict(say=say, v=dict(k="a", n=n, chips=chips))


BEATS = [
    dict(say="Here's something strange. Most lies are told when the truth would have been easier. So why do we do it? Let's answer the questions people actually ask.",
         v=dict(k="hook"), sfx=[("hit", 0, 0.6)], gap=0.6),
    Q(1, "How often do people actually lie?"),
    Ans(1, "More than they think. In a well-known diary study by psychologist Bella DePaulo, people recorded every lie they told. The average was one or two a day. Most were small: I'm fine. I love it. I'm almost there.",
        ["≈ 1–2 lies per day", "mostly small"]),
    Q(2, "Why lie when the truth costs nothing?"),
    Ans(2, "Because the truth rarely feels free. Most lies are told to dodge a tiny moment of discomfort: an awkward pause, a disappointed face. The brain treats that small social pain as a threat, and the lie is the fastest exit. In other words, we often aren't lying to fool someone. We're lying to escape a feeling.",
        ["avoids discomfort", "fastest exit"]),
    Q(3, "Do liars know they're lying?"),
    Ans(3, "Not always. A repeated lie gets easier. A brain imaging study at University College London found that the brain's emotional response to lying shrinks each time people keep doing it. Small lies quietly train the brain for bigger ones.",
        ["emotional alarm fades", "small lies scale up"]),
    Q(4, "Why lie about things that don't even matter?"),
    Ans(4, "For some people, lying is about control, not content. Keeping others slightly misinformed gives them a sense of power. For others, it's an old habit from childhood, where honesty was punished and a good story kept them safe.",
        ["control, not content", "childhood survival habit"]),
    Q(5, "Can you tell when someone is lying?"),
    Ans(5, "Honestly? Not easily. Across hundreds of studies, people spot lies only slightly better than a coin flip: about fifty four percent. Nervous eyes and fidgeting are myths. A better clue is inconsistency, details that shift each time the story is told.",
        ["54% accuracy", "watch for shifting details"]),
    Q(6, "So what do you do with a liar?"),
    Ans(6, "Don't fight over one lie. Watch the pattern. One lie is a moment. A pattern is a character. And make honesty safe around you, because people lie less to those who don't punish the truth. And when the pattern is clear, believe it the first time.",
        ["one lie = moment", "pattern = character"]),
    dict(say="The truth is usually easier. It just doesn't feel that way in the moment. And that small gap, between easy and comfortable, is where most lies are born.",
         v=dict(k="gap")),
    dict(say="What's the most unnecessary lie someone has ever told you? Drop it in the comments.",
         v=dict(k="question"), sfx=[("ding", 0.3, 0.6)]),
]

MINT = hx("7cf5c8")
PINK = hx("ff7eb6")
WHITE = (245, 243, 255)
VI = hx("1b1140")
PAL = dict(bg=hx("221656"), fg=WHITE, acc=MINT, acc2=PINK, dim=hx("9d92d6"), gy=900, s=290, bubble=WHITE, bubtxt=VI, screen=MINT)


class Style(Base):
    cap = dict(font="spacegrotesk", size=46, w=600, y=1015, fill=(235, 230, 255), hl=MINT, maxw=1600, stroke=2, sfill=VI)
    xfade = 0.3

    def setup(self):
        bg = gradient(hx("2b1a6e"), hx("0f0a2a"))
        d = D(bg)
        for i, (x, y, r, c) in enumerate(((300, 200, 380, PINK), (1650, 850, 460, MINT), (1500, 150, 260, hx("6a5cff")))):
            for k in range(14):
                rr = r * (1 - k / 14)
                d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=A(c, 0.012))
        self.BG = texture(bg, 3, 2)
        self.bf = F("spacegrotesk", 34, 600)

    def card(self, d, q, n, reveal, cursor, small=False):
        if small:
            box = (260, 60, 1660, 170)
            fs = 44
        else:
            box = (260, 380, 1660, 660)
            fs = 74
        rrect(d, box, 30, fill=A((255, 255, 255), 0.09), outline=A((255, 255, 255), 0.25), width=2)
        text(d, (box[0] + 50, box[1] + (55 if small else 70)), f"Q{n}", F("spacegrotesk", 40 if small else 46, 700), PINK, "lm")
        s = q[:int(len(q) * clamp01(reveal))]
        f = F("spacegrotesk", fs, 700)
        x0 = box[0] + (150 if small else 50)
        y0 = box[1] + (55 if small else 180)
        d.text((x0, y0), s, font=f, fill=A(WHITE, 1), anchor="lm")
        if cursor:
            cx = x0 + f.getlength(s) + 8
            d.rectangle((cx, y0 - fs * 0.45, cx + 6, y0 + fs * 0.45), fill=A(MINT, 1))

    def answer(self, d, n, lt, t, b):
        if n == 1:
            figure(d, 960, 860, 300, "stand", WHITE, t, face="smile", head_fill=VI)
            for i, (x, y, s) in enumerate(((560, 420, "I'm fine."), (1350, 360, "I love it!"), (700, 640, "Almost there!"))):
                bubble(d, x, y, s, self.bf, WHITE, VI, alpha=ease((lt - 8 - i * 1.0) / 0.3))
            text(d, (1400, 640), "1–2", F("spacegrotesk", 140, 700), MINT, alpha=ease((lt - 5) / 0.4))
            text(d, (1400, 730), "lies a day", F("spacegrotesk", 40, 500), WHITE, alpha=ease((lt - 5) / 0.4))
        elif n == 2:
            figure(d, 720, 860, 300, "hold", WHITE, t, face="smile", head_fill=VI)
            rrect(d, (680, 560, 800, 660), 8, fill=A(PINK, 1))
            d.rectangle((732, 560, 748, 660), fill=A(MINT, 1))
            figure(d, 1150, 860, 300, "stand", PAL["dim"], t, face="smile", head_fill=VI, flip=True)
            bubble(d, 740, 330, "I love it!", self.bf, WHITE, VI, alpha=ease((lt - 1) / 0.3))
            ga = ease((lt - 3) / 0.5)
            rrect(d, (1380, 300, 1760, 700), 26, fill=A((255, 255, 255), 0.08 * ga))
            text(d, (1570, 350), "discomfort", F("spacegrotesk", 36, 600), WHITE, alpha=ga)
            h = 280 * (1 - 0.8 * ease((lt - 5) / 2))
            d.rectangle((1520, 680 - h, 1620, 680), fill=A(PINK, ga))
        elif n == 3:
            text(d, (960, 270), "Emotional response to lying", F("spacegrotesk", 40, 600), WHITE, alpha=ease(lt / 0.4))
            for i in range(6):
                hgt = 380 * (0.92 ** 0) * (1 - i * 0.14)
                aa = ease((lt - 1 - i * 0.7) / 0.4)
                x = 560 + i * 160
                d.rectangle((x - 50, 840 - hgt * aa, x + 50, 840), fill=A(mixc(PINK, MINT, i / 5), 1))
                text(d, (x, 880), f"lie {i + 1}", F("spacegrotesk", 30, 500), PAL["dim"], alpha=aa)
            text(d, (960, 950), "Garrett et al., Nature Neuroscience (2016)", F("spacegrotesk", 26), PAL["dim"], alpha=ease((lt - 3) / 0.5))
        elif n == 4:
            figure(d, 700, 860, 330, "arms_up", PINK, t, face="smirk", head_fill=VI)
            fx = 1150
            figure(d, fx, 860, 260, "arms_up", WHITE, t, face="o", head_fill=VI, alpha=ease(lt / 0.4))
            for dx in (-60, 60):
                d.line([(700 + dx * 1.4, 520), (fx + dx, 640)], fill=A(PAL["dim"], 0.8 * ease((lt - 1) / 0.5)), width=2)
            text(d, (700, 410), "control", F("spacegrotesk", 46, 700), PINK, alpha=ease((lt - 1.5) / 0.4))
            figure(d, 1550, 860, 170, "sad", MINT, t, face="frown", head_fill=VI, alpha=ease((lt - 7) / 0.5))
            text(d, (1550, 590), "childhood habit", F("spacegrotesk", 34, 600), MINT, alpha=ease((lt - 7) / 0.5))
        elif n == 5:
            cx, cy, r = 960, 740, 300
            d.arc((cx - r, cy - r, cx + r, cy + r), 180, 360, fill=A((255, 255, 255), 0.15), width=40)
            v = ease((lt - 1) / 2) * 0.54
            d.arc((cx - r, cy - r, cx + r, cy + r), 180, 180 + 180 * v, fill=A(MINT, 1), width=40)
            d.line([(cx, cy - r - 30), (cx, cy - r + 50)], fill=A(PINK, 1), width=4)
            text(d, (cx, cy - r - 55), "coin flip 50%", F("spacegrotesk", 30, 600), PINK)
            text(d, (cx, cy - 70), f"{int(v * 100)}%", F("spacegrotesk", 130, 700), WHITE)
            text(d, (cx, cy + 30), "lie-detection accuracy", F("spacegrotesk", 34), PAL["dim"])
            text(d, (960, 950), "Bond & DePaulo, meta-analysis (2006)", F("spacegrotesk", 26), PAL["dim"], alpha=ease((lt - 3) / 0.5))
        elif n == 6:
            figure(d, 560, 860, 300, "hips", WHITE, t, face="flat", head_fill=VI)
            a1 = ease((lt - 1.5) / 0.4)
            d.ellipse((980 - 30, 500 - 30, 980 + 30, 500 + 30), fill=A(PINK, a1))
            text(d, (980, 580), "a moment", F("spacegrotesk", 36, 600), WHITE, alpha=a1)
            for i in range(7):
                aa = ease((lt - 4 - i * 0.25) / 0.3)
                x = 1180 + i * 80
                d.ellipse((x - 24, 500 - 24, x + 24, 500 + 24), fill=A(PINK, aa))
            text(d, (1420, 580), "a character", F("spacegrotesk", 36, 600), WHITE, alpha=ease((lt - 6) / 0.4))

    def draw(self, img, b, lt, t):
        d = D(img)
        v = b.v
        k = v["k"]
        if k == "hook":
            text(d, (W / 2, 380), "Why do people lie", F("spacegrotesk", 110, 700), WHITE, alpha=ease(lt / 0.4))
            text(d, (W / 2, 520), "when the truth is easier?", F("spacegrotesk", 110, 700), MINT, alpha=ease((lt - 0.6) / 0.4))
            for i in range(6):
                a = ease((lt - 5 - i * 0.3) / 0.3)
                x = 560 + i * 160
                rrect(d, (x - 60, 680, x + 60, 760), 20, fill=A((255, 255, 255), 0.1 * a), outline=A(PINK, a), width=2)
                text(d, (x, 720), f"Q{i + 1}", F("spacegrotesk", 36, 700), PINK, alpha=a)
        elif k == "q":
            self.card(d, v["q"], v["n"], (lt - 0.1) / 1.2, int(t * 2.5) % 2 == 0)
        elif k == "a":
            q = self.beats[b.i - 1].v["q"]
            self.card(d, q, v["n"], 1, False, small=True)
            self.answer(d, v["n"], lt, t, b)
            for i, c in enumerate(v["chips"]):
                aa = ease((lt - b.dur * (0.35 + 0.3 * i)) / 0.3)
                f = F("spacegrotesk", 30, 700)
                wdt = f.getlength(c) + 50
                x0 = 260
                y0 = 220 + i * 70
                rrect(d, (x0, y0, x0 + wdt, y0 + 52), 26, fill=A(MINT if i == 0 else PINK, aa))
                text(d, (x0 + 25, y0 + 26), c, f, VI, "lm", alpha=aa)
        elif k == "gap":
            text(d, (W / 2, 330), "the gap between", F("spacegrotesk", 50, 500), PAL["dim"], alpha=ease(lt / 0.4))
            x = lerp(0, 1, ease((lt - 1) / 1.5))
            text(d, (W / 2 - 160 - 200 * x, 470), "EASY", F("spacegrotesk", 110, 700), MINT, alpha=ease((lt - 0.4) / 0.4))
            text(d, (W / 2 + 160 + 200 * x, 470), "COMFORTABLE", F("spacegrotesk", 80, 700), PINK, "lm" if False else "mm", alpha=ease((lt - 0.4) / 0.4))
            text(d, (W / 2, 650), "is where lies are born.", F("spacegrotesk", 70, 700), WHITE, alpha=ease((lt - 5) / 0.5))
        elif k == "question":
            a = ease(lt / 0.4)
            rrect(d, (260, 260, 1660, 760), 36, fill=A((255, 255, 255), 0.1 * a), outline=A(MINT, a), width=3)
            text(d, (W / 2, 340), "YOUR ANSWER ↓", F("spacegrotesk", 40, 700), MINT, alpha=a)
            para(d, W / 2, 510, "What's the most unnecessary lie someone has told you?", F("spacegrotesk", 74, 700), WHITE, 1250, alpha=a)
            text(d, (W / 2, 680), "drop it in the comments", F("spacegrotesk", 40, 500), PINK, alpha=ease((lt - 1) / 0.4))

    def show_cap(self, b):
        return b.v["k"] not in ("question", "hook", "q")
