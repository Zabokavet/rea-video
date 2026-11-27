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
    sit = P.get("sit", False)
    hip_y = gy - h * (0.30 if sit else 0.47) + by
    sh_y = hip_y - h * 0.33
    tilt = math.radians(P.get("tilt", 0) * facing)
    neck = (x + math.sin(tilt) * h * 0.02, sh_y - h * 0.02)
    hx_, hy_ = neck[0] + math.sin(tilt) * r * 1.3, neck[1] - r * 1.15
    sw, hw = h * 0.115, h * 0.10
    top, bot = look["top"], look["bottom"]
    # legs
    lw = int(h * 0.06)
    shoe = look.get("shoes", hx("3a2a22"))
    if sit:
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
        hem = (hip_y + h * 0.27) if not sit else hip_y + h * 0.06
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
        a1, a2 = P[key]
        a1 *= facing if side == 1 else facing
        a2 *= facing if side == 1 else facing
        s0 = (x + side * sw * 0.92, sh_y + h * 0.02)
        d1, d2 = _v(a1), _v(a2)
        e = (s0[0] + d1[0] * ua, s0[1] + d1[1] * ua)
        hnd = (e[0] + d2[0] * fa, e[1] + d2[1] * fa)
        d.line([s0, e, hnd], fill=A_(top), width=aw, joint="curve")
        d.ellipse((e[0] - aw / 2, e[1] - aw / 2, e[0] + aw / 2, e[1] + aw / 2), fill=A_(top))
        hr = h * 0.03
        d.ellipse((hnd[0] - hr, hnd[1] - hr, hnd[0] + hr, hnd[1] + hr), fill=A_(sk))
        hands["lhand" if side < 0 else "rhand"] = hnd
    # hair back layer
    hair = look["hair"]
    st = look.get("hair_style", "short")
    if st in ("long", "bob"):
        ln = r * (2.4 if st == "long" else 0.95)
        for k in (-1, 1):
            d.rounded_rectangle((hx_ + k * r * 0.55 - r * 0.62, hy_ - r * 0.6, hx_ + k * r * 0.55 + r * 0.62, hy_ + ln), radius=r * 0.5, fill=A_(hair))
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
    d.rectangle((x - facing * s * 0.28 - 8, gy - s * 1.0, x - facing * s * 0.05, gy - s * 0.92), fill=A(dk, 1))
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
        f = F("montserrat", 84, 900)
        lines = wrap(self.HOOK, f, 920)
        lh = 96
        y0 = 330 - (len(lines) - 1) * lh / 2
        tw = max(f.getlength(l) for l in lines)
        rrect(d, (W / 2 - tw / 2 - 40, y0 - 70, W / 2 + tw / 2 + 40, y0 + (len(lines) - 1) * lh + 70), 26, fill=(15, 10, 8, int(200 * a)))
        for i, l in enumerate(lines):
            text(d, (W / 2, y0 + i * lh), l, f, self.ACC if i == len(lines) - 1 else (255, 255, 255), alpha=a)

    def end_frame(self, img, lt):
        img.paste(gradient(hx("f6dcc0"), hx("e9b98f")))
        d = D(img)
        a = ease(lt / 0.4)
        text(d, (W / 2, 820), "COMMENT", F("montserrat", 60, 700), hx("7a4a2a"), alpha=a)
        para(d, W / 2, 1000, self.KEYWORD, F("montserrat", 120, 900), hx("3a2216"), 960, alpha=a)
        heart(d, W / 2, 1230, 90, A(hx("d9534f"), a))

    def frame(self, t):
        img = Base.frame(self, t)
        self.hook(img, t)
        return img

    def show_cap(self, b):
        return b.v.get("k") != "end"
