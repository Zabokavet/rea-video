"""Shared pieces for the vertical (9:16) story reels: characters, settings, captions, hook and end frame.

Run with SC_VERTICAL=1 so draw.W, draw.H = 1080, 1920.
"""
import math
import random
from draw import *  # noqa
from engine import Base

SKIN = {"light": hx("f1cbb0"), "fair": hx("f4d4bf"), "tan": hx("d9a27e"), "brown": hx("a86f4c"), "deep": hx("7a4a30")}

# pose: (left arm (upper, lower)), (right arm), sit, head tilt, eyes, mouth
POSE = {
    "stand": dict(la=(-12, -6), ra=(12, 6)),
    "window": dict(la=(-12, -6), ra=(25, 150), tilt=0),
    "flowers": dict(la=(-12, -6), ra=(50, 110)),
    "give": dict(la=(-12, -6), ra=(70, 85)),
    "phone": dict(la=(-12, -6), ra=(20, 168)),
    "refuse": dict(la=(60, 150), ra=(60, 150)),
    "cry": dict(la=(30, 165), ra=(-30, -165), tilt=10),
    "hands_face": dict(la=(20, 170), ra=(-20, -170), tilt=14),
    "hold": dict(la=(45, 100), ra=(-45, -100)),
    "talk": dict(la=(-12, -6), ra=(45, 120)),
    "sit": dict(la=(30, 75), ra=(35, 80), sit=True),
    "sit_hold": dict(la=(45, 90), ra=(-45, -90), sit=True),
    "sit_talk": dict(la=(30, 75), ra=(50, 130), sit=True),
    "kneel": dict(la=(40, 95), ra=(55, 80), sit=True),
    "kneel_pray": dict(la=(35, 150), ra=(-35, -150), sit=True, tilt=6),
    "cross": dict(la=(28, 100), ra=(-28, -100)),
    "pray": dict(la=(35, 150), ra=(-35, -150), tilt=6),
    "wave": dict(la=(-12, -6), ra=(140, 170)),
    "carry": dict(la=(-12, -6), ra=(8, 2)),
    "hug": dict(la=(70, 95), ra=(70, 95)),
    "sit_sad": dict(la=(40, 80), ra=(45, 85), sit=True, tilt=10),
    "sit_hands_face": dict(la=(20, 170), ra=(-20, -170), sit=True, tilt=14),
    "sit_phone": dict(la=(30, 75), ra=(20, 168), sit=True),
    "sit_eat": dict(la=(30, 75), ra=(60, 140), sit=True),
}


def _v(a):
    r = math.radians(a)
    return math.sin(r), math.cos(r)


def person(d, x, gy, h, look, pose="stand", t=0.0, facing=1, eyes="open", mouth="soft", tears=0.0, alpha=1.0, breathe=True):
    """Filled, softly shaded character. look: dict(skin, hair, hair_style, top, bottom, skirt, shoes, glasses, age)
    Returns dict with 'lhand', 'rhand', 'head' positions."""
    P = POSE.get(pose, POSE["stand"])
    sk = look["skin"]
    A_ = lambda c, a=1.0: A(c, a * alpha)
    r = h * 0.072
    by = math.sin(t * 1.8) * h * 0.003 if breathe else 0
    knl = pose.startswith("kneel")
    sit = P.get("sit", False) and not knl
    hip_y = gy - h * (0.30 if sit else (0.26 if knl else 0.47)) + by
    sh_y = hip_y - h * 0.33
    tilt = math.radians(P.get("tilt", 0) * facing)
    neck = (x + math.sin(tilt) * h * 0.02, sh_y - h * 0.02)
    hx_, hy_ = neck[0] + math.sin(tilt) * r * 1.3, neck[1] - r * 1.15
    sw, hw = h * 0.115, h * 0.10
    top, bot = look["top"], look["bottom"]
    # legs
    lw = int(h * 0.06)
    shoe = look.get("shoes", hx("3a2a22"))
    if knl:
        for k in (-1, 1):
            kx = x + k * h * 0.03 + facing * h * 0.02
            d.line([(x + k * hw * 0.4, hip_y), (kx, gy - h * 0.03)], fill=A_(bot), width=lw)
            d.line([(kx, gy - h * 0.03), (kx - facing * h * 0.2, gy - h * 0.02)], fill=A_(look.get("leg", bot)), width=int(lw * 0.85))
            d.ellipse((kx - facing * h * 0.2 - h * 0.04, gy - h * 0.04, kx - facing * h * 0.2 + h * 0.03, gy), fill=A_(shoe))
    elif sit:
        for k in (-1, 1):
            kx = x + facing * h * 0.22 + k * h * 0.03
            d.line([(x + k * hw * 0.5, hip_y), (kx, hip_y + h * 0.01)], fill=A_(bot), width=lw)
            d.line([(kx, hip_y + h * 0.01), (kx + facing * h * 0.01, gy - h * 0.02)], fill=A_(look.get("leg", bot)), width=int(lw * 0.85))
            d.ellipse((kx - h * 0.04 + facing * h * 0.02, gy - h * 0.03, kx + h * 0.05 + facing * h * 0.02, gy), fill=A_(shoe))
    else:
        for k in (-1, 1):
            fx = x + k * h * 0.045
            d.line([(x + k * hw * 0.45, hip_y), (fx, gy - h * 0.025)], fill=A_(look.get("leg", bot)), width=lw)
            d.ellipse((fx - h * 0.04 + facing * h * 0.01, gy - h * 0.035, fx + h * 0.045 + facing * h * 0.01, gy), fill=A_(shoe))
    # skirt / trousers top
    if look.get("skirt"):
        hem = (hip_y + h * 0.27) if not (sit or knl) else hip_y + h * 0.1
        if sit:
            d.polygon([(x - hw, hip_y - h * 0.02), (x + hw, hip_y - h * 0.02), (x + facing * h * 0.26 + hw * 0.3, hem), (x - hw * 0.7, hem)], fill=A_(bot))
        else:
            d.polygon([(x - hw, hip_y - h * 0.02), (x + hw, hip_y - h * 0.02), (x + hw * 1.45, hem), (x - hw * 1.45, hem)], fill=A_(bot))
    else:
        d.rounded_rectangle((x - hw, hip_y - h * 0.03, x + hw, hip_y + h * 0.05), radius=h * 0.03, fill=A_(bot))
    # torso
    d.polygon([(x - sw, sh_y), (x + sw, sh_y), (x + hw * 1.05, hip_y + h * 0.01), (x - hw * 1.05, hip_y + h * 0.01)], fill=A_(top))
    d.ellipse((x - sw - h * 0.03, sh_y - h * 0.03, x - sw + h * 0.05, sh_y + h * 0.05), fill=A_(top))
    d.ellipse((x + sw - h * 0.05, sh_y - h * 0.03, x + sw + h * 0.03, sh_y + h * 0.05), fill=A_(top))
    shade = mixc(top, (0, 0, 0), 0.18)
    d.polygon([(x + facing * sw * 0.2, sh_y + h * 0.02), (x + facing * sw, sh_y + h * 0.02), (x + facing * hw * 1.05, hip_y), (x + facing * hw * 0.3, hip_y)],
              fill=A_(shade, 0.35))
    if look.get("collar"):
        d.polygon([(x - h * 0.04, sh_y - h * 0.005), (x + h * 0.04, sh_y - h * 0.005), (x, sh_y + h * 0.06)], fill=A_(look["collar"]))
    # neck
    d.rectangle((neck[0] - r * 0.35, neck[1] - r * 0.4, neck[0] + r * 0.35, sh_y + h * 0.01), fill=A_(sk))
    # arms
    hands = {}
    aw = int(h * 0.052)
    ua, fa = h * 0.17, h * 0.16
    for side, key in ((-1, "la"), (1, "ra")):
        if facing < 0:  # true mirror: swap arms, then flip angles
            key = "ra" if key == "la" else "la"
        a1, a2 = P[key]
        a1 *= facing
        a2 *= facing
        s0 = (x + side * sw * 0.92, sh_y + h * 0.02)
        d1, d2 = _v(a1), _v(a2)
        e = (s0[0] + d1[0] * ua, s0[1] + d1[1] * ua)
        hnd = (e[0] + d2[0] * fa, e[1] + d2[1] * fa)
        d.line([s0, e, hnd], fill=A_(top), width=aw, joint="curve")
        d.ellipse((e[0] - aw / 2, e[1] - aw / 2, e[0] + aw / 2, e[1] + aw / 2), fill=A_(top))
        hr = h * 0.03
        d.ellipse((hnd[0] - hr, hnd[1] - hr, hnd[0] + hr, hnd[1] + hr), fill=A_(look.get("hand", sk)))
        hands["lhand" if side < 0 else "rhand"] = hnd
    # hair back layer
    hair = look["hair"]
    st = look.get("hair_style", "short")
    if st in ("long", "bob"):
        ln = r * (2.4 if st == "long" else 0.95)
        for k in (-1, 1):
            d.rounded_rectangle((hx_ + k * r * 0.86 - r * 0.38, hy_ - r * 0.6, hx_ + k * r * 0.86 + r * 0.38, hy_ + ln), radius=r * 0.36, fill=A_(hair))
    # head
    d.ellipse((hx_ - r, hy_ - r * 1.08, hx_ + r, hy_ + r * 1.08), fill=A_(sk))
    d.ellipse((hx_ - facing * r * 1.0 - r * 0.18, hy_ - r * 0.15, hx_ - facing * r * 1.0 + r * 0.18, hy_ + r * 0.3), fill=A_(sk))
    # hair front
    if st == "bun":
        d.ellipse((hx_ - facing * r * 0.5 - r * 0.55, hy_ - r * 1.75, hx_ - facing * r * 0.5 + r * 0.55, hy_ - r * 0.75), fill=A_(hair))
        d.chord((hx_ - r * 1.05, hy_ - r * 1.15, hx_ + r * 1.05, hy_ + r * 0.35), 180, 360, fill=A_(hair))
    elif st == "short":
        d.chord((hx_ - r * 1.07, hy_ - r * 1.2, hx_ + r * 1.07, hy_ + r * 0.25), 180, 360, fill=A_(hair))
        d.polygon([(hx_ - r * 1.05, hy_ - r * 0.2), (hx_ - r * 0.6, hy_ - r * 0.95), (hx_ + facing * r * 0.3, hy_ - r * 0.6)], fill=A_(hair))
    else:
        d.chord((hx_ - r * 1.15, hy_ - r * 1.2, hx_ + r * 1.15, hy_ + r * 0.45), 180, 360, fill=A_(hair))
        d.polygon([(hx_ + facing * r * 1.1, hy_ - r * 0.2), (hx_ + facing * r * 0.1, hy_ - r * 1.0), (hx_ - facing * r * 0.7, hy_ - r * 0.5)], fill=A_(hair))
    # face
    fx = hx_ + facing * r * 0.18
    ey = hy_ + r * 0.05
    ink = mixc(sk, (40, 25, 20), 0.75)
    blink = (t % 4.3) < 0.13
    for k in (-1, 1):
        ex = fx + k * r * 0.38
        if eyes == "closed" or eyes == "sad" and blink or blink:
            d.arc((ex - r * 0.16, ey - r * 0.12, ex + r * 0.16, ey + r * 0.14), 10, 170, fill=A_(ink), width=max(2, int(r * 0.08)))
        else:
            d.ellipse((ex - r * 0.1, ey - r * 0.13, ex + r * 0.1, ey + r * 0.13), fill=A_(ink))
            d.ellipse((ex - r * 0.03 + r * 0.03, ey - r * 0.08, ex + r * 0.03 + r * 0.03, ey - r * 0.02), fill=A_((255, 255, 255), 0.9))
        by_ = ey - r * 0.36
        bc = A_(mixc(hair, ink, 0.4), 0.8)
        bw = max(2, int(r * 0.06))
        if eyes == "sad":
            # inner end raised: worried, not angry
            inner, outer = (ex - k * r * 0.18, by_ - r * 0.1), (ex + k * r * 0.2, by_ + r * 0.02)
            d.line([inner, outer], fill=bc, width=bw)
        else:
            d.arc((ex - r * 0.2, by_ - r * 0.12, ex + r * 0.2, by_ + r * 0.1), 205, 335, fill=bc, width=bw)
    if look.get("glasses"):
        for k in (-1, 1):
            ex = fx + k * r * 0.38
            d.ellipse((ex - r * 0.27, ey - r * 0.22, ex + r * 0.27, ey + r * 0.22), outline=A_(hx("6b5a4a")), width=max(2, int(r * 0.06)))
        d.line([(fx - r * 0.11, ey), (fx + r * 0.11, ey)], fill=A_(hx("6b5a4a")), width=max(2, int(r * 0.06)))
    d.ellipse((fx - r * 0.65, ey + r * 0.2, fx - r * 0.3, ey + r * 0.45), fill=A_(hx("e8907a"), 0.25))
    d.ellipse((fx + r * 0.3, ey + r * 0.2, fx + r * 0.65, ey + r * 0.45), fill=A_(hx("e8907a"), 0.25))
    my = hy_ + r * 0.58
    mw = r * 0.3
    mc = A_(mixc(sk, hx("8a3a3a"), 0.6))
    mlw = max(2, int(r * 0.09))
    if mouth == "smile":
        d.arc((fx - mw, my - mw * 0.8, fx + mw, my + mw * 0.5), 20, 160, fill=mc, width=mlw)
    elif mouth == "sad":
        d.arc((fx - mw, my - mw * 0.1, fx + mw, my + mw * 1.0), 200, 340, fill=mc, width=mlw)
    elif mouth == "open":
        d.ellipse((fx - mw * 0.45, my - mw * 0.3, fx + mw * 0.45, my + mw * 0.45), fill=mc)
    elif mouth == "talk":
        o = mw * (0.1 + 0.35 * abs(math.sin(t * 9)))
        d.ellipse((fx - mw * 0.45, my - o, fx + mw * 0.45, my + o), fill=mc)
    else:
        d.line([(fx - mw * 0.6, my), (fx + mw * 0.6, my)], fill=mc, width=mlw)
    if look.get("age", 0) > 60:
        for k in (-1, 1):
            d.arc((fx + k * r * 0.38 - r * 0.25, ey + r * 0.05, fx + k * r * 0.38 + r * 0.25, ey + r * 0.3), 20, 160, fill=A_(mixc(sk, ink, 0.3), 0.6),
                  width=max(1, int(r * 0.04)))
    if tears > 0:
        for k in (-1, 1):
            tx = fx + k * r * 0.38
            ln = r * 0.7 * tears
            d.line([(tx, ey + r * 0.15), (tx + k * r * 0.03, ey + r * 0.15 + ln)], fill=A_(hx("bfe3ff"), 0.85), width=max(2, int(r * 0.07)))
    hands["head"] = (hx_, hy_, r)
    return hands


def bouquet(d, x, y, s, t=0, alpha=1.0):
    for i in range(5):
        a = -0.5 + i * 0.25
        d.line([(x, y + s * 0.5), (x + math.sin(a) * s * 0.5, y - s * 0.2)], fill=A(hx("4f7a3a"), alpha), width=max(2, int(s * 0.05)))
    cols = [hx("f28fa8"), hx("ffd27a"), hx("ffffff"), hx("e86a7a"), hx("f5b0c8"), hx("ffc0a0")]
    for i, (dx, dy) in enumerate(((-0.25, -0.3), (0.0, -0.42), (0.25, -0.3), (-0.12, -0.15), (0.14, -0.15), (0, -0.25))):
        cx, cy = x + dx * s, y + dy * s + math.sin(t * 2 + i) * 1.5
        rr = s * 0.13
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=A(cols[i], alpha))
        d.ellipse((cx - rr * 0.35, cy - rr * 0.35, cx + rr * 0.35, cy + rr * 0.35), fill=A(mixc(cols[i], (120, 60, 40), 0.35), alpha))
    d.polygon([(x - s * 0.22, y + s * 0.0), (x + s * 0.22, y + s * 0.0), (x + s * 0.06, y + s * 0.55), (x - s * 0.06, y + s * 0.55)], fill=A(hx("f3ead8"), alpha))


def envelope(d, x, y, s, alpha=1.0):
    d.rectangle((x - s * 0.5, y - s * 0.32, x + s * 0.5, y + s * 0.32), fill=A(hx("fbf6ec"), alpha), outline=A(hx("c9b99a"), alpha), width=2)
    d.line([(x - s * 0.5, y - s * 0.32), (x, y + s * 0.05), (x + s * 0.5, y - s * 0.32)], fill=A(hx("c9b99a"), alpha), width=2)


def chair(d, x, gy, s, col, facing=1):
    dk = mixc(col, (0, 0, 0), 0.25)
    d.rectangle((x - s * 0.28, gy - s * 0.48, x + s * 0.28, gy - s * 0.40), fill=A(col, 1))
    d.rectangle((x - facing * s * 0.28 - 8, gy - s * 1.05, x - facing * s * 0.28 + 8, gy), fill=A(dk, 1))
    xa, xb = sorted((x - facing * s * 0.28 - 8 * facing, x - facing * s * 0.05))
    d.rectangle((xa, gy - s * 1.0, xb, gy - s * 0.92), fill=A(dk, 1))
    d.rectangle((x + facing * s * 0.26 - 7, gy - s * 0.42, x + facing * s * 0.26 + 7, gy), fill=A(dk, 1))


def light_grade(img, warm=(255, 214, 160), strength=0.10):
    """warm colour wash; applied to precomputed backgrounds only (cheap)."""
    arr = np.asarray(img).astype(np.float32)
    arr = arr * (1 - strength) + np.array(warm, np.float32) * strength
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8))


class ReelStyle(Base):
    """Common reel layout: hook text (first 3.4 s), lower-third karaoke captions, end frame."""
    HOOK = ""
    KEYWORD = ""
    ACC = hx("ffd36b")
    xfade = 0.6
    cap = dict(font="montserrat", w=800, size=62, y=1560, fill=(255, 255, 255), hl=hx("ffd36b"), stroke=5, sfill=(20, 14, 10), maxw=900, pop=True)

    def hook(self, img, t):
        if t > 3.6:
            return
        d = D(img)
        a = ease(t / 0.25) * (1 - ease((t - 3.2) / 0.4))
        f = F("montserrat", 80, 900)
        lines = wrap(self.HOOK, f, 940)
        lh = 96
        y0 = 250 - (len(lines) - 1) * lh / 2
        tw = max(f.getlength(l) for l in lines)
        rrect(d, (W / 2 - tw / 2 - 40, y0 - 70, W / 2 + tw / 2 + 40, y0 + (len(lines) - 1) * lh + 70), 26, fill=(15, 10, 8, int(200 * a)))
        for i, l in enumerate(lines):
            text(d, (W / 2, y0 + i * lh), l, f, self.ACC if i == len(lines) - 1 else (255, 255, 255), alpha=a)

    def end_frame(self, img, lt):
        img.paste(gradient(hx("f6dcc0"), hx("e9b98f")))
        d = D(img)
        a = ease(lt / 0.4)
        size = 120
        while len(wrap(self.KEYWORD, F("montserrat", size, 900), 960)) > 2 and size > 60:
            size -= 6
        f = F("montserrat", size, 900)
        n = len(wrap(self.KEYWORD, f, 960))
        hgt = n * size * 1.25
        text(d, (W / 2, 1000 - hgt / 2 - 90), "COMMENT", F("montserrat", 60, 700), hx("7a4a2a"), alpha=a)
        para(d, W / 2, 1000, self.KEYWORD, f, hx("3a2216"), 960, alpha=a)
        heart(d, W / 2, 1000 + hgt / 2 + 100, 90, A(hx("d9534f"), a))

    def frame(self, t):
        img = Base.frame(self, t)
        self.hook(img, t)
        return img

    def show_cap(self, b):
        return b.v.get("k") != "end"


# =====================================================================================
# Data-driven reels: a video module only provides CAST, BGS, NARRATION, SCENES, POST.
# =====================================================================================
GYR = 1380


def _sky(c1, c2, w, h):
    return gradient(c1, c2, w=w, h=h)


def build_bg(kind, p):
    """p: palette dict. Returns a 1080x1920 RGB background."""
    night = p.get("night", False)
    wall1, wall2 = p.get("wall", (hx("f2dcb6"), hx("d9ae80")))
    floor = p.get("floor", hx("8a5a3a"))
    img = gradient(wall1, wall2)
    d = D(img)
    if kind in ("room", "kitchen", "hall", "bedroom", "mansion", "classroom", "hospital", "restaurant", "bakery", "office", "stage"):
        d.rectangle((0, GYR, W, H), fill=A(floor, 1))
        for y in range(GYR, H, 48):
            d.line([(0, y), (W, y)], fill=A(mixc(floor, (0, 0, 0), 0.25), 0.5), width=3)
        sky = p.get("sky", (hx("fff1cf"), hx("ffcf8a")) if not night else (hx("0f1630"), hx("2a2f55")))
        if kind in ("hall", "mansion"):
            for wx in (90, 420, 750):
                s = _sky(sky[0], sky[1], 240, 700)
                img.paste(s, (wx, 300))
                d = D(img)
                d.rounded_rectangle((wx, 300, wx + 240, 1000), radius=0, outline=A(p.get("trim", hx("f7efe2")), 1), width=16)
                d.line([(wx + 120, 300), (wx + 120, 1000)], fill=A(p.get("trim", hx("f7efe2")), 1), width=10)
            if kind == "mansion":
                d.line([(W / 2, 0), (W / 2, 160)], fill=A(hx("c9a85a"), 1), width=6)
                for i in range(7):
                    a = i / 6 * math.pi
                    d.ellipse((W / 2 + math.cos(a) * 140 - 14, 180 + math.sin(a) * 40 - 14, W / 2 + math.cos(a) * 140 + 14, 180 + math.sin(a) * 40 + 14),
                              fill=A(hx("fff2c0"), 1))
                d.ellipse((W / 2 - 160, 150, W / 2 + 160, 240), outline=A(hx("c9a85a"), 1), width=6)
        elif kind not in ("classroom", "stage"):
            wx0, wy0, wx1, wy1 = p.get("win", (70, 330, 470, 1010))
            img.paste(_sky(sky[0], sky[1], wx1 - wx0, wy1 - wy0), (wx0, wy0))
            d = D(img)
            if night:
                d.ellipse((wx1 - 150, wy0 + 60, wx1 - 70, wy0 + 140), fill=A(hx("f3efd8"), 1))
                for i in range(18):
                    rr = random.Random(i)
                    sx, sy = rr.uniform(wx0 + 10, wx1 - 10), rr.uniform(wy0 + 10, wy1 - 200)
                    d.ellipse((sx - 2, sy - 2, sx + 2, sy + 2), fill=A((255, 255, 255), 0.7))
            else:
                d.ellipse(((wx0 + wx1) / 2 - 90, wy0 + 160, (wx0 + wx1) / 2 + 90, wy0 + 340), fill=A((255, 250, 225), 0.75))
                d.rectangle((wx0, wy1 - 250, wx1, wy1), fill=A(p.get("hills", hx("9fbf7a")), 0.7))
            trim = p.get("trim", hx("f7efe2"))
            d.rectangle((wx0, wy0, wx1, wy1), outline=A(trim, 1), width=22)
            d.line([((wx0 + wx1) / 2, wy0), ((wx0 + wx1) / 2, wy1)], fill=A(trim, 1), width=14)
            d.line([(wx0, (wy0 + wy1) / 2), (wx1, (wy0 + wy1) / 2)], fill=A(trim, 1), width=14)
            if p.get("curtain"):
                for cx in (wx0 - 30, wx1 + 10):
                    d.rounded_rectangle((cx - 10, wy0 - 40, cx + 70, wy1 + 90), radius=30, fill=A(p["curtain"], 1))
            if not night:
                d.polygon([(wx0 + 30, wy0 + 40), (wx1, wy0 + 40), (W + 200, GYR + 300), (wx0 + 300, GYR + 300)], fill=A((255, 236, 190), 0.14))
        if kind == "kitchen":
            cab = p.get("cab", hx("e9e2d2"))
            d.rectangle((560, 330, W, 640), fill=A(cab, 1))
            for x in range(560, W, 130):
                d.rectangle((x + 8, 340, x + 122, 630), outline=A(mixc(cab, (0, 0, 0), 0.2), 1), width=4)
            d.rectangle((520, 1040, W, 1100), fill=A(hx("b9a68a"), 1))
            d.rectangle((540, 1100, W, GYR), fill=A(cab, 1))
            d.rectangle((760, 990, 880, 1040), fill=A(hx("3a3a3e"), 1))
        if kind == "bedroom":
            d.rounded_rectangle((520, 1060, W + 40, GYR - 10), radius=30, fill=A(p.get("bed", hx("e8dcc8")), 1))
            d.rounded_rectangle((520, 980, 600, GYR - 10), radius=20, fill=A(hx("6e4a30"), 1))
            d.rounded_rectangle((620, 1010, 800, 1080), radius=30, fill=A((255, 255, 255), 1))
        if kind == "classroom":
            d.rectangle((120, 380, 960, 860), fill=A(hx("2f4a3a"), 1))
            d.rectangle((120, 380, 960, 860), outline=A(hx("8a6a44"), 1), width=18)
            d.rectangle((120, 860, 960, 880), fill=A(hx("8a6a44"), 1))
        if kind == "hospital":
            d.rectangle((560, 640, 760, 820), fill=A(hx("1c2a2a"), 1))
            pts = [(570 + i * 10, 730 + (40 if i % 6 == 3 else (-40 if i % 6 == 4 else 0))) for i in range(19)]
            d.line(pts, fill=A(hx("6affc0"), 1), width=4)
            d.rectangle((650, 820, 670, 1100), fill=A(hx("9aa4a4"), 1))
        if kind == "restaurant":
            for x in (200, 540, 880):
                d.ellipse((x - 40, 330, x + 40, 410), fill=A(hx("ffd28a"), 0.9))
                d.ellipse((x - 120, 250, x + 120, 490), fill=A(hx("ffd28a"), 0.08))
            d.rectangle((0, 1050, W, 1090), fill=A(hx("6a2e2a"), 1))
        if kind == "bakery":
            for y in (420, 620, 820):
                d.rectangle((560, y, W, y + 18), fill=A(hx("7a5236"), 1))
                for x in range(580, W, 90):
                    d.ellipse((x, y - 60, x + 80, y + 4), fill=A(hx("d9a05a"), 1))
                    d.arc((x + 10, y - 50, x + 70, y - 10), 200, 340, fill=A(hx("b37a3a"), 1), width=4)
            d.rectangle((520, 1060, W, GYR), fill=A(hx("8a5a3a"), 1))
        if kind == "office":
            d.rectangle((560, 1040, W, 1080), fill=A(hx("5a4636"), 1))
            d.rectangle((600, 1080, 640, GYR), fill=A(hx("4a3a2c"), 1))
            d.rectangle((760, 900, 960, 1040), fill=A(hx("22262e"), 1))
            d.rectangle((775, 915, 945, 1025), fill=A(hx("8fb4d8"), 0.9))
        if kind == "stage":
            d.rectangle((0, 0, W, 260), fill=A(p.get("curtain", hx("7a1f2a")), 1))
            for x in range(0, W, 90):
                d.line([(x, 0), (x + 20, 260)], fill=A((0, 0, 0), 0.15), width=10)
            d.polygon([(W / 2 - 300, 0), (W / 2 + 300, 0), (W / 2 + 520, GYR), (W / 2 - 520, GYR)], fill=A((255, 240, 200), 0.1))
    elif kind in ("street", "park", "busstop", "garden", "farm", "cemetery", "porch"):
        sky = p.get("sky", (hx("ffd9a8"), hx("f6efe2")) if not night else (hx("0c1226"), hx("2a2f55")))
        img = gradient(sky[0], sky[1])
        d = D(img)
        ground = p.get("ground", hx("7c8c63"))
        if kind in ("street", "busstop"):
            city(d, 1150, p.get("bld", hx("8a7a72") if not night else hx("151827")), seed=p.get("seed", 3), h=(250, 650),
                 win=hx("ffd27a") if night else None)
            d.rectangle((0, 1150, W, GYR), fill=A(hx("9a948c") if not night else hx("3a3a42"), 1))
            d.rectangle((0, GYR, W, H), fill=A(hx("4a4a50") if not night else hx("1e1e24"), 1))
            for x in range(0, W, 180):
                d.rectangle((x, GYR + 200, x + 100, GYR + 220), fill=A(hx("e8e2d0"), 0.6))
            if night:
                for x in (180, 820):
                    d.line([(x, 700), (x, GYR)], fill=A(hx("15151a"), 1), width=10)
                    d.polygon([(x - 30, 700), (x + 30, 700), (x + 220, GYR), (x - 220, GYR)], fill=A(hx("ffd890"), 0.1))
                    d.ellipse((x - 26, 680, x + 26, 720), fill=A(hx("ffe6b0"), 1))
            if kind == "busstop":
                d.rectangle((520, 820, 1060, 850), fill=A(hx("3a4a5a"), 1))
                d.rectangle((540, 850, 560, GYR), fill=A(hx("3a4a5a"), 1))
                d.rectangle((1020, 850, 1040, GYR), fill=A(hx("3a4a5a"), 1))
                d.rectangle((600, 1180, 980, 1210), fill=A(hx("5a4a3a"), 1))
                d.rectangle((560, 860, 1020, 1150), fill=A(hx("cfe3ef"), 0.25))
        else:
            for i in range(9):
                x = i * 140 - 40
                d.ellipse((x - 140, 900, x + 160, 1220), fill=A(p.get("trees", hx("6f7d62")), 0.85))
            d.rectangle((0, 1120, W, H), fill=A(ground, 1))
            if kind == "park":
                d.rectangle((560, 1230, 980, 1260), fill=A(hx("7a5236"), 1))
                d.rectangle((560, 1170, 980, 1195), fill=A(hx("7a5236"), 1))
                for x in (590, 950):
                    d.rectangle((x - 8, 1260, x + 8, 1320), fill=A(hx("3a3030"), 1))
            if kind == "farm":
                for y in range(1180, H, 60):
                    d.line([(0, y), (W, y + 30)], fill=A(mixc(ground, (0, 0, 0), 0.2), 0.6), width=8)
                d.polygon([(760, 1000), (900, 920), (1040, 1000)], fill=A(hx("8a3a2a"), 1))
                d.rectangle((780, 1000, 1020, 1130), fill=A(hx("b0543a"), 1))
            if kind == "porch":
                d.rectangle((420, 520, W, 1130), fill=A(p.get("house", hx("e8d6b8")), 1))
                d.rectangle((640, 760, 860, 1130), fill=A(hx("6e4a30"), 1))
                d.ellipse((820, 940, 840, 960), fill=A(hx("d9b45a"), 1))
                d.polygon([(380, 520), (W + 40, 520), (W + 40, 420), (700, 320)], fill=A(hx("7a3a2a"), 1))
            if kind == "cemetery":
                rnd = random.Random(3)
                for i in range(7):
                    x, y = rnd.uniform(40, W - 40), rnd.uniform(1130, 1220)
                    d.rounded_rectangle((x - 34, y - 70, x + 34, y + 20), radius=26, fill=A(hx("a4a39e"), 1))
        if night:
            d.ellipse((800, 200, 900, 300), fill=A(hx("f3efd8"), 1))
    elif kind in ("beach", "road"):
        sky = p.get("sky", (hx("ff9a6a"), hx("ffd9a0")))
        img = gradient(sky[0], sky[1])
        d = D(img)
        if kind == "beach":
            d.ellipse((W / 2 - 130, 820, W / 2 + 130, 1080), fill=A(hx("fff0c0"), 0.9))
            d.rectangle((0, 980, W, 1200), fill=A(p.get("sea", hx("3a7ab0")), 1))
            for i in range(10):
                y = 1000 + i * 20
                d.line([(0, y), (W, y)], fill=A((255, 230, 190), 0.12 + 0.02 * i), width=3)
            d.rectangle((0, 1200, W, H), fill=A(p.get("sand", hx("e8c890")), 1))
            d.polygon([(0, 1200), (W, 1200), (W, 1240), (0, 1260)], fill=A((255, 255, 255), 0.5))
        else:
            for i in range(9):
                x = i * 140 - 40
                d.ellipse((x - 140, 920, x + 160, 1200), fill=A(p.get("trees", hx("4a5a62")), 0.8))
            d.rectangle((0, 1100, W, H), fill=A(p.get("ground", hx("5a6a5a")), 1))
            d.polygon([(W * 0.62, 1100), (W * 0.7, 1100), (W * 1.3, H), (W * 0.1, H)], fill=A(hx("4a4a50"), 1))
            for i in range(6):
                y = 1120 + i * i * 22
                d.line([(W * 0.66 + i * 30, y), (W * 0.66 + i * 36, y + 20 + i * 6)], fill=A(hx("e8e2d0"), 0.7), width=4 + i)
    elif kind == "car":
        img = gradient(hx("0b0d14"), hx("161a24"))
        d = D(img)
        sky = p.get("sky", (hx("0c1226"), hx("232a45")))
        img.paste(_sky(sky[0], sky[1], W, 700), (0, 300))
        d = D(img)
        city(d, 1000, hx("0f121c"), seed=8, h=(80, 320), win=hx("ffcf7a"))
        for i in range(6):
            x = 100 + i * 170
            d.ellipse((x - 20, 940, x + 20, 980), fill=A(hx("ffefc0"), 0.6))
        d.polygon([(0, 300), (W, 300), (W, 360), (0, 330)], fill=A(hx("07080c"), 1))
        d.rectangle((0, 1000, W, H), fill=A(hx("12141a"), 1))
        d.rounded_rectangle((-50, 980, W + 50, 1150), radius=60, fill=A(hx("1c1f27"), 1))
        d.ellipse((560, 900, 1000, 1340), outline=A(hx("2a2d36"), 1), width=36)
        d.line([(780, 1120), (780, 1340)], fill=A(hx("2a2d36"), 1), width=30)
    if p.get("grade"):
        img = light_grade(img, p["grade"], p.get("grade_s", 0.08))
    return vignette(texture(img, 4, 2), 0.45)


def prop(d, name, x, y, s=1.0, t=0.0, col=None):
    c = col
    if name == "armchair":
        armchair_(d, x, y, 380 * s, c or hx("b8695a"))
    elif name == "chair":
        chair(d, x, y, 380 * s, c or hx("7a5236"), facing=1 if s > 0 else -1)
    elif name == "chair_l":
        chair(d, x, y, 380, c or hx("7a5236"), facing=-1)
    elif name == "table":
        w = 300 * s
        d.rectangle((x - w, y - 30, x + w, y), fill=A(c or hx("f3ead8"), 1))
        d.polygon([(x - w, y), (x + w, y), (x + w - 20, y + 80), (x - w + 20, y + 80)], fill=A(c or hx("f3ead8"), 1))
        for k in (-1, 1):
            d.rectangle((x + k * (w - 40) - 10, y + 80, x + k * (w - 40) + 10, GYR), fill=A(hx("6e4a30"), 1))
    elif name == "plate":
        d.ellipse((x - 60 * s, y - 16 * s, x + 60 * s, y + 16 * s), fill=A((250, 250, 250), 1), outline=A(hx("c9c2b4"), 1), width=3)
    elif name == "food":
        d.ellipse((x - 60 * s, y - 16 * s, x + 60 * s, y + 16 * s), fill=A((250, 250, 250), 1))
        d.ellipse((x - 38 * s, y - 22 * s, x + 38 * s, y + 6 * s), fill=A(c or hx("d98a4a"), 1))
    elif name == "pot":
        d.rounded_rectangle((x - 70 * s, y - 80 * s, x + 70 * s, y), radius=18 * s, fill=A(c or hx("6a6a70"), 1))
        d.rectangle((x - 82 * s, y - 86 * s, x + 82 * s, y - 72 * s), fill=A(mixc(c or hx("6a6a70"), (0, 0, 0), 0.2), 1))
        for k in (-1, 1):
            d.rectangle((x + k * 82 * s - 14 * s, y - 64 * s, x + k * 82 * s + 14 * s, y - 52 * s), fill=A(hx("2a2a2e"), 1))
        d.ellipse((x - 50 * s, y - 96 * s, x + 50 * s, y - 76 * s), fill=A(hx("e8dcc0"), 1))
    elif name == "bouquet":
        bouquet(d, x, y, 120 * s, t)
    elif name == "envelope":
        envelope(d, x, y, 100 * s)
    elif name == "phone":
        d.rounded_rectangle((x - 30 * s, y - 52 * s, x + 30 * s, y + 52 * s), radius=10 * s, fill=A(hx("0f0f12"), 1))
        d.rounded_rectangle((x - 24 * s, y - 44 * s, x + 24 * s, y + 44 * s), radius=6 * s, fill=A(c or hx("9fc3ff"), 0.95))
    elif name == "shoes_old":
        for k in (0, 1):
            xx = x + k * 90 * s
            d.chord((xx - 50 * s, y - 50 * s, xx + 50 * s, y + 10 * s), 180, 360, fill=A(hx("6a5242"), 1))
            d.rectangle((xx - 50 * s, y - 20 * s, xx + 50 * s, y), fill=A(hx("6a5242"), 1))
            d.line([(xx - 20 * s, y - 35 * s), (xx + 5 * s, y - 15 * s)], fill=A(hx("3a2a20"), 1), width=4)
            d.ellipse((xx + 10 * s, y - 30 * s, xx + 26 * s, y - 16 * s), fill=A(hx("3a2a20"), 1))
    elif name == "shoes_new":
        for k in (0, 1):
            xx = x + k * 80 * s
            d.chord((xx - 42 * s, y - 42 * s, xx + 42 * s, y + 8 * s), 180, 360, fill=A(c or hx("e8eef5"), 1))
            d.rectangle((xx - 42 * s, y - 16 * s, xx + 42 * s, y), fill=A(c or hx("e8eef5"), 1))
            d.line([(xx - 42 * s, y - 4 * s), (xx + 42 * s, y - 4 * s)], fill=A(hx("4a7ad9"), 1), width=6)
    elif name == "jar":
        d.rounded_rectangle((x - 60 * s, y - 150 * s, x + 60 * s, y), radius=24 * s, fill=A(hx("dbeef2"), 0.55), outline=A(hx("a9c6cc"), 1), width=4)
        d.rectangle((x - 50 * s, y - 175 * s, x + 50 * s, y - 150 * s), fill=A(hx("b08a4a"), 1))
        for i in range(14):
            rr = random.Random(i)
            cx, cy = x + rr.uniform(-40, 40) * s, y - rr.uniform(10, 100) * s
            d.ellipse((cx - 14 * s, cy - 6 * s, cx + 14 * s, cy + 6 * s), fill=A(hx("d9b45a") if i % 3 else hx("b9b9b9"), 1))
        for i in range(4):
            rr = random.Random(i + 40)
            cx, cy = x + rr.uniform(-30, 30) * s, y - rr.uniform(60, 130) * s
            d.rectangle((cx - 16 * s, cy - 8 * s, cx + 16 * s, cy + 8 * s), fill=A(hx("fbf6ec"), 1))
    elif name == "bowl":
        d.chord((x - 70 * s, y - 70 * s, x + 70 * s, y + 30 * s), 0, 180, fill=A(c or hx("a0703c"), 1))
        d.line([(x - 70 * s, y - 20 * s), (x + 70 * s, y - 20 * s)], fill=A(mixc(c or hx("a0703c"), (0, 0, 0), 0.3), 1), width=5)
    elif name == "bread":
        d.ellipse((x - 70 * s, y - 40 * s, x + 70 * s, y + 20 * s), fill=A(hx("d9a05a"), 1))
        for k in (-30, 0, 30):
            d.arc((x + k * s - 18 * s, y - 34 * s, x + k * s + 18 * s, y - 4 * s), 200, 340, fill=A(hx("a8703a"), 1), width=4)
    elif name == "basket":
        d.chord((x - 120 * s, y - 120 * s, x + 120 * s, y + 40 * s), 0, 180, fill=A(hx("b88a4a"), 1))
        for k in range(-2, 3):
            prop(d, "bread", x + k * 45 * s, y - 50 * s, 0.6 * s)
        d.chord((x - 120 * s, y - 60 * s, x + 120 * s, y + 40 * s), 0, 180, fill=A(hx("b88a4a"), 1))
    elif name == "bike":
        cc = c or hx("c0392b")
        for k in (-1, 1):
            d.ellipse((x + k * 120 * s - 80 * s, y - 160 * s, x + k * 120 * s + 80 * s, y), outline=A(hx("222222"), 1), width=int(10 * s))
        d.line([(x - 120 * s, y - 80 * s), (x - 10 * s, y - 80 * s), (x + 120 * s, y - 80 * s), (x + 40 * s, y - 190 * s), (x - 60 * s, y - 190 * s),
                (x - 10 * s, y - 80 * s)], fill=A(cc, 1), width=int(12 * s), joint="curve")
        d.line([(x + 40 * s, y - 190 * s), (x + 60 * s, y - 230 * s), (x + 100 * s, y - 230 * s)], fill=A(hx("222222"), 1), width=int(10 * s))
        d.ellipse((x - 90 * s, y - 210 * s, x - 30 * s, y - 190 * s), fill=A(hx("222222"), 1))
    elif name == "medicine":
        d.rounded_rectangle((x - 30 * s, y - 80 * s, x + 30 * s, y), radius=10 * s, fill=A(hx("e9a23a"), 0.9))
        d.rectangle((x - 26 * s, y - 96 * s, x + 26 * s, y - 80 * s), fill=A((250, 250, 250), 1))
    elif name == "bed":
        d.rounded_rectangle((x - 300 * s, y - 220 * s, x + 300 * s, y - 80 * s), radius=30 * s, fill=A(c or hx("e8eef0"), 1))
        d.rectangle((x - 300 * s, y - 80 * s, x - 280 * s, y), fill=A(hx("9aa4a4"), 1))
        d.rectangle((x + 280 * s, y - 80 * s, x + 300 * s, y), fill=A(hx("9aa4a4"), 1))
        d.rounded_rectangle((x - 300 * s, y - 330 * s, x - 270 * s, y - 80 * s), radius=10, fill=A(hx("9aa4a4"), 1))
    elif name == "patient":  # person lying in bed (head + blanket)
        d.rounded_rectangle((x - 230 * s, y - 280 * s, x + 260 * s, y - 200 * s), radius=40 * s, fill=A(c or hx("a8c6d8"), 1))
        d.ellipse((x - 290 * s, y - 300 * s, x - 200 * s, y - 210 * s), fill=A(SKIN["fair"], 1))
        d.chord((x - 292 * s, y - 302 * s, x - 198 * s, y - 230 * s), 180, 360, fill=A(hx("dcd6cc"), 1))
        d.arc((x - 262 * s, y - 262 * s, x - 236 * s, y - 248 * s), 10, 170, fill=A(hx("3a2a20"), 1), width=3)
    elif name == "tree":
        tc = c or hx("5d8a4a")
        d.rectangle((x - 30 * s, y - 420 * s, x + 30 * s, y), fill=A(hx("6e4a30"), 1))
        for (dx, dy, r) in ((0, -560, 210), (-150, -460, 160), (150, -460, 160), (-70, -680, 150), (90, -660, 150)):
            d.ellipse((x + (dx - r) * s, y + (dy - r) * s, x + (dx + r) * s, y + (dy + r) * s), fill=A(tc, 1))
        if s > 0.7 and col is None:
            for i in range(8):
                rr = random.Random(i)
                fx, fy = x + rr.uniform(-220, 220) * s, y + rr.uniform(-720, -400) * s
                d.ellipse((fx - 16 * s, fy - 16 * s, fx + 16 * s, fy + 16 * s), fill=A(hx("f2a63a"), 1))
    elif name == "sapling":
        d.line([(x, y), (x, y - 160 * s)], fill=A(hx("6e4a30"), 1), width=int(10 * s))
        for k in (-1, 1):
            d.ellipse((x + k * 40 * s - 40 * s, y - 180 * s, x + k * 40 * s + 40 * s, y - 130 * s), fill=A(hx("6fa85a"), 1))
        d.chord((x - 70 * s, y - 20 * s, x + 70 * s, y + 30 * s), 180, 360, fill=A(hx("6e4a30"), 1))
    elif name == "umbrella":
        d.chord((x - 220 * s, y - 120 * s, x + 220 * s, y + 120 * s), 180, 360, fill=A(c or hx("c0392b"), 1))
        d.line([(x, y), (x, y + 260 * s)], fill=A(hx("2a2a2a"), 1), width=8)
    elif name == "rain":
        rain(d, t, (200, 215, 235), n=180, alpha=0.35, speed=1400)
    elif name == "diploma":
        d.rectangle((x - 70 * s, y - 20 * s, x + 70 * s, y + 20 * s), fill=A(hx("f3ead8"), 1))
        d.rectangle((x - 8 * s, y - 22 * s, x + 8 * s, y + 22 * s), fill=A(hx("c0392b"), 1))
    elif name == "cap_gown":
        d.polygon([(x - 90 * s, y), (x, y - 40 * s), (x + 90 * s, y), (x, y + 40 * s)], fill=A(hx("1c1c22"), 1))
        d.line([(x + 40 * s, y), (x + 60 * s, y + 70 * s)], fill=A(hx("d9b45a"), 1), width=5)
    elif name == "podium":
        d.polygon([(x - 140, y - 300), (x + 140, y - 300), (x + 110, y), (x - 110, y)], fill=A(c or hx("5a3a24"), 1))
        d.rectangle((x - 160, y - 320, x + 160, y - 290), fill=A(mixc(c or hx("5a3a24"), (0, 0, 0), 0.2), 1))
    elif name == "audience":
        for i in range(9):
            xx = 60 + i * 120
            d.ellipse((xx - 38, y - 40, xx + 38, y + 36), fill=A(c or hx("2a2026"), 1))
            d.rounded_rectangle((xx - 55, y + 30, xx + 55, y + 200), radius=30, fill=A(c or hx("2a2026"), 1))
    elif name == "bus":
        d.rounded_rectangle((x - 520, y - 420, x + 520, y - 40), radius=40, fill=A(c or hx("e8b43a"), 1))
        for i in range(6):
            d.rectangle((x - 470 + i * 160, y - 370, x - 350 + i * 160, y - 250), fill=A(hx("2a3440"), 1))
        for k in (-330, 330):
            d.ellipse((x + k - 70, y - 120, x + k + 70, y + 20), fill=A(hx("1c1c1c"), 1))
    elif name == "mopbucket":
        d.rectangle((x - 60, y - 90, x + 60, y), fill=A(hx("e8b43a"), 1))
        d.line([(x + 20, y - 80), (x + 80, y - 420)], fill=A(hx("8a6a44"), 1), width=10)
    elif name == "money":
        for i in range(4):
            d.rectangle((x - 70 * s, y - 14 * s - i * 12 * s, x + 70 * s, y - i * 12 * s), fill=A(hx("7fb37a"), 1), outline=A(hx("4a7a46"), 1), width=2)
    elif name == "gift":
        d.rectangle((x - 60 * s, y - 100 * s, x + 60 * s, y), fill=A(c or hx("d9534f"), 1))
        d.rectangle((x - 10 * s, y - 100 * s, x + 10 * s, y), fill=A(hx("f7e3a0"), 1))
    elif name == "candle":
        candle(d, x, y, 160 * s, hx("f3ead8"), t=t)
    elif name == "lamp":
        d.polygon([(x - 60, y - 520), (x + 60, y - 520), (x + 90, y - 430), (x - 90, y - 430)], fill=A(hx("f5c87a"), 1))
        d.line([(x, y - 430), (x, y)], fill=A(hx("2a2a2a"), 1), width=8)
        d.ellipse((x - 260, y - 640, x + 260, y - 300), fill=A((255, 200, 120), 0.07))
    elif name == "suitcase":
        d.rounded_rectangle((x - 90 * s, y - 150 * s, x + 90 * s, y), radius=16 * s, fill=A(c or hx("4a5a7a"), 1))
        d.rounded_rectangle((x - 30 * s, y - 180 * s, x + 30 * s, y - 150 * s), radius=8, outline=A(hx("222222"), 1), width=6)
    elif name == "photo":
        d.rectangle((x - 70 * s, y - 90 * s, x + 70 * s, y + 90 * s), fill=A(hx("7a5236"), 1))
        d.rectangle((x - 56 * s, y - 76 * s, x + 56 * s, y + 76 * s), fill=A(hx("e9d6b8"), 1))
        d.ellipse((x - 22 * s, y - 50 * s, x + 22 * s, y - 6 * s), fill=A(hx("c9a883"), 1))
        d.chord((x - 40 * s, y - 4 * s, x + 40 * s, y + 70 * s), 180, 360, fill=A(hx("c9a883"), 1))
    elif name == "papers":
        for i in range(3):
            d.polygon([(x - 80 * s + i * 8, y - 10 - i * 6), (x + 80 * s + i * 8, y - 10 - i * 6), (x + 70 * s + i * 8, y + 20 - i * 6),
                       (x - 90 * s + i * 8, y + 20 - i * 6)], fill=A((250, 250, 245), 1), outline=A(hx("c9c2b4"), 1))
    elif name == "ringing":
        prop(d, "phone", x, y, s, t, hx("bfe3ff"))
        for i in range(3):
            rr = 50 + ((t * 110 + i * 45) % 135)
            for sg in (-1, 1):
                d.arc((x - rr, y - rr, x + rr, y + rr), (-50 if sg > 0 else 130), (50 if sg > 0 else 230), fill=A((220, 235, 255), 0.6 * (1 - rr / 185)), width=4)
    elif name == "cup":
        d.rounded_rectangle((x - 30 * s, y - 50 * s, x + 30 * s, y), radius=10 * s, fill=A(c or hx("f6f1e8"), 1))
        d.arc((x + 18 * s, y - 40 * s, x + 50 * s, y - 12 * s), -90, 90, fill=A(c or hx("f6f1e8"), 1), width=int(7 * s))
        d.ellipse((x - 42 * s, y - 8 * s, x + 42 * s, y + 8 * s), fill=A(hx("e8e2d6"), 1))
    elif name == "steam":
        for i in range(3):
            yy = y - ((t * 40 + i * 25) % 75)
            d.arc((x - 14 + i * 8, yy - 20, x + 6 + i * 8, yy), 90, 270, fill=A((255, 255, 255), 0.5 * (1 - ((t * 40 + i * 25) % 75) / 75)), width=3)
    elif name == "bricks":
        for r_ in range(int(5 * s)):
            for c_ in range(5):
                bx = x - 150 + c_ * 62 + (31 if r_ % 2 else 0)
                by = y - (r_ + 1) * 32
                d.rectangle((bx, by, bx + 58, by + 28), fill=A(hx("b0543a"), 1), outline=A(hx("7a3424"), 1), width=2)
    elif name == "book":
        d.rectangle((x - 60 * s, y - 80 * s, x + 60 * s, y), fill=A(c or hx("6a4a7a"), 1))
        d.rectangle((x - 50 * s, y - 74 * s, x + 54 * s, y - 6 * s), fill=A(hx("f3ead8"), 1))
        d.rectangle((x - 60 * s, y - 80 * s, x - 48 * s, y), fill=A(mixc(c or hx("6a4a7a"), (0, 0, 0), 0.3), 1))
    elif name == "box":
        d.rectangle((x - 80 * s, y - 70 * s, x + 80 * s, y), fill=A(c or hx("d9a05a"), 1))
        d.rectangle((x - 86 * s, y - 84 * s, x + 86 * s, y - 64 * s), fill=A(mixc(c or hx("d9a05a"), (0, 0, 0), 0.15), 1))
    elif name == "broom":
        d.line([(x, y), (x + 60 * s, y - 420 * s)], fill=A(hx("8a6a44"), 1), width=int(10 * s))
        d.polygon([(x - 50 * s, y + 10), (x + 40 * s, y + 10), (x + 20 * s, y - 60 * s), (x - 20 * s, y - 60 * s)], fill=A(hx("d9b45a"), 1))
    elif name == "dash":
        d.rounded_rectangle((-50, y, W + 50, y + 200), radius=60, fill=A(hx("1c1f27"), 1))
        d.rectangle((0, y + 150, W, H), fill=A(hx("12141a"), 1))
        d.ellipse((x - 230, y - 120, x + 230, y + 340), outline=A(hx("2a2d36"), 1), width=36)


def armchair_(d, x, gy, s, col):
    dk = mixc(col, (0, 0, 0), 0.25)
    d.rounded_rectangle((x - s * 0.55, gy - s * 1.15, x + s * 0.55, gy - s * 0.35), radius=s * 0.18, fill=A(dk, 1))
    d.rounded_rectangle((x - s * 0.62, gy - s * 0.55, x + s * 0.62, gy - s * 0.25), radius=s * 0.1, fill=A(col, 1))
    for k in (-1, 1):
        d.rounded_rectangle((x + k * s * 0.62 - s * 0.14, gy - s * 0.75, x + k * s * 0.62 + s * 0.14, gy - s * 0.25), radius=s * 0.08, fill=A(col, 1))
        d.rectangle((x + k * s * 0.5 - 8, gy - s * 0.25, x + k * s * 0.5 + 8, gy), fill=A(hx("4a3020"), 1))


HELD = {"bouquet": (0, -20, 1.0), "envelope": (30, -10, 1.0), "phone": (0, 25, 0.7), "pot": (0, 40, 0.9), "bread": (0, -10, 0.7),
        "jar": (0, 60, 0.6), "bowl": (0, 10, 0.7), "diploma": (20, 0, 1.0), "medicine": (0, 10, 0.6), "money": (30, 10, 0.8),
        "shoes_new": (-40, 30, 0.6), "gift": (0, 40, 0.8), "umbrella": (0, -260, 0.9), "letter": (30, -10, 1.0), "papers": (40, 0, 0.6), "cup": (10, 20, 0.9), "book": (20, 30, 0.8), "box": (0, 30, 0.7), "broom": (0, 200, 0.9)}


# series defaults (imported into each reel module)
VOICES = {"n": ("af_heart", 0.8)}  # the one clean narrator for the whole series
GAP = 0.9
LEAD = 0.15
END_HOLD = 0.0
CAP_WORDS = 4


class DataReel(ReelStyle):
    xfade = 0.35

    def setup(self):
        m = self.tl.mod
        self.HOOK, self.KEYWORD = m.HOOK, m.KEYWORD
        self.CAST = m.CAST
        self.bgs = {k: build_bg(kind, pal) for k, (kind, pal) in m.BGS.items()}
        self.BG = next(iter(self.bgs.values()))
        rnd = random.Random(1)
        self.dust = [(rnd.uniform(60, 1000), rnd.uniform(400, 1350)) for _ in range(36)]

    def bg(self, t):
        return self.BG.copy()

    def actor(self, d, a, lt, b, t):
        look = self.CAST[a["who"]]
        dur = max(1.0, b.dur)
        at = a.get("at", 0.5)
        sw = lt >= (at * dur if at <= 1 else at)
        g = lambda k, dflt: a.get(k + "2", a.get(k, dflt)) if sw else a.get(k, dflt)
        x = a.get("x", W / 2)
        pose = g("p", "stand")
        if "from" in a:
            wd = a.get("walk", 2.5)
            x = lerp(a["from"], a["x"], eio(lt / wd))
        tears = a.get("tears", 0)
        if isinstance(tears, str):
            tears = ease((lt - float(tears)) / 1.2)
        if sw and "tears2" in a:
            tears = a["tears2"]
        hd = person(d, x, a.get("gy", GYR), a.get("h", look.get("h", 900)), look, pose, t + x * 0.01, facing=g("f", 1), eyes=g("e", "open"),
                    mouth=g("m", "soft"), tears=tears, alpha=ease((lt - a.get("delay", 0)) / 0.4) if a.get("delay") else 1.0)
        hold = g("hold", None)
        if hold:
            hand = hd["rhand"] if a.get("hand", "r") == "r" else hd["lhand"]
            ox, oy, s = HELD.get(hold, (0, 0, 1.0))
            f = g("f", 1)
            if pose in ("hold", "hug", "sit_hold", "carry_both", "kneel_pray", "pray"):
                hand = ((hd["rhand"][0] + hd["lhand"][0]) / 2, (hd["rhand"][1] + hd["lhand"][1]) / 2)
                ox = 0
            prop(d, "envelope" if hold == "letter" else hold, hand[0] + ox * f, hand[1] + oy, s, t)
        return hd

    def draw(self, img, b, lt, t):
        v = b.v
        if v.get("k") == "end":
            self.end_frame(img, lt)
            return
        img.paste(self.bgs[v["bg"]])
        d = D(img)
        for pr in v.get("back", []):
            prop(d, pr[0], pr[1], pr[2], pr[3] if len(pr) > 3 else 1.0, t, pr[4] if len(pr) > 4 else None)
        for a in v.get("actors", []):
            self.actor(d, a, lt, b, t)
        for pr in v.get("props", []):
            prop(d, pr[0], pr[1], pr[2], pr[3] if len(pr) > 3 else 1.0, t, pr[4] if len(pr) > 4 else None)
        fx = v.get("fx", [])
        if "dust" in fx:
            for i, (x, y) in enumerate(self.dust):
                yy = y + math.sin(t * 0.4 + i) * 20
                xx = x + math.cos(t * 0.3 + i * 2) * 14
                d.ellipse((xx - 2.5, yy - 2.5, xx + 2.5, yy + 2.5), fill=A((255, 245, 210), 0.3 + 0.2 * math.sin(t + i)))
        if "rain" in fx:
            rain(d, t, (200, 215, 235), n=180, alpha=0.3, speed=1400)
        if "snow" in fx:
            particles(d, t, (255, 255, 255), n=90, alpha=0.6, speed=-60, r=(2, 5))
        if "glow" in fx:
            d.rectangle((0, 0, W, H), fill=(255, 225, 180, int(45 * ease(lt / 3))))
        if "dark" in fx:
            d.rectangle((0, 0, W, H), fill=(0, 0, 10, 70))
        if "flash" in fx:
            d.rectangle((0, 0, W, H), fill=(255, 240, 210, int(110 * (1 - ease(lt / 1.2)))))


def make_beats(narration, scenes, last_gap=1.0, end=2.3):
    lines = [l.strip() for l in narration.strip().split("\n") if l.strip()]
    assert len(lines) == len(scenes), (len(lines), len(scenes))
    beats = [dict(say=l, v=s) for l, s in zip(lines, scenes)]
    beats[0]["sfx"] = [("hit", 0.0, 0.3)]
    beats[-1]["gap"] = last_gap
    beats.append(dict(say="", v=dict(k="end"), gap=end))
    return beats
