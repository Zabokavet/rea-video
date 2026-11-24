from engine import *

TITLE = "The Scorpion and the Frog - Why People Never Really Change"
VOICES = {"n": ("bm_fable", 0.84)}
GAP = 0.9
MUSIC = dict(kind="piano+pad", root=130.8, prog=[0, -3, 5, 7], qual=["M", "m", "M", "M"], bar=6, step=0.5, pat=[0, 1, 2, 3, 2, 1], vol=0.1)


def S(say, k, **kw):
    return dict(say=say, v=dict(k=k, **kw))


BEATS = [
    S("A scorpion asked a frog for a ride across the river. Saying no would have been the smartest thing the frog ever did.", "title", sfx=[("ding", 0, 0.5)], gap=0.9),
    S("Once upon a time, on the bank of a wide river, a scorpion needed to cross. He could not swim. So he called down to a frog. Carry me on your back, he said.", "bank",
      b=[(420, 360, "Carry me across?", 6.5, (1, 1))]),
    S("The frog laughed nervously. If I carry you, you'll sting me. The scorpion smiled. Why would I? If I sting you, we both drown. It would make no sense.", "bank",
      b=[(840, 380, "You'll sting me!", 0.8, (-1, 1)), (420, 360, "Then we'd both drown. Why would I?", 3.5, (1, 1))]),
    S("The logic was perfect. And the frog, who always wanted to believe the best in others, said: climb on.", "bank", climb=True,
      b=[(840, 380, "...Climb on.", 4.5, (-1, 1))]),
    S("Halfway across, in the deepest water, the frog felt a sharp pain in his back.", "ride", sting=True, sfx=[("hit", 3.6, 0.6)]),
    S("As the poison spread and they both began to sink, the frog cried out: why? Now we'll both die!", "sink", b=[(900, 380, "Why?! Now we'll both die!", 1.5, (0, 1))]),
    S("And the scorpion answered: I couldn't help it. It's my nature.", "nature", gap=1.2, sfx=[("boom", 0.2, 0.5)]),
    S("The frog's last thought was not about the poison. It was about the promise. The scorpion had sounded so reasonable.", "nature2"),
    S("This fable has survived for generations because we keep living it. We meet someone who has hurt others before, and they give us a perfect reason why they'd never hurt us.", "moral"),
    S("Psychologists often repeat a simple rule. The best predictor of future behavior is past behavior. Not promises. Not explanations. Patterns.", "pattern"),
    S("But here's the honest part. People can change. Long-term studies show personality traits do shift across a lifetime, slowly, and mostly through effort the person chooses for themselves. Rarely, because someone else needed them to.", "change"),
    S("The frog made three mistakes. He trusted logic over history. He believed the scorpion's words over the scorpion's record. And he believed his kindness would be the exception.", "mistakes"),
    S("So before you carry someone across your river, ask one question. What have they done, to people just like me? If the answer stings, believe it. Kindness that ignores the evidence isn't kindness. It's just a ride across the river.", "ask"),
    S("Have you ever carried a scorpion? What did they say to convince you? Tell me in the comments.", "question", sfx=[("ding", 0.3, 0.5)]),
]

GOLD = hx("f3c969")
CREAM = hx("fff4dc")
INK = hx("2c2018")
FROG = hx("6cbf6a")
SCORP = hx("4a2c22")
WY = 640


class Style(Base):
    cap = dict(font="lora", size=48, w=600, y=1008, fill=CREAM, hl=GOLD, bar=(30, 20, 15, 200), maxw=1500, barr=30)
    xfade = 0.6

    def setup(self):
        sky = gradient(hx("f6b27a"), hx("7b5ea7"))
        sky = Image.fromarray(np.asarray(sky)[::-1].copy())
        d = D(sky)
        for i, (c, base, amp, ph) in enumerate(((hx("8e6aa8"), 520, 70, 0.3), (hx("5d4a86"), 580, 50, 1.7))):
            pts = [(x, base - amp * (0.5 + 0.5 * math.sin(x / 260 + ph)) - 20 * math.sin(x / 90)) for x in range(0, W + 20, 20)]
            d.polygon(pts + [(W, H), (0, H)], fill=A(c, 1))
        d.rectangle((0, WY, W, H), fill=A(hx("3f6f9a"), 1))
        for i in range(30):
            d.line([(0, WY + i * 15), (W, WY + i * 15)], fill=A(hx("2d5378"), 0.05 * i / 3), width=15)
        bankL = [(0, 560), (300, 575), (420, 610), (470, WY + 10), (0, WY + 40)]
        bankR = [(W, 560), (1620, 575), (1500, 610), (1450, WY + 10), (W, WY + 40)]
        for poly in (bankL, bankR):
            d.polygon(poly, fill=A(hx("5b7d3a"), 1))
        rnd = random.Random(2)
        for i in range(40):
            x = rnd.choice([rnd.uniform(10, 440), rnd.uniform(1480, 1900)])
            h = rnd.uniform(40, 120)
            d.line([(x, 600), (x + rnd.uniform(-10, 10), 600 - h)], fill=A(hx("3e5e28"), 1), width=4)
        self.DAY = vignette(texture(sky, 5, 2, blur=1), 0.45)
        night = Image.fromarray((np.asarray(self.DAY).astype(np.float32) * np.array([0.35, 0.38, 0.55])).astype(np.uint8))
        self.NIGHT = night
        paper = texture(Image.new("RGB", (W, H), hx("f3e6c8")), 8, 2, blur=1)
        dd = D(paper)
        rrect(dd, (40, 40, W - 40, H - 40), 30, outline=A(hx("b89a62"), 1), width=6)
        rrect(dd, (60, 60, W - 60, H - 60), 24, outline=A(hx("b89a62"), 0.6), width=2)
        self.PAPER = vignette(paper, 0.35)

    def bg(self, t):
        b = self.tl.beat_at(t)
        if b.v["k"] in ("nature", "nature2"):
            return self.NIGHT.copy()
        if b.v["k"] in ("moral", "pattern", "change", "mistakes", "ask", "question", "title"):
            return self.PAPER.copy()
        return self.DAY.copy()

    def waves(self, d, t):
        water(d, WY + 10, t, hx("a9cfee"), alpha=0.5, amp=6, n=6, h=380)

    def draw(self, img, b, lt, t):
        v = b.v
        k = v["k"]
        if k in ("nature", "nature2"):
            img.paste(self.NIGHT)
        elif k in ("moral", "pattern", "change", "mistakes", "ask", "question", "title"):
            img.paste(self.PAPER)
        else:
            img.paste(self.DAY)
        d = D(img)
        if k == "title":
            text(d, (W / 2, 300), "The Scorpion", F("abril", 130), INK, alpha=ease(lt / 0.6))
            text(d, (W / 2, 420), "& the Frog", F("abril", 110), hx("3d7a3c"), alpha=ease((lt - 0.4) / 0.6))
            frog(d, 760, 820, 220, FROG, hx("2f6b33"), t)
            scorpion(d, 1220, 820, 300, SCORP, t, flip=True, sting=0.3 + 0.2 * math.sin(t * 2))
            text(d, (W / 2, 560), "a fable about why people rarely change", F("lora", 44, 500), hx("6b5640"), alpha=ease((lt - 1.5) / 0.6))
        elif k == "bank":
            sx = 330
            if v.get("climb"):
                sx = lerp(330, 600, eio((lt - 5) / 1.5))
            fx = 640
            sy = lerp(590, WY + 5 - 60, eio((lt - 5) / 1.5)) if v.get("climb") else 590
            self.waves(d, t)
            frog(d, fx, WY + 30, 150, FROG, hx("2f6b33"), t, face="smile" if b.i != 2 else "frown")
            scorpion(d, sx, sy, 200 if not v.get("climb") or lt < 5 else lerp(200, 150, ease((lt - 5) / 1.5)), SCORP, t, flip=False, sting=0.1)
            for (x, y, s, ta, tail) in v.get("b", []):
                bubble(d, x, y, s, F("lora", 36, 600), CREAM, INK, tail=tail, alpha=ease((lt - ta) / 0.3))
        elif k in ("ride", "sink"):
            if k == "ride":
                fx = lerp(640, 960, clamp01(lt / 3.5))
                sink = 0
            else:
                fx = 960
                sink = ease(lt / max(1, b.dur)) * 200
            sting = ease((lt - 3.5) / 0.3) if v.get("sting") else (1 if k == "sink" else 0)
            fy = WY + 30 + sink
            frog(d, fx, fy, 150, FROG, hx("2f6b33"), t, face="frown" if sting > 0.5 else "smile")
            scorpion(d, fx - 10, fy - 70, 140, SCORP, t, sting=sting)
            if v.get("sting") and 3.5 < lt < 4.4:
                d.rectangle((0, 0, W, H), fill=A((255, 40, 40), 0.25 * (1 - (lt - 3.5) / 0.9)))
            d.rectangle((0, WY + 40, W, H), fill=A(hx("3f6f9a"), 0.45 if k == "sink" else 0.15))
            self.waves(d, t)
            if k == "sink":
                for i in range(8):
                    by = fy - ((t * 120 + i * 60) % 300)
                    d.ellipse((fx - 60 + i * 15 - 6, by - 6, fx - 60 + i * 15 + 6, by + 6), outline=A(CREAM, 0.7), width=2)
            for (x, y, s, ta, tail) in v.get("b", []):
                bubble(d, x, y, s, F("lora", 36, 600), CREAM, INK, tail=tail, alpha=ease((lt - ta) / 0.3))
        elif k == "nature":
            scorpion(d, W / 2 + 120, 700, 520, hx("1a0f0b"), t, sting=0.6 + 0.1 * math.sin(t * 2))
            text(d, (W / 2, 250), "“It's my nature.”", F("abril", 110), GOLD, alpha=ease((lt - 2.2) / 0.8))
        elif k == "nature2":
            frog(d, W / 2, 760, 260, hx("4b7d4a"), hx("234d28"), t, face="frown")
            text(d, (W / 2, 280), "It sounded so reasonable.", F("abril", 90), GOLD, alpha=ease((lt - 3) / 0.8))
        elif k == "moral":
            text(d, (W / 2, 180), "THE MORAL", F("abril", 64), hx("8a5a2a"), alpha=ease(lt / 0.5))
            para(d, W / 2, 420, "We keep meeting scorpions with perfect reasons.", F("lora", 76, 700), INK, 1400, alpha=ease((lt - 1) / 0.6))
            for i in range(3):
                scorpion(d, 600 + i * 360, 800, 160, SCORP, t + i, flip=i % 2 == 1, sting=0.2)
        elif k == "pattern":
            text(d, (W / 2, 220), "Past behavior", F("abril", 100), INK, alpha=ease(lt / 0.5))
            text(d, (W / 2, 340), "predicts future behavior.", F("lora", 70, 700), hx("8a5a2a"), alpha=ease((lt - 1) / 0.5))
            for i, (w_, ta, crossed) in enumerate((("promises", 6.0, True), ("explanations", 7.0, True), ("PATTERNS", 8.2, False))):
                aa = ease((lt - ta) / 0.4)
                x = 520 + i * 440
                text(d, (x, 620), w_, F("abril" if not crossed else "lora", 72 if not crossed else 60, 700), hx("3d7a3c") if not crossed else hx("8a7a60"),
                     alpha=aa)
                if crossed:
                    line_prog(d, (x - 170, 620), (x + 170, 620), ease((lt - ta - 0.4) / 0.4), hx("b33a2a"), 6)
        elif k == "change":
            text(d, (W / 2, 200), "Can people change?", F("abril", 90), INK, alpha=ease(lt / 0.5))
            pts = [(300 + i * 26, 700 - 260 * (1 - math.exp(-i / 22)) - 12 * math.sin(i / 3)) for i in range(51)]
            n = int(51 * ease((lt - 3) / 5)) + 1
            d.line([(300, 760), (1620, 760)], fill=A(INK, 0.6), width=3)
            text(d, (1620, 800), "years", F("lora", 34), INK, "rm")
            if n > 1:
                d.line(pts[:n], fill=A(hx("3d7a3c"), 1), width=8)
            text(d, (W / 2, 880), "Yes — slowly, by their own choice.", F("lora", 52, 700), hx("8a5a2a"), alpha=ease((lt - 7) / 0.5))
            text(d, (W / 2, 300), "Roberts et al., Psychological Bulletin (2017)", F("lora", 30), hx("8a7a60"), alpha=ease((lt - 4) / 0.5))
        elif k == "mistakes":
            text(d, (W / 2, 180), "The frog's three mistakes", F("abril", 80), INK, alpha=ease(lt / 0.5))
            for i, (s, ta) in enumerate((("Logic over history", 3.0), ("Words over record", 5.5), ("“I'll be the exception”", 8.5))):
                aa = ease((lt - ta) / 0.4)
                y = 380 + i * 170
                d.ellipse((470, y - 50, 570, y + 50), fill=A(hx("3d7a3c"), aa))
                text(d, (520, y), str(i + 1), F("abril", 60), CREAM, alpha=aa)
                text(d, (620, y), s, F("lora", 66, 700), INK, "lm", alpha=aa)
        elif k == "ask":
            text(d, (W / 2, 300), "Before you carry anyone across your river, ask:", F("lora", 52, 600), hx("6b5640"), alpha=ease(lt / 0.5))
            para(d, W / 2, 480, "“What have they done to people just like me?”", F("abril", 88), INK, 1500, alpha=ease((lt - 3) / 0.6))
            text(d, (W / 2, 700), "If the answer stings — believe it.", F("lora", 60, 700), hx("b33a2a"), alpha=ease((lt - 7) / 0.6))
        elif k == "question":
            a = ease(lt / 0.5)
            scorpion(d, 380, 900, 220, SCORP, t, sting=0.3)
            frog(d, 1560, 900, 180, FROG, hx("2f6b33"), t)
            text(d, (W / 2, 320), "Have you ever carried a scorpion?", F("abril", 90), INK, alpha=a)
            text(d, (W / 2, 460), "What did they say to convince you?", F("lora", 60, 700), hx("8a5a2a"), alpha=ease((lt - 1.5) / 0.5))
            text(d, (W / 2, 590), "Tell me in the comments.", F("lora", 48, 500), hx("6b5640"), alpha=ease((lt - 3) / 0.5))

    def show_cap(self, b):
        return b.v["k"] not in ("question", "title")
