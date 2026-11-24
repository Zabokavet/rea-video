from engine import *

TITLE = "Is Forgiveness Strength or Weakness"
VOICES = {"m": ("af_sky", 0.9), "a": ("bf_lily", 0.88), "b": ("am_adam", 0.9)}
GAP = 0.6
CAP_WORDS = 6
MUSIC = dict(kind="pad+pulse", root=98.0, prog=[0, -2, 3, -4], qual=["m", "M", "M", "M"], bar=8, bpm=64, vol=0.08)


def Mo(say, **kw):
    return dict(say=say, who="m", v=dict(**kw))


def Sa(say, card, **kw):
    return dict(say=say, who="a", v=dict(card=card, **kw))


def Sb(say, card, **kw):
    return dict(say=say, who="b", v=dict(card=card, **kw))


BEATS = [
    Mo("Forgive and forget, they say. But is forgiveness the strongest thing you can do, or the weakest? Tonight, two sides argue it out. You decide.", hook=True,
       sfx=[("boom", 0, 0.7)], gap=0.8),
    Mo("Round one: what forgiveness does for you. Arguing that forgiveness is strength, the floor is yours.", round=1, rt="What does it do for you?", sfx=[("ding", 0, 0.4)]),
    Sa("Thank you. Research on forgiveness, including work by psychologist Everett Worthington, links it to lower stress, better sleep and less rumination. Holding a grudge keeps your body in a low-grade fight. Forgiveness ends the fight inside you. That takes strength.",
       "health"),
    Sb("But who pays for that peace? Too often, people forgive because they're pressured, to keep the family calm or the relationship intact. Forgiving someone who hasn't changed teaches them there's no cost. That isn't strength. That's subsidizing harm.",
       "pressure"),
    Mo("Round two: does forgiveness invite the same behavior again?", round=2, rt="Does it invite a repeat?", sfx=[("ding", 0, 0.4)]),
    Sa("Forgiveness is not reconciliation. You can forgive someone and never let them back in. Forgiveness is an internal release. Trust is a separate decision, and it's earned over time.",
       "doors"),
    Sb("In theory. In practice, the person who hurt you rarely hears the difference. They hear: it's okay. One study of married couples found that when partners kept forgiving repeated bad behavior, that behavior was more likely to continue.",
       "loop"),
    Mo("Round three: is forgiveness ever weakness?", round=3, rt="Is it ever weakness?", sfx=[("ding", 0, 0.4)]),
    Sa("When it's fake. Forgiveness that skips your anger, that hurries to be nice, isn't forgiveness at all. It's avoidance. Real forgiveness comes after you've fully named what happened.",
       "mask"),
    Sb("And I'll concede this: forgiveness by choice can be powerful. My point is narrower. Forgiveness on demand, given just to keep someone else comfortable, is weakness dressed as virtue.",
       "demand"),
    Mo("So here is the verdict. Both sides agree on more than they think. Forgiveness is strength when it's a choice, made after you've seen the harm clearly, with your boundaries still in place. It becomes weakness when it's a requirement: rushed, pressured, or used to excuse what is still happening.",
       verdict=True, sfx=[("riser", 0, 0.6)]),
    Mo("Forgive freely, if it frees you. But never let forgiveness become the door they walk back through.", verdict=True, final=True),
    Mo("So, which side won for you? Strength, or weakness? Vote in the comments, and tell us why.", q=True, sfx=[("ding", 0.3, 0.5)]),
]

GOLD = hx("f2c14e")
CRIM = hx("e2445c")
TEALC = hx("7fd6e8")
WHITE = (240, 240, 245)
STAGE = hx("0c0a14")
AX, BX, MX = 420, 1500, 960
COL = {"a": GOLD, "b": CRIM, "m": TEALC}


class Style(Base):
    cap = dict(font="Inter", size=44, w=600, y=1015, fill=WHITE, hl=TEALC, bar=(0, 0, 0, 200), maxw=1500, barr=10)
    xfade = 0.3

    def setup(self):
        bg = gradient(hx("1b1630"), STAGE)
        d = D(bg)
        d.rectangle((0, 760, W, H), fill=A(hx("17121f"), 1))
        for x, c in ((AX, GOLD), (BX, CRIM)):
            pass
        self.BG = vignette(bg, 0.5)
        rnd = random.Random(1)
        self.aud = [(rnd.uniform(0, W), rnd.uniform(0, 1)) for _ in range(70)]
        self.round = []
        r, rt = 0, ""
        for b in self.beats:
            r = b.v.get("round", r)
            rt = b.v.get("rt", rt)
            self.round.append((r, rt))

    def cross(self, b):
        return True

    def cap_style(self, ch):
        c = dict(self.cap)
        c["hl"] = COL[ch[0]["who"]]
        return c

    def stage(self, d, b, lt, t):
        who = b.who
        for x, c, k in ((AX, GOLD, "a"), (BX, CRIM, "b"), (MX, TEALC, "m")):
            on = who == k
            a = 0.16 if on else 0.05
            top = 0
            w_ = 300 if k != "m" else 200
            d.polygon([(x - 40, top), (x + 40, top), (x + w_, 860), (x - w_, 860)], fill=A(c, a))
            d.ellipse((x - w_, 820, x + w_, 900), fill=A(c, a * 1.5))
        # moderator desk
        figure(d, MX, 700, 170, "talk" if who == "m" and lt < b.dur else "stand", TEALC, t, face="smile", head_fill=STAGE)
        d.rectangle((MX - 140, 640, MX + 140, 720), fill=A(hx("2a2540"), 1))
        text(d, (MX, 680), "MODERATOR", F("Inter", 22, 800), TEALC)
        for x, c, k, lab in ((AX, GOLD, "a", "STRENGTH"), (BX, CRIM, "b", "WEAKNESS")):
            on = who == k and lt < b.dur
            figure(d, x, 800, 310, "talk" if on else "stand", c, t + (0 if k == "a" else 2), face="flat", head_fill=STAGE, flip=k == "b")
            podium(d, x, 910, 260, c, hx("221d33"), lab, F("dmserif", 46), c)
        for x, ph in self.aud:
            y = 1010 + 30 * ph
            d.ellipse((x - 30, y - 34, x + 30, y + 26), fill=A((5, 4, 9), 1))
            d.rectangle((x - 44, y + 10, x + 44, y + 80), fill=A((5, 4, 9), 1))

    def card(self, d, b, lt, t):
        k = b.v["card"]
        side = b.who
        c = COL[side]
        x0 = 80 if side == "a" else W - 80 - 760
        x1 = x0 + 760
        y0, y1 = 140, 470
        a = ease((lt - 0.4) / 0.4)
        rrect(d, (x0, y0, x1, y1), 18, fill=A(hx("120f1c"), 0.94 * a), outline=A(c, a), width=3)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        p = lambda s_: ease((lt - s_ * b.dur) / 0.5) * a
        if k == "health":
            chain(d, x0 + 80, cy - 40, cx - 40, cy - 40, (150, 150, 160), s=20, lw=5, alpha=a * (1 - p(0.55)))
            figure(d, cx + 160, cy + 120, 170, "arms_up" if lt > 0.55 * b.dur else "sad", c, t, face="smile" if lt > 0.55 * b.dur else "frown",
                   head_fill=STAGE, alpha=a)
            for i, s in enumerate(("lower stress", "better sleep", "less rumination")):
                text(d, (x0 + 40, y0 + 60 + i * 50), s, F("Inter", 32, 700), c, "lm", alpha=p(0.15 + i * 0.08))
        elif k == "pressure":
            figure(d, cx, cy + 120, 160, "sad", c, t, face="frown", head_fill=STAGE, alpha=a)
            for i, ang in enumerate((-150, -30, 200, -20)):
                ar = math.radians([-160, -20, 180, 0][i])
                sx, sy = cx + math.cos(ar) * 300, cy + 40 + math.sin(ar) * 80
                arrow(d, (sx, sy), (cx + math.cos(ar) * 90, cy + 40 + math.sin(ar) * 40), (180, 180, 190), 5, 18, p(0.1 + i * 0.05))
            text(d, (cx, y0 + 50), "\"just forgive, keep the peace\"", F("Inter", 32, 700), WHITE, alpha=p(0.1))
            text(d, (cx, y1 - 40), "no change + forgiveness = no cost", F("Inter", 30, 800), c, alpha=p(0.55))
        elif k == "doors":
            for i, (lab, sub) in enumerate((("FORGIVE", "inside you"), ("TRUST", "earned over time"))):
                dx = cx - 180 + i * 360
                door(d, dx, y1 - 30, 220, c if i == 0 else (170, 170, 180), fill=hx("1d1830"), open_=0.0 if i else 0.0)
                text(d, (dx, y0 + 50), lab, F("dmserif", 44), c if i == 0 else WHITE, alpha=p(0.1 + i * 0.3))
                text(d, (dx, y0 + 95), sub, F("Inter", 26, 600), (190, 190, 200), alpha=p(0.1 + i * 0.3))
            d.line([(cx, y0 + 40), (cx, y1 - 40)], fill=A(WHITE, 0.4 * a), width=3)
        elif k == "loop":
            r = 120
            for i in range(3):
                a0 = (t * 90 + i * 120) % 360
                d.arc((cx - r, cy - r + 20, cx + r, cy + r + 20), a0, a0 + 90, fill=A(c, a), width=10)
            text(d, (cx, cy + 20), "REPEAT", F("dmserif", 48), WHITE, alpha=a)
            text(d, (cx, y1 - 34), "McNulty, J. Family Psychology (2011)", F("Inter", 24, 500), (170, 170, 180), alpha=p(0.5))
        elif k == "mask":
            mask(d, cx - 150, cy + 10, 200, hx("eae3d2"), eye=STAGE, smile=True)
            text(d, (cx + 170, cy - 40), "fake forgiveness", F("dmserif", 40), WHITE, alpha=p(0.1))
            text(d, (cx + 170, cy + 20), "= avoidance", F("dmserif", 40), c, alpha=p(0.3))
            text(d, (cx + 170, cy + 100), "name it first", F("Inter", 30, 800), GOLD, alpha=p(0.7))
        elif k == "demand":
            figure(d, cx - 170, cy + 130, 160, "point", (180, 180, 190), t, face="angry", head_fill=STAGE, alpha=a)
            figure(d, cx + 170, cy + 130, 160, "sad", c, t, face="frown", head_fill=STAGE, flip=True, alpha=a)
            bubble(d, cx - 150, y0 + 70, "Just forgive him already.", F("Inter", 30, 700), (230, 230, 235), STAGE, alpha=p(0.25))
            text(d, (cx + 170, y0 + 60), "on demand", F("dmserif", 40), c, alpha=p(0.55))

    def draw(self, img, b, lt, t):
        d = D(img)
        v = b.v
        self.stage(d, b, lt, t)
        r, rt = self.round[b.i]
        if v.get("hook"):
            a = ease(lt / 0.4)
            rrect(d, (360, 140, 1560, 470), 20, fill=A(hx("0f0c18"), 0.92 * a), outline=A(WHITE, 0.3 * a), width=2)
            text(d, (MX, 220), "THE DEBATE", F("Inter", 34, 800), TEALC, alpha=a)
            text(d, (MX, 320), "Is forgiveness", F("dmserif", 84), WHITE, alpha=a)
            text(d, (MX - 45, 415), "strength", F("dmserif", 84), GOLD, "rm", alpha=ease((lt - 1) / 0.4))
            text(d, (MX, 415), "or", F("dmserif", 60), WHITE, alpha=ease((lt - 1.3) / 0.4))
            text(d, (MX + 45, 415), "weakness?", F("dmserif", 84), CRIM, "lm", alpha=ease((lt - 1.6) / 0.4))
            return
        if r and not v.get("verdict") and not v.get("q"):
            rrect(d, (MX - 380, 40, MX + 380, 118), 39, fill=A(hx("0f0c18"), 0.9), outline=A(TEALC, 0.8), width=2)
            text(d, (MX, 79), f"ROUND {r}/3 · {rt.upper()}", F("Inter", 30, 800), WHITE)
        if v.get("card"):
            self.card(d, b, lt, t)
        if v.get("round") and b.who == "m":
            s = lerp(1.4, 1, ease(lt / 0.3))
            text(d, (MX, 330), f"ROUND {r}", F("dmserif", int(130 * s)), TEALC, alpha=ease(lt / 0.3))
        if v.get("verdict"):
            a = ease(lt / 0.5)
            rrect(d, (300, 130, 1620, 600), 20, fill=A(hx("0f0c18"), 0.95 * a), outline=A(TEALC, a), width=3)
            text(d, (MX, 190), "THE VERDICT", F("Inter", 36, 800), TEALC, alpha=a)
            if not v.get("final"):
                tilt = math.sin(lt * 1.2) * 0.6 * (1 - ease((lt - 4) / 3))
                balance(d, MX, 240, 170, WHITE, tiltv=tilt, lc=GOLD, rc=CRIM)
                text(d, (MX - 330, 470), "STRENGTH", F("dmserif", 44), GOLD, alpha=a)
                text(d, (MX - 330, 520), "when it's a choice", F("Inter", 30, 600), WHITE, alpha=ease((lt - 6) / 0.5))
                text(d, (MX + 330, 470), "WEAKNESS", F("dmserif", 44), CRIM, alpha=a)
                text(d, (MX + 330, 520), "when it's a requirement", F("Inter", 30, 600), WHITE, alpha=ease((lt - 13) / 0.5))
            else:
                para(d, MX, 330, "Forgive freely, if it frees you.", F("dmserif", 70), GOLD, 1200, alpha=a)
                para(d, MX, 470, "Never let it become the door they walk back through.", F("dmserif", 52), WHITE, 1200, alpha=ease((lt - 2.5) / 0.5))
        if v.get("q"):
            a = ease(lt / 0.4)
            rrect(d, (300, 130, 1620, 600), 20, fill=A(hx("0f0c18"), 0.95 * a), outline=A(WHITE, 0.4 * a), width=2)
            text(d, (MX, 200), "YOU DECIDE", F("Inter", 36, 800), TEALC, alpha=a)
            text(d, (MX, 300), "Which side won?", F("dmserif", 90), WHITE, alpha=a)
            for x, lab, c in ((MX - 250, "STRENGTH", GOLD), (MX + 250, "WEAKNESS", CRIM)):
                aa = ease((lt - 1) / 0.4)
                rrect(d, (x - 200, 400, x + 200, 500), 50, fill=A(c, aa))
                text(d, (x, 450), lab, F("Inter", 40, 900), STAGE, alpha=aa)
            text(d, (MX, 555), "vote in the comments — and tell us why", F("Inter", 30, 500), (190, 190, 200), alpha=ease((lt - 2) / 0.4))
