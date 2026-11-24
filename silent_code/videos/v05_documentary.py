from engine import *

TITLE = "The Psychology of Revenge - Why It Never Heals You"
VOICES = {"n": ("am_onyx", 0.84)}
GAP = 0.95
CRF = 23
MUSIC = dict(kind="drone+pad", root=73.4, prog=[0, 1, -2, 0], qual=["m", "M", "m", "m"], bar=10, vol=0.16, nzcut=250)

BEATS = [
    dict(say="In 2008, researchers gave ordinary people the chance to take revenge. The ones who took it felt worse. And they never saw it coming.",
         v=dict(k="dark"), sfx=[("boom", 0, 0.9)], gap=0.9),
    dict(say="This is the psychology of revenge, and why it never heals you.",
         v=dict(k="title"), gap=1.0),
    dict(say="Revenge feels like justice. When someone wounds us, the brain processes social pain in some of the same regions as physical pain. And something ancient wakes up: the urge to restore the balance.",
         v=dict(k="city", ch="I · The Hunger")),
    dict(say="In a 2004 study published in the journal Science, researchers scanned people's brains as they decided to punish someone who had betrayed their trust. A reward area, the dorsal striatum, lit up. Revenge, it turns out, is anticipated like a prize.",
         v=dict(k="neural")),
    dict(say="But anticipation is the trap. The pleasure lives in the planning. Not in the act.",
         v=dict(k="neural", dim=True)),
    dict(say="Psychologists Kevin Carlsmith, Timothy Wilson and Daniel Gilbert designed a group game in which one player betrayed everyone. Some participants were allowed to punish the betrayer. Others were not.",
         v=dict(k="circle", ch="II · The Experiment")),
    dict(say="The punishers predicted they would feel better. They felt worse. They kept thinking about the betrayer, while those who could not punish moved on faster.",
         v=dict(k="loop")),
    dict(say="This is revenge's hidden cost: rumination. By striking back, you keep the wound open. You stay emotionally tied to the person who hurt you, replaying them, giving them rent-free space in your mind.",
         v=dict(k="chain")),
    dict(say="And revenge rarely ends. The other side almost never sees your strike as fair. They see a new injury, and the cycle repeats. Feuds have lasted generations on exactly this logic.",
         v=dict(k="mirror")),
    dict(say="So what actually heals? Not forgetting. Not even, necessarily, forgiving. Healing comes from a closure you create yourself.",
         v=dict(k="road", ch="III · The Way Out")),
    dict(say="Name what happened, clearly and honestly. Set the boundary that stops it from happening again. Then pour the energy revenge would have consumed into building a life that person has no part in.",
         v=dict(k="steps")),
    dict(say="The old saying gets one thing wrong. The best revenge isn't living well to prove a point. It's living well, and no longer caring whether they see it.",
         v=dict(k="sunrise")),
    dict(say="Have you ever taken revenge on someone? Did it actually make you feel better? Tell me honestly, in the comments.",
         v=dict(k="question"), sfx=[("hit", 0.2, 0.4)]),
]

BAR = 132
GOLD = hx("e8c78f")
TEAL = hx("6fa7b3")


class Style(Base):
    cap = dict(font="ebgaramond", size=44, w=500, y=1010, fill=(205, 205, 200), hl=GOLD, maxw=1600)
    xfade = 0.8

    def setup(self):
        self.grain = Grain(4)
        self.bgs = {
            "black": Image.new("RGB", (W, H), (6, 6, 8)),
            "city": vignette(gradient(hx("0d1e26"), hx("1d3a40")), 0.6),
            "neural": vignette(radial(hx("1a1410"), hx("050505"), r=900), 0.5),
            "cool": vignette(radial(hx("16232b"), hx("06090b"), r=1100), 0.6),
            "road": vignette(gradient(hx("140f22"), hx("b0603a")), 0.5),
            "sun": vignette(gradient(hx("2a2340"), hx("f0a060")), 0.4),
        }
        rnd = random.Random(5)
        self.nodes = []
        while len(self.nodes) < 70:
            x, y = rnd.uniform(-1, 1), rnd.uniform(-1, 1)
            if x * x + y * y < 1:
                self.nodes.append((W / 2 + x * 420, 520 + y * 260))
        self.edges = [(i, j) for i in range(70) for j in range(i + 1, 70)
                      if math.dist(self.nodes[i], self.nodes[j]) < 120]

    def bg(self, t):
        return self.bgs["black"].copy()

    def chapter(self, d, s, lt):
        if s:
            a = ease((lt - 0.5) / 0.8) * (1 - ease((lt - 5) / 1))
            text(d, (110, BAR + 70), s.upper(), F("cinzel", 36, 600), GOLD, "lm", alpha=a)

    def draw(self, img, b, lt, t):
        v = b.v
        k = v["k"]
        pan = lt * 6
        key = {"city": "city", "neural": "neural", "circle": "cool", "loop": "cool", "chain": "cool", "mirror": "cool",
               "road": "road", "steps": "road", "sunrise": "sun"}.get(k, "black")
        img.paste(self.bgs[key])
        d = D(img)
        if k == "dark":
            a = ease((lt - 0.3) / 1.5)
            text(d, (W / 2, 540), "2008", F("cinzel", 150, 500), (200, 200, 200), alpha=a * 0.9)
            text(d, (W / 2, 650), "an experiment in revenge", F("ebgaramond", 50), GOLD, alpha=ease((lt - 2) / 1.2))
        elif k == "title":
            s = 1 + lt * 0.01
            text(d, (W / 2, 500), "THE PSYCHOLOGY", F("cinzel", int(60 * s), 500), (190, 190, 190), alpha=ease(lt / 1.2))
            text(d, (W / 2, 610), "OF REVENGE", F("cinzel", int(140 * s), 700), GOLD, alpha=ease((lt - 0.6) / 1.2))
        elif k == "city":
            city(d, 790, hx("071014"), seed=9, h=(200, 520), win=hx("e0b070"))
            lx = 1180 - pan
            d.line([(lx, 300), (lx, 790)], fill=A(hx("0a0a0a"), 1), width=10)
            d.line([(lx, 300), (lx - 60, 300)], fill=A(hx("0a0a0a"), 1), width=8)
            d.polygon([(lx - 70, 310), (lx - 250, 790), (lx + 130, 790)], fill=A(GOLD, 0.13))
            d.ellipse((lx - 80, 300, lx - 50, 322), fill=A((255, 230, 180), 1))
            d.rectangle((0, 790, W, H), fill=A(hx("05090b"), 1))
            figure(d, lx - 70, 790, 260, "sad", (8, 8, 10), t, face=None, head_fill=(8, 8, 10), lw=12)
            rain(d, t, (180, 210, 220), n=220, alpha=0.18, speed=1300)
        elif k == "neural":
            dim = 0.35 if v.get("dim") else 1.0
            glow = ease((lt - 3.5) / 2) * dim
            for i, j in self.edges:
                d.line([self.nodes[i], self.nodes[j]], fill=A(TEAL, 0.12), width=2)
            for idx, (x, y) in enumerate(self.nodes):
                pul = 0.5 + 0.5 * math.sin(t * 2 + idx)
                r = 4 + 2 * pul
                d.ellipse((x - r, y - r, x + r, y + r), fill=A(TEAL, 0.4 + 0.4 * pul))
            cx, cy = W / 2 + 60, 540
            for k2, a2 in ((160, 0.05), (110, 0.08), (70, 0.12), (36, 0.4)):
                rr = k2 * (0.9 + 0.1 * math.sin(t * 3))
                d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=A((255, 150, 60), a2 * glow))
            a = ease((lt - 5) / 0.8) * dim
            d.line([(cx + 40, cy - 30), (cx + 360, cy - 200), (cx + 560, cy - 200)], fill=A(GOLD, a), width=2)
            text(d, (cx + 370, cy - 230), "dorsal striatum — reward", F("ebgaramond", 40), GOLD, "lm", alpha=a)
            text(d, (W - 110, H - BAR - 40), "de Quervain et al., Science (2004)", F("ebgaramond", 30), (150, 150, 150), "rm", alpha=a)
        elif k == "circle":
            for i in range(6):
                ang = math.pi + i / 5 * math.pi
                x = W / 2 + math.cos(ang) * 560 - pan
                y = 830 + math.sin(ang) * 120
                betray = i == 3
                c = hx("d05040") if betray and lt > 3 else hx("a9b9c2")
                figure(d, x, y, 240, "point_l" if betray and lt > 3 else "stand", c, t + i, face="smirk" if betray else "flat",
                       head_fill=hx("10181d"), flip=x > W / 2)
            text(d, (W - 110, H - BAR - 40), "Carlsmith, Wilson & Gilbert, J. Personality & Social Psychology (2008)", F("ebgaramond", 28),
                 (150, 150, 150), "rm", alpha=ease((lt - 2) / 1))
        elif k == "loop":
            figure(d, 760, 830, 300, "sit_sad", hx("a9b9c2"), t, face="frown", head_fill=hx("10181d"))
            chair(d, 760, 830, 300, hx("4a5a62"))
            cx, cy = 1200, 430
            for i in range(3):
                a0 = (t * 120 + i * 120) % 360
                d.arc((cx - 160, cy - 160, cx + 160, cy + 160), a0, a0 + 80, fill=A(hx("d05040"), 0.8), width=8)
            figure(d, cx, cy + 90, 150, "smirk" if False else "stand", hx("d05040"), t, face="smirk", head_fill=hx("10181d"))
            for i, (x, y) in enumerate(((930, 610), (990, 560), (1050, 520))):
                r = 10 + i * 6
                d.ellipse((x - r, y - r, x + r, y + r), outline=A(hx("a9b9c2"), 0.8), width=3)
            text(d, (520, 330), "felt worse", F("ebgaramond", 64), GOLD, alpha=ease((lt - 3.5) / 0.8))
            text(d, (520, 410), "kept replaying", F("ebgaramond", 64), GOLD, alpha=ease((lt - 6) / 0.8))
        elif k == "chain":
            x1 = 560 - pan
            x2 = 1360 + pan
            figure(d, x1, 820, 290, "sad", hx("a9b9c2"), t, face="frown", head_fill=hx("10181d"))
            figure(d, x2, 820, 290, "stand", hx("d05040"), t, face="smirk", head_fill=hx("10181d"), flip=True)
            chain(d, x1 + 40, 650, x2 - 40, 650, hx("8a8f94"), s=20, lw=5, alpha=ease((lt - 1) / 1.5))
            text(d, (W / 2, 330), "RUMINATION", F("cinzel", 90, 700), GOLD, alpha=ease((lt - 1.2) / 1))
        elif k == "mirror":
            ph = int(lt / 2.2) % 2
            for i, (x, fl, c) in enumerate(((760, False, hx("a9b9c2")), (1160, True, hx("d05040")))):
                pose = "fist" if ph == i else "sad"
                figure(d, x, 820, 290, pose, c, t, face="angry" if ph == i else "frown", head_fill=hx("10181d"), flip=fl)
            n = int(lt / 2.2) + 1
            for j in range(min(n, 12)):
                xx = 640 + j * 55
                d.line([(xx, 330), (xx - 10, 400)], fill=A(GOLD, 0.8), width=5)
            text(d, (W / 2, 260), "THE CYCLE", F("cinzel", 60, 700), GOLD, alpha=ease((lt - 0.5) / 1))
        elif k in ("road", "steps", "sunrise"):
            hzn = 600
            sun_y = hzn + 40 - (ease(lt / 8) * 120 if k == "sunrise" else 0)
            for r_, a_ in ((260, 0.06), (170, 0.1), (100, 0.6)):
                d.ellipse((W / 2 - r_, sun_y - r_, W / 2 + r_, sun_y + r_), fill=A((255, 210, 150), a_))
            d.rectangle((0, hzn, W, H), fill=A(hx("1a1020"), 1))
            d.polygon([(W / 2 - 18, hzn), (W / 2 + 18, hzn), (W / 2 + 700, H), (W / 2 - 700, H)], fill=A(hx("2e1e2a"), 1))
            for j in range(8):
                y0 = hzn + (j + (t * 0.4) % 1) ** 2 * 7
                d.line([(W / 2, y0), (W / 2, y0 + 4 + j * 2)], fill=A(GOLD, 0.6), width=3)
            prog = {"road": 0, "steps": 0.4, "sunrise": 0.75}[k] + 0.3 * clamp01(lt / max(1, b.dur))
            sc = lerp(320, 60, prog)
            figure(d, W / 2 + 40 * (1 - prog), lerp(1000, hzn + 20, prog), sc, "walk", (12, 8, 14), t, face=None, lw=max(4, int(sc * 0.05)),
                   head_fill=(12, 8, 14))
            if k == "steps":
                for i, s in enumerate(("Name it.", "Set the boundary.", "Build a life they're not part of.")):
                    ta = [0.5, 3.5, 7.0][i]
                    text(d, (130, 280 + i * 90), s, F("ebgaramond", 62), (245, 225, 200), "lm", alpha=ease((lt - ta) / 0.8))
            if k == "sunrise":
                text(d, (W / 2, 300), "Live well — and stop needing them to see it.", F("ebgaramond", 66), (255, 240, 220), alpha=ease((lt - 5) / 1.2))
        elif k == "question":
            a = ease(lt / 1.2)
            text(d, (W / 2, 420), "Have you ever taken revenge?", F("cinzel", 80, 600), (230, 230, 230), alpha=a)
            text(d, (W / 2, 530), "Did it actually make you feel better?", F("ebgaramond", 66), GOLD, alpha=ease((lt - 2.5) / 1))
            text(d, (W / 2, 650), "— tell me honestly in the comments —", F("ebgaramond", 42), (160, 160, 160), alpha=ease((lt - 4) / 1))
        self.chapter(d, v.get("ch"), lt)

    def frame(self, t):
        img = Base.frame(self, t)
        img = self.grain.apply(img, t)
        d = D(img)
        d.rectangle((0, 0, W, BAR), fill=(0, 0, 0, 255))
        d.rectangle((0, H - BAR, W, H), fill=(0, 0, 0, 255))
        if t < 1.2:
            d.rectangle((0, 0, W, H), fill=(0, 0, 0, int(255 * (1 - ease(t / 1.2)))))
        if self.cap:
            self.captions(img, t)
        return img

    def show_cap(self, b):
        return False  # captions drawn after grain/letterbox in frame()

    def captions(self, img, t):
        b = self.tl.beat_at(t)
        if b.v["k"] in ("question", "title"):
            return
        Base.captions(self, img, t)
