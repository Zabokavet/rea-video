from engine import *

TITLE = "The Friend Who Smiled While I Was Falling"
VOICES = {"n": ("am_michael", 0.94)}
MUSIC = dict(kind="pad+piano", root=98.0, prog=[0, -4, 3, -2], qual=["m", "M", "M", "M"], bar=8, step=1.0,
             pat=[0, 2, 1, 3], vol=0.13)

M = "acc"  # Marcus colour key

BEATS = [
    dict(say="He was the first person I called when my life fell apart. I didn't know he was the reason it was falling.",
         v=dict(k="hook"), sfx=[("boom", 0.0, 0.8)], gap=0.7),
    dict(say="Marcus and I met at nineteen. Same cheap apartment building, same big dreams, same broken coffee machine in the lobby.",
         v=dict(k="scene", ch="Part one · The friend", figs=[dict(x=500, to=820, f="smile"), dict(x=1500, to=1100, flip=True, c=M, f="smile")])),
    dict(say="For ten years, he was the brother I chose. He knew my plans, my fears, my weak spots. I told him everything, because that's what you do with family.",
         v=dict(k="scene", figs=[dict(x=720, p="sit", f="smile"), dict(x=1200, p="sit", flip=True, c=M, f="smile")],
                props=[("table", 960, None, 1.0, "dim")], bubbles=[(700, 330, "Here's my plan...", 0.6), (1220, 380, "I've got you.", 3.0)])),
    dict(say="Then, last spring, things started going wrong. Small things at first.",
         v=dict(k="chapter", a="Part two", b="The cracks"), sfx=[("whoosh", 0, 0.6)]),
    dict(say="A promotion I was promised went to someone else. My boss had heard I was \"thinking about leaving.\" I had only said that to one person.",
         v=dict(k="scene", figs=[dict(x=760, p="sad", f="frown"), dict(x=1180, p="hips", flip=True, c="dim", f="flat")],
                bubbles=[(1210, 360, "I hear you're thinking about leaving?", 0.5)], props=[("q", 620, 420, 0.8, "acc2")])),
    dict(say="A woman I was seeing suddenly went cold. She'd been told I was \"still hung up on my ex.\" Again, I had only said that to one person.",
         v=dict(k="scene", figs=[dict(x=760, p="reach", f="frown"), dict(x=1100, to=1600, c="rose", hair="rose", dur=4)],
                props=[("broken", 960, 330, 0.8, "rose")])),
    dict(say="And every time something broke, Marcus was there. Bringing beer. Shaking his head. Saying, \"Man, you have the worst luck.\"",
         v=dict(k="scene", figs=[dict(x=760, p="sit_sad", f="frown"), dict(x=1150, p="talk", flip=True, c=M, f="smirk")],
                props=[("chair", 760, None, 1.0, "dim")], bubbles=[(1180, 380, "Man... you have the worst luck.", 1.0)])),
    dict(say="Psychologists have a name for this: covert competition. Someone who stays close, not because they love your rise, but because they want a front-row seat to your fall.",
         v=dict(k="concept", word="Covert competition", sub="close to you — invested in your fall"), sfx=[("hit", 0.2, 0.5)]),
    dict(say="They rarely attack you openly. They leak your secrets \"by accident.\" They offer comfort after damage they quietly caused. Your pain makes them feel taller.",
         v=dict(k="scene", figs=[dict(x=960, p="stand", c=M, f="smile")], props=[("mask", 960, 400, 1.0, "fg", True), ("dagger", 1180, 760, 1.0, "acc2", 200)])),
    dict(say="The truth didn't arrive in one moment. It arrived in pieces.",
         v=dict(k="chapter", a="Part three", b="The pieces"), sfx=[("whoosh", 0, 0.6)]),
    dict(say="A message he forgot to close, open on his laptop. My name, and the words: \"Don't worry. He'll never figure it out.\"",
         v=dict(k="message", msg="Don't worry. He'll never figure it out.")),
    dict(say="I didn't scream. I didn't send a long message. I just sat there, and for the first time, I understood the smile.",
         v=dict(k="scene", figs=[dict(x=960, p="sit_sad", f="flat")], props=[("chair", 960, None, 1.0, "dim"), ("moon", 1500, 220, 1.0, "fg")])),
    dict(say="Because when you finally see someone clearly, you don't need a fight. You need a door.",
         v=dict(k="chapter", a="Part four", b="The quiet exit"), sfx=[("whoosh", 0, 0.6)]),
    dict(say="I stopped sharing plans. I answered his calls slower, then not at all. No speech. No confrontation. A quiet exit gives a person like that nothing to feed on.",
         v=dict(k="scene", figs=[dict(x=500, to=1300, dur=6, f="flat")], props=[("door", 1400, None, 1.0, "fg", 1.0), ("phone", 360, 780, 0.8, "dim")])),
    dict(say="If you're wondering whether someone in your life is like Marcus, watch one thing: how they react to your good news. Real friends light up. Competitors go quiet, then change the subject.",
         v=dict(k="split", sfx=None)),
    dict(say="Your secrets are a test. Most people pass. Some don't. And the ones who fail usually smile the widest.",
         v=dict(k="concept", word="Your secrets are a test.", sub="the ones who fail usually smile the widest")),
    dict(say="Have you ever discovered a friend was quietly working against you? How did you find out? Tell me in the comments.",
         v=dict(k="question", q="Have you ever discovered a “friend” was quietly working against you?", s="How did you find out? Tell me below."),
         sfx=[("ding", 0.3, 0.6)]),
]

PAL = dict(bg=hx("1a1426"), fg=hx("f3e6d0"), acc=hx("5fc4b5"), acc2=hx("f2a65a"), dim=hx("8a7f99"), rose=hx("e58fa0"),
           gy=800, s=330, bubble=hx("f3e6d0"), bubtxt=hx("1a1426"), tear=hx("7fb7ff"))


class Style(Base):
    cap = dict(font="lora", size=56, w=500, y=985, fill=(243, 230, 208), hl=(242, 166, 90), stroke=3, sfill=(15, 10, 22), maxw=1500)

    def setup(self):
        bg = radial(hx("34284a"), hx("100b17"), cy=420, r=1300)
        d = D(bg)
        for i in range(90):
            rr = random.Random(i)
            x, y = rr.uniform(0, W), rr.uniform(0, 600)
            d.ellipse((x - 1.5, y - 1.5, x + 1.5, y + 1.5), fill=A(PAL["fg"], rr.uniform(0.1, 0.5)))
        d.rectangle((0, PAL["gy"], W, H), fill=A(hx("0d0913"), 0.85))
        d.line([(0, PAL["gy"]), (W, PAL["gy"])], fill=A(PAL["dim"], 0.6), width=3)
        self.BG = vignette(texture(bg, 5, 2, blur=1), 0.5)
        self.bf = F("lora", 34, 600)

    def cross(self, b):
        return True

    def draw(self, img, b, lt, t):
        d = D(img)
        v = b.v
        k = v.get("k")
        if k == "hook":
            y = lerp(-200, 700, eio(lt / 5.5))
            figure(d, 1400, y + 330, 260, "arms_up", PAL["fg"], t, face="o", head_fill=PAL["bg"])
            figure(d, 1400, 170, 200, "stand", PAL["acc"], t, face="smile", head_fill=PAL["bg"], alpha=ease((lt - 1.5) / 1))
            text(d, (180, 420), "He smiled", F("playfair_i", 120, 700), PAL["fg"], "lm", ease(lt / 0.5))
            text(d, (180, 560), "while I was falling.", F("playfair_i", 120, 700), PAL["acc2"], "lm", ease((lt - 0.8) / 0.5))
        elif k == "scene":
            if v.get("ch"):
                text(d, (80, 80), v["ch"].upper(), F("cinzel", 34, 600), PAL["dim"], "lm", ease(lt / 0.6))
            scene(d, v, lt, t, PAL, bfont=self.bf)
        elif k == "chapter":
            a = ease(lt / 0.6)
            text(d, (W / 2, 420), v["a"].upper(), F("cinzel", 46, 600), PAL["dim"], alpha=a)
            text(d, (W / 2, 540), v["b"], F("playfair_i", 130, 600), PAL["fg"], alpha=ease((lt - 0.3) / 0.6))
            ww = 300 * ease((lt - 0.4) / 0.8)
            d.line([(W / 2 - ww, 650), (W / 2 + ww, 650)], fill=A(PAL["acc2"], 0.9), width=3)
        elif k == "concept":
            text(d, (W / 2, 450), v["word"], F("playfair", 104, 800), PAL["fg"], alpha=ease(lt / 0.5))
            text(d, (W / 2, 580), v["sub"], F("lora", 46, 400), PAL["acc"], alpha=ease((lt - 0.6) / 0.5))
        elif k == "message":
            rrect(d, (560, 170, 1360, 720), 30, fill=A(hx("0e0a14"), 1), outline=A(PAL["dim"], 1), width=4)
            rrect(d, (600, 210, 1320, 680), 18, fill=A(hx("231b31"), 1))
            text(d, (640, 260), "Messages", F("Inter", 32, 700), PAL["dim"], "lm")
            bubble(d, 900, 360, "Is he suspicious?", F("Inter", 34), hx("3a3050"), PAL["fg"], tail=(-1, 1), alpha=ease((lt - 0.4) / 0.3))
            bubble(d, 1030, 540, v["msg"], F("Inter", 36, 600), PAL["acc"], hx("101010"), tail=(1, 1), alpha=ease((lt - 2.0) / 0.3),
                   reveal=(lt - 2.0) / 2.0)
            if lt > 4.5:
                text(d, (1400, 220), "!", F("archivoblack", 140), PAL["acc2"], alpha=ease((lt - 4.5) / 0.3))
        elif k == "split":
            d.line([(W / 2, 140), (W / 2, 760)], fill=A(PAL["dim"], 0.6), width=3)
            text(d, (W / 4, 150), "REAL FRIEND", F("cinzel", 50, 700), PAL["acc"], alpha=ease(lt / 0.5))
            text(d, (3 * W / 4, 150), "COMPETITOR", F("cinzel", 50, 700), PAL["acc2"], alpha=ease((lt - 0.4) / 0.5))
            figure(d, W / 4 - 120, 780, 280, "stand", PAL["fg"], t, face="smile", head_fill=PAL["bg"])
            figure(d, W / 4 + 130, 780, 280, "arms_up", PAL["acc"], t, flip=True, face="smile", head_fill=PAL["bg"], alpha=ease((lt - 3) / 0.5))
            figure(d, 3 * W / 4 - 120, 780, 280, "stand", PAL["fg"], t, face="smile", head_fill=PAL["bg"])
            figure(d, 3 * W / 4 + 130, 780, 280, "cross", PAL["acc2"], t, flip=True, face="flat", head_fill=PAL["bg"], alpha=ease((lt - 3) / 0.5))
            bubble(d, W / 4 - 120, 330, "I got the job!", self.bf, PAL["fg"], PAL["bg"], alpha=ease((lt - 1) / 0.3))
            bubble(d, 3 * W / 4 - 120, 330, "I got the job!", self.bf, PAL["fg"], PAL["bg"], alpha=ease((lt - 1) / 0.3))
            bubble(d, W / 4 + 170, 400, "YES! Tell me everything!", self.bf, PAL["acc"], PAL["bg"], tail=(1, 1), alpha=ease((lt - 6.5) / 0.3))
            bubble(d, 3 * W / 4 + 170, 400, "Oh. Anyway...", self.bf, PAL["acc2"], PAL["bg"], tail=(1, 1), alpha=ease((lt - 8.5) / 0.3))
        elif k == "question":
            a = ease(lt / 0.6)
            rrect(d, (260, 230, 1660, 760), 26, fill=A(hx("0f0a16"), 0.85 * a), outline=A(PAL["acc2"], a), width=3)
            text(d, (W / 2, 300), "YOUR TURN", F("cinzel", 40, 700), PAL["acc2"], alpha=a)
            para(d, W / 2, 470, v["q"], F("playfair", 70, 700), PAL["fg"], 1250, alpha=a)
            text(d, (W / 2, 680), v["s"], F("lora", 42), PAL["acc"], alpha=ease((lt - 1) / 0.5))

    def show_cap(self, b):
        return b.v.get("k") not in ("question", "hook")
