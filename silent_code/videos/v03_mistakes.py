from engine import *

TITLE = "7 Mistakes That Make Smart People Look Weak"
VOICES = {"n": ("am_puck", 0.9)}
GAP = 0.55
MUSIC = dict(kind="pulse+pad+hats", root=110.0, prog=[0, 0, -2, -4], qual=["m", "m", "M", "M"], bar=4, bpm=96, vol=0.1)

R = "rd"
G = "gr"


def M(n, head, say, figs, bubbles=(), props=()):
    return dict(say=say, v=dict(k="m", n=n, h=head, figs=list(figs), bubbles=list(bubbles), props=list(props)), sfx=[("hit", 0, 0.5)])


def X(n, head, say, figs, bubbles=(), props=()):
    return dict(say=say, v=dict(k="f", n=n, h=head, figs=list(figs), bubbles=list(bubbles), props=list(props)), sfx=[("ding", 0.1, 0.4)])


BEATS = [
    dict(say="You can be the smartest person in the room, and still be the one nobody takes seriously. Here are seven small mistakes that cause it.",
         v=dict(k="hook"), sfx=[("boom", 0, 0.8)], gap=0.6),
    M(1, "OVER-APOLOGIZING", "Mistake one: over-apologizing. Sorry, quick question. Sorry, one more thing. Every unnecessary sorry tells people your presence is a burden.",
      [dict(x=760, p="sad", f="frown"), dict(x=1180, p="cross", flip=True, c="dim")], [(700, 380, "Sorry... sorry, quick question...", 0.5, (0, 1))]),
    X(1, "SAY \"THANK YOU\" INSTEAD", "The fix: swap sorry for thank you. Not, sorry I'm late. Thank you for waiting. Same politeness, twice the strength.",
      [dict(x=760, p="hips", f="smile"), dict(x=1180, p="stand", flip=True, c="dim", f="smile")], [(720, 380, "Thank you for waiting.", 0.5)]),
    M(2, "EXPLAINING TOO MUCH", "Mistake two: explaining too much. When you justify every decision, you invite people to judge it. A long explanation sounds like a defense.",
      [dict(x=760, p="talk2", f="o"), dict(x=1180, p="cross", flip=True, c="dim", f="smirk")],
      [(700, 340, "...and also because, and you see, the reason is, I mean...", 0.4, (0, 1), 520)]),
    X(2, "ONE REASON. THEN STOP.", "The fix: give one reason, then stop talking. Silence after a clear sentence sounds like certainty.",
      [dict(x=760, p="stand", f="flat"), dict(x=1180, p="stand", flip=True, c="dim", f="flat")], [(740, 400, "I can't this week.", 0.5)]),
    M(3, "LAUGHING AT YOUR OWN DISRESPECT", "Mistake three: laughing along with jokes made at your expense. You think it shows you're easygoing. It actually teaches people where your boundary isn't.",
      [dict(x=760, p="shrug", f="smile"), dict(x=1180, p="point_l", flip=True, c="dim", f="smirk")], [(1220, 360, "Ha! Classic you, always messing up.", 0.4, (0, 1))]),
    X(3, "DON'T LAUGH. STAY NEUTRAL.", "The fix: don't laugh. A calm, neutral face and a short, interesting, ends the game faster than any comeback.",
      [dict(x=760, p="cross", f="flat"), dict(x=1180, p="sad", flip=True, c="dim", f="flat")], [(740, 400, "Interesting.", 2.0)]),
    M(4, "ALWAYS INSTANTLY AVAILABLE", "Mistake four: replying instantly, every single time. Constant availability quietly signals that your time has no value.",
      [dict(x=900, p="phone", f="o")], [], [("phone", 1010, 560, 0.7, "acc"), ("ex", 1150, 420, 0.8, "rd")]),
    X(4, "RESPOND ON YOUR PRIORITIES", "The fix: respond when it suits your priorities. Not to play games, but because your attention is worth protecting.",
      [dict(x=900, p="sit", f="smile")], [], [("chair", 900, None, 1.0, "dim"), ("phone", 1200, 800, 0.6, "dim")]),
    M(5, "ASKING FOR APPROVAL", "Mistake five: asking for approval after you speak. Does that make sense? Is that okay? Your idea was strong. The question made it weak.",
      [dict(x=760, p="talk", f="flat"), dict(x=1180, p="stand", flip=True, c="dim")], [(700, 380, "...does that make sense? Is that okay?", 0.4)]),
    X(5, "END WITH A FULL STOP.", "The fix: end your point with a full stop. Let people ask if they're confused. Most of the time, they won't be.",
      [dict(x=760, p="hips", f="flat"), dict(x=1180, p="think", flip=True, c="dim")], [(720, 380, "That's the plan.", 0.4)]),
    M(6, "HIDING YOUR COMPETENCE", "Mistake six: hiding your competence to be liked. Smart people often shrink to avoid seeming arrogant. But people follow the confident, not the hidden.",
      [dict(x=760, p="hug_self", f="frown", s=0.8), dict(x=1180, p="hips", flip=True, c="dim", f="smirk")], [], [("crown", 760, 470, 0.7, "acc")]),
    X(6, "STATE STRENGTHS AS FACTS", "The fix: state your strengths as plain facts, without decoration. I'm good at this. Let me take it.",
      [dict(x=900, p="point", f="smile")], [(840, 380, "I'm good at this. Let me take it.", 0.6)], [("crown", 900, 430, 0.6, "acc")]),
    M(7, "ARGUING WITH WALLS", "Mistake seven: arguing with people who aren't listening. Smart people believe a better argument will always win. With some people, nothing will.",
      [dict(x=760, p="talk2", f="angry"), dict(x=1180, p="back", flip=True, c="dim")], [(700, 360, "But the data clearly shows-", 0.4)], [("wall", 1000, None, 0.9, "dim")]),
    X(7, "LEAVE EGO FIGHTS", "The fix: notice when the conversation is about ego, not truth. Then leave it. Walking away is not losing. It's choosing.",
      [dict(x=900, to=1500, dur=4, f="flat"), dict(x=500, p="talk2", c="dim", f="angry")], []),
    dict(say="Strength isn't loud. Most of the time, it's simply the absence of these small leaks.",
         v=dict(k="sum"), sfx=[("riser", 0, 0.7)]),
    dict(say="Which of these seven do you catch yourself doing the most? Be honest in the comments.",
         v=dict(k="question"), sfx=[("ding", 0.3, 0.6)]),
]

BGC = hx("15161a")
YEL = hx("ffd23f")
RED = hx("ff4a4a")
GRN = hx("3ddc84")
PAL = dict(bg=BGC, fg=hx("f2f2f2"), acc=YEL, dim=hx("8c8f99"), rd=RED, gr=GRN, gy=820, s=340, bubble=hx("f2f2f2"), bubtxt=BGC,
           screen=hx("5aa0ff"))


class Style(Base):
    cap = dict(font="anton", size=64, y=965, fill=(255, 255, 255), hl=YEL, stroke=5, sfill=(0, 0, 0), upper=True, maxw=1300, pop=True)
    xfade = 0.2

    def setup(self):
        bg = Image.new("RGB", (W, H), BGC)
        d = D(bg)
        for x in range(-H, W, 60):
            d.line([(x, H), (x + H, 0)], fill=A((255, 255, 255), 0.018), width=22)
        d.rectangle((0, 820, W, H), fill=A((0, 0, 0), 0.35))
        self.BG = vignette(bg, 0.5)
        self.bf = F("Inter", 36, 700)

    def draw(self, img, b, lt, t):
        d = D(img)
        v = b.v
        k = v["k"]
        if k == "hook":
            s = 1 + 0.04 * math.sin(lt * 2)
            text(d, (W / 2, 330), "7 MISTAKES", F("anton", int(190 * s)), YEL, alpha=ease(lt / 0.3), stroke=6)
            text(d, (W / 2, 500), "THAT MAKE SMART PEOPLE", F("anton", 90), (255, 255, 255), alpha=ease((lt - 0.4) / 0.3))
            text(d, (W / 2, 620), "LOOK WEAK", F("anton", 150), RED, alpha=ease((lt - 0.8) / 0.3), stroke=4)
        elif k in ("m", "f"):
            mis = k == "m"
            col = RED if mis else GRN
            lab = f"MISTAKE #{v['n']}" if mis else "THE FIX"
            sl = ease(lt / 0.35)
            rrect(d, (lerp(-400, 60, sl), 60, lerp(-400, 60, sl) + 330, 140), 12, fill=A(col, 1))
            text(d, (lerp(-400, 60, sl) + 165, 101), lab, F("anton", 52), (10, 10, 10))
            text(d, (W - 80, 100), f"{v['n']}/7", F("anton", 60), PAL["dim"], "rm")
            text(d, (W / 2, 220), v["h"], F("anton", 84), YEL if mis else GRN, alpha=ease((lt - 0.2) / 0.3), stroke=3)
            scene(d, v, lt, t, PAL, bfont=self.bf)
            if mis:
                cross_x(d, 1600, 560, 70, RED, 18, ease((lt - 1.0) / 0.5))
            else:
                check(d, 1600, 560, 160, GRN, 22, ease((lt - 1.0) / 0.6))
        elif k == "sum":
            text(d, (W / 2, 420), "STRENGTH ISN'T LOUD.", F("anton", 130), (255, 255, 255), alpha=ease(lt / 0.4))
            text(d, (W / 2, 580), "IT'S THE ABSENCE OF SMALL LEAKS.", F("anton", 74), YEL, alpha=ease((lt - 1.5) / 0.4))
        elif k == "question":
            a = ease(lt / 0.4)
            text(d, (W / 2, 220), "COMMENT 👇" if False else "COMMENT BELOW", F("anton", 64), RED, alpha=a)
            para(d, W / 2, 400, "WHICH MISTAKE DO YOU MAKE THE MOST?", F("anton", 110), (255, 255, 255), 1500, alpha=a, stroke=4)
            for i in range(7):
                x = 420 + i * 180
                aa = ease((lt - 0.8 - i * 0.12) / 0.3)
                rrect(d, (x - 70, 610, x + 70, 750), 18, fill=A(YEL, aa))
                text(d, (x, 680), str(i + 1), F("anton", 90), BGC, alpha=aa)

    def show_cap(self, b):
        return b.v["k"] not in ("question", "hook", "sum")
