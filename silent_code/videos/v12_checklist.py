from engine import *

TITLE = "The Self-Respect Checklist - 9 Things to Check Every Morning"
VOICES = {"n": ("am_eric", 0.84)}
GAP = 0.85
MUSIC = dict(kind="pad+piano+hats", root=146.8, prog=[0, 5, 7, 4], qual=["M", "M", "M", "m"], bar=4, step=0.5, pat=[0, 2, 3, 1], bpm=92, vol=0.08)

ITEMS = ["Kept a promise to myself", "My goals before notifications", "Stopped chasing", "No hidden yeses", "A kind inner voice",
         "Respected my body", "Stopped over-explaining", "One boundary, held", "One proud moment"]


def I(n, q, say, **sc):
    return dict(say=say, v=dict(k="item", n=n, q=q, sc=sc), sfx=[("tick", 1.2, 0.6), ("ding", 1.25, 0.25)])


BEATS = [
    dict(say="Self-respect isn't a feeling you wait for. It's a handful of small decisions you make before nine a.m. Here are nine to check, every single morning.",
         v=dict(k="hook"), sfx=[("ding", 0, 0.5)], gap=0.8),
    I(1, "Did I keep yesterday's promise to myself?", "One. Did I keep yesterday's promise to myself? Self-trust is built like any trust: through kept promises. Confidence grows from follow-through, not affirmations. So keep one small promise today.",
      figs=[dict(x=1350, p="hips", f="smile")], props=[("clock", 1600, 400, 0.8, "acc")]),
    I(2, "My goals first, or everyone's notifications?", "Two. Am I starting with my goals, or with everyone else's notifications? Checking your phone first hands your attention to other people's priorities. Give yourself the first fifteen minutes.",
      figs=[dict(x=1350, p="sit", f="smile")], props=[("chair", 1350, None, 1.0, "dim"), ("phone", 1650, 840, 0.6, "dim")]),
    I(3, "Am I chasing someone who isn't walking toward me?", "Three. Am I chasing anyone who isn't walking toward me? Relationships need effort from both sides. If you're the only one running, stop and notice who turns around. Self-respect means you stop auditioning for a role in someone's life.",
      figs=[dict(x=1150, to=1350, dur=3, f="frown"), dict(x=1650, p="back", c="dim")]),
    I(4, "Did I say yes when I meant no?", "Four. Did I say yes to something I meant no to? Every hidden yes teaches people that your limits are negotiable, and quietly teaches you to resent them.",
      figs=[dict(x=1250, p="cross", f="flat"), dict(x=1600, p="talk", flip=True, c="dim", f="smile")], bubbles=[(1250, 420, "No, I can't. But thanks.", 0.8)]),
    I(5, "Do I talk to myself like I'd talk to a friend?", "Five. Am I speaking to myself the way I'd speak to a friend? Research on self-compassion, led by psychologist Kristin Neff, links a kinder inner voice to more resilience, not less discipline.",
      figs=[dict(x=1350, p="hug_self", f="smile")], props=[("heart", 1350, 440, 0.6, "acc")]),
    I(6, "Is my body getting basic respect?", "Six. Is my body getting basic respect? Sleep, water, movement. Sleep loss alone makes the brain's emotional alarm far more reactive. You can't hold boundaries on four hours of sleep.",
      figs=[dict(x=1350, p="arms_up", f="smile")], props=[("moon", 1660, 640, 0.8, "acc")]),
    I(7, "Am I over-explaining to someone who chose to misunderstand?", "Seven. Am I explaining myself to someone who has already decided to misunderstand me? Say it clearly once. That's enough. Repeating it to someone who won't hear it is just begging, politely.",
      figs=[dict(x=1250, p="stand", f="flat"), dict(x=1600, p="cross", flip=True, c="dim", f="smirk")], bubbles=[(1250, 420, "I've said what I needed to say.", 0.8)]),
    I(8, "What's one boundary I'll hold today?", "Eight. What is one boundary I need to hold today? Name it in the morning, while you're calm. It's much harder to invent a boundary in the middle of a conflict.",
      figs=[dict(x=1300, p="point", f="flat")], props=[("wall", 1520, None, 0.7, "acc")]),
    I(9, "Will future me be proud of one thing I do today?", "Nine. Will I do one thing today that future me will be proud of? Not a huge thing. One honest call, one finished task, one walk away from something beneath you.",
      figs=[dict(x=1350, p="fist", f="smile")], props=[("crown", 1350, 470, 0.6, "acc")]),
    dict(say="You won't tick all nine every day, and that's not the point. The point is that you're checking. Which means you've already decided you're worth checking on.",
         v=dict(k="full"), sfx=[("riser", 0, 0.6)]),
    dict(say="Which item on this list is the hardest one for you? Tell me in the comments. And screenshot the list for tomorrow morning.",
         v=dict(k="question"), sfx=[("ding", 0.3, 0.6)]),
]

BROWN = hx("3b2a20")
ORANGE = hx("ff8a3d")
CREAM = hx("fffaf2")
SAGE = hx("5fa37a")
PAL = dict(bg=hx("ffe7cf"), fg=BROWN, acc=ORANGE, dim=hx("b49a86"), gy=860, s=290, bubble=CREAM, bubtxt=BROWN, headfill=hx("ffe9d6"), lw=8, screen=ORANGE)
CX0, CY0, CX1, CY1 = 110, 90, 900, 950


class Style(Base):
    cap = dict(font="fredoka", size=46, w=600, y=1012, fill=BROWN, hl=(255, 255, 255), hlbox=ORANGE + (255,), bar=CREAM + (235,), maxw=1500, barr=30)
    xfade = 0.3

    def setup(self):
        bg = gradient(hx("ffd9b3"), hx("ffeedd"))
        d = D(bg)
        for r, a in ((520, 0.08), (360, 0.12), (200, 0.35)):
            d.ellipse((1500 - r, 260 - r, 1500 + r, 260 + r), fill=A((255, 200, 120), a))
        d.rectangle((0, 860, W, H), fill=A(hx("f4cfa8"), 1))
        self.BG = texture(bg, 3, 2)
        self.done = {}
        for b in self.beats:
            if b.v.get("k") == "item":
                self.done[b.v["n"]] = b.t0 + 1.2

    def card(self, d, now, cur=None, a=1.0):
        rrect(d, (CX0 + 12, CY0 + 16, CX1 + 12, CY1 + 16), 28, fill=A((120, 70, 30), 0.15 * a))
        rrect(d, (CX0, CY0, CX1, CY1), 28, fill=A(CREAM, a))
        text(d, (CX0 + 50, CY0 + 60), "SELF-RESPECT CHECKLIST", F("fredoka", 40, 700), ORANGE, "lm", alpha=a)
        text(d, (CX1 - 40, CY0 + 60), "every morning", F("patrickhand", 34), PAL["dim"], "rm", alpha=a)
        d.line([(CX0 + 40, CY0 + 110), (CX1 - 40, CY0 + 110)], fill=A(PAL["dim"], 0.5 * a), width=2)
        for i, s in enumerate(ITEMS):
            n = i + 1
            y = CY0 + 160 + i * 84
            visible = n in self.done and now >= self.done[n] - 1.2
            if not visible:
                continue
            ia = ease((now - (self.done[n] - 1.2)) / 0.4) * a
            if cur == n:
                rrect(d, (CX0 + 24, y - 36, CX1 - 24, y + 36), 18, fill=A(hx("ffe3cc"), ia))
            bx = CX0 + 60
            rrect(d, (bx - 22, y - 22, bx + 22, y + 22), 8, outline=A(BROWN, ia), width=4)
            ck = ease((now - self.done[n]) / 0.4)
            if ck > 0:
                check(d, bx + 2, y, 40, SAGE, 8, ck)
            text(d, (bx + 50, y), s, F("patrickhand", 44), BROWN, "lm", alpha=ia)

    def draw(self, img, b, lt, t):
        d = D(img)
        v = b.v
        k = v["k"]
        now = b.t0 + lt
        if k == "hook":
            text(d, (W / 2, 330), "SELF-RESPECT", F("fredoka", 140, 700), BROWN, alpha=ease(lt / 0.4))
            text(d, (W / 2, 470), "is a checklist, not a feeling", F("patrickhand", 80), ORANGE, alpha=ease((lt - 1.5) / 0.4))
            for i in range(9):
                aa = ease((lt - 5 - i * 0.12) / 0.3)
                x = 560 + i * 100
                rrect(d, (x - 34, 620, x + 34, 688), 10, outline=A(BROWN, aa), width=5)
                check(d, x + 2, 654, 50, SAGE, 8, ease((lt - 6 - i * 0.12) / 0.3))
        elif k == "item":
            self.card(d, now, v["n"])
            text(d, (1350, 160), f"{v['n']:02d}", F("fredoka", 110, 700), ORANGE, alpha=ease(lt / 0.3))
            para(d, 1400, 300, v["q"], F("patrickhand", 56), BROWN, 900, alpha=ease((lt - 0.3) / 0.4))
            scene(d, v["sc"], lt, t, PAL, bfont=F("patrickhand", 40))
        elif k == "full":
            self.card(d, now + 99)
            text(d, (1400, 380), "You're worth", F("fredoka", 90, 700), BROWN, alpha=ease((lt - 6) / 0.5))
            text(d, (1400, 490), "checking on.", F("fredoka", 90, 700), ORANGE, alpha=ease((lt - 6.5) / 0.5))
        elif k == "question":
            self.card(d, now + 99)
            a = ease(lt / 0.4)
            rrect(d, (1000, 250, 1810, 760), 28, fill=A(BROWN, a))
            text(d, (1405, 320), "COMMENT BELOW", F("fredoka", 36, 700), ORANGE, alpha=a)
            para(d, 1405, 480, "Which one is the hardest for you?", F("fredoka", 68, 700), CREAM, 700, alpha=a)
            text(d, (1405, 680), "📸 screenshot for tomorrow" if False else "screenshot this list for tomorrow", F("patrickhand", 42), hx("ffd2ad"),
                 alpha=ease((lt - 3) / 0.4))

    def show_cap(self, b):
        return b.v["k"] not in ("question", "hook")
