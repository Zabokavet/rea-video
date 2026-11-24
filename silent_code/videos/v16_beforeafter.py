from engine import *

TITLE = "The Day He Stopped Explaining Himself"
VOICES = {"n": ("am_echo", 0.86)}
GAP = 0.8
MUSIC = dict(kind="pad+piano", root=103.8, prog=[0, -2, 3, 5], qual=["m", "M", "M", "M"], bar=6, step=0.75, pat=[0, 2, 1, 3], vol=0.1)


def Bf(n, sit, say, figs, bubbles, props=()):
    return dict(say=say, v=dict(k="before", n=n, sit=sit, figs=figs, bubbles=bubbles, props=list(props)), sfx=[("whoosh", 0, 0.3)])


def Af(n, sit, say, figs, bubbles, props=()):
    return dict(say=say, v=dict(k="after", n=n, sit=sit, figs=figs, bubbles=bubbles, props=list(props)), sfx=[("whoosh", 0, 0.5), ("ding", 0.6, 0.3)])


SAM = "fg"
BEATS = [
    dict(say="For thirty one years, he explained himself to everyone. Then one Tuesday, he stopped. This is what changed.",
         v=dict(k="hook"), sfx=[("boom", 0, 0.7)], gap=0.8),
    dict(say="Meet Sam. Same job, same friends, same family. The only thing that changes in this story, is him.",
         v=dict(k="intro")),
    Bf(1, "THE BOSS", "Before. His boss questions his report. Sam launches into a five minute defense: apologizing, over-detailing, sweating.",
       [dict(x=800, p="talk2", f="o", tear=True), dict(x=1150, p="cross", flip=True, c="dim", f="flat")],
       [(780, 360, "Sorry, so basically, the thing is, I was going to, and also, sorry...", 0.5, (0, 1), 520)], [("table", 980, None, 0.8, "dim")]),
    Af(1, "THE BOSS", "After. Same question. Sam says: I stand by the numbers. Happy to walk you through any line. Then he stops talking. His boss nods.",
       [dict(x=800, p="hips", f="flat"), dict(x=1150, p="stand", flip=True, c="dim", f="smile")],
       [(800, 380, "I stand by the numbers.", 1.0)], [("table", 980, None, 0.8, "dim")]),
    Bf(2, "THE INVITE", "Before. A friend invites him out. He's exhausted, but he types a whole paragraph of excuses, then goes anyway, and resents it all night.",
       [dict(x=900, p="phone", f="frown", tear=True)], [(900, 330, "Hey so I'm SO sorry, it's just been a long week and I...", 0.5, (0, 1), 520)], [("phone", 1000, 540, 0.6, "dim")]),
    Af(2, "THE INVITE", "After. I'm going to stay in tonight. Have fun. No paragraph. No guilt. His friend replies with a thumbs up.",
       [dict(x=900, p="sit", f="smile")], [(900, 360, "Staying in tonight. Have fun!", 0.8)], [("chair", 900, None, 1.0, "dim")]),
    Bf(3, "THE EX", "Before. His ex texts at midnight: we need to talk. He replies within seconds, and spends two hours re-explaining a breakup that already happened.",
       [dict(x=900, p="phone", f="o")], [(1250, 330, "we need to talk.", 0.3, (-1, 1))], [("phone", 1000, 540, 0.6, "dim"), ("moon", 1600, 230, 0.8, "dim"), ("clock", 400, 380, 0.8, "dim")]),
    Af(3, "THE EX", "After. He reads it in the morning, and he doesn't reply. Closure isn't a conversation someone else has to approve.",
       [dict(x=900, p="stand", f="flat")], [(1250, 330, "we need to talk.", 0.3, (-1, 1))], [("phone", 1300, 830, 0.5, "dim")]),
    Bf(4, "FAMILY DINNER", "Before. At dinner, his mother criticizes his career. He argues, justifies, and practically begs her to understand.",
       [dict(x=760, p="beg", f="frown"), dict(x=1160, p="sit", flip=True, c="dim", f="frown", hair="dim")], [(1160, 330, "When will you get a real job?", 0.4)], [("table", 960, None, 0.9, "dim"), ("chair", 1160, None, 1.0, "dim", True)]),
    Af(4, "FAMILY DINNER", "After. I know you see it differently, Mom. I'm happy with my choice. Could you pass the salad? The argument has nowhere to land.",
       [dict(x=760, p="sit", f="smile"), dict(x=1160, p="sit", flip=True, c="dim", f="flat", hair="dim")], [(760, 330, "I'm happy with my choice. Salad?", 0.6)],
       [("table", 960, None, 0.9, "dim"), ("chair", 760, None, 1.0, "dim"), ("chair", 1160, None, 1.0, "dim", True)]),
    dict(say="Here's the psychology. Over-explaining is often a fawn habit: seeking safety through approval. Each extra explanation quietly says, your judgment of me matters more than mine. People sense that, and they push harder.",
         v=dict(k="psych")),
    dict(say="When Sam stopped explaining, he didn't become cold. He became clear. One reason, one sentence, then silence. And silence, it turns out, reads as confidence.",
         v=dict(k="clear")),
    dict(say="The rule he lives by now: explain once, to people who want to understand you. To people who have already decided to misunderstand you, don't explain at all.",
         v=dict(k="rule")),
    dict(say="Who do you still over-explain yourself to? Your boss, your family, an ex? Tell me in the comments.",
         v=dict(k="question"), sfx=[("ding", 0.3, 0.6)]),
]

GOLD = hx("f2b134")
PB = dict(bg=hx("2b2c30"), fg=hx("c9c9cc"), dim=hx("77787d"), gy=860, s=290, bubble=hx("9a9aa0"), bubtxt=hx("1c1c1f"), headfill=hx("2b2c30"), tear=hx("8fb3ff"),
          screen=hx("8a8fa0"))
PA = dict(bg=hx("fbf2e4"), fg=hx("1f2a37"), dim=hx("9a8f80"), gy=860, s=290, bubble=hx("1f2a37"), bubtxt=hx("fbf2e4"), headfill=hx("fbf2e4"), screen=GOLD)


class Style(Base):
    cap = dict(font="Inter", size=46, w=700, y=1005, fill=(255, 255, 255), hl=GOLD, bar=(0, 0, 0, 160), maxw=1500, barr=12)
    xfade = 0.3

    def setup(self):
        b = radial(hx("3a3b40"), hx("141416"), r=1100)
        D(b).rectangle((0, 860, W, H), fill=A((0, 0, 0), 0.35))
        self.BB = vignette(texture(b, 9, 2), 0.7, 1.6)
        a = gradient(hx("fff7ea"), hx("f6dfbf"))
        da = D(a)
        for r, al in ((600, 0.06), (380, 0.1), (200, 0.25)):
            da.ellipse((1650 - r, 150 - r, 1650 + r, 150 + r), fill=A((255, 214, 140), al))
        da.rectangle((0, 860, W, H), fill=A(hx("ecd3b0"), 1))
        self.BA = a
        self.BG = self.BA
        self.bfb = F("Inter", 32, 500)
        self.bfa = F("Inter", 34, 700)

    def cross(self, b):
        return b.v["k"] != "after"

    def render_beat(self, img, b, lt, t):
        v = b.v
        k = v["k"]
        if k == "before":
            img.paste(self.BB)
            d = D(img)
            sh = math.sin(t * 9) * 4
            vv = dict(v, figs=[dict(f, x=f["x"] + sh) for f in v["figs"]])
            scene(d, vv, lt, t, PB, bfont=self.bfb)
            rrect(d, (70, 60, 330, 140), 8, fill=A(hx("55565c"), 1))
            text(d, (200, 100), "BEFORE", F("bebas", 70), hx("d0d0d4"))
            text(d, (W / 2, 100), f"SITUATION {v['n']} · {v['sit']}", F("Inter", 32, 800), hx("9a9aa0"))
        elif k == "after":
            img.paste(self.BA)
            d = D(img)
            scene(d, v, lt, t, PA, bfont=self.bfa)
            rrect(d, (70, 60, 330, 140), 8, fill=A(GOLD, 1))
            text(d, (200, 100), "AFTER", F("bebas", 70), hx("1f2a37"))
            text(d, (W / 2, 100), f"SITUATION {v['n']} · {v['sit']}", F("Inter", 32, 800), hx("1f2a37"))
            if v["n"] == 3:
                text(d, (1250, 520), "no reply.", F("Inter", 44, 800), GOLD, alpha=ease((lt - 3) / 0.4))
        else:
            img.paste(self.BA)
            d = D(img)
            ink = hx("1f2a37")
            if k == "hook":
                img.paste(self.BB.crop((0, 0, W // 2, H)), (0, 0))
                d = D(img)
                figure(d, 480, 860, 320, "talk2", PB["fg"], t, face="o", head_fill=PB["bg"], accent=PB["tear"])
                figure(d, 1440, 860, 320, "hips", ink, t, face="flat", head_fill=PA["bg"])
                text(d, (480, 220), "explaining", F("bebas", 120), hx("9a9aa0"), alpha=ease(lt / 0.4))
                text(d, (1440, 220), "silent", F("bebas", 120), ink, alpha=ease((lt - 2.5) / 0.4))
                d.line([(W / 2, 0), (W / 2, H)], fill=A(GOLD, 1), width=6)
            elif k == "intro":
                figure(d, W / 2, 860, 340, "stand", ink, t, face="smile", head_fill=PA["bg"])
                text(d, (W / 2, 250), "Meet Sam.", F("bebas", 140), ink, alpha=ease(lt / 0.4))
                text(d, (W / 2, 360), "only one thing changes: him", F("Inter", 40, 600), PA["dim"], alpha=ease((lt - 3) / 0.4))
            elif k == "psych":
                text(d, (W / 2, 200), "OVER-EXPLAINING =", F("bebas", 90), ink, alpha=ease(lt / 0.4))
                text(d, (W / 2, 310), "seeking safety through approval", F("Inter", 50, 700), GOLD, alpha=ease((lt - 1) / 0.4))
                L, R = balance(d, W / 2, 470, 260, ink, tiltv=-ease((lt - 5) / 1.0), lc=hx("9a8f80"), rc=GOLD)
                text(d, (L[0], L[1] + 200), "their judgment", F("Inter", 34, 700), ink, alpha=ease((lt - 5) / 0.4))
                text(d, (R[0], R[1] + 200), "yours", F("Inter", 34, 700), ink, alpha=ease((lt - 5) / 0.4))
            elif k == "clear":
                text(d, (W / 2, 300), "Not cold.", F("bebas", 150), PA["dim"], alpha=ease(lt / 0.4))
                text(d, (W / 2, 460), "CLEAR.", F("bebas", 190), GOLD, alpha=ease((lt - 2) / 0.4))
                for i, s in enumerate(("one reason", "one sentence", "silence")):
                    aa = ease((lt - 4 - i * 1.0) / 0.4)
                    text(d, (560 + i * 400, 680), s, F("Inter", 46, 800), ink, alpha=aa)
            elif k == "rule":
                text(d, (W / 2, 220), "THE RULE", F("bebas", 80), GOLD, alpha=ease(lt / 0.4))
                para(d, W / 2, 420, "Explain once to people who want to understand you.", F("Inter", 60, 800), ink, 1500, alpha=ease((lt - 0.5) / 0.4))
                para(d, W / 2, 640, "To people who've decided to misunderstand — don't explain at all.", F("Inter", 52, 600), PA["dim"], 1500,
                     alpha=ease((lt - 5) / 0.4))
            elif k == "question":
                a = ease(lt / 0.4)
                rrect(d, (260, 220, 1660, 780), 30, fill=A(ink, a))
                text(d, (W / 2, 300), "COMMENT BELOW", F("Inter", 34, 800), GOLD, alpha=a)
                para(d, W / 2, 470, "Who do you still over-explain yourself to?", F("bebas", 110), PA["bg"], 1200, alpha=a)
                for i, s in enumerate(("YOUR BOSS", "FAMILY", "AN EX")):
                    aa = ease((lt - 1.5 - i * 0.3) / 0.3)
                    x = 660 + i * 300
                    rrect(d, (x - 120, 640, x + 120, 710), 35, outline=A(GOLD, aa), width=3)
                    text(d, (x, 675), s, F("Inter", 30, 800), GOLD, alpha=aa)

    def draw(self, img, b, lt, t):
        self.render_beat(img, b, lt, t)
        if b.v["k"] == "after" and lt < 0.9:
            p = self.beats[b.i - 1]
            prev = Image.new("RGB", (W, H))
            self.render_beat(prev, p, p.t1 - p.t0, t)
            x = int(W * eio(lt / 0.9))
            img.paste(prev.crop((x, 0, W, H)), (x, 0))
            D(img).line([(x, 0), (x, H)], fill=A(GOLD, 1), width=8)

    def show_cap(self, b):
        return b.v["k"] not in ("question", "hook")
