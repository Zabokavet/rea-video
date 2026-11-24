from engine import *

TITLE = "The Coworker Everyone Trusted - Until the Mask Fell"
VOICES = {"n": ("bf_isabella", 0.88)}
GAP = 0.7
MUSIC = dict(kind="pad+pulse", root=92.5, prog=[0, -2, -4, -5], qual=["m", "M", "M", "m"], bar=8, bpm=56, vol=0.1)


def RF(n, title, say, **kw):
    return dict(say=say, v=dict(k="flag", n=n, title=title, **kw), sfx=[("scratch", 0.2, 0.7), ("hit", 0.0, 0.3)])


BEATS = [
    dict(say="Everyone in the office loved Daniel. That was the first red flag. Nobody saw it, until the mask fell.",
         v=dict(k="hook"), sfx=[("boom", 0, 0.7)], gap=0.8),
    dict(say="Case file: Daniel, thirty four, project manager. Charming, helpful, first to bring coffee, last to leave. Within three months, he knew everyone's birthday, and everyone's problems.",
         v=dict(k="profile"), sfx=[("page", 0, 0.8)]),
    RF(1, "He collected information", "Red flag one: he collected information. Not gossip, exactly. Just questions. How's your manager treating you? What do you really think of the new director? People felt cared for. Daniel was building a file.",
       figs=[dict(x=1180, p="talk", c="red", f="smile"), dict(x=1460, p="talk", flip=True, f="smile")], bubbles=[(1180, 360, "So... what do you REALLY think of the director?", 0.6)]),
    RF(2, "A different person in every room", "Red flag two: he was a different person depending on the room. Warm with executives, dismissive with interns. How someone treats people who have no power over them is one of the clearest windows into their character.",
       rooms=True),
    RF(3, "Small, constant credit theft", "Red flag three: small thefts of credit. In meetings, Daniel would repeat a colleague's idea, slightly better phrased, and the room would remember it as his. Too small to complain about. Too frequent to be an accident.",
       figs=[dict(x=1150, p="sad", f="frown"), dict(x=1450, p="point", c="red", f="smile", flip=True)], bubbles=[(1460, 360, "Building on MY idea here...", 0.6)],
       props=[("crown", 1450, 455, 0.5, "red")]),
    RF(4, "Triangulation", "Red flag four: triangulation. He told Sara that Mark doubted her work. He told Mark that Sara was struggling. Each felt Daniel was their only ally. Meanwhile, they stopped talking to each other.",
       tri=True),
    RF(5, "Never once at fault", "Red flag five: no one could name a single time he admitted a mistake. Every failed project had a reason, and the reason was always someone else.",
       figs=[dict(x=1300, p="shrug", c="red", f="smirk")], props=[("q", 1080, 420, 0.6, "dim"), ("q", 1520, 420, 0.6, "dim")]),
    dict(say="The mask fell in a single afternoon. Two colleagues finally compared notes over lunch, and the stories didn't match. Within a week, five more people came forward with the same pattern.",
         v=dict(k="fall"), sfx=[("hit", 3.5, 0.7)]),
    dict(say="This profile matches what researchers call the dark triad: Machiavellianism, narcissism, and psychopathy. Not a diagnosis, but a cluster of traits: strategic charm, a hunger for admiration, and low empathy. At work, these people often rise fast, because charm is easier to see than character.",
         v=dict(k="triad"), sfx=[("page", 0, 0.7)]),
    dict(say="The lessons from this case. Watch how people treat those who can't help them. Compare notes, because manipulators depend on isolated stories. And document everything, calmly, with dates.",
         v=dict(k="lessons")),
    dict(say="Charm is not character. The most dangerous person in the room is rarely the loudest. It's the one everyone agrees is so nice.",
         v=dict(k="close"), sfx=[("hit", 0.2, 0.5)]),
    dict(say="Have you worked with a Daniel? What was the moment you realized? Share your case in the comments.",
         v=dict(k="question"), sfx=[("page", 0, 0.7)]),
]

MAN = hx("e6c98f")
MAN2 = hx("d9b97a")
INK = hx("2a2622")
RED = hx("c8282d")
PAL = dict(bg=MAN, fg=INK, red=RED, dim=hx("8a7a5a"), gy=820, s=250, bubble=hx("fffaf0"), bubtxt=INK, headfill=MAN, lw=7)
FX0, FY0, FX1, FY1 = 120, 60, 1800, 940
MID = 900


class Style(Base):
    cap = dict(font="courierprime", size=40, y=1010, fill=(25, 25, 25), hl=RED, bar=(245, 240, 228, 245), maxw=1600, barr=4, barpad=22)
    xfade = 0.3

    def setup(self):
        bg = texture(Image.new("RGB", (W, H), hx("2c3236")), 10, 3, blur=2)
        d = D(bg)
        rrect(d, (FX0 + 14, FY0 + 18, FX1 + 14, FY1 + 18), 12, fill=A((0, 0, 0), 0.5))
        rrect(d, (FX0, FY0 - 30, FX0 + 360, FY0 + 20), 14, fill=A(MAN2, 1))
        rrect(d, (FX0, FY0, MID, FY1), 8, fill=A(MAN2, 1))
        rrect(d, (MID, FY0, FX1, FY1), 8, fill=A(MAN, 1))
        d.line([(MID, FY0), (MID, FY1)], fill=A((0, 0, 0), 0.25), width=4)
        bg = texture(bg, 5, 2, seed=8)
        self.BG = vignette(bg, 0.5)
        self.tf = F("specialelite", 40)
        self.bf = F("courierprime", 30)
        self.flag_at = {}
        for b in self.beats:
            if b.v.get("k") == "flag":
                self.flag_at[b.v["n"]] = b.t0

    def flagicon(self, d, x, y, s, on, a=1.0):
        d.line([(x, y), (x, y + s)], fill=A(INK, a), width=4)
        d.polygon([(x, y), (x + s * 0.7, y + s * 0.2), (x, y + s * 0.42)], fill=A(RED if on else hx("b8a780"), a))

    def polaroid(self, d, t, masked=1.0, lt=0):
        x0, y0 = 200, 130
        d.rectangle((x0 + 8, y0 + 10, x0 + 328, y0 + 400), fill=A((0, 0, 0), 0.3))
        d.rectangle((x0, y0, x0 + 320, y0 + 390), fill=A((250, 248, 240), 1))
        d.rectangle((x0 + 20, y0 + 20, x0 + 300, y0 + 300), fill=A(hx("3c4a52"), 1))
        figure(d, x0 + 160, y0 + 330, 240, "stand", (240, 240, 240), t, face="smirk", head_fill=hx("3c4a52"))
        if masked > 0:
            my = y0 + 92 + (1 - masked) * 140
            mask(d, x0 + 160, my, 70, hx("f5f0e0"), eye=INK, smile=True)
        text(d, (x0 + 160, y0 + 350), "Daniel, 34", F("caveat", 40, 600), INK)
        d.rectangle((x0 + 120, y0 - 18, x0 + 200, y0 + 14), fill=A((240, 240, 200), 0.6))

    def left(self, d, b, lt, t):
        v = b.v
        masked = 1.0
        if v["k"] == "fall":
            masked = 1 - ease((lt - 3.2) / 1.0)
        elif b.i > 7:
            masked = 0
        self.polaroid(d, t, masked, lt)
        text(d, (580, 150), "CASE #0417", F("specialelite", 36), RED, "lm")
        lines = ["SUBJECT: Daniel", "ROLE: Project manager", "REPUTATION: \"so nice\"", "STATUS: trusted by all"]
        if b.i > 7:
            lines[3] = "STATUS: pattern confirmed"
        for i, s in enumerate(lines):
            a = 1 if b.i > 1 else ease((lt - 1.5 - i * 1.6) / 0.4)
            text(d, (230, 600 + i * 60), s, F("specialelite", 34), INK, "lm", alpha=a)
        # red flag tracker
        text(d, (230, 870), "RED FLAGS:", F("specialelite", 32), INK, "lm")
        now = b.t0 + lt
        for n in range(1, 6):
            on = n in self.flag_at and now >= self.flag_at[n] + 0.3
            self.flagicon(d, 470 + (n - 1) * 70, 845, 50, on)

    def draw(self, img, b, lt, t):
        d = D(img)
        v = b.v
        k = v["k"]
        if k == "hook":
            img.paste(self.BG)
            self.polaroid(d, t, 1.0)
            text(d, (1300, 380), "Everyone loved Daniel.", F("specialelite", 56), INK, alpha=ease(lt / 0.5))
            text(d, (1300, 480), "That was red flag #1.", F("specialelite", 56), RED, alpha=ease((lt - 2.5) / 0.5))
            self.flagicon(d, 1240, 560, 120, True, ease((lt - 2.8) / 0.4))
            return
        self.left(d, b, lt, t)
        cx = (MID + FX1) / 2
        if k == "profile":
            text(d, (cx, 200), "PROFILE", F("specialelite", 54), INK, alpha=ease(lt / 0.4))
            for i, s in enumerate(("charming", "helpful", "first with coffee", "last to leave", "knows everyone's problems")):
                a = ease((lt - 2.5 - i * 1.2) / 0.4)
                text(d, (cx, 330 + i * 90), s, F("caveat", 64, 600), hx("1d3f8a"), alpha=a)
            arc_prog(d, cx, 690, 290 if False else 0, RED, 0)
            if lt > 9.5:
                d.ellipse((cx - 300, 650, cx + 300, 740), outline=A(RED, ease((lt - 9.5) / 0.6)), width=5)
        elif k == "flag":
            self.flagicon(d, MID + 70, 120, 70, True)
            text(d, (MID + 140, 150), f"RED FLAG #{v['n']}", F("specialelite", 44), RED, "lm")
            text(d, (MID + 70, 240), v["title"], F("specialelite", 46), INK, "lm", alpha=ease((lt - 0.3) / 0.4))
            scribble(d, MID + 70, MID + 70 + F("specialelite", 46).getlength(v["title"]), 275, RED, 5, ease((lt - 0.8) / 0.8), amp=3, seed=v["n"])
            if v.get("rooms"):
                for i, (lab, pose, face, other) in enumerate((("EXECUTIVES", "talk", "smile", "stand"), ("INTERNS", "cross", "smirk", "sad"))):
                    x = MID + 230 + i * 450
                    a = ease((lt - 1 - i * 4) / 0.5)
                    rrect(d, (x - 190, 340, x + 190, 850), 10, outline=A(INK, a), width=3)
                    text(d, (x, 380), lab, F("specialelite", 34), INK, alpha=a)
                    figure(d, x - 70, 820, 230, pose, RED, t, face=face, head_fill=MAN, alpha=a, lw=7)
                    figure(d, x + 80, 820, 200 if i else 240, other, INK, t, face="smile" if i == 0 else "frown", head_fill=MAN, flip=True, alpha=a, lw=7)
            elif v.get("tri"):
                P = {"D": (cx, 380), "S": (cx - 300, 760), "M": (cx + 300, 760)}
                for (a_, b_), ta in ((("D", "S"), 1.0), (("D", "M"), 3.5)):
                    arrow(d, P[a_], P[b_], RED, 5, 22, ease((lt - ta) / 0.8))
                if lt > 7.5:
                    d.line([P["S"], P["M"]], fill=A(INK, 0.5), width=4)
                    cross_x(d, cx, 760, 34, RED, 8, ease((lt - 8) / 0.5))
                for key, (x, y) in P.items():
                    c = RED if key == "D" else INK
                    figure(d, x, y + 60, 160, "stand" if key == "D" else "sad", c, t, face="smirk" if key == "D" else "frown", head_fill=MAN, lw=6)
                    text(d, (x, y + 95), {"D": "Daniel", "S": "Sara", "M": "Mark"}[key], F("caveat", 40, 700), c)
            else:
                scene(d, v, lt, t, PAL, bfont=self.bf)
        elif k == "fall":
            text(d, (cx, 200), "EXHIBIT A — LUNCH NOTES", F("specialelite", 42), INK, alpha=ease(lt / 0.4))
            for i, (x, rot_txt) in enumerate(((cx - 210, "He said Mark\ndoubted me."), (cx + 210, "He said Sara\nwas failing."))):
                a = ease((lt - 0.8 - i * 0.8) / 0.4)
                d.rectangle((x - 180, 300, x + 180, 560), fill=A(hx("fff6a8"), a))
                para(d, x, 430, rot_txt, F("caveat", 46, 600), INK, 330, alpha=a)
            if lt > 3.2:
                s = lerp(1.6, 1.0, ease((lt - 3.2) / 0.25))
                f = F("specialelite", int(70 * s))
                rrect(d, (cx - 390 * s, 690 - 60 * s, cx + 390 * s, 690 + 60 * s), 8, outline=A(RED, 0.9), width=8)
                text(d, (cx, 690), "PATTERN CONFIRMED", f, RED, alpha=0.9)
            text(d, (cx, 850), "+5 colleagues came forward", F("specialelite", 36), INK, alpha=ease((lt - 8) / 0.5))
        elif k == "triad":
            text(d, (cx, 180), "ANALYSIS: THE DARK TRIAD", F("specialelite", 44), INK, alpha=ease(lt / 0.4))
            P = [(cx, 330), (cx - 280, 720), (cx + 280, 720)]
            labs = [("Machiavellianism", "strategic charm"), ("Narcissism", "hunger for admiration"), ("Psychopathy", "low empathy")]
            for i in range(3):
                line_prog(d, P[i], P[(i + 1) % 3], ease((lt - 1 - i * 0.4) / 0.6), RED, 5)
            for i, ((x, y), (a_, b_)) in enumerate(zip(P, labs)):
                aa = ease((lt - 2 - i * 1.2) / 0.4)
                d.ellipse((x - 16, y - 16, x + 16, y + 16), fill=A(RED, aa))
                yy = y - 100 if i == 0 else y + 60
                text(d, (x, yy), a_, F("specialelite", 34), INK, alpha=aa)
                text(d, (x, yy + 42), b_, F("caveat", 38, 600), hx("1d3f8a"), alpha=ease((lt - 9 - i * 1.5) / 0.4))
            text(d, (cx, 560), "traits, not a diagnosis", F("caveat", 36, 600), hx("7a6a50"), alpha=ease((lt - 6) / 0.5))
        elif k == "lessons":
            text(d, (cx, 180), "LESSONS FROM CASE #0417", F("specialelite", 44), INK, alpha=ease(lt / 0.4))
            for i, (s, ta) in enumerate((("Watch how they treat people who can't help them", 1.5),
                                        ("Compare notes — isolation is their tool", 5.0), ("Document everything, with dates", 9.5))):
                aa = ease((lt - ta) / 0.4)
                y = 320 + i * 180
                d.rectangle((MID + 80, y - 60, FX1 - 80, y + 80), fill=A((255, 253, 245), aa))
                d.line([(MID + 80, y - 30), (FX1 - 80, y - 30)], fill=A(RED, 0.5 * aa), width=2)
                text(d, (MID + 110, y - 2), f"{i + 1}.", F("specialelite", 40), RED, "lm", alpha=aa)
                para(d, MID + 170, y + 22, s, F("caveat", 46, 600), INK, 700, align="l", alpha=aa)
        elif k == "close":
            text(d, (cx, 420), "CHARM", F("specialelite", 100), INK, alpha=ease(lt / 0.4))
            text(d, (cx, 520), "is not", F("caveat", 70, 600), RED, alpha=ease((lt - 0.4) / 0.4))
            text(d, (cx, 630), "CHARACTER", F("specialelite", 100), INK, alpha=ease((lt - 0.8) / 0.4))
        elif k == "question":
            text(d, (cx, 230), "OPEN CASE", F("specialelite", 50), RED, alpha=ease(lt / 0.4))
            para(d, cx, 450, "Have you worked with a Daniel? What was the moment you realized?", F("specialelite", 52), INK, 760, alpha=ease(lt / 0.5))
            text(d, (cx, 700), "Share your case in the comments.", F("caveat", 52, 700), hx("1d3f8a"), alpha=ease((lt - 1.5) / 0.4))

    def show_cap(self, b):
        return b.v["k"] not in ("question", "hook")
