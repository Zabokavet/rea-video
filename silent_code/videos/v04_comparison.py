from engine import *

TITLE = "Quiet Confidence vs Loud Arrogance"
VOICES = {"n": ("bm_george", 0.93)}
GAP = 0.6
MUSIC = dict(kind="pad+drone", root=87.3, prog=[0, 3, -2, 5], qual=["m", "M", "M", "m"], bar=8, vol=0.11, nzcut=300)

LX, RX = 480, 1440


def S(n, name, say, L, R):
    return dict(say=say, v=dict(k="sign", n=n, name=name, L=L, R=R), sfx=[("whoosh", 0, 0.5)])


BEATS = [
    dict(say="One of them walks into a room and everyone notices. The other walks in, and everyone notices too. Only one of them is actually strong.",
         v=dict(k="hook"), sfx=[("boom", 0, 0.7)], gap=0.7),
    dict(say="From far away, arrogance and confidence can look the same. Up close, they are opposites. Arrogance is a performance for other people. Confidence is a relationship with yourself. Here's how to tell them apart, sign by sign.",
         v=dict(k="intro")),
    S(1, "VOLUME", "Sign one: volume. The arrogant person needs to be heard, so they talk over others and raise their voice to win. The confident person speaks at a normal volume, because they simply assume they'll be listened to.",
      dict(figs=[dict(x=380, p="talk", c="L", f="flat"), dict(x=600, p="stand", flip=True, c="dim", f="smile")], bubbles=[(380, 400, "Here's what I think.", 0.5)], note="Calm, steady voice"),
      dict(figs=[dict(x=1340, p="fist", c="R", f="angry"), dict(x=1580, p="sad", flip=True, c="dim", f="o")], bubbles=[(1360, 380, "LISTEN TO ME!", 0.5)], note="Talks over everyone")),
    S(2, "LISTENING", "Sign two: listening. Arrogance listens only to reload, waiting for a gap to talk again. Confidence listens to understand, and isn't threatened when someone else knows more.",
      dict(figs=[dict(x=380, p="think", c="L", f="smile"), dict(x=600, p="talk", flip=True, c="dim", f="smile")], bubbles=[(620, 400, "Actually, I studied this...", 0.5)], note="Curious, not threatened"),
      dict(figs=[dict(x=1340, p="talk2", c="R", f="smirk"), dict(x=1580, p="talk", flip=True, c="dim", f="o")], bubbles=[(1330, 380, "Yeah, yeah. Anyway—", 1.5)], note="Waiting to reload")),
    S(3, "MISTAKES", "Sign three: mistakes. The arrogant person defends every error, blames someone else, and never says the words, I was wrong. The confident person admits it quickly, because one mistake doesn't shake their sense of worth.",
      dict(figs=[dict(x=440, p="shrug", c="L", f="smile")], bubbles=[(440, 400, "I was wrong. I'll fix it.", 0.5)], note="Owns it fast"),
      dict(figs=[dict(x=1340, p="point", c="R", f="angry"), dict(x=1590, p="sad", flip=True, c="dim", f="frown")], bubbles=[(1330, 380, "That's on YOU.", 0.5)], note="Blames, defends, denies")),
    S(4, "OTHER PEOPLE'S WINS", "Sign four: other people's success. Arrogance competes with everyone, so your win feels like its loss. Confidence can genuinely celebrate you, because your light doesn't dim theirs.",
      dict(figs=[dict(x=380, p="arms_up", c="L", f="smile"), dict(x=600, p="stand", flip=True, c="dim", f="smile")], props=[("crown", 600, 470, 0.6, "gold")], note="Celebrates you"),
      dict(figs=[dict(x=1340, p="cross", c="R", f="frown"), dict(x=1580, p="stand", flip=True, c="dim", f="smile")], props=[("crown", 1580, 470, 0.6, "gold")], note="Your win = their loss")),
    S(5, "VALIDATION", "Sign five: validation. Arrogance constantly needs an audience: likes, praise, the last word. Confidence is comfortable unseen. It doesn't need a witness to know its own value.",
      dict(figs=[dict(x=440, p="sit", c="L", f="smile")], props=[("chair", 440, None, 1.0, "dim")], note="Comfortable unseen"),
      dict(figs=[dict(x=1440, p="phone", c="R", f="o")], props=[("phone", 1540, 520, 0.7, "R")], bubbles=[(1420, 330, "Did you see my post?? Did you like it?", 0.5)],
           note="Needs an audience")),
    S(6, "SILENCE", "Sign six: silence. For the arrogant, silence feels like losing, so they fill it. For the confident, silence is comfortable. They can sit in a quiet room and feel completely at ease.",
      dict(figs=[dict(x=440, p="sit", c="L", f="flat")], props=[("chair", 440, None, 1.0, "dim"), ("moon", 700, 300, 0.8, "L")], note="At ease in quiet"),
      dict(figs=[dict(x=1440, p="talk2", c="R", f="o")], bubbles=[(1440, 360, "So anyway, as I was saying, me, me, me...", 0.5)], note="Must fill every gap")),
    dict(say="Here's the psychology underneath. Researchers describe a pattern called fragile self-esteem: high on the surface, unstable underneath. Loud arrogance is often a fortress, built around a fear of being ordinary. True confidence doesn't need walls.",
         v=dict(k="fort")),
    dict(say="So the next time someone dominates a room, don't ask who's the loudest. Ask who's the calmest. That's usually where the real strength is.",
         v=dict(k="calm")),
    dict(say="Think of the most confident person you know in real life. Are they loud, or quiet? Tell me in the comments.",
         v=dict(k="question"), sfx=[("ding", 0.3, 0.6)]),
]

LB, RB = hx("0f2536"), hx("3a1010")
LC, RC = hx("bfe3ff"), hx("ffc2b0")
GOLD = hx("f5c86a")
PALL = dict(bg=LB, fg=LC, L=LC, R=RC, dim=hx("7f93a6"), gold=GOLD, gy=800, s=300, bubble=hx("eaf6ff"), bubtxt=LB)
PALR = dict(PALL, bg=RB, dim=hx("a68a85"), bubble=hx("ffe6df"), bubtxt=RB)


class Style(Base):
    cap = dict(font="Inter", size=48, w=600, y=990, fill=(235, 235, 235), hl=GOLD, bar=(0, 0, 0, 170), maxw=1500, barr=40)

    def setup(self):
        l = gradient(hx("13324a"), hx("08141e"))
        r = gradient(hx("4a1414"), hx("1c0707"))
        bg = l.copy()
        bg.paste(r.crop((W // 2, 0, W, H)), (W // 2, 0))
        d = D(bg)
        d.rectangle((0, 800, W, H), fill=A((0, 0, 0), 0.3))
        self.BG = vignette(texture(bg, 4, 2), 0.35)
        self.bf = F("Inter", 32, 600)

    def headers(self, d, a=1.0):
        text(d, (LX, 70), "QUIET CONFIDENCE", F("cormorant", 64, 700), LC, alpha=a)
        text(d, (RX, 70), "LOUD ARROGANCE", F("archivoblack", 54), RC, alpha=a)
        d.line([(W / 2, 0), (W / 2, 800)], fill=A((255, 255, 255), 0.25 * a), width=3)

    def draw(self, img, b, lt, t):
        d = D(img)
        v = b.v
        k = v["k"]
        if k == "hook":
            figure(d, LX, 800, 330, "stand", LC, t, face="flat", head_fill=LB, alpha=ease(lt / 0.5))
            figure(d, RX, 800, 330, "fist", RC, t, face="angry", head_fill=RB, alpha=ease((lt - 1.2) / 0.5))
            text(d, (W / 2, 160), "Only one of them is strong.", F("cormorant", 90, 700), (255, 255, 255), alpha=ease((lt - 4.5) / 0.6))
            d.ellipse((W / 2 - 60, 480, W / 2 + 60, 600), fill=A((0, 0, 0), 0.7), outline=A(GOLD, 1), width=4)
            text(d, (W / 2, 540), "VS", F("archivoblack", 52), GOLD)
        elif k == "intro":
            self.headers(d, ease(lt / 0.5))
            text(d, (LX, 420), "a relationship", F("cormorant", 80, 600), LC, alpha=ease((lt - 6) / 0.5))
            text(d, (LX, 510), "with yourself", F("cormorant", 80, 600), LC, alpha=ease((lt - 6.3) / 0.5))
            text(d, (RX, 420), "A PERFORMANCE", F("archivoblack", 70), RC, alpha=ease((lt - 4) / 0.5))
            text(d, (RX, 510), "FOR OTHERS", F("archivoblack", 70), RC, alpha=ease((lt - 4.3) / 0.5))
        elif k == "sign":
            self.headers(d)
            rrect(d, (W / 2 - 280, 140, W / 2 + 280, 220), 40, fill=A((0, 0, 0), 0.6), outline=A(GOLD, 1), width=2)
            text(d, (W / 2, 180), f"SIGN {v['n']} · {v['name']}", F("Inter", 34, 800), GOLD)
            scene(d, v["L"], lt, t, PALL, bfont=self.bf)
            dl = b.dur * 0.45
            scene(d, v["R"], lt - 0.2, t, PALR, bfont=self.bf)
            text(d, (LX, 860), "✓ " + v["L"]["note"] if False else v["L"]["note"], F("cormorant", 48, 700), LC, alpha=ease((lt - dl) / 0.5))
            text(d, (RX, 860), v["R"]["note"].upper(), F("archivoblack", 34), RC, alpha=ease((lt - 1) / 0.5))
        elif k == "fort":
            self.headers(d)
            figure(d, LX, 760, 300, "stand", LC, t, face="smile", head_fill=LB)
            fx = RX
            figure(d, fx, 760, 220, "hug_self", RC, t, face="frown", head_fill=RB)
            h = 165 * ease((lt - 3) / 2.5)
            for i, x in enumerate(range(fx - 250, fx + 260, 70)):
                top = 760 - h - (40 if i % 2 == 0 else 0) * (h > 0)
                d.rectangle((x, top, x + 64, 760), fill=A(hx("5a2a24"), 1), outline=A(RB, 1), width=3)
            text(d, (RX, 860), "FRAGILE SELF-ESTEEM", F("archivoblack", 40), RC, alpha=ease((lt - 3) / 0.5))
            text(d, (LX, 860), "No walls needed", F("cormorant", 52, 700), LC, alpha=ease((lt - 12) / 0.5))
        elif k == "calm":
            a = ease(lt / 0.5)
            text(d, (W / 2, 360), "Don't ask who's the loudest.", F("cormorant", 92, 600), (220, 220, 220), alpha=a)
            text(d, (W / 2, 500), "Ask who's the calmest.", F("cormorant", 110, 700), GOLD, alpha=ease((lt - 2.2) / 0.6))
        elif k == "question":
            a = ease(lt / 0.5)
            text(d, (W / 2, 240), "Comment below", F("cormorant", 56, 700), GOLD, alpha=a)
            para(d, W / 2, 420, "The most confident person you know — loud, or quiet?", F("cormorant", 96, 700), (255, 255, 255), 1400, alpha=a)
            for x, lab, c, f in ((LX + 160, "QUIET", LC, F("cormorant", 80, 700)), (RX - 160, "LOUD", RC, F("archivoblack", 64))):
                aa = ease((lt - 1) / 0.4)
                rrect(d, (x - 190, 610, x + 190, 740), 20, outline=A(c, aa), width=4)
                text(d, (x, 675), lab, f, c, alpha=aa)

    def show_cap(self, b):
        return b.v["k"] not in ("question", "hook")
