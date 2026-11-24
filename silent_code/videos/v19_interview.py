from engine import *

TITLE = "A Psychologist Explains Why They Always Come Back"
VOICES = {"i": ("af_kore", 0.9), "e": ("bf_alice", 0.88)}
GAP = 0.5
CAP_WORDS = 6
MUSIC = dict(kind="pad+hats", root=110.0, prog=[0, -4, -2, 3], qual=["m", "M", "M", "M"], bar=8, bpm=70, vol=0.06)


def Iv(say, shot="ci", **kw):
    return dict(say=say, who="i", v=dict(shot=shot, **kw))


def Ex(say, shot="ce", key=None, **kw):
    return dict(say=say, who="e", v=dict(shot=shot, key=key, **kw))


BEATS = [
    Iv("They left. They swore they were done. And then, months later, a message: hey, I've been thinking about you. Why do they always come back?", "wide", hook=True,
       sfx=[("boom", 0, 0.5)]),
    Ex("Because for some people, leaving was never the end. It was a pause. When someone keeps returning to a relationship they damaged, it's usually not about love. It's about what the relationship gives them.", "wide"),
    Iv("What does it give them?"),
    Ex("Attention. Validation. A sense of control. Some psychologists call it supply. You were a reliable source of it. When their new sources run dry, they come back to check whether yours is still open.", key="SUPPLY"),
    Iv("There's a name for this, isn't there?"),
    Ex("Hoovering. Like the vacuum cleaner: an attempt to suck you back in. It tends to happen at predictable moments. Your birthday. The holidays. When their new relationship fails. And very often, right when you've started to heal.", key="HOOVERING",
       when=["your birthday", "the holidays", "their new relationship fails", "you start to heal"]),
    Iv("Why right then?"),
    Ex("Because they sense they're losing access. Your healing feels like rejection to them. So the message arrives. I miss you. I've changed. Do you remember that trip?", key="LOSING ACCESS",
       texts=["I miss you.", "I've changed.", "remember that trip?"]),
    Iv("And why is it so hard to ignore?", "wide"),
    Ex("Because of how the relationship was built. Hot and cold treatment creates intermittent reinforcement, the most habit-forming reward pattern we know. Your brain learned to crave the good moments precisely because they were unpredictable. One message can light that circuit up again.",
       key="INTERMITTENT REINFORCEMENT"),
    Iv("So what should someone do when that message arrives?"),
    Ex("First, don't reply in the moment. Second, ask one question: what has actually changed, and how would I know? Not words. Actions, over time. Real change shows up as accountability, consistency, and respect for your boundaries, including your no.",
       key="ACTIONS OVER TIME", steps=["don't reply in the moment", "what has actually changed?", "accountability · consistency · respect"]),
    Iv("Do people ever come back for good reasons?"),
    Ex("Sometimes, yes. And they're easy to recognize. They don't pressure you. They name what they did, without excuses. And they're willing to wait. A hoover wants an answer tonight.", key="PATIENCE vs URGENCY"),
    Iv("That's a powerful distinction.", "wide"),
    Ex("If they come back with urgency, it's for them. If they come back with patience, it might be for you.", "wide", gap=0.9),
    Iv("Has someone come back into your life just as you'd started to heal? What did they say? Share your story in the comments.", "wide", q=True,
       sfx=[("ding", 0.3, 0.5)]),
]

TEAL = hx("35c2b8")
NAVY = hx("0d1826")
WHITE = (240, 244, 248)
CHAR = {
    "i": dict(skin=hx("c98f6a"), shirt=hx("b8323f"), hair=hx("2a1a14"), style="long", name="Maya Collins", role="Host, Mind Matters"),
    "e": dict(skin=hx("f0c9a8"), shirt=hx("2f6f73"), hair=hx("9a9aa0"), style="bun", name="Dr. Ruth Alder", role="Clinical psychologist (dramatized)"),
}


def bust(d, cx, by, s, c, t, talking, facing=1):
    sk, sh, hr = c["skin"], c["shirt"], c["hair"]
    hx0 = cx + facing * s * 0.04
    hy = by - s * 0.98
    if c["style"] == "long":
        d.rounded_rectangle((hx0 - s * 0.31, hy - s * 0.3, hx0 + s * 0.31, hy + s * 0.42), radius=s * 0.25, fill=A(hr, 1))
    d.chord((cx - s * 0.62, by - s * 0.62, cx + s * 0.62, by + s * 0.7), 180, 360, fill=A(sh, 1))
    d.rectangle((cx - s * 0.62, by - s * 0.02, cx + s * 0.62, by + s * 0.5), fill=A(sh, 1))
    d.polygon([(cx - s * 0.16, by - s * 0.56), (cx + s * 0.16, by - s * 0.56), (cx, by - s * 0.3)], fill=A((245, 245, 245), 1))
    d.rectangle((cx - s * 0.09, by - s * 0.72, cx + s * 0.09, by - s * 0.52), fill=A(sk, 1))
    d.ellipse((hx0 - s * 0.24, hy - s * 0.3, hx0 + s * 0.24, hy + s * 0.3), fill=A(sk, 1))
    if c["style"] == "long":
        d.chord((hx0 - s * 0.26, hy - s * 0.33, hx0 + s * 0.26, hy + s * 0.05), 180, 360, fill=A(hr, 1))
        d.polygon([(hx0 - s * 0.26, hy - s * 0.12), (hx0 + facing * s * 0.05, hy - s * 0.3), (hx0 - s * 0.05, hy - s * 0.12)], fill=A(hr, 1))
    else:
        d.chord((hx0 - s * 0.25, hy - s * 0.32, hx0 + s * 0.25, hy + 0.0 * s), 180, 360, fill=A(hr, 1))
        d.ellipse((hx0 - facing * s * 0.2 - s * 0.13, hy - s * 0.42, hx0 - facing * s * 0.2 + s * 0.13, hy - s * 0.16), fill=A(hr, 1))
    ex = hx0 + facing * s * 0.05
    ey = hy - s * 0.02
    blink = (t % 4.1) < 0.12
    for k in (-1, 1):
        x = ex + k * s * 0.09
        if blink:
            d.line([(x - s * 0.025, ey), (x + s * 0.025, ey)], fill=A((30, 20, 20), 1), width=max(2, int(s * 0.012)))
        else:
            d.ellipse((x - s * 0.022, ey - s * 0.026, x + s * 0.022, ey + s * 0.026), fill=A((30, 20, 20), 1))
        if c["style"] == "bun":
            d.ellipse((x - s * 0.06, ey - s * 0.05, x + s * 0.06, ey + s * 0.05), outline=A((40, 40, 50), 1), width=max(2, int(s * 0.012)))
    if c["style"] == "bun":
        d.line([(ex - s * 0.03, ey), (ex + s * 0.03, ey)], fill=A((40, 40, 50), 1), width=max(2, int(s * 0.012)))
    mo = s * (0.012 + (0.035 * abs(math.sin(t * 12) * math.sin(t * 5.3)) if talking else 0))
    my = hy + s * 0.14
    d.ellipse((ex - s * 0.06, my - mo, ex + s * 0.06, my + mo), fill=A((110, 40, 40), 1))
    d.arc((ex - s * 0.07, my - s * 0.04, ex + s * 0.07, my + s * 0.03), 20, 160, fill=A((90, 50, 40), 0.6), width=max(1, int(s * 0.008)))


class Style(Base):
    cap = dict(font="Inter", size=44, w=600, y=1010, fill=WHITE, hl=TEAL, bar=(5, 10, 18, 215), maxw=1500, barr=4)
    xfade = 0

    def setup(self):
        st = gradient(hx("12233a"), hx("070d16"))
        d = D(st)
        rnd = random.Random(8)
        for i in range(36):
            x, y, r = rnd.uniform(0, W), rnd.uniform(60, 600), rnd.uniform(14, 46)
            c = rnd.choice([hx("ffb86b"), TEAL, hx("6aa8ff"), (255, 255, 255)])
            d.ellipse((x - r, y - r, x + r, y + r), fill=A(c, rnd.uniform(0.12, 0.35)))
        st = st.filter(ImageFilter.GaussianBlur(6))
        d = D(st)
        rrect(d, (560, 150, 1360, 600), 10, fill=A(hx("0b1522"), 1), outline=A(hx("23384f"), 1), width=6)
        text(d, (960, 340), "MIND", F("montserrat", 110, 900), TEAL)
        text(d, (960, 450), "MATTERS", F("montserrat", 70, 300), WHITE)
        d.rectangle((0, 760, W, H), fill=A(hx("0a121d"), 1))
        d.ellipse((260, 720, 1660, 820), fill=A(hx("16263a"), 1))
        self.STUDIO = st
        self.BLUR = st.filter(ImageFilter.GaussianBlur(18))
        self.BLUR = Image.fromarray((np.asarray(self.BLUR).astype(np.float32) * 0.8).astype(np.uint8))
        self.BG = st
        self.first = {}
        for b in self.beats:
            self.first.setdefault(b.who, b.i)

    def bg(self, t):
        return self.STUDIO.copy()

    def wide(self, img, b, lt, t):
        img.paste(self.STUDIO)
        d = D(img)
        for x, who, fac in ((620, "i", 1), (1300, "e", -1)):
            d.rounded_rectangle((x - 130, 640, x + 130, 840), radius=30, fill=A(hx("3a2f2a"), 1))
            bust(d, x, 760, 260, CHAR[who], t + (0 if who == "i" else 1.3), b.who == who and lt < b.dur, facing=fac)
        d.polygon([(760, 820), (1160, 820), (1120, 880), (800, 880)], fill=A(hx("2b2622"), 1))
        d.rectangle((800, 880, 1120, 1000), fill=A(hx("1f1b18"), 1))
        for x in (870, 1050):
            d.line([(x, 820), (x + (20 if x < 960 else -20), 740)], fill=A((30, 30, 30), 1), width=6)
            d.ellipse((x + (20 if x < 960 else -20) - 12, 720, x + (20 if x < 960 else -20) + 12, 750), fill=A((40, 40, 40), 1))

    def close(self, img, b, lt, t, who):
        img.paste(self.BLUR)
        d = D(img)
        if who == "e":
            bust(d, 640, 1000, 620, CHAR["e"], t + 1.3, lt < b.dur, facing=1)
        else:
            bust(d, 1280, 1000, 620, CHAR["i"], t, lt < b.dur, facing=-1)
        return d

    def draw(self, img, b, lt, t):
        v = b.v
        shot = v["shot"]
        if shot == "wide":
            self.wide(img, b, lt, t)
            d = D(img)
        else:
            d = self.close(img, b, lt, t, "e" if shot == "ce" else "i")
        if v.get("hook"):
            a = ease(lt / 0.4) * (1 - ease((lt - 8.5) / 0.6))
            rrect(d, (360, 110, 1560, 300), 8, fill=A(NAVY, a))
            text(d, (960, 170), "WHY DO THEY ALWAYS", F("montserrat", 54, 800), WHITE, alpha=a)
            text(d, (960, 245), "COME BACK?", F("montserrat", 72, 900), TEAL, alpha=a)
        if v.get("key"):
            a = ease((lt - 0.8) / 0.4)
            x0 = 1150
            d.rectangle((x0, 220, x0 + 12, 300), fill=A(TEAL, a))
            text(d, (x0 + 36, 260), v["key"], F("montserrat", 46 if len(v["key"]) < 20 else 36, 900), WHITE, "lm", alpha=a)
            y = 360
            for key, items in (("when", v.get("when")), ("texts", v.get("texts")), ("steps", v.get("steps"))):
                if not items:
                    continue
                for j, s in enumerate(items):
                    ta = b.dur * (0.3 + 0.6 * j / len(items))
                    aa = ease((lt - ta) / 0.4)
                    if key == "texts":
                        bubble(d, x0 + 250, y + j * 120, s, F("Inter", 34, 600), hx("e9eef3"), NAVY, tail=(-1, 1), alpha=aa)
                    else:
                        rrect(d, (x0, y + j * 90 - 32, x0 + 640, y + j * 90 + 32), 6, fill=A(NAVY, 0.85 * aa))
                        text(d, (x0 + 24, y + j * 90), s, F("Inter", 32, 600), WHITE, "lm", alpha=aa)
        if self.first.get(b.who) == b.i:
            c = CHAR[b.who]
            lower_third(d, 80, 820, c["name"], c["role"], F("montserrat", 38, 800), F("Inter", 26, 500), NAVY, hx("1d3550"), TEAL,
                        x_in=(lt - 0.5) / 0.6 if lt < 6 else 1 - (lt - 6) / 0.6)
        if v.get("q"):
            a = ease(lt / 0.5)
            rrect(d, (300, 140, 1620, 560), 10, fill=A(NAVY, 0.92 * a), outline=A(TEAL, a), width=3)
            text(d, (960, 210), "TELL US", F("montserrat", 40, 900), TEAL, alpha=a)
            para(d, 960, 360, "Has someone come back just as you'd started to heal? What did they say?", F("montserrat", 54, 800), WHITE, 1150, alpha=a)
            text(d, (960, 500), "share your story in the comments", F("Inter", 34, 500), (180, 200, 220), alpha=ease((lt - 1.5) / 0.4))
        text(d, (W - 60, 60), "LIVE · DRAMATIZED INTERVIEW", F("montserrat", 20, 700), (170, 185, 200), "rm")
        d.ellipse((W - 440, 52, W - 424, 68), fill=A(hx("ff4d4d"), 1 if int(t * 1.5) % 2 == 0 else 0.3))
