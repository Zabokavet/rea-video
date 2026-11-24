from engine import *

TITLE = "5 Lies About Narcissists Everyone Believes"
VOICES = {"n": ("af_jessica", 0.83)}
GAP = 0.75
MUSIC = dict(kind="pad+pulse+hats", root=103.8, prog=[0, -4, -2, 3], qual=["m", "M", "M", "M"], bar=4, bpm=84, vol=0.09)


def My(n, myth, say):
    return dict(say=say, v=dict(k="myth", n=n, myth=myth), gap=0.35)


def Tr(n, head, say, sc):
    return dict(say=say, v=dict(k="truth", n=n, head=head, sc=sc), sfx=[("scratch", 0.0, 0.9), ("ding", 0.7, 0.3)])


BEATS = [
    dict(say="Most of what you've heard about narcissists is wrong. And believing these five myths is exactly what keeps people stuck with one.",
         v=dict(k="hook"), sfx=[("hit", 0, 0.6)], gap=0.7),
    My(1, "Narcissists are always loud and arrogant.", "Myth number one: narcissists are always loud and arrogant."),
    Tr(1, "Many are quiet.", "Many are quiet. Researchers separate grandiose narcissism from vulnerable, or covert, narcissism. The covert type is shy, hypersensitive to criticism, quietly resentful, and still convinced they deserve special treatment. They often play the misunderstood victim, not the star.", "covert"),
    My(2, "They love themselves too much.", "Myth number two: narcissists love themselves too much."),
    Tr(2, "Their self-image is fragile.", "Their self-image is often fragile. Much of the behavior is armor. They need constant admiration because their sense of worth wobbles without it. It's less self-love, and more self-defense.", "armor"),
    My(3, "Anyone selfish is a narcissist.", "Myth number three: anyone selfish is a narcissist."),
    Tr(3, "It's a pattern, not a mood.", "Narcissistic personality disorder is a clinical diagnosis, found in only a few percent of adults, depending on the study. Everyone has some narcissistic traits. It becomes a disorder when the pattern is rigid, lasting, and harms the people around them.", "dots"),
    My(4, "You can love them into changing.", "Myth number four: if you love them enough, they'll change."),
    Tr(4, "Love is not treatment.", "Love alone doesn't rewrite deep patterns. Change is possible, but it usually requires the person to see the problem themselves and commit to long-term therapy. Your patience is kind. It is not treatment. If you're waiting for someone to change, watch what they do, not what they promise.", "love"),
    My(5, "They always know exactly what they're doing.", "Myth number five: narcissists always know exactly what they're doing."),
    Tr(5, "Often, it's automatic.", "Some are calculating. Many are not fully aware. Their defenses run on autopilot, which is why arguing with logic rarely works. That doesn't excuse the behavior, but it changes your response: boundaries, not debates. State the limit once, calmly, and then act on it.", "bound"),
    dict(say="And the most dangerous myth of all? That you'd recognize one immediately. Usually, you recognize the pattern long after you've fallen for the charm. Charm is a performance. Patterns are the truth.",
         v=dict(k="final"), sfx=[("riser", 0, 0.6)]),
    dict(say="Which of these myths did you believe? Or is there one I missed? Tell me in the comments.",
         v=dict(k="question"), sfx=[("ding", 0.3, 0.6)]),
]

PAPER = hx("f4f1ea")
INK = hx("141414")
RED = hx("e0262b")
TEAL = hx("0f8b7d")
GREY = hx("9a958a")
PAL = dict(bg=PAPER, fg=INK, red=RED, teal=TEAL, dim=GREY, gy=900, s=280, bubble=INK, bubtxt=PAPER, lw=8)


class Style(Base):
    cap = dict(font="Inter", size=44, w=700, y=1012, fill=(250, 250, 250), hl=hx("ffd84d"), bar=(20, 20, 20, 240), maxw=1500, barr=6)
    xfade = 0.25

    def setup(self):
        bg = texture(Image.new("RGB", (W, H), PAPER), 6, 2)
        d = D(bg)
        d.line([(80, 80), (W - 80, 80)], fill=A(INK, 1), width=4)
        d.line([(80, 92), (W - 80, 92)], fill=A(INK, 1), width=1)
        text(d, (80, 50), "THE SILENT CODE · MYTH FILES", F("Inter", 22, 800), INK, "lm")
        self.BG = bg
        self.bf = F("Inter", 34, 600)
        self.mf = F("dmserif", 92)

    def myth_block(self, d, n, myth, a=1.0, small=False, cross=0.0):
        if small:
            f = F("dmserif", 50)
            y = 190
            text(d, (W / 2, 140), f"MYTH #{n}", F("Inter", 26, 800), GREY, alpha=a)
            text(d, (W / 2, y), myth, f, GREY, alpha=a)
            w = f.getlength(myth)
            if cross > 0:
                scribble(d, W / 2 - w / 2 - 20, W / 2 + w / 2 + 20, y, RED, 10, cross, amp=7, seed=n)
            return
        text(d, (W / 2, 300), f"MYTH #{n}", F("Inter", 40, 800), RED, alpha=a)
        para(d, W / 2, 520, f"“{myth}”", self.mf, INK, 1500, alpha=a)

    def truth_scene(self, d, sc, lt, t):
        if sc == "covert":
            figure(d, 760, 900, 300, "sit_sad", INK, t, face="frown", head_fill=PAPER, lw=8)
            chair(d, 760, 900, 300, GREY)
            bubble(d, 760, 470, "Nobody appreciates me...", self.bf, INK, PAPER, alpha=ease((lt - 2.5) / 0.3))
            figure(d, 1250, 900, 300, "fist", GREY, t, face="angry", head_fill=PAPER, lw=8, alpha=0.35)
            text(d, (760, 945), "VULNERABLE", F("Inter", 26, 800), TEAL)
            text(d, (1250, 945), "GRANDIOSE", F("Inter", 26, 800), GREY)
        elif sc == "armor":
            figure(d, 960, 900, 320, "hold", INK, t, face="flat", head_fill=PAPER, lw=8)
            cx, cy = 960, 760
            pts = [(cx - 85, cy - 95), (cx + 85, cy - 95), (cx + 78, cy + 30), (cx, cy + 105), (cx - 78, cy + 30)]
            d.polygon(pts, fill=A(hx("d9d4c7"), 1), outline=A(INK, 1))
            d.line(pts + [pts[0]], fill=A(INK, 1), width=6)
            c = ease((lt - 3) / 1)
            line_prog(d, (cx - 20, cy - 95), (cx + 10, cy - 40), c * 3, INK, 4)
            line_prog(d, (cx + 10, cy - 40), (cx - 15, cy + 30), c * 3 - 1, INK, 4)
            line_prog(d, (cx - 15, cy + 30), (cx + 20, cy + 100), c * 3 - 2, INK, 4)
            text(d, (cx + 330, 560), "admire me", F("caveat", 60, 700), RED, alpha=ease((lt - 5) / 0.4))
            text(d, (cx - 330, 640), "or I crack", F("caveat", 60, 700), RED, alpha=ease((lt - 6.5) / 0.4))
        elif sc == "dots":
            for i in range(100):
                r_, c_ = divmod(i, 20)
                x = 580 + c_ * 40
                y = 580 + r_ * 50
                on = i in (13, 47, 71)
                a = ease((lt - 0.5 - i * 0.02) / 0.3)
                d.ellipse((x - 13, y - 13, x + 13, y + 13), fill=A(RED if on else hx("cfc9bb"), a))
            text(d, (W / 2, 490), "a few in every hundred adults", F("Inter", 40, 700), INK, alpha=ease((lt - 3) / 0.4))
            text(d, (W / 2, 880), "rigid · lasting · harmful", F("dmserif", 56), TEAL, alpha=ease((lt - 11) / 0.5))
        elif sc == "love":
            figure(d, 760, 900, 300, "reach", INK, t, face="smile", head_fill=PAPER, lw=8)
            figure(d, 1200, 900, 300, "cross", GREY, t, face="flat", head_fill=PAPER, lw=8, flip=True)
            heart(d, 980, 640 + math.sin(t * 3) * 8, 110, A(RED, 1))
            text(d, (980, 470), "≠ therapy" if False else "is not therapy", F("dmserif", 54), TEAL, alpha=ease((lt - 9) / 0.4))
        elif sc == "bound":
            figure(d, 700, 900, 300, "talk2", GREY, t, face="angry", head_fill=PAPER, lw=8)
            bubble(d, 690, 470, "You ALWAYS... you NEVER...", self.bf, INK, PAPER, alpha=ease((lt - 1) / 0.3))
            d.line([(960, 520), (960, 920)], fill=A(TEAL, ease((lt - 7) / 0.5)), width=10)
            figure(d, 1200, 900, 300, "point_l", INK, t, face="flat", head_fill=PAPER, lw=8, flip=False)
            bubble(d, 1230, 470, "I'm not discussing this.", self.bf, TEAL, PAPER, alpha=ease((lt - 9) / 0.3))

    def draw(self, img, b, lt, t):
        d = D(img)
        v = b.v
        k = v["k"]
        if k == "hook":
            text(d, (W / 2, 330), "5 LIES", F("dmserif", 220), INK, alpha=ease(lt / 0.4))
            text(d, (W / 2, 500), "about narcissists everyone believes", F("dmserif", 70), INK, alpha=ease((lt - 0.5) / 0.4))
            line_prog(d, (700, 430), (1220, 430), ease((lt - 1.2) / 0.6), RED, 10)
            text(d, (W / 2, 700), "#3 surprises almost everyone", F("Inter", 40, 700), RED, alpha=ease((lt - 4) / 0.4))
        elif k == "myth":
            self.myth_block(d, v["n"], v["myth"], ease(lt / 0.4))
        elif k == "truth":
            myth = self.beats[b.i - 1].v["myth"]
            self.myth_block(d, v["n"], myth, 1, small=True, cross=ease(lt / 0.5))
            sl = ease((lt - 0.5) / 0.4)
            f = F("Inter", 34, 800)
            rrect(d, (W / 2 - 110, 262, W / 2 + 110, 316), 6, fill=A(TEAL, sl))
            text(d, (W / 2, 289), "TRUTH", f, PAPER, alpha=sl)
            text(d, (W / 2, 380), v["head"], F("dmserif", 78), TEAL, alpha=ease((lt - 0.8) / 0.4))
            self.truth_scene(d, v["sc"], lt, t)
        elif k == "final":
            text(d, (W / 2, 300), "THE MOST DANGEROUS MYTH", F("Inter", 44, 800), RED, alpha=ease(lt / 0.4))
            para(d, W / 2, 470, "“I'd recognize one immediately.”", F("dmserif", 100), INK, 1500, alpha=ease((lt - 0.5) / 0.4))
            if lt > 3:
                scribble(d, 260, 1660, 470, RED, 12, ease((lt - 3) / 0.7), amp=8, seed=3)
            text(d, (W / 2, 700), "You see the pattern long after the charm.", F("dmserif", 60), TEAL, alpha=ease((lt - 5) / 0.5))
        elif k == "question":
            a = ease(lt / 0.4)
            text(d, (W / 2, 260), "YOUR TURN", F("Inter", 44, 800), RED, alpha=a)
            para(d, W / 2, 450, "Which myth did you believe?", F("dmserif", 110), INK, 1500, alpha=a)
            text(d, (W / 2, 620), "…or which one did I miss?", F("dmserif", 64), TEAL, alpha=ease((lt - 2) / 0.4))
            for i in range(5):
                aa = ease((lt - 1 - i * 0.15) / 0.3)
                x = 660 + i * 150
                d.rectangle((x - 50, 720, x + 50, 820), outline=A(INK, aa), width=4)
                text(d, (x, 770), str(i + 1), F("dmserif", 60), INK, alpha=aa)

    def show_cap(self, b):
        return b.v["k"] not in ("question", "hook", "myth")
