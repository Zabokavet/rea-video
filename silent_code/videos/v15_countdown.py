from engine import *

TITLE = "10 Sentences That End an Argument Instantly"
VOICES = {"n": ("am_liam", 0.82)}
GAP = 0.9
MUSIC = dict(kind="pulse+pad+tick", root=110.0, prog=[0, 0, 1, -1], qual=["m"], bar=4, bpm=72, tick_every=0.8333, vol=0.1)


def N(n, quote, say):
    return dict(say=say, v=dict(k="num", n=n, q=quote), sfx=[("whoosh", 0, 0.4), ("hit", 0.15, 0.5)])


BEATS = [
    dict(say="Most arguments aren't won. They're ended. And the right sentence can end one in seconds. Here are ten, counting down to the most powerful.",
         v=dict(k="hook"), sfx=[("riser", 0.5, 0.8)], gap=0.7),
    N(10, "You might be right.", "Number ten. You might be right. It costs you nothing, and it removes the fuel. People argue hardest when they feel unheard. This tells them they've been heard."),
    N(9, "Let me make sure I understand you.", "Nine. Let me make sure I understand you. Then repeat their point back. Feeling understood lowers defensiveness faster than any counterargument."),
    N(8, "What would a good outcome look like for you?", "Eight. What would a good outcome look like for you? This moves the conversation from who's right, to what's next."),
    N(7, "I need twenty minutes. Then I'll come back.", "Seven. I need twenty minutes, and then I'll come back. When your heart rate spikes, your thinking narrows. Relationship researcher John Gottman found that taking a real break when flooded prevents damage. The key is promising to return, and then actually coming back."),
    N(6, "I'm not going to argue about this.", "Six. I'm not going to argue about this. Said calmly, not coldly. Some arguments are traps. Refusing to step into one is a boundary, not a defeat."),
    N(5, "That's fair. I hadn't thought of that.", "Five. That's a fair point. I hadn't thought of that. Admitting one valid point makes you more persuasive on everything else, because you've proven you're listening."),
    N(4, "We see this differently, and that's okay.", "Four. We see this differently, and that's okay. Not every disagreement needs a winner. Sometimes the mature ending is simply agreeing to disagree."),
    N(3, "I'm sorry. I was wrong about that part.", "Three. I'm sorry. I was wrong about that part. A specific apology, with no but attached, is one of the most disarming sentences in any language."),
    N(2, "Are we arguing about this — or something else?", "Two. Are we really arguing about this, or about something else? Many fights about dishes are really about feeling unappreciated. Name the real issue, and the fake one disappears."),
    N(1, "I care about you more than I care about winning this.", "And number one. I care about you more than I care about winning this. Between people who matter to each other, this sentence changes the goal, from victory, to connection. Say it slowly. And mean it."),
    dict(say="Which of these would have saved your last argument? Or tell me the sentence that works for you. Comment below.",
         v=dict(k="question"), sfx=[("boom", 0.1, 0.6)]),
]

MAG = hx("ff2bd6")
CYN = hx("2be4ff")
YEL = hx("ffe14d")
WHITE = (245, 245, 255)
BGC = hx("07060d")


def glow_text(s, font, col, pad=80, blur=18):
    w = int(font.getlength(s)) + pad * 2
    h = int(font.size * 1.3) + pad * 2
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((w / 2, h / 2), s, font=font, fill=col + (255,), anchor="mm")
    g = im.filter(ImageFilter.GaussianBlur(blur))
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.alpha_composite(g)
    out.alpha_composite(g)
    d2 = ImageDraw.Draw(out)
    d2.text((w / 2, h / 2), s, font=font, fill=(255, 255, 255, 255), anchor="mm", stroke_width=3, stroke_fill=col + (255,))
    return out


class Style(Base):
    cap = dict(font="oswald", size=52, w=600, y=1000, fill=(235, 235, 245), hl=CYN, upper=True, maxw=1500, stroke=4, sfill=(0, 0, 0))
    xfade = 0.15

    def setup(self):
        bg = radial(hx("1a0f2e"), BGC, cy=500, r=1100)
        d = D(bg)
        for i in range(0, W, 80):
            d.line([(i, 700), (W / 2 + (i - W / 2) * 3, H)], fill=A(MAG, 0.12), width=2)
        for j in range(8):
            y = 700 + (j ** 1.8) * 6
            d.line([(0, y), (W, y)], fill=A(MAG, 0.12), width=2)
        self.BG = vignette(bg, 0.5)
        f = F("bebas", 520)
        self.nums = {n: glow_text(str(n), f, MAG if n > 1 else YEL) for n in range(1, 11)}
        self.hookimg = glow_text("10", F("bebas", 420), CYN)

    def figures(self, d, lt, t, b, x0=1250):
        calm = lt > 1.6
        p1, p2 = ("talk2", "fist") if not calm else ("stand", "stand")
        f1, f2 = ("angry", "angry") if not calm else ("smile", "smile")
        figure(d, x0, 880, 200, p1, CYN, t, face=f1, head_fill=BGC)
        figure(d, x0 + 260, 880, 200, p2, MAG, t, face=f2, head_fill=BGC, flip=True)
        if not calm:
            for i in range(3):
                ang = t * 6 + i * 2
                x = x0 + 130 + math.cos(ang) * 40
                y = 640 + math.sin(ang) * 20
                text(d, (x, y), "#!", F("bebas", 40), YEL)

    def draw(self, img, b, lt, t):
        d = D(img)
        v = b.v
        k = v["k"]
        if k == "hook":
            text(d, (W / 2, 260), "SENTENCES THAT END", F("oswald", 90, 700), WHITE, alpha=ease(lt / 0.3))
            text(d, (W / 2, 370), "AN ARGUMENT INSTANTLY", F("oswald", 90, 700), CYN, alpha=ease((lt - 0.4) / 0.3))
            s = 0.6 + 0.4 * back(lt / 0.6)
            im = self.hookimg.resize((int(self.hookimg.width * s), int(self.hookimg.height * s)))
            img.paste(im, (int(W / 2 - im.width / 2), int(700 - im.height / 2)), im)
        elif k == "num":
            n = v["n"]
            s = lerp(1.35, 1.0, ease(lt / 0.35))
            im = self.nums[n]
            if abs(s - 1) > 0.01:
                im = im.resize((int(im.width * s), int(im.height * s)))
            pulse = 1 + 0.02 * math.sin(t * 2 * math.pi * 72 / 60)
            img.paste(im, (int(430 - im.width / 2), int(470 - im.height / 2)), im)
            d = D(img)
            text(d, (430, 840), "TENSION", F("oswald", 28, 600), (160, 160, 180))
            lvl = (11 - n) / 10
            d.rectangle((230, 870, 630, 890), outline=A((120, 120, 140), 1), width=2)
            d.rectangle((233, 873, 233 + 394 * lvl * ease(lt / 0.8), 887), fill=A(mixc(CYN, MAG, lvl), 1))
            qa = ease((lt - 0.5) / 0.4)
            rrect(d, (820, 200, 1820, 560), 24, fill=A((255, 255, 255), 0.05 * qa), outline=A(CYN if n > 1 else YEL, qa), width=3)
            text(d, (860, 240), "SAY:", F("oswald", 30, 700), CYN if n > 1 else YEL, "lm", alpha=qa)
            para(d, 1320, 395, f"“{v['q']}”", F("oswald", 70 if len(v["q"]) < 40 else 60, 600), WHITE, 900, alpha=qa)
            self.figures(d, lt, t, b)
            for i in range(10):
                x = 760 + i * 110
                on = (10 - i) >= n
                d.ellipse((x - 9, 120 - 9, x + 9, 120 + 9), fill=A(MAG if (10 - i) > n else (YEL if (10 - i) == n else (60, 60, 70)), 1))
        elif k == "question":
            a = ease(lt / 0.4)
            text(d, (W / 2, 300), "WHICH ONE WOULD HAVE", F("oswald", 90, 700), WHITE, alpha=a)
            text(d, (W / 2, 410), "SAVED YOUR LAST ARGUMENT?", F("oswald", 90, 700), CYN, alpha=a)
            for i in range(10):
                aa = ease((lt - 1 - i * 0.08) / 0.2)
                x = 420 + i * 120
                rrect(d, (x - 48, 560, x + 48, 660), 12, outline=A(MAG if i else YEL, aa), width=3)
                text(d, (x, 610), str(10 - i), F("bebas", 64), WHITE, alpha=aa)
            text(d, (W / 2, 780), "COMMENT BELOW", F("oswald", 50, 700), YEL, alpha=ease((lt - 2.5) / 0.4))

    def show_cap(self, b):
        return b.v["k"] != "question"
