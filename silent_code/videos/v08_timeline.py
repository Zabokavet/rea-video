from engine import *

TITLE = "How a Manipulator Takes Over Your Life in 90 Days"
VOICES = {"n": ("am_fenrir", 0.88)}
GAP = 0.7
MUSIC = dict(kind="drone+tick+pulse", root=82.4, prog=[0, 1, 0, -1], qual=["m"], bar=8, bpm=60, tick_every=1.0, vol=0.13, nzcut=300)

PH = [(1, 14, "LOVE BOMBING"), (15, 30, "MIRRORING"), (31, 45, "ISOLATION"), (46, 60, "HOT & COLD"), (61, 75, "GASLIGHTING"), (76, 90, "DEPENDENCE")]


def Dd(day, say, **kw):
    return dict(say=say, v=dict(k="day", day=day, **kw), sfx=[("tick", 0, 0.8), ("whoosh", 0.05, 0.3)])


BEATS = [
    dict(say="Ninety days. That's often all it takes. Not with violence. Not with threats. With attention. Here is the timeline, day by day.",
         v=dict(k="hook", day=0), sfx=[("boom", 0, 0.8)], gap=0.8),
    Dd(1, "Day one. They notice you. Really notice you. They remember the small things you said. They message first, every time. It feels like being chosen.",
       figs=[dict(x=900, p="phone", c="rd", f="smile"), dict(x=1350, p="stand", flip=True, f="smile")], props=[("phone", 1000, 560, 0.6, "rd")],
       bubbles=[(900, 330, "I remember what you said about your dad.", 0.6)]),
    Dd(10, "Day ten. The intensity is unusual. Constant compliments, huge promises, talk of the future. Psychologists call this love bombing: overwhelming affection that speeds up attachment before you've had time to judge the person.",
       figs=[dict(x=950, p="arms_up", c="rd", f="smile"), dict(x=1350, p="stand", flip=True, f="smile")], props=[("heart", 1150, 360, 0.7, "rd")],
       bubbles=[(900, 300, "I've never felt this way about anyone.", 0.6)]),
    Dd(21, "Day twenty one. They mirror you perfectly. Your music, your values, even your wounds. They share a secret, and invite you to share yours. Now they have your map.",
       figs=[dict(x=1000, p="talk", c="rd", f="smile"), dict(x=1300, p="talk", flip=True, f="smile")], bubbles=[(1000, 330, "Me too. Exactly the same.", 0.6)]),
    Dd(35, "Day thirty five. The first quiet cut. They don't forbid your friends. They just sigh when you see them. Your friends seem a little jealous, don't they? Slowly, seeing other people starts to feel like a betrayal.",
       figs=[dict(x=900, p="cross", c="rd", f="frown"), dict(x=1200, to=1450, dur=3, f="flat"), dict(x=1640, p="wave", flip=True, c="dim", f="smile"),
             dict(x=1760, p="stand", flip=True, c="dim", f="smile")], bubbles=[(880, 330, "Go... have fun, I guess.", 0.8)]),
    Dd(50, "Day fifty. Hot and cold begins. Warm one day, distant the next, for no clear reason. This is intermittent reinforcement, the same unpredictable reward pattern that makes slot machines addictive. You start working for the good days.",
       hotcold=True),
    Dd(64, "Day sixty four. You bring up something that hurt you. They calmly say it never happened, or that you're too sensitive. This is gaslighting. Its goal isn't to win the argument. It's to make you doubt your own memory.",
       figs=[dict(x=950, p="hips", c="rd", f="flat"), dict(x=1350, p="sad", flip=True, f="o")], props=[("q", 1480, 420, 0.7, "dim"), ("q", 1240, 380, 0.5, "dim")],
       bubbles=[(950, 320, "That never happened. You're too sensitive.", 0.6)]),
    Dd(80, "Day eighty. You check their mood before you speak. You apologize for things you didn't do. Your independence is almost gone. And the strangest part? You defend them to everyone.",
       figs=[dict(x=950, p="stand", c="rd", f="smirk"), dict(x=1350, p="slump", flip=True, f="frown", s=0.85)], props=[("chain", 1010, 650, 1.0, "dim", 1300, 650)]),
    Dd(90, "Day ninety. The takeover is complete, and it never once felt like a takeover. It felt like love. Then like confusion. Then like it was all your fault.",
       figs=[dict(x=1000, p="hips", c="rd", f="smirk"), dict(x=1380, p="sit_sad", flip=True, f="frown")], props=[("crown", 1000, 445, 0.6, "rd")]),
    dict(say="But this timeline has a weakness. Every stage depends on speed and secrecy. So slow everything down. Keep your friends close, especially when someone new resents them. And write down what happens, so no one can rewrite your memory.",
         v=dict(k="counter", day=90), sfx=[("riser", 0, 0.7)]),
    dict(say="And remember the rule. Real love is consistent, not intense. Intensity in the first month is not a sign of destiny. It's a sign to slow down and watch.",
         v=dict(k="rule", day=90)),
    dict(say="So be honest. On which day would you have noticed? Day ten, day fifty, or never? Tell me in the comments.",
         v=dict(k="question", day=90), sfx=[("hit", 0.2, 0.5)]),
]

RED = hx("ff3344")
WHITE = (235, 235, 235)
DIM = hx("6a6f78")
PAL = dict(bg=hx("0b0c0e"), fg=WHITE, rd=RED, dim=DIM, gy=860, s=270, bubble=hx("e8e8e8"), bubtxt=hx("0b0c0e"), screen=RED)


def indep(day):
    return max(0.06, 1 - day / 90 * 0.94)


class Style(Base):
    cap = dict(font="jetbrains", size=40, w=600, y=1018, fill=(230, 230, 230), hl=(10, 10, 10), hlbox=RED + (255,), maxw=1600)
    xfade = 0.25

    def setup(self):
        bg = radial(hx("16181c"), hx("060607"), r=1200)
        d = D(bg)
        for y in range(0, H, 4):
            d.line([(0, y), (W, y)], fill=A((255, 255, 255), 0.012))
        self.BG = vignette(bg, 0.5)
        self.days = []
        last = 0
        for b in self.beats:
            day = b.v.get("day", last)
            self.days.append((last, day))
            last = day
        self.bf = F("jetbrains", 30, 600)

    def bg(self, t):
        return self.BG.copy()

    def hud(self, d, b, lt, t):
        a0, a1 = self.days[b.i]
        day = lerp(a0, a1, ease(lt / 1.0))
        text(d, (70, 60), "CASE FILE // 90-DAY TAKEOVER", F("jetbrains", 26, 700), DIM, "lm")
        if int(t * 1.5) % 2 == 0:
            d.ellipse((W - 190, 48, W - 166, 72), fill=A(RED, 1))
        text(d, (W - 150, 60), "REC", F("jetbrains", 26, 700), RED, "lm")
        # timeline
        x0, x1, y = 120, W - 120, 150
        d.line([(x0, y), (x1, y)], fill=A(DIM, 0.6), width=4)
        for i, (s, e, name) in enumerate(PH):
            xs, xe = lerp(x0, x1, (s - 1) / 90), lerp(x0, x1, e / 90)
            on = day >= s
            d.line([(xs + 3, y), (xe - 3, y)], fill=A(RED if on else DIM, 0.9 if on else 0.4), width=8)
            text(d, ((xs + xe) / 2, y + 30), name, F("jetbrains", 18, 700), RED if s <= day <= e + 0.5 else DIM, alpha=0.9)
        for dd in range(0, 91, 10):
            xx = lerp(x0, x1, dd / 90)
            d.line([(xx, y - 10), (xx, y - 2)], fill=A(DIM, 1), width=2)
            text(d, (xx, y - 26), str(dd), F("jetbrains", 16), DIM)
        px = lerp(x0, x1, day / 90)
        d.polygon([(px, y + 8), (px - 10, y - 12), (px + 10, y - 12)], fill=A(WHITE, 1))
        # counter
        if b.v["k"] != "hook":
            text(d, (110, 330), "DAY", F("jetbrains", 40, 700), DIM, "lm")
            text(d, (100, 440), f"{int(round(day)):03d}", F("jetbrains", 150, 800), WHITE, "lm")
            ph = next((n for s, e, n in PH if s <= day <= e + 0.5), "")
            text(d, (110, 545), ph, F("jetbrains", 36, 700), RED, "lm")
            # meters
            for i, (lab, val, c) in enumerate((("YOUR INDEPENDENCE", indep(day), WHITE), ("THEIR CONTROL", 1 - indep(day) + 0.03, RED))):
                yy = 650 + i * 100
                text(d, (110, yy), lab, F("jetbrains", 22, 700), DIM, "lm")
                d.rectangle((110, yy + 22, 560, yy + 48), outline=A(DIM, 1), width=2)
                d.rectangle((114, yy + 26, 114 + 442 * clamp01(val), yy + 44), fill=A(c, 0.9))

    def draw(self, img, b, lt, t):
        d = D(img)
        v = b.v
        k = v["k"]
        if k == "hook":
            n = int(clamp01(lt / 4) * 90)
            text(d, (W / 2, 470), f"{n:02d}", F("jetbrains", 260, 800), RED, alpha=ease(lt / 0.3))
            text(d, (W / 2, 640), "DAYS", F("jetbrains", 80, 700), WHITE, alpha=ease(lt / 0.3))
            text(d, (W / 2, 760), "to take over a life", F("jetbrains", 44, 500), DIM, alpha=ease((lt - 2) / 0.5))
        elif k == "day":
            if v.get("hotcold"):
                warm = int(lt / 1.6) % 2 == 0
                figure(d, 950, 860, 270, "wave" if warm else "back", RED, t, face="smile" if warm else None, head_fill=PAL["bg"],
                       flip=not warm)
                figure(d, 1350, 860, 270, "reach", WHITE, t, face="flat", head_fill=PAL["bg"], flip=True)
                text(d, (950, 440), "WARM" if warm else "COLD", F("jetbrains", 60, 800), RED if warm else hx("6fa8ff"))
                text(d, (1450, 300), "intermittent reinforcement", F("jetbrains", 30, 600), DIM, alpha=ease((lt - 4) / 0.5))
            else:
                scene(d, v, lt, t, PAL, bfont=self.bf)
        elif k == "counter":
            text(d, (1200, 320), "THE WEAKNESS: SPEED + SECRECY", F("jetbrains", 42, 800), RED, alpha=ease(lt / 0.4))
            for i, s in enumerate(("SLOW EVERYTHING DOWN", "KEEP YOUR FRIENDS CLOSE", "WRITE IT DOWN")):
                ta = [3.5, 5.5, 10.5][i]
                aa = ease((lt - ta) / 0.4)
                y = 450 + i * 120
                rrect(d, (760, y - 45, 1700, y + 45), 6, outline=A(WHITE, aa), width=2)
                check(d, 820, y, 50, RED, 8, aa)
                text(d, (880, y), s, F("jetbrains", 40, 700), WHITE, "lm", alpha=aa)
        elif k == "rule":
            text(d, (1200, 420), "CONSISTENT", F("jetbrains", 110, 800), WHITE, alpha=ease(lt / 0.4))
            text(d, (1200, 540), ">", F("jetbrains", 90, 800), RED, alpha=ease((lt - 0.6) / 0.4))
            text(d, (1200, 660), "INTENSE", F("jetbrains", 110, 800), RED, alpha=ease((lt - 1.2) / 0.4))
        elif k == "question":
            a = ease(lt / 0.4)
            text(d, (1200, 330), "WHEN WOULD YOU", F("jetbrains", 70, 800), WHITE, alpha=a)
            text(d, (1200, 420), "HAVE NOTICED?", F("jetbrains", 70, 800), WHITE, alpha=a)
            for i, s in enumerate(("DAY 10", "DAY 50", "NEVER")):
                aa = ease((lt - 1 - i * 0.4) / 0.3)
                x = 880 + i * 320
                rrect(d, (x - 130, 540, x + 130, 640), 6, fill=A(RED if i == 2 else (40, 40, 44), aa))
                text(d, (x, 590), s, F("jetbrains", 44, 800), WHITE, alpha=aa)
            text(d, (1200, 730), "comment below", F("jetbrains", 36, 600), DIM, alpha=ease((lt - 2.5) / 0.4))

    def overlay(self, img, b, lt, t):
        self.hud(D(img), b, lt, t)

    def show_cap(self, b):
        return b.v["k"] not in ("question", "hook")
