from engine import *
from reel_lib import *

TITLE = "Reel 1 - The Son Who Paid a Stranger to Visit His Mother"
OUTDIR = os.path.join(ROOT, "out_reels")
VOICES = {"n": ("af_heart", 0.8)}  # series narrator: same voice for all 5 reels
GAP = 0.9
LEAD = 0.15
END_HOLD = 0.0
CAP_WORDS = 4
MUSIC = dict(kind="pad+piano", root=110.0, prog=[0, -4, 3, -2], qual=["m", "M", "M", "M"], bar=6, step=0.75, pat=[0, 1, 2, 3, 2, 1], vol=0.11)

NARRATION = """Every Sunday, Mrs. Rose waited by the window.
Her son Daniel lived overseas. He could not visit — but he did what he thought was the next best thing.
He paid a neighbor, Miss Claire, fifty dollars a week to sit with his mother, bring her flowers, and report back.
For two years, the reports came: 'Your mother is fine. She smiled today.'
Then one Sunday, the phone rang. Mrs. Rose was gone.
At the funeral, Daniel pressed an envelope into Miss Claire's hand — the last payment.
She refused it, in tears.
'I never took your money,' she said. 'Not once. I visited your mother because my own son lives ten minutes away… and he never comes.'
Daniel understood too late: some things can be bought. A mother's last Sundays are not one of them.
Moral of the story: presence cannot be outsourced."""

SCENES = ["window", "abroad", "arrive", "visits", "phone", "envelope", "refuse", "confess", "breakdown", "moral"]
BEATS = [dict(say=line, v=dict(k=k)) for line, k in zip(NARRATION.split("\n"), SCENES)]
BEATS[0]["sfx"] = [("hit", 0.0, 0.35)]
BEATS[4]["sfx"] = [("tick", 0.9, 0.5), ("tick", 1.3, 0.5)]
BEATS[-1]["gap"] = 1.0
BEATS.append(dict(say="", v=dict(k="end"), gap=2.3))

ROSE = dict(skin=SKIN["fair"], hair=hx("dcd6cc"), hair_style="bun", top=hx("9a83b3"), bottom=hx("5b4a60"), skirt=True, leg=hx("e9cbb4"),
            shoes=hx("4a3428"), glasses=True, age=78, collar=hx("f3eee6"))
CLAIRE = dict(skin=SKIN["tan"], hair=hx("5a3a26"), hair_style="bob", top=hx("4f7a5a"), bottom=hx("3d3a40"), shoes=hx("2e2420"), age=52)
DANIEL = dict(skin=SKIN["light"], hair=hx("2a1d16"), hair_style="short", top=hx("2c3a52"), bottom=hx("22262e"), shoes=hx("1c1a1a"), age=32,
              collar=hx("e8e8e8"))
GY = 1380


def armchair(d, x, gy, s, col):
    dk = mixc(col, (0, 0, 0), 0.25)
    d.rounded_rectangle((x - s * 0.55, gy - s * 1.15, x + s * 0.55, gy - s * 0.35), radius=s * 0.18, fill=A(dk, 1))
    d.rounded_rectangle((x - s * 0.62, gy - s * 0.55, x + s * 0.62, gy - s * 0.25), radius=s * 0.1, fill=A(col, 1))
    for k in (-1, 1):
        d.rounded_rectangle((x + k * s * 0.62 - s * 0.14, gy - s * 0.75, x + k * s * 0.62 + s * 0.14, gy - s * 0.25), radius=s * 0.08, fill=A(col, 1))
        d.rectangle((x + k * s * 0.5 - 8, gy - s * 0.25, x + k * s * 0.5 + 8, gy), fill=A(hx("4a3020"), 1))


class Style(ReelStyle):
    xfade = 0.35
    HOOK = "HE PAID A STRANGER TO VISIT HIS OWN MOTHER"
    KEYWORD = 'TYPE "MAMA"'

    def setup(self):
        # --- home: warm golden small-town living room
        home = gradient(hx("f2dcb6"), hx("d9ae80"))
        d = D(home)
        d.rectangle((0, 1050, W, GY), fill=A(hx("c99a6e"), 0.35))
        d.rectangle((0, GY, W, H), fill=A(hx("8a5a3a"), 1))
        for y in range(GY, H, 46):
            d.line([(0, y), (W, y)], fill=A(hx("6e4428"), 0.5), width=3)
        wx0, wy0, wx1, wy1 = 70, 330, 470, 1010
        sky = gradient(hx("fff1cf"), hx("ffcf8a"), w=wx1 - wx0, h=wy1 - wy0)
        home.paste(sky, (wx0, wy0))
        d = D(home)
        d.ellipse((150, 520, 330, 700), fill=A((255, 250, 225), 0.8))
        d.rectangle((wx0, 760, wx1, wy1), fill=A(hx("9fbf7a"), 0.7))
        for xx in range(wx0 + 20, wx1, 70):
            d.ellipse((xx - 40, 700, xx + 50, 800), fill=A(hx("7da35a"), 0.8))
        d.rectangle((wx0, wy0, wx1, wy1), outline=A(hx("f7efe2"), 1), width=22)
        d.line([((wx0 + wx1) / 2, wy0), ((wx0 + wx1) / 2, wy1)], fill=A(hx("f7efe2"), 1), width=14)
        d.line([(wx0, (wy0 + wy1) / 2), (wx1, (wy0 + wy1) / 2)], fill=A(hx("f7efe2"), 1), width=14)
        for cx in (wx0 - 30, wx1 + 10):
            d.rounded_rectangle((cx - 10, wy0 - 40, cx + 70, wy1 + 90), radius=30, fill=A(hx("a2453a"), 1))
        d.rectangle((wx0 - 70, wy0 - 52, wx1 + 110, wy0 - 38), fill=A(hx("5a3a24"), 1))
        d.polygon([(wx0 + 30, wy0 + 40), (wx1, wy0 + 40), (W + 200, GY + 300), (380, GY + 300)], fill=A((255, 236, 190), 0.16))
        d.rectangle((640, 420, 880, 640), fill=A(hx("7a5236"), 1))
        d.rectangle((660, 440, 860, 620), fill=A(hx("e9d6b8"), 1))
        d.ellipse((720, 470, 800, 550), fill=A(hx("c9a883"), 1))
        d.chord((690, 530, 830, 640), 180, 360, fill=A(hx("c9a883"), 1))
        self.HOME = vignette(light_grade(texture(home, 4, 2)), 0.45)
        # --- overseas apartment at dusk
        ap = gradient(hx("3d4a63"), hx("1c2233"))
        d = D(ap)
        city_win = gradient(hx("e89a6a"), hx("2c2f55"), w=760, h=640)
        city_win = Image.fromarray(np.asarray(city_win)[::-1].copy())
        ap.paste(city_win, (160, 300))
        d = D(ap)
        city(d, 940, hx("151827"), seed=6, h=(120, 420), win=hx("ffd27a"))
        d.rectangle((0, 940, 160, H), fill=A(hx("2a3146"), 1))
        d.rectangle((920, 300, W, H), fill=A(hx("2a3146"), 1))
        d.rectangle((160, 300, 920, 940), outline=A(hx("12151f"), 1), width=16)
        d.rectangle((0, GY, W, H), fill=A(hx("1a1e2b"), 1))
        d.polygon([(820, 520), (900, 520), (940, 600), (780, 600)], fill=A(hx("f5c87a"), 1))
        d.line([(860, 600), (860, GY)], fill=A(hx("0e1018"), 1), width=8)
        d.ellipse((620, 480, 1080, 760), fill=A((255, 200, 120), 0.07))
        self.AP = vignette(ap, 0.5)
        # --- funeral: soft overcast, warm-grey
        fu = gradient(hx("d8cfc2"), hx("b9b0a6"))
        d = D(fu)
        for i in range(9):
            x = i * 140 - 40
            d.ellipse((x - 120, 880, x + 140, 1180), fill=A(hx("6f7d62"), 0.85))
        d.rectangle((0, 1080, W, H), fill=A(hx("7c8c63"), 1))
        rnd = random.Random(3)
        for i in range(7):
            x = rnd.uniform(40, W - 40)
            y = rnd.uniform(1090, 1180)
            d.rounded_rectangle((x - 34, y - 70, x + 34, y + 20), radius=26, fill=A(hx("a4a39e"), 1))
        for i in range(5):
            x = 80 + i * 70
            d.ellipse((x - 26, 960, x + 26, 1010), fill=A(hx("2a2828"), 0.55))
            d.rounded_rectangle((x - 40, 1000, x + 40, 1120), radius=24, fill=A(hx("2a2828"), 0.55))
        d.ellipse((780, 1010, 1000, 1130), fill=A(hx("5d7a4a"), 1))
        for i in range(10):
            a = i / 10 * 2 * math.pi
            d.ellipse((890 + math.cos(a) * 90 - 18, 1070 + math.sin(a) * 45 - 18, 890 + math.cos(a) * 90 + 18, 1070 + math.sin(a) * 45 + 18),
                      fill=A(rnd.choice([hx("ffffff"), hx("f2c8d4"), hx("f7e3a0")]), 1))
        self.FU = vignette(light_grade(texture(fu, 4, 2), strength=0.06), 0.45)
        self.BG = self.HOME
        self.dust = [(random.Random(i).uniform(120, 900), random.Random(i + 50).uniform(400, 1300)) for i in range(40)]

    def bg(self, t):
        return self.HOME.copy()

    def motes(self, d, t):
        for i, (x, y) in enumerate(self.dust):
            yy = y + math.sin(t * 0.4 + i) * 20 - (t * 6) % 40
            xx = x + math.cos(t * 0.3 + i * 2) * 14
            d.ellipse((xx - 2.5, yy - 2.5, xx + 2.5, yy + 2.5), fill=A((255, 245, 210), 0.35 + 0.25 * math.sin(t + i)))

    def draw(self, img, b, lt, t):
        k = b.v["k"]
        if k == "end":
            self.end_frame(img, lt)
            return
        bgk = {"abroad": "AP", "phone": "AP", "envelope": "FU", "refuse": "FU", "confess": "FU", "breakdown": "FU"}.get(k, "HOME")
        img.paste(getattr(self, bgk))
        d = D(img)
        prog = lt / max(1.0, b.dur)
        if k == "window":
            person(d, 650, GY, 904, ROSE, "window", t, facing=-1, eyes="open", mouth="soft")
            self.motes(d, t)
        elif k == "abroad":
            hd = person(d, 620, GY, 951, DANIEL, "hold", t, facing=1, eyes="sad", mouth="soft")
            px, py = (hd["lhand"][0] + hd["rhand"][0]) / 2, (hd["lhand"][1] + hd["rhand"][1]) / 2 - 30
            d.rounded_rectangle((px - 32, py - 55, px + 32, py + 55), radius=10, fill=A(hx("0f0f12"), 1))
            d.rounded_rectangle((px - 26, py - 47, px + 26, py + 47), radius=6, fill=A(hx("9fc3ff"), 0.9))
        elif k == "arrive":
            armchair(d, 330, GY, 380, hx("b8695a"))
            person(d, 360, GY, 812, ROSE, "sit", t, facing=1, eyes="open", mouth="smile" if prog > 0.3 else "soft")
            cx = lerp(1150, 790, eio(lt / 2.5))
            hd = person(d, cx, GY, 904, CLAIRE, "flowers" if lt > 2.5 else "stand", t, facing=-1, eyes="open", mouth="smile")
            if lt > 2.5:
                bouquet(d, hd["rhand"][0], hd["rhand"][1] - 20, 120, t)
            self.motes(d, t)
        elif k == "visits":
            armchair(d, 330, GY, 380, hx("b8695a"))
            person(d, 360, GY, 812, ROSE, "sit_talk", t, facing=1, eyes="open", mouth="talk" if int(lt / 1.6) % 2 == 0 else "smile")
            person(d, 790, GY, 812, CLAIRE, "sit", t, facing=-1, eyes="open", mouth="smile" if int(lt / 1.6) % 2 == 0 else "talk")
            bouquet(d, 570, 1110, 120, t)
            self.motes(d, t)
        elif k == "phone":
            fell = lt > 1.9
            hd = person(d, 560, GY, 974, DANIEL, "phone", t, facing=1, eyes="sad" if fell else "open", mouth="open" if fell else "soft", tears=ease((lt - 2.8) / 1.5))
            px, py = hd["rhand"]
            d.rounded_rectangle((px - 18, py - 60, px + 18, py + 20), radius=8, fill=A(hx("0f0f12"), 1))
            if lt < 1.8:
                for i in range(3):
                    rr = 40 + ((lt * 120 + i * 40) % 120)
                    d.arc((px - rr, py - 20 - rr, px + rr, py - 20 + rr), -60, 60, fill=A((255, 240, 200), 0.5 * (1 - rr / 160)), width=4)
        elif k == "envelope":
            hd = person(d, 300, GY, 951, DANIEL, "give", t, facing=1, eyes="sad", mouth="sad")
            person(d, 850, GY, 904, CLAIRE, "stand", t, facing=-1, eyes="sad", mouth="sad")
            envelope(d, hd["rhand"][0] + 30, hd["rhand"][1] - 10, 100)
        elif k == "refuse":
            hd = person(d, 300, GY, 951, DANIEL, "give", t, facing=1, eyes="sad", mouth="soft")
            person(d, 850, GY, 904, CLAIRE, "refuse", t, facing=-1, eyes="sad", mouth="sad", tears=ease((lt - 0.3) / 1.0))
            envelope(d, hd["rhand"][0] + 30, hd["rhand"][1] - 10, 100)
        elif k == "confess":
            person(d, 360, GY, 951, DANIEL, "stand", t, facing=1, eyes="open", mouth="open")
            person(d, 790, GY, 904, CLAIRE, "talk", t, facing=-1, eyes="sad", mouth="talk" if lt < b.dur else "sad", tears=1.0)
        elif k == "breakdown":
            person(d, 360, GY, 951, DANIEL, "hands_face" if prog > 0.15 else "stand", t, facing=1, eyes="closed", mouth="sad", tears=1.0)
            person(d, 800, GY, 904, CLAIRE, "hold", t, facing=-1, eyes="sad", mouth="sad", tears=1.0)
        elif k == "moral":
            armchair(d, 600, GY, 420, hx("b8695a"))
            bouquet(d, 900, 1230, 130, t)
            d.rectangle((850, 1260, 950, GY), fill=A(hx("6e4a30"), 1))
            self.motes(d, t)
            d.rectangle((0, 0, W, H), fill=(255, 230, 190, int(40 * ease(lt / 3))))
