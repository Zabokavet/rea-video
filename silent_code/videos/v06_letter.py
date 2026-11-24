from engine import *

TITLE = "A Letter to the Man Who Was Always 'Fine'"
VOICES = {"n": ("bf_emma", 0.84)}
GAP = 0.9
MUSIC = dict(kind="piano+pad", root=110.0, prog=[0, -4, 5, -2], qual=["M", "M", "M", "m"], bar=8, step=0.8, pat=[0, 2, 3, 1, 2, 0], vol=0.14)


def P(page, say, **kw):
    return dict(say=say, v=dict(k="page", page=page, **kw), sfx=[("pen", 0.1, 0.6)])


BEATS = [
    P(0, "Dear you. The one who always says, I'm fine. I have known for years that you're not.", gap=1.0, first=True),
    P(0, "You said it at the funeral. You said it when the job ended. You said it with a smile so practiced that everyone believed you. Everyone but me."),
    P(0, "I know why you do it. Somewhere along the way, someone taught you that a strong man carries everything quietly. That needing anyone is a debt. That tears are a leak to be fixed."),
    P(0, "I remember the night your father left. You were twelve, and the next morning you made breakfast for everyone like nothing had happened. They called you mature. I think that was the day you learned to disappear behind the word fine."),
    P(1, "But I want you to know something true. Hiding a feeling doesn't make it smaller. Researchers who study emotional suppression have found it raises stress in the body, and leaves people feeling more alone, even in a full room."),
    P(1, "That is the real cost of fine. Not one big collapse, but a slow distance. From the people who love you. And from yourself."),
    P(1, "Men are less likely to ask for help, and more likely to show pain as anger, as silence, or as working until midnight. I have watched you do all three."),
    P(1, "And I know what you will say. That other people have it worse. That talking won't change anything. But pain is not a competition. It doesn't have to be the worst to deserve a voice."),
    P(2, "So here is what I'm asking. Not a speech. Not a breakdown. Just one honest sentence, to one person you trust. Today was hard. I'm not okay. I miss him. Any of those will do."),
    P(2, "And if you can't say it yet, that's alright too. Call me, and say nothing at all. I will know what it means. You have spent years being the wall everyone leans on. Let me be the wall, for once."),
    P(2, "Strength was never about carrying it alone. Real strength is letting someone see the weight, and staying anyway."),
    P(2, "You don't have to be fine with me. You never did. With love, always. Someone who sees you.", gap=1.4),
    dict(say="If you're the one who is always fine, what would you say if someone really asked how you are? Write it in the comments. Someone out there needs to read it.",
         v=dict(k="env"), sfx=[("page", 0, 0.7)]),
]

INK = hx("1f2a4a")
PAPER = hx("f2e7d0")
PX0, PY0, PX1, PY1 = 330, 40, 1590, 1045
LM = PX0 + 150
LH = 58
FS = 46


class Style(Base):
    cap = None
    xfade = 0.6

    def setup(self):
        desk = gradient(hx("3a2416"), hx("1a0f08"))
        desk = texture(desk, 14, 3, seed=4, blur=2)
        d = D(desk)
        for i in range(30):
            y = random.Random(i).uniform(0, H)
            d.line([(0, y), (W, y + random.Random(i + 9).uniform(-30, 30))], fill=A((0, 0, 0), 0.08), width=3)
        sh = Image.new("RGB", (W, H), (0, 0, 0))
        page = Image.new("RGB", (PX1 - PX0, PY1 - PY0), PAPER)
        page = texture(page, 7, 2, seed=2, blur=1)
        pd = D(page)
        for y in range(140 - PY0 + 8, PY1 - PY0 - 30, LH):
            pd.line([(40, y), (PX1 - PX0 - 40, y)], fill=A(hx("9fb6d0"), 0.45), width=2)
        pd.line([(LM - PX0 - 30, 0), (LM - PX0 - 30, PY1 - PY0)], fill=A(hx("d08080"), 0.55), width=2)
        pd.ellipse((PX1 - PX0 - 300, PY1 - PY0 - 260, PX1 - PX0 - 90, PY1 - PY0 - 50), outline=A(hx("b08a5a"), 0.25), width=10)
        desk.paste(page, (PX0, PY0))
        light = radial((255, 230, 190), (0, 0, 0), cx=W * 0.42, cy=H * 0.3, r=1500)
        arr = np.asarray(desk).astype(np.float32) * (0.55 + 0.6 * np.asarray(light).astype(np.float32) / 255)
        self.BG = vignette(Image.fromarray(arr.clip(0, 255).astype(np.uint8)), 0.55)
        self.font = F("caveat", FS, 500)
        self.layout()

    def layout(self):
        self.pos = {}
        pages = {}
        for b in self.beats:
            if b.v.get("k") == "page":
                pages.setdefault(b.v["page"], []).append(b)
        maxx = PX1 - 90
        for pg, bs in pages.items():
            y = 140
            for b in bs:
                x = LM + 50
                for w in b.words:
                    wd = self.font.getlength(w["w"])
                    if x + wd > maxx:
                        x = LM
                        y += LH
                    self.pos[id(w)] = (x, y, pg)
                    x += wd + self.font.getlength(" ")
                y += LH

    def bg(self, t):
        return self.BG.copy()

    def cross(self, b):
        p = self.beats[b.i - 1]
        return p.v.get("page") != b.v.get("page")

    def draw(self, img, b, lt, t):
        d = D(img)
        v = b.v
        if v["k"] == "page":
            pg = v["page"]
            now = b.t0 + lt
            pen = None
            for bb in self.beats:
                if bb.v.get("page") != pg:
                    continue
                for w in bb.words:
                    x, y, _ = self.pos[id(w)]
                    if now >= w["t1"]:
                        d.text((x, y), w["w"], font=self.font, fill=A(INK, 0.92), anchor="ls")
                        pen = (x + self.font.getlength(w["w"]), y)
                    elif now >= w["t0"]:
                        fr = clamp01((now - w["t0"]) / max(0.05, w["t1"] - w["t0"]))
                        part = w["w"][:max(1, int(len(w["w"]) * fr + 0.5))]
                        d.text((x, y), part, font=self.font, fill=A(INK, 0.92), anchor="ls")
                        pen = (x + self.font.getlength(part), y)
            text(d, (PX1 - 60, 72), ["I", "II", "III"][pg], F("caveat", 40), INK, "rm", alpha=0.5)
            if pen and now < b.t0 + b.dur + 0.2:
                px, py = pen[0] + 6, pen[1] - 6
                ang = math.radians(-35)
                L = 260
                ex, ey = px + math.cos(ang) * L, py + math.sin(ang) * L
                d.line([(px + 6, py - 6), (ex, ey)], fill=A(hx("111111"), 1), width=22)
                d.line([(px + 50, py - 36), (ex, ey)], fill=A(hx("2b2b33"), 1), width=26)
                d.polygon([(px, py), (px + 22, py - 6), (px + 8, py - 22)], fill=A(hx("c9a55a"), 1))
        elif v["k"] == "env":
            a = ease(lt / 0.8)
            ex0, ey0, ex1, ey1 = 460, 250, 1460, 830
            d.rectangle((ex0, ey0, ex1, ey1), fill=A(hx("e8d7b5"), a))
            d.polygon([(ex0, ey0), (ex1, ey0), ((ex0 + ex1) / 2, 560)], fill=A(hx("dcc8a2"), a), outline=A(hx("b79c70"), a))
            d.ellipse(((ex0 + ex1) / 2 - 45, 515, (ex0 + ex1) / 2 + 45, 605), fill=A(hx("8c1f22"), a))
            text(d, ((ex0 + ex1) / 2, 560), "♥" if False else "S", F("cinzel", 50, 700), hx("e8c0a0"), alpha=a)
            para(d, (ex0 + ex1) / 2, 700, "If someone really asked how you are — what would you say?", F("caveat", 58, 600), INK, 900,
                 alpha=ease((lt - 1) / 0.8), reveal=(lt - 1) / 3)
            text(d, (W / 2, 920), "Write it in the comments. Someone needs to read it.", F("caveat", 54, 500), (240, 220, 190),
                 alpha=ease((lt - 4.5) / 0.8))
