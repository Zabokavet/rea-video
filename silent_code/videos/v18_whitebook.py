from engine import *

TITLE = "10 Rules of Emotional Control"
VOICES = {"n": ("af_nicole", 1.1)}
GAP = 0.7
MUSIC = dict(kind="pad+piano", root=130.8, prog=[0, 7, 9, 5], qual=["M", "M", "m", "M"], bar=8, step=1.0, pat=[0, 2, 3, 1], vol=0.08)

NUM = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]
RULES = [
    "Name it to tame it. Putting a feeling into words, I feel angry, engages the thinking brain and quiets the alarm. Labeling an emotion is the first act of control.",
    "Give it ninety seconds. The first surge of emotion is a physical wave that rises and falls. If you don't feed it with new thoughts, it passes faster than you expect.",
    "Breathe out longer than you breathe in. A slow exhale activates the body's calming system and lowers your heart rate within a few breaths.",
    "Never decide while flooded. Choices made in rage or panic are the ones we regret most. Sleep on it. Morning has better judgment.",
    "Separate the feeling from the fact. I feel rejected is real. I am unwanted is a story. Question the story before you believe it.",
    "Don't argue by text. Without a voice or a face, the brain fills every gap with the worst possible meaning.",
    "Move your body. A ten minute walk burns off stress chemistry and shifts your mood more reliably than thinking harder.",
    "Expect your triggers. Know the people and moments that set you off, and decide your response before you're in the room.",
    "Silence is a response too. Not every provocation deserves your energy. Choosing not to react is still a choice, and often the strongest one.",
    "Forgive yourself quickly. You will lose control sometimes. Repair it, learn from it, and move on, because shame only makes the next outburst more likely.",
]

# spread, page assignment
BEATS = [dict(say="You can't control what you feel. But you can control what you do next. Here are ten rules of emotional control, one page at a time.",
              v=dict(k="page", spread=0, page=0, head=0, title=True), sfx=[("page", 0, 0.6)], gap=0.9)]
for i, r in enumerate(RULES):
    spread = 0 if i < 2 else 1 + (i - 2) // 4
    page = 1 if i < 2 else ((i - 2) % 4) // 2
    first = (i == 2 or i == 6)
    BEATS.append(dict(say=f"Rule {NUM[i]}. {r}", v=dict(k="page", spread=spread, page=page, head=2, n=i + 1),
                      sfx=[("page", 0, 0.7)] if first else []))
BEATS.append(dict(say="Remember this. Control is not a cage around your feelings. It is the space between what you feel, and what you do.",
                  v=dict(k="page", spread=3, page=0, head=0), sfx=[("page", 0, 0.7)], gap=0.9))
BEATS.append(dict(say="Which rule do you need most this week? Write its number in the comments.",
                  v=dict(k="page", spread=3, page=1, head=0, q=True), sfx=[("ding", 0.2, 0.4)]))

PAPER = (252, 251, 247)
INK = hx("1e1e1e")
ACC = hx("b2452f")
GREYT = (200, 200, 196)
HL = hx("ffe98a")
BX0, BY0, BX1, BY1 = 110, 60, 1810, 1020
SP = W // 2
PAGES = [(BX0 + 70, SP - 60), (SP + 60, BX1 - 70)]
FS = 44
LH = 64


class Style(Base):
    cap = None
    xfade = 0

    def setup(self):
        bg = radial(hx("e9e6df"), hx("bdb8ad"), r=1300)
        d = D(bg)
        rrect(d, (BX0 + 10, BY0 + 20, BX1 + 10, BY1 + 26), 18, fill=A((0, 0, 0), 0.22))
        rrect(d, (BX0 - 14, BY0 - 6, BX1 + 14, BY1 + 14), 16, fill=A(hx("6e3b2a"), 1))
        bg.paste(Image.new("RGB", (BX1 - BX0, BY1 - BY0), PAPER), (BX0, BY0))
        arr = np.asarray(bg).astype(np.float32)
        xs = np.arange(W, dtype=np.float32)
        sh = 1 - 0.16 * np.exp(-((xs - SP) / 40) ** 2) - 0.04 * np.exp(-((xs - SP) / 200) ** 2)
        arr[BY0:BY1, BX0:BX1] *= sh[None, BX0:BX1, None]
        self.BG = Image.fromarray(arr.clip(0, 255).astype(np.uint8))
        d = D(self.BG)
        for y in (BY1 + 2, BY1 + 6):
            d.line([(BX0, y), (BX1, y)], fill=A((225, 222, 214), 1), width=3)
        self.fb = F("ebgaramond", FS)
        self.fh = F("playfair", FS + 4, 800)
        self.layout()

    def layout(self):
        self.pos = {}
        self.lines = {}
        cur = {}
        for b in self.beats:
            sp, pg = b.v["spread"], b.v["page"]
            x0, x1 = PAGES[pg]
            key = (sp, pg)
            if key not in cur:
                cur[key] = BY0 + 150 if not b.v.get("title") else BY0 + 520
                if b.v.get("q"):
                    cur[key] = BY0 + 330
            y = cur[key]
            x = x0
            line = 0
            for j, w in enumerate(b.words):
                f = self.fh if j < b.v["head"] else self.fb
                wd = f.getlength(w["w"])
                if j == b.v["head"] and j > 0:
                    x = x0
                    y += LH
                if x + wd > x1:
                    x = x0
                    y += LH
                self.pos[id(w)] = (x, y, f, j < b.v["head"])
                x += wd + f.getlength(" ")
            cur[key] = y + LH * 1.7

    def render_spread(self, img, sp, now, t, only_page=None):
        d = D(img)
        for b in self.beats:
            if b.v["spread"] != sp:
                continue
            if only_page is not None and b.v["page"] != only_page:
                continue
            if b.v.get("title") and now >= b.t0 - 0.5:
                x0, x1 = PAGES[0]
                cx = (x0 + x1) / 2
                text(d, (cx, BY0 + 140), "TEN RULES OF", F("playfair", 44, 600), ACC)
                text(d, (cx, BY0 + 230), "Emotional", F("playfair", 96, 800), INK)
                text(d, (cx, BY0 + 330), "Control", F("playfair_i", 96, 700), INK)
            if b.v.get("q") and now >= b.t0 - 0.2:
                x0, x1 = PAGES[1]
                text(d, ((x0 + x1) / 2, BY0 + 200), "Your turn", F("playfair_i", 80, 700), ACC)
            if now < b.t0:
                continue
            cur_line_y = None
            cur_w = None
            for w in b.words:
                if w["t0"] <= now:
                    cur_w = w
            if cur_w is not None:
                cur_line_y = self.pos[id(cur_w)][1]
            for w in b.words:
                x, y, f, head = self.pos[id(w)]
                done = now >= b.t1 - 0.01 or w["t0"] <= now
                if not done and (cur_line_y is None or y > cur_line_y):
                    continue
                col = (ACC if head else INK) if done else GREYT
                if cur_w is w and now < b.t0 + b.dur:
                    wd = f.getlength(w["w"])
                    d.rectangle((x - 4, y - FS * 0.95, x + wd + 4, y + FS * 0.3), fill=A(HL, 0.9))
                d.text((x, y), w["w"], font=f, fill=A(col, 1), anchor="ls")
        return d

    def hand_pos(self, now):
        b = self.tl.beat_at(now)
        cur = None
        for w in b.words:
            if w["t0"] <= now:
                cur = w
        if cur is None or now > b.t0 + b.dur + 0.3:
            return None
        x, y, f, _ = self.pos[id(cur)]
        wd = f.getlength(cur["w"])
        fr = clamp01((now - cur["t0"]) / max(0.05, cur["t1"] - cur["t0"]))
        return (x + wd * (0.2 + 0.6 * fr), y + 22)

    def draw(self, img, b, lt, t):
        now = b.t0 + lt
        sp = b.v["spread"]
        prev_sp = self.beats[b.i - 1].v["spread"] if b.i else sp
        TURN = 0.8
        if sp != prev_sp and lt < TURN:
            p = lt / TURN
            old = self.BG.copy()
            self.render_spread(old, prev_sp, now, t)
            new = self.BG.copy()
            self.render_spread(new, sp, now, t)
            img.paste(old)
            pw = SP - BX0
            if p < 0.5:
                img.paste(new.crop((SP, BY0, BX1, BY1)), (SP, BY0))
                w_ = int(pw * (1 - 2 * p))
                if w_ > 2:
                    pg = old.crop((SP, BY0, BX1, BY1)).resize((w_, BY1 - BY0))
                    img.paste(pg, (SP, BY0))
                    D(img).rectangle((SP, BY0, SP + w_, BY1), fill=(0, 0, 0, int(60 * p * 2)))
            else:
                img.paste(new.crop((SP, BY0, BX1, BY1)), (SP, BY0))
                w_ = int(pw * (2 * p - 1))
                if w_ > 2:
                    pg = new.crop((BX0, BY0, SP, BY1)).resize((w_, BY1 - BY0))
                    img.paste(pg, (SP - w_, BY0))
                    D(img).rectangle((SP - w_, BY0, SP, BY1), fill=(0, 0, 0, int(60 * (1 - (2 * p - 1)))))
            return
        self.render_spread(img, sp, now, t)
        d = D(img)
        x0, x1 = PAGES[0]
        text(d, ((x0 + x1) / 2, BY1 - 40), str(sp * 2 + 1), F("ebgaramond", 28), (150, 150, 145))
        x0, x1 = PAGES[1]
        text(d, ((x0 + x1) / 2, BY1 - 40), str(sp * 2 + 2), F("ebgaramond", 28), (150, 150, 145))
        if b.v.get("q"):
            for i in range(10):
                x = PAGES[1][0] + 40 + (i % 5) * 120
                y = BY0 + 600 + (i // 5) * 120
                a = ease((lt - 2 - i * 0.1) / 0.3)
                d.ellipse((x - 40, y - 40, x + 40, y + 40), outline=A(ACC, a), width=3)
                text(d, (x, y), str(i + 1), F("playfair", 44, 700), INK, alpha=a)
        hp = self.hand_pos(now)
        if hp is not None:
            if not hasattr(self, "_hp"):
                self._hp = hp
            self._hp = (lerp(self._hp[0], hp[0], 0.35), lerp(self._hp[1], hp[1], 0.35))
            hand_point(d, self._hp[0], self._hp[1], 110, skin=hx("f1c9a5"), cuff=hx("2d3b55"), outline=hx("9c6b4e"))
