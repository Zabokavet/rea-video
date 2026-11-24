from engine import *

TITLE = "The 5 Stages of Losing Yourself in a Relationship"
VOICES = {"n": ("af_sarah", 0.9)}
GAP = 0.8
_x = {}
MUSIC = dict(kind="pad+piano+hats", root=130.8, prog=[0, 5, -3, 3], qual=["M", "M", "m", "M"], bar=6, step=0.5,
             pat=[0, 1, 2, 1, 3, 1], bpm=80, vol=0.09)

STAGES = ["Merging", "Editing", "Shrinking", "Mirroring", "Emptiness"]

BEATS = [
    dict(say="You didn't lose yourself overnight. You lost yourself in five quiet stages, and most people never notice stage two.",
         v=dict(k="hook"), sfx=[("hit", 0.0, 0.6)], gap=0.6),
    dict(say="Psychologists call it self-silencing. In its extreme form, enmeshment: your identity slowly dissolving into someone else's. And no one forces it on you. You hand yourself over one small compromise at a time, usually just to keep the peace. Here's how it happens.",
         v=dict(k="intro", st=0)),
    dict(say="Stage one: merging. At the start, it feels beautiful. Same food, same shows, same weekends. Merging is normal in early love. The danger is that you stop noticing what you gave up to keep things smooth.",
         v=dict(k="stage", st=1, signs=["Same tastes, same plans", "Feels like closeness", "Small sacrifices go unnoticed"]), sfx=[("whoosh", 0, 0.5)]),
    dict(say="Stage two: editing. You pre-check your words. You soften opinions before you say them. You think, is this worth the reaction? Almost everyone misses this stage, because it looks like maturity. It isn't. It's fear wearing a nice outfit.",
         v=dict(k="stage", st=2, signs=["You rehearse sentences", "Opinions get softened", "Fear disguised as maturity"]), sfx=[("whoosh", 0, 0.5)]),
    dict(say="Stage three: shrinking. Your friends hear from you less. Your hobbies start to feel selfish. Every plan begins with, let me check first. Your world gets smaller, and you call it commitment.",
         v=dict(k="stage", st=3, signs=["Friends fade out", "Hobbies feel 'selfish'", "\"Let me check first\""]), sfx=[("whoosh", 0, 0.5)]),
    dict(say="Stage four: mirroring. You don't know what you think until you know what they think. Their mood becomes your weather. If they're calm, you're safe. If they're cold, you're anxious all day.",
         v=dict(k="stage", st=4, signs=["Their opinion becomes yours", "Their mood = your weather", "Calm = safe, cold = panic"]), sfx=[("whoosh", 0, 0.5)]),
    dict(say="Stage five: emptiness. Someone asks, what do you actually enjoy? And you can't answer. Not because you're boring, but because you've been living as a supporting character in your own life. This is where people say, I don't even recognize myself anymore.",
         v=dict(k="stage", st=5, signs=["\"What do you enjoy?\" ...silence", "No preferences left", "A side character in your own life"]), sfx=[("whoosh", 0, 0.5)]),
    dict(say="Now the hopeful part. These stages work in reverse. Your identity comes back the same way it left: through small, repeated acts.",
         v=dict(k="reverse", st=5), sfx=[("riser", 0, 0.8)]),
    dict(say="Say one honest opinion a day, even a tiny one. Rebuild one friendship you let fade. Do one thing alone that is purely yours. And when you feel the urge to ask permission, pause first, and ask yourself what you want.",
         v=dict(k="plan", items=["One honest opinion a day", "Rebuild one faded friendship", "One thing that is purely yours", "Pause before asking permission"])),
    dict(say="Remember this. A healthy relationship never asks you to disappear. It doesn't need a smaller version of you. It makes room for two whole people.",
         v=dict(k="whole")),
    dict(say="Which stage were you in when you finally noticed? Tell me in the comments. Someone reading needs to know they're not alone.",
         v=dict(k="question"), sfx=[("ding", 0.3, 0.6)]),
]

BG = hx("f6f1ea")
NAVY = hx("1f2a44")
CORAL = hx("ff6b57")
TEAL = hx("2bb3a3")
MUTED = hx("b8b1a6")
RADII = [170, 165, 135, 100, 65, 30]


class Style(Base):
    cap = dict(font="montserrat", w=800, size=46, y=1000, fill=(255, 255, 255), hl=(255, 255, 255), hlbox=CORAL + (255,),
               bar=NAVY + (235,), upper=True, maxw=1400, pop=True)
    xfade = 0.3

    def setup(self):
        bg = Image.new("RGB", (W, H), BG)
        d = D(bg)
        for x in range(0, W, 48):
            for y in range(0, H, 48):
                d.ellipse((x - 1.5, y - 1.5, x + 1.5, y + 1.5), fill=A(MUTED, 0.45))
        self.BG = bg
        st = 0
        self.stage_of = []
        for b in self.beats:
            st = b.v.get("st", st)
            self.stage_of.append(st)

    def tracker(self, d, b, lt):
        st = self.stage_of[b.i]
        if b.i == 0 or b.v["k"] in ("question",):
            return
        x0, x1, y = 560, 1360, 92
        d.line([(x0, y), (x1, y)], fill=A(MUTED, 1), width=6)
        if st > 1:
            prog = (st - 2 + ease(lt / 0.8)) / 4 if b.v["k"] == "stage" else (st - 1) / 4
            d.line([(x0, y), (lerp(x0, x1, prog), y)], fill=A(NAVY, 1), width=6)
        f = F("montserrat", 20, 700)
        for i in range(5):
            x = lerp(x0, x1, i / 4)
            n = i + 1
            if n < st:
                d.ellipse((x - 20, y - 20, x + 20, y + 20), fill=A(NAVY, 1))
                text(d, (x, y), str(n), f, (255, 255, 255))
            elif n == st:
                pr = 26 + 4 * math.sin(lt * 4)
                d.ellipse((x - pr - 8, y - pr - 8, x + pr + 8, y + pr + 8), fill=A(CORAL, 0.2))
                d.ellipse((x - 26, y - 26, x + 26, y + 26), fill=A(CORAL, 1))
                text(d, (x, y), str(n), F("montserrat", 24, 800), (255, 255, 255))
            else:
                d.ellipse((x - 20, y - 20, x + 20, y + 20), fill=A(BG, 1), outline=A(MUTED, 1), width=4)
                text(d, (x, y), str(n), f, MUTED)
            text(d, (x, y + 48), STAGES[i].upper(), F("montserrat", 17, 700), NAVY if n <= st else MUTED)

    def venn(self, d, cx, cy, r_you, sep, dotted=False, a=1.0):
        rt = 190
        tx = cx + 120
        d.ellipse((tx - rt, cy - rt, tx + rt, cy + rt), fill=A(CORAL, 0.85 * a))
        text(d, (tx + 60, cy), "THEM", F("montserrat", 34, 800), (255, 255, 255), alpha=a)
        yx = cx - 120 - sep + (170 - r_you) * 0.8
        if dotted:
            for i in range(24):
                ang = i / 24 * 2 * math.pi
                px, py = yx + math.cos(ang) * r_you, cy + math.sin(ang) * r_you
                d.ellipse((px - 4, py - 4, px + 4, py + 4), fill=A(NAVY, a))
        else:
            d.ellipse((yx - r_you, cy - r_you, yx + r_you, cy + r_you), fill=A(TEAL, 0.9 * a))
        if r_you > 50:
            text(d, (yx, cy), "YOU", F("montserrat", int(max(20, r_you * 0.22)), 800), (255, 255, 255) if not dotted else NAVY, alpha=a)
        else:
            text(d, (yx, cy - r_you - 34), "you?", F("montserrat", 28, 700), NAVY, alpha=a)

    def draw(self, img, b, lt, t):
        d = D(img)
        v = b.v
        k = v["k"]
        if k == "hook":
            a = ease(lt / 0.4)
            text(d, (W / 2, 330), "5 STAGES", F("montserrat", 60, 800), CORAL, alpha=a)
            text(d, (W / 2, 470), "of losing yourself", F("montserrat", 120, 900), NAVY, alpha=a)
            text(d, (W / 2, 610), "most people miss stage 2", F("montserrat", 56, 600), TEAL, alpha=ease((lt - 3.2) / 0.4))
            r = lerp(170, 40, eio(lt / 6))
            self.venn(d, W / 2 - 60, 840 - 40, r * 0.5, -20, a=0.0)
        elif k == "intro":
            sep = lerp(240, 80, eio(lt / 4))
            self.venn(d, 640, 560, 170, sep)
            text(d, (1350, 470), "Self-silencing", F("montserrat", 78, 900), NAVY, alpha=ease(lt / 0.5))
            text(d, (1350, 570), "→ enmeshment", F("montserrat", 56, 700), CORAL, alpha=ease((lt - 2.5) / 0.5))
            text(d, (1350, 650), "identity dissolving into theirs", F("montserrat", 34, 500), NAVY, alpha=ease((lt - 3.5) / 0.5))
        elif k == "stage":
            st = v["st"]
            r = lerp(RADII[st - 1], RADII[st], eio(lt / 1.4))
            sep = lerp(80, 0, (st - 1) / 4)
            self.venn(d, 600, 560, r, sep, dotted=st == 5 and lt > 1.4)
            x = 1080
            a = ease(lt / 0.4)
            text(d, (x, 330), f"STAGE {st}", F("montserrat", 40, 800), CORAL, "lm", alpha=a)
            text(d, (x - 6, 420), STAGES[st - 1], F("montserrat", 110, 900), NAVY, "lm", alpha=a)
            dur = b.dur
            for i, s in enumerate(v["signs"]):
                ta = 1.2 + i * dur / 3.3
                aa = ease((lt - ta) / 0.4)
                yy = 560 + i * 92
                d.ellipse((x, yy - 14, x + 28, yy + 14), fill=A(TEAL, aa))
                text(d, (x + 52, yy + (1 - aa) * 20), s, F("montserrat", 42, 600), NAVY, "lm", alpha=aa)
        elif k == "reverse":
            r = lerp(30, 170, eio((lt - 0.8) / 4))
            self.venn(d, 640, 560, r, lerp(0, 80, eio(lt / 4)))
            text(d, (1350, 470), "It works", F("montserrat", 90, 900), NAVY, alpha=ease(lt / 0.5))
            text(d, (1350, 580), "in reverse.", F("montserrat", 90, 900), TEAL, alpha=ease((lt - 0.8) / 0.5))
            arrow(d, (1150, 700), (1550, 700), CORAL, 8, 28, x=ease((lt - 1.5) / 1.0))
        elif k == "plan":
            text(d, (W / 2, 240), "REBUILD YOURSELF", F("montserrat", 64, 900), NAVY, alpha=ease(lt / 0.4))
            n = len(v["items"])
            for i, s in enumerate(v["items"]):
                ta = 0.6 + i * b.dur / (n + 0.3)
                aa = ease((lt - ta) / 0.4)
                y = 380 + i * 120
                rrect(d, (460, y - 46, 1460, y + 46), 46, fill=A((255, 255, 255), aa), outline=A(MUTED, aa), width=2)
                d.ellipse((480, y - 32, 544, y + 32), fill=A(TEAL, aa))
                text(d, (512, y), str(i + 1), F("montserrat", 34, 800), (255, 255, 255), alpha=aa)
                text(d, (580, y), s, F("montserrat", 42, 600), NAVY, "lm", alpha=aa)
        elif k == "whole":
            a = ease(lt / 0.6)
            for cx, c, lab in ((760, TEAL, "YOU"), (1160, CORAL, "THEM")):
                d.ellipse((cx - 210, 520 - 210, cx + 210, 520 + 210), fill=A(c, 0.85 * a))
                text(d, (cx + (-80 if lab == "YOU" else 80), 520), lab, F("montserrat", 46, 800), (255, 255, 255), alpha=a)
            text(d, (W / 2, 180), "Two whole people.", F("montserrat", 84, 900), NAVY, alpha=ease((lt - 1.5) / 0.5))
        elif k == "question":
            a = ease(lt / 0.5)
            rrect(d, (240, 200, 1680, 820), 40, fill=A(NAVY, a))
            text(d, (W / 2, 300), "COMMENT BELOW", F("montserrat", 38, 800), CORAL, alpha=a)
            para(d, W / 2, 470, "Which stage were you in when you finally noticed?", F("montserrat", 76, 900), (255, 255, 255), 1250, alpha=a)
            for i in range(5):
                x = 640 + i * 160
                d.ellipse((x - 44, 680 - 44, x + 44, 680 + 44), fill=A(CORAL if i == 1 else TEAL, ease((lt - 0.6 - i * 0.15) / 0.3)))
                text(d, (x, 680), str(i + 1), F("montserrat", 40, 800), (255, 255, 255), alpha=ease((lt - 0.6 - i * 0.15) / 0.3))

    def overlay(self, img, b, lt, t):
        self.tracker(D(img), b, lt)

    def show_cap(self, b):
        return b.v["k"] not in ("question", "hook")
