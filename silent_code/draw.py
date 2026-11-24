"""Drawing primitives shared by all 20 styles."""
import os, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1920, 1080, 24
FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
_fc = {}
_WN = [(400, "Regular"), (500, "Medium"), (600, "SemiBold"), (700, "Bold"), (800, "ExtraBold"), (900, "Black")]
STATIC = {"Inter": [(k, f"Inter-{n}.otf") for k, n in _WN],
          "jetbrains": [(k, f"jetbrains-{n}.ttf") for k, n in _WN[:5]]}


def F(name, size, w=None):
    key = (name, int(size), w)
    if key in _fc:
        return _fc[key]
    p = os.path.join(FONTS, name + ".ttf")
    if name in STATIC:
        ww = w or 400
        lab = min(STATIC[name], key=lambda kv: abs(kv[0] - ww))[1]
        p = os.path.join(FONTS, lab)
        w = None
    if not os.path.exists(p):
        raise FileNotFoundError(p)
    if False:
        p = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    f = ImageFont.truetype(p, int(size))
    if w is not None:
        try:
            axes = f.get_variation_axes()
            vals = []
            for a in axes:
                nm = a.get("name", b"")
                nm = nm.decode() if isinstance(nm, bytes) else str(nm)
                if "eight" in nm.lower() or nm.lower() == "wght":
                    vals.append(max(a["minimum"], min(a["maximum"], w)))
                else:
                    vals.append(a["default"])
            f.set_variation_by_axes(vals)
        except Exception:
            pass
    _fc[key] = f
    return f


def clamp01(x):
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def ease(x):
    x = clamp01(x)
    return 1 - (1 - x) ** 3


def eio(x):
    x = clamp01(x)
    return 3 * x * x - 2 * x * x * x


def back(x):
    x = clamp01(x)
    c = 1.70158
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def lerp(a, b, x):
    return a + (b - a) * x


def hx(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def A(c, a):
    return (c[0], c[1], c[2], int(255 * clamp01(a)))


def mixc(c1, c2, x):
    return tuple(int(lerp(a, b, x)) for a, b in zip(c1, c2))


def D(img):
    return ImageDraw.Draw(img, "RGBA")


# ---------------------------------------------------------------- backgrounds
def gradient(c1, c2, vertical=True, w=W, h=H):
    t = np.linspace(0, 1, h if vertical else w, dtype=np.float32)
    a = np.array(c1, np.float32)
    b = np.array(c2, np.float32)
    g = a[None, :] * (1 - t[:, None]) + b[None, :] * t[:, None]
    if vertical:
        arr = np.repeat(g[:, None, :], w, axis=1)
    else:
        arr = np.repeat(g[None, :, :], h, axis=0)
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8))


def radial(inner, outer, cx=W / 2, cy=H / 2, r=1100, w=W, h=H):
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt((x - cx) ** 2 + (y - cy) ** 2) / r
    d = np.clip(d, 0, 1)[..., None]
    arr = np.array(inner, np.float32) * (1 - d) + np.array(outer, np.float32) * d
    return Image.fromarray(arr.astype(np.uint8))


def vignette(img, strength=0.55, power=2.2):
    w, h = img.size
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2) / 1.414
    m = 1 - strength * np.clip(d, 0, 1) ** power
    arr = np.asarray(img).astype(np.float32) * m[..., None]
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8))


def texture(img, amp=10, scale=1, seed=1, blur=0):
    rng = np.random.default_rng(seed)
    w, h = img.size
    n = rng.standard_normal((h // scale + 1, w // scale + 1)).astype(np.float32)
    if scale > 1:
        n = np.kron(n, np.ones((scale, scale), np.float32))[:h, :w]
    if blur:
        nimg = Image.fromarray(((n * 40) + 128).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(blur))
        n = (np.asarray(nimg).astype(np.float32) - 128) / 40
    arr = np.asarray(img).astype(np.float32) + n[..., None] * amp
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8))


class Grain:
    def __init__(self, amp=9, n=6, seed=3):
        rng = np.random.default_rng(seed)
        self.g = [(rng.standard_normal((H, W, 1)) * amp).astype(np.int16) for _ in range(n)]

    def apply(self, img, t):
        g = self.g[int(t * 6) % len(self.g)]
        arr = np.asarray(img).astype(np.int16) + g
        return Image.fromarray(arr.clip(0, 255).astype(np.uint8))


# ---------------------------------------------------------------- text
def wrap(s, font, maxw):
    out = []
    for para in s.split("\n"):
        line = ""
        for w in para.split(" "):
            t = (line + " " + w).strip()
            if font.getlength(t) <= maxw or not line:
                line = t
            else:
                out.append(line)
                line = w
        out.append(line)
    return out


def text(d, xy, s, font, fill, anchor="mm", alpha=1.0, stroke=0, sfill=(0, 0, 0)):
    if alpha <= 0:
        return
    if len(fill) == 3:
        fill = A(fill, alpha)
    else:
        fill = fill[:3] + (int(fill[3] * alpha),)
    sf = A(sfill, alpha) if stroke else None
    d.text(xy, s, font=font, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=sf)


def para(d, x, y, s, font, fill, maxw, align="c", lh=1.25, alpha=1.0, valign="m", reveal=1.0, stroke=0, sfill=(0, 0, 0)):
    lines = wrap(s, font, maxw)
    size = font.size
    tot = len(lines) * size * lh
    yy = y - tot / 2 + size * lh / 2 if valign == "m" else y + size * lh / 2
    nchar = sum(len(l) for l in lines)
    budget = int(nchar * clamp01(reveal) + 0.5)
    anchor = {"c": "mm", "l": "lm", "r": "rm"}[align]
    for l in lines:
        if budget <= 0:
            break
        part = l[:budget]
        budget -= len(l)
        text(d, (x, yy), part, font, fill, anchor, alpha, stroke, sfill)
        yy += size * lh
    return tot


def rrect(d, box, r, fill=None, outline=None, width=1):
    x0, y0, x1, y1 = box
    if x1 < x0:
        x0, x1 = x1, x0
    if y1 < y0:
        y0, y1 = y1, y0
    d.rounded_rectangle((x0, y0, x1, y1), radius=r, fill=fill, outline=outline, width=width)


def line_prog(d, p0, p1, x, col, w):
    x = clamp01(x)
    if x <= 0:
        return
    d.line([p0, (lerp(p0[0], p1[0], x), lerp(p0[1], p1[1], x))], fill=col, width=int(w))


def arrow(d, p0, p1, col, w=6, head=22, x=1.0):
    x = clamp01(x)
    if x <= 0:
        return
    e = (lerp(p0[0], p1[0], x), lerp(p0[1], p1[1], x))
    d.line([p0, e], fill=col, width=int(w))
    ang = math.atan2(e[1] - p0[1], e[0] - p0[0])
    pts = [e, (e[0] - head * math.cos(ang - 0.45), e[1] - head * math.sin(ang - 0.45)),
           (e[0] - head * math.cos(ang + 0.45), e[1] - head * math.sin(ang + 0.45))]
    d.polygon(pts, fill=col)


def check(d, cx, cy, s, col, w, x=1.0):
    p0, p1, p2 = (cx - s * 0.5, cy), (cx - s * 0.15, cy + s * 0.38), (cx + s * 0.55, cy - s * 0.45)
    x = clamp01(x)
    if x <= 0:
        return
    if x < 0.35:
        line_prog(d, p0, p1, x / 0.35, col, w)
    else:
        d.line([p0, p1], fill=col, width=int(w), joint="curve")
        line_prog(d, p1, p2, (x - 0.35) / 0.65, col, w)


def cross_x(d, cx, cy, s, col, w, x=1.0):
    line_prog(d, (cx - s, cy - s), (cx + s, cy + s), x * 2, col, w)
    line_prog(d, (cx + s, cy - s), (cx - s, cy + s), x * 2 - 1, col, w)


def arc_prog(d, cx, cy, r, col, w, x=1.0, start=-90):
    if x <= 0:
        return
    d.arc((cx - r, cy - r, cx + r, cy + r), start, start + 360 * clamp01(x), fill=col, width=int(w))


def scribble(d, x0, x1, y, col, w, x=1.0, amp=6, seed=0):
    rnd = random.Random(seed)
    n = 18
    pts = []
    for i in range(int(n * clamp01(x)) + 1):
        pts.append((lerp(x0, x1, i / n), y + rnd.uniform(-amp, amp)))
    if len(pts) > 1:
        d.line(pts, fill=col, width=int(w), joint="curve")


# ---------------------------------------------------------------- stick figures
POSES = {
    "stand": dict(la=(-12, -6), ra=(12, 6), ll=(-9, -4), rl=(9, 4)),
    "wave": dict(la=(-12, -6), ra=(140, 170), ll=(-9, -4), rl=(9, 4)),
    "arms_up": dict(la=(-150, -170), ra=(150, 170), ll=(-12, -6), rl=(12, 6)),
    "sad": dict(la=(-4, -2), ra=(4, 2), ll=(-5, -3), rl=(5, 3), tilt=8, head=10),
    "slump": dict(la=(10, 20), ra=(18, 28), ll=(-5, -3), rl=(5, 3), tilt=16, head=16),
    "cross": dict(la=(28, 100), ra=(-28, -100), ll=(-9, -4), rl=(9, 4)),
    "point": dict(la=(-12, -6), ra=(95, 92), ll=(-9, -4), rl=(9, 4)),
    "point_l": dict(la=(-95, -92), ra=(12, 6), ll=(-9, -4), rl=(9, 4)),
    "shrug": dict(la=(-65, -155), ra=(65, 155), ll=(-9, -4), rl=(9, 4)),
    "hips": dict(la=(-40, 40), ra=(40, -40), ll=(-12, -8), rl=(12, 8), tilt=-2),
    "phone": dict(la=(-12, -6), ra=(25, 165), ll=(-9, -4), rl=(9, 4), head=6),
    "think": dict(la=(30, 95), ra=(20, 170), ll=(-9, -4), rl=(9, 4)),
    "sit": dict(la=(30, 70), ra=(40, 80), ll=(85, 0), rl=(80, -5)),
    "sit_sad": dict(la=(40, 80), ra=(45, 85), ll=(85, 0), rl=(80, -5), tilt=12, head=14),
    "kneel": dict(la=(60, 110), ra=(70, 120), ll=(15, -85), rl=(-5, 5)),
    "beg": dict(la=(110, 150), ra=(120, 160), ll=(15, -85), rl=(-5, 5), tilt=10),
    "talk": dict(la=(-12, -6), ra=(55, 120), ll=(-9, -4), rl=(9, 4)),
    "talk2": dict(la=(-55, -120), ra=(55, 120), ll=(-9, -4), rl=(9, 4)),
    "reach": dict(la=(-12, -6), ra=(80, 80), ll=(-9, -4), rl=(9, 4), tilt=8),
    "walk": dict(la=(-12, -6), ra=(12, 6), ll=(-9, -4), rl=(9, 4), walk=1),
    "run": dict(la=(-12, -6), ra=(12, 6), ll=(-9, -4), rl=(9, 4), walk=2, tilt=10),
    "hug_self": dict(la=(40, 120), ra=(-40, -120), ll=(-5, -3), rl=(5, 3), tilt=6, head=8),
    "fist": dict(la=(-12, -6), ra=(150, 175), ll=(-12, -6), rl=(12, 6)),
    "back": dict(la=(-6, -2), ra=(6, 2), ll=(-6, -3), rl=(6, 3), noface=1),
    "hold": dict(la=(60, 95), ra=(-60, -95), ll=(-9, -4), rl=(9, 4)),
    "lie": dict(la=(-12, -6), ra=(12, 6), ll=(-9, -4), rl=(9, 4), rot=90),
}


def _dir(a):
    r = math.radians(a)
    return math.sin(r), math.cos(r)


def figure(d, x, gy, s, pose="stand", col=(240, 240, 240), t=0.0, flip=False, face="flat", lw=None,
           head_fill=None, alpha=1.0, bob=True, accent=None, hair=None):
    P = dict(POSES.get(pose, POSES["stand"]))
    sg = -1 if flip else 1
    lw = lw or max(3, int(s * 0.035))
    c = A(col, alpha)
    tilt = P.get("tilt", 0)
    if P.get("walk"):
        sp = 7 if P["walk"] == 1 else 11
        k = 28 if P["walk"] == 1 else 40
        ph = math.sin(t * sp)
        P["ll"] = (ph * k, ph * k - 12)
        P["rl"] = (-ph * k, -ph * k - 12)
        P["la"] = (-ph * k * 0.8, -ph * k * 0.8 + 10)
        P["ra"] = (ph * k * 0.8, ph * k * 0.8 + 10)
    if pose in ("talk", "talk2"):
        w = math.sin(t * 5) * 8
        P["ra"] = (P["ra"][0] + w, P["ra"][1] + w * 1.5)
    hl, body, ua, fa, th, sh = 0.11 * s, 0.36 * s, 0.2 * s, 0.19 * s, 0.24 * s, 0.24 * s
    by = math.sin(t * 2.2) * s * 0.006 if bob else 0
    # build in local coords relative to hip (0,0), y down
    tr = math.radians(tilt * sg)
    neck = (math.sin(tr) * body, -math.cos(tr) * body)

    def limb(base, ang, l1, l2):
        a1, a2 = ang
        d1 = _dir(a1 * sg)
        d2 = _dir(a2 * sg)
        p1 = (base[0] + d1[0] * l1, base[1] + d1[1] * l1)
        p2 = (p1[0] + d2[0] * l2, p1[1] + d2[1] * l2)
        return [base, p1, p2]

    sh_pt = (neck[0] * 0.9, neck[1] * 0.9)
    arms = [limb(sh_pt, P["la"], ua, fa), limb(sh_pt, P["ra"], ua, fa)]
    legs = [limb((0, 0), P["ll"], th, sh), limb((0, 0), P["rl"], th, sh)]
    hd = P.get("head", 0) * sg
    hr = math.radians(tilt * sg + hd)
    head = (neck[0] + math.sin(hr) * hl * 1.05, neck[1] - math.cos(hr) * hl * 1.05)
    allpts = [p for L in legs for p in L]
    low = max(p[1] for p in allpts)
    rot = P.get("rot", 0)

    def tf(p):
        px, py = p
        if rot:
            r = math.radians(rot * sg)
            px, py = px * math.cos(r) - py * math.sin(r), px * math.sin(r) + py * math.cos(r)
            return (x + px, gy - s * 0.05 + py)
        return (x + px, gy - low + py + by)

    for L in legs + [[(0, 0), neck]] + arms:
        d.line([tf(p) for p in L], fill=c, width=lw, joint="curve")
    for L in arms + legs:
        e = tf(L[-1])
        d.ellipse((e[0] - lw * 0.5, e[1] - lw * 0.5, e[0] + lw * 0.5, e[1] + lw * 0.5), fill=c)
    hx_, hy_ = tf(head)
    hf = A(head_fill, alpha) if head_fill else None
    if hair:
        d.pieslice((hx_ - hl * 1.05, hy_ - hl * 1.1, hx_ + hl * 1.05, hy_ + hl * 1.0), 180, 360, fill=A(hair, alpha))
    d.ellipse((hx_ - hl, hy_ - hl, hx_ + hl, hy_ + hl), fill=hf, outline=c, width=lw)
    if hair:
        d.chord((hx_ - hl, hy_ - hl, hx_ + hl, hy_ + hl * 0.2), 180, 360, fill=A(hair, alpha))
    if P.get("noface") or face is None or rot:
        return (hx_, hy_, hl)
    ex = hl * 0.38
    fx = hx_ + sg * hl * 0.12
    ey = hy_ - hl * 0.12
    er = max(2, hl * 0.09)
    blink = (t % 3.7) < 0.12
    for k in (-1, 1):
        if blink:
            d.line([(fx + k * ex - er, ey), (fx + k * ex + er, ey)], fill=c, width=max(2, lw // 2))
        else:
            d.ellipse((fx + k * ex - er, ey - er, fx + k * ex + er, ey + er), fill=c)
    my = hy_ + hl * 0.42
    mw = hl * 0.42
    mlw = max(2, lw // 2)
    if face == "smile":
        d.arc((fx - mw, my - mw * 0.9, fx + mw, my + mw * 0.5), 20, 160, fill=c, width=mlw)
    elif face == "frown":
        d.arc((fx - mw, my - mw * 0.1, fx + mw, my + mw * 1.1), 200, 340, fill=c, width=mlw)
    elif face == "o":
        d.ellipse((fx - mw * 0.3, my - mw * 0.4, fx + mw * 0.3, my + mw * 0.3), outline=c, width=mlw)
    elif face == "smirk":
        d.line([(fx - mw * 0.6, my), (fx + mw * 0.5, my - mw * 0.35)], fill=c, width=mlw)
    elif face == "angry":
        d.line([(fx - mw * 0.7, my), (fx + mw * 0.7, my)], fill=c, width=mlw)
        for k in (-1, 1):
            d.line([(fx + k * ex - er * 2, ey - er * 3 + (er if k < 0 else -er) * -1), (fx + k * ex + er * 2, ey - er * 3 + (er if k > 0 else -er) * -1)],
                   fill=c, width=mlw)
    else:
        d.line([(fx - mw * 0.55, my), (fx + mw * 0.55, my)], fill=c, width=mlw)
    if accent:  # tear / sweat
        d.ellipse((fx + ex - er, ey + er * 3, fx + ex + er, ey + er * 6), fill=A(accent, alpha))
    return (hx_, hy_, hl)


# ---------------------------------------------------------------- props
def bubble(d, x, y, s, font, fill, txt_col, tail=(0, 1), maxw=520, alpha=1.0, outline=None, lw=3, pad=26, reveal=1.0):
    lines = wrap(s, font, maxw)
    lh = font.size * 1.22
    tw = max(font.getlength(l) for l in lines)
    th = lh * len(lines)
    box = (x - tw / 2 - pad, y - th / 2 - pad * 0.7, x + tw / 2 + pad, y + th / 2 + pad * 0.7)
    tx, ty = tail
    tb = (x + tx * tw * 0.25, box[3] if ty > 0 else box[1])
    tip = (tb[0] + tx * 40, tb[1] + ty * 45)
    f = A(fill, alpha) if fill else None
    o = A(outline, alpha) if outline else None
    d.polygon([(tb[0] - 18, tb[1] - 2 * ty), (tb[0] + 18, tb[1] - 2 * ty), tip], fill=f or o, outline=o)
    rrect(d, box, 22, fill=f, outline=o, width=lw)
    para(d, x, y, s, font, txt_col, maxw, alpha=alpha, reveal=reveal)
    return box


def heart(d, cx, cy, s, fill, outline=None, w=3, broken=0.0):
    pts = []
    for i in range(60):
        a = i / 60 * 2 * math.pi
        px = 16 * math.sin(a) ** 3
        py = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((cx + px * s / 32, cy + py * s / 32))
    if broken <= 0:
        d.polygon(pts, fill=fill, outline=outline)
        return
    off = broken * s * 0.18
    left = [p for p in pts if p[0] <= cx]
    right = [p for p in pts if p[0] >= cx]
    crack = [(cx, cy - s * 0.2), (cx - s * 0.08, cy), (cx + s * 0.06, cy + s * 0.15), (cx, cy + s * 0.45)]
    lp = [(p[0] - off, p[1] + off * 0.3) for p in left + crack[::-1]]
    rp = [(p[0] + off, p[1] + off * 0.3) for p in crack + right]
    d.polygon(lp, fill=fill, outline=outline)
    d.polygon(rp, fill=fill, outline=outline)


def phone(d, x, y, s, col, screen=(40, 120, 255), lw=4, glow=0.0):
    w, h = s * 0.5, s
    if glow > 0:
        for k in range(5, 0, -1):
            rrect(d, (x - w / 2 - k * 10, y - h - k * 10, x + w / 2 + k * 10, y + k * 10), s * 0.12, fill=A(screen, 0.05 * glow))
    rrect(d, (x - w / 2, y - h, x + w / 2, y), s * 0.08, fill=A(col, 1), outline=None)
    rrect(d, (x - w / 2 + s * 0.04, y - h + s * 0.08, x + w / 2 - s * 0.04, y - s * 0.08), s * 0.04, fill=A(screen, 1))


def door(d, x, gy, s, col, fill=None, open_=0.0, lw=5, light=(255, 220, 150)):
    w, h = s * 0.5, s
    if open_ > 0:
        d.rectangle((x - w / 2, gy - h, x + w / 2, gy), fill=A(light, 0.9))
        ow = w * (1 - open_ * 0.8)
        d.polygon([(x - w / 2, gy - h), (x - w / 2 + ow, gy - h - s * 0.04 * open_), (x - w / 2 + ow, gy + s * 0.04 * open_), (x - w / 2, gy)],
                  fill=A(fill or (40, 40, 40), 1), outline=A(col, 1))
    else:
        d.rectangle((x - w / 2, gy - h, x + w / 2, gy), fill=A(fill, 1) if fill else None, outline=A(col, 1), width=lw)
        d.ellipse((x + w * 0.3 - 7, gy - h * 0.5 - 7, x + w * 0.3 + 7, gy - h * 0.5 + 7), fill=A(col, 1))


def table(d, x, gy, s, col, lw=5):
    d.line([(x - s * 0.6, gy - s * 0.45), (x + s * 0.6, gy - s * 0.45)], fill=A(col, 1), width=lw + 3)
    for k in (-0.5, 0.5):
        d.line([(x + k * s, gy - s * 0.45), (x + k * s, gy)], fill=A(col, 1), width=lw)


def chair(d, x, gy, s, col, lw=5, flip=False):
    sg = -1 if flip else 1
    d.line([(x - s * 0.22, gy - s * 0.42), (x + s * 0.22, gy - s * 0.42)], fill=A(col, 1), width=lw + 2)
    d.line([(x - sg * s * 0.22, gy - s * 0.42), (x - sg * s * 0.22, gy - s * 0.95)], fill=A(col, 1), width=lw)
    for k in (-0.2, 0.2):
        d.line([(x + k * s, gy - s * 0.42), (x + k * s, gy)], fill=A(col, 1), width=lw)


def moon(d, cx, cy, r, col, bgc):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=A(col, 1))
    d.ellipse((cx - r + r * 0.45, cy - r - r * 0.1, cx + r + r * 0.45, cy + r - r * 0.1), fill=A(bgc, 1))


def rain(d, t, col, n=140, seed=1, alpha=0.35, speed=900, length=40, slant=-0.15, box=(0, 0, W, H)):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    hh = y1 - y0
    for i in range(n):
        x = rnd.uniform(x0, x1)
        ph = rnd.uniform(0, hh)
        y = y0 + (ph + t * speed * rnd.uniform(0.8, 1.2)) % hh
        d.line([(x, y), (x + slant * length, y + length)], fill=A(col, alpha), width=2)


def particles(d, t, col, n=60, seed=2, alpha=0.25, speed=20, r=(1, 3), box=(0, 0, W, H)):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    for i in range(n):
        x = rnd.uniform(x0, x1) + math.sin(t * 0.3 + i) * 20
        y = y0 + (rnd.uniform(0, y1 - y0) - t * speed * rnd.uniform(0.5, 1.5)) % (y1 - y0)
        rr = rnd.uniform(*r)
        a = alpha * (0.5 + 0.5 * math.sin(t * 1.3 + i * 1.7))
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=A(col, a))


def city(d, gy, col, seed=4, h=(120, 420), alpha=1.0, win=None, t=0):
    rnd = random.Random(seed)
    x = -20
    while x < W + 20:
        bw = rnd.uniform(70, 170)
        bh = rnd.uniform(*h)
        d.rectangle((x, gy - bh, x + bw, gy), fill=A(col, alpha))
        if win:
            for wy in range(int(gy - bh + 20), int(gy - 20), 34):
                for wx in range(int(x + 14), int(x + bw - 20), 28):
                    if rnd.random() < 0.22:
                        d.rectangle((wx, wy, wx + 10, wy + 14), fill=A(win, 0.6 * alpha))
        x += bw + rnd.uniform(-10, 8)


def mask(d, cx, cy, s, col, eye=(0, 0, 0), smile=True, lw=4):
    d.ellipse((cx - s * 0.5, cy - s * 0.62, cx + s * 0.5, cy + s * 0.62), fill=A(col, 1))
    for k in (-1, 1):
        d.ellipse((cx + k * s * 0.2 - s * 0.1, cy - s * 0.18, cx + k * s * 0.2 + s * 0.1, cy - s * 0.04), fill=A(eye, 1))
    if smile:
        d.arc((cx - s * 0.22, cy + s * 0.02, cx + s * 0.22, cy + s * 0.32), 20, 160, fill=A(eye, 1), width=lw)
    else:
        d.arc((cx - s * 0.22, cy + s * 0.2, cx + s * 0.22, cy + s * 0.5), 200, 340, fill=A(eye, 1), width=lw)


def chain(d, x0, y0, x1, y1, col, s=26, lw=6, alpha=1.0):
    n = int(math.hypot(x1 - x0, y1 - y0) / (s * 1.4)) + 1
    for i in range(n):
        px = lerp(x0, x1, i / max(1, n - 1))
        py = lerp(y0, y1, i / max(1, n - 1))
        if i % 2 == 0:
            d.ellipse((px - s, py - s * 0.55, px + s, py + s * 0.55), outline=A(col, alpha), width=lw)
        else:
            d.ellipse((px - s * 0.4, py - s * 0.8, px + s * 0.4, py + s * 0.8), outline=A(col, alpha), width=lw)


def clock(d, cx, cy, r, col, t, lw=6, fill=None, speed=1.0):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=A(col, 1), width=lw, fill=A(fill, 1) if fill else None)
    for k in range(12):
        a = k / 12 * 2 * math.pi
        d.line([(cx + math.sin(a) * r * 0.82, cy - math.cos(a) * r * 0.82), (cx + math.sin(a) * r * 0.92, cy - math.cos(a) * r * 0.92)],
               fill=A(col, 1), width=max(2, lw // 2))
    a1 = t * speed * 2 * math.pi / 6
    a2 = a1 / 12
    d.line([(cx, cy), (cx + math.sin(a1) * r * 0.72, cy - math.cos(a1) * r * 0.72)], fill=A(col, 1), width=lw)
    d.line([(cx, cy), (cx + math.sin(a2) * r * 0.48, cy - math.cos(a2) * r * 0.48)], fill=A(col, 1), width=lw + 2)


def balance(d, cx, cy, s, col, tiltv=0.0, lw=6, lc=None, rc=None):
    d.line([(cx, cy), (cx, cy + s * 0.9)], fill=A(col, 1), width=lw)
    d.line([(cx - s * 0.3, cy + s * 0.9), (cx + s * 0.3, cy + s * 0.9)], fill=A(col, 1), width=lw)
    a = math.radians(tiltv * 18)
    dx, dy = math.cos(a) * s * 0.7, math.sin(a) * s * 0.7
    L, R = (cx - dx, cy - dy), (cx + dx, cy + dy)
    d.line([L, R], fill=A(col, 1), width=lw)
    for p, c in ((L, lc), (R, rc)):
        d.line([p, (p[0] - s * 0.18, p[1] + s * 0.35)], fill=A(col, 1), width=3)
        d.line([p, (p[0] + s * 0.18, p[1] + s * 0.35)], fill=A(col, 1), width=3)
        d.chord((p[0] - s * 0.22, p[1] + s * 0.2, p[0] + s * 0.22, p[1] + s * 0.5), 0, 180, fill=A(c or col, 1))
    return L, R


def dagger(d, x, y, s, col, ang=0, handle=(120, 80, 50)):
    a = math.radians(ang)

    def r(px, py):
        return (x + px * math.cos(a) - py * math.sin(a), y + px * math.sin(a) + py * math.cos(a))
    d.polygon([r(0, -s), r(s * 0.08, -s * 0.15), r(-s * 0.08, -s * 0.15)], fill=A(col, 1))
    d.polygon([r(-s * 0.2, -s * 0.15), r(s * 0.2, -s * 0.15), r(s * 0.2, -s * 0.08), r(-s * 0.2, -s * 0.08)], fill=A(handle, 1))
    d.polygon([r(-s * 0.05, -s * 0.08), r(s * 0.05, -s * 0.08), r(s * 0.05, s * 0.2), r(-s * 0.05, s * 0.2)], fill=A(handle, 1))


def candle(d, cx, gy, s, col, flame=(255, 190, 90), t=0):
    d.rectangle((cx - s * 0.12, gy - s * 0.6, cx + s * 0.12, gy), fill=A(col, 1))
    fl = 1 + 0.08 * math.sin(t * 13) + 0.05 * math.sin(t * 7.3)
    for k, a in ((3.0, 0.05), (2.0, 0.08), (1.3, 0.12)):
        rr = s * 0.18 * k * fl
        d.ellipse((cx - rr, gy - s * 0.75 - rr, cx + rr, gy - s * 0.75 + rr), fill=A(flame, a))
    d.ellipse((cx - s * 0.06, gy - s * 0.86 * fl, cx + s * 0.06, gy - s * 0.63), fill=A(flame, 1))
    d.ellipse((cx - s * 0.03, gy - s * 0.76, cx + s * 0.03, gy - s * 0.64), fill=A((255, 250, 230), 1))


def sun_rays(d, cx, cy, r, col, t, n=14, alpha=0.08):
    for i in range(n):
        a = i / n * 2 * math.pi + t * 0.05
        b = a + math.pi / n * 0.6
        d.polygon([(cx, cy), (cx + math.cos(a) * r, cy + math.sin(a) * r), (cx + math.cos(b) * r, cy + math.sin(b) * r)], fill=A(col, alpha))


def frog(d, cx, gy, s, col=(90, 170, 90), dark=(40, 90, 50), t=0, face="smile"):
    by = math.sin(t * 2) * s * 0.01
    d.ellipse((cx - s * 0.55, gy - s * 0.55 + by, cx + s * 0.55, gy + by), fill=A(col, 1))
    d.ellipse((cx - s * 0.35, gy - s * 0.3 + by, cx + s * 0.35, gy + by), fill=A(mixc(col, (240, 240, 200), 0.5), 1))
    for k in (-1, 1):
        ex = cx + k * s * 0.28
        ey = gy - s * 0.58 + by
        d.ellipse((ex - s * 0.16, ey - s * 0.16, ex + s * 0.16, ey + s * 0.16), fill=A(col, 1))
        d.ellipse((ex - s * 0.1, ey - s * 0.1, ex + s * 0.1, ey + s * 0.1), fill=A((250, 250, 240), 1))
        d.ellipse((ex - s * 0.05, ey - s * 0.05, ex + s * 0.05, ey + s * 0.05), fill=A((20, 20, 20), 1))
        d.ellipse((cx + k * s * 0.6 - s * 0.18, gy - s * 0.12, cx + k * s * 0.6 + s * 0.18, gy + s * 0.02), fill=A(dark, 1))
    if face == "smile":
        d.arc((cx - s * 0.25, gy - s * 0.5 + by, cx + s * 0.25, gy - s * 0.25 + by), 20, 160, fill=A(dark, 1), width=max(3, int(s * 0.03)))
    else:
        d.arc((cx - s * 0.2, gy - s * 0.35 + by, cx + s * 0.2, gy - s * 0.15 + by), 200, 340, fill=A(dark, 1), width=max(3, int(s * 0.03)))


def scorpion(d, cx, gy, s, col=(60, 40, 30), t=0, flip=False, sting=0.0):
    sg = -1 if flip else 1
    c = A(col, 1)
    # body segments
    for i in range(4):
        r = s * (0.16 - i * 0.015)
        x = cx - sg * i * s * 0.22
        d.ellipse((x - r * 1.2, gy - s * 0.2 - r, x + r * 1.2, gy - s * 0.2 + r), fill=c)
    # legs
    for i in range(4):
        x = cx - sg * i * s * 0.18
        for k in (-1, 1):
            d.line([(x, gy - s * 0.2), (x + k * s * 0.12, gy - s * 0.08), (x + k * s * 0.2, gy)], fill=c, width=max(3, int(s * 0.025)))
    # tail arc: goes back from the body, curls up and over it
    base = (cx - sg * s * 0.72, gy - s * 0.24)
    pts = [base]
    curl = 1 + sting * 0.35
    seg = s * 0.13
    for i in range(1, 7):
        th = math.radians(i * 30 * curl)
        px, py = pts[-1]
        pts.append((px - sg * math.cos(th) * seg, py - math.sin(th) * seg))
    for i, p in enumerate(pts):
        r = s * (0.07 - i * 0.006)
        d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=c)
    tip = pts[-1]
    d.polygon([tip, (tip[0] + sg * s * 0.13, tip[1] + s * 0.03), (tip[0] + sg * s * 0.03, tip[1] + s * 0.12)], fill=A((180, 40, 30), 1))
    # claws
    for k in (-1, 1):
        px = cx + sg * s * 0.3
        py = gy - s * 0.2 + k * s * 0.08
        d.line([(cx + sg * s * 0.12, gy - s * 0.2), (px, py)], fill=c, width=max(4, int(s * 0.035)))
        d.pieslice((px - s * 0.1, py - s * 0.08, px + s * 0.14, py + s * 0.08), 200 if sg > 0 else -20, 520 if sg > 0 else 300, fill=c)
    # eye
    d.ellipse((cx + sg * s * 0.05 - 5, gy - s * 0.3 - 5, cx + sg * s * 0.05 + 5, gy - s * 0.3 + 5), fill=A((230, 60, 40), 1))


def water(d, y, t, col, alpha=0.5, amp=10, n=5, h=200):
    for k in range(n):
        yy = y + k * h / n
        pts = [(x, yy + math.sin(x / 90 + t * 1.5 + k) * amp) for x in range(0, W + 41, 40)]
        d.line(pts, fill=A(col, alpha * (1 - k / n * 0.6)), width=3)


def podium(d, cx, gy, s, col, front, label=None, font=None, txt=(255, 255, 255)):
    d.polygon([(cx - s * 0.5, gy - s * 0.9), (cx + s * 0.5, gy - s * 0.9), (cx + s * 0.42, gy), (cx - s * 0.42, gy)], fill=A(front, 1))
    d.rectangle((cx - s * 0.55, gy - s * 0.96, cx + s * 0.55, gy - s * 0.88), fill=A(col, 1))
    if label and font:
        text(d, (cx, gy - s * 0.45), label, font, txt)


def hand_point(d, x, y, s, skin=(240, 205, 175), cuff=(40, 50, 70), outline=(150, 110, 90)):
    """A cartoon pointing hand whose fingertip is at (x, y), arm coming from bottom-right."""
    o = A(outline, 1)
    # sleeve
    d.polygon([(x + s * 0.9, y + s * 0.55), (x + s * 1.8, y + s * 1.6), (x + s * 2.4, y + s * 1.1), (x + s * 1.4, y + s * 0.15)], fill=A(cuff, 1))
    # palm
    d.rounded_rectangle((x + s * 0.35, y + s * 0.05, x + s * 1.15, y + s * 0.75), radius=s * 0.25, fill=A(skin, 1), outline=o, width=3)
    # index finger
    d.rounded_rectangle((x - s * 0.02, y - s * 0.07, x + s * 0.65, y + s * 0.15), radius=s * 0.1, fill=A(skin, 1), outline=o, width=3)
    # curled fingers
    for k in range(3):
        yy = y + s * (0.22 + k * 0.17)
        d.rounded_rectangle((x + s * 0.28, yy, x + s * 0.62, yy + s * 0.17), radius=s * 0.08, fill=A(skin, 1), outline=o, width=3)
    # thumb
    d.rounded_rectangle((x + s * 0.5, y - s * 0.12, x + s * 0.95, y + s * 0.12), radius=s * 0.1, fill=A(skin, 1), outline=o, width=3)


def lower_third(d, x, y, name, role, f1, f2, c1, c2, accent, x_in=1.0):
    w = max(f1.getlength(name), f2.getlength(role)) + 80
    xo = lerp(-w - 40, 0, ease(x_in))
    d.rectangle((x + xo, y, x + xo + 12, y + 120), fill=A(accent, 1))
    d.rectangle((x + xo + 12, y, x + xo + w, y + 70), fill=A(c1, 0.95))
    d.rectangle((x + xo + 12, y + 70, x + xo + w * 0.85, y + 120), fill=A(c2, 0.95))
    text(d, (x + xo + 40, y + 36), name, f1, (255, 255, 255), "lm")
    text(d, (x + xo + 40, y + 96), role, f2, (230, 230, 230), "lm")


# ---------------------------------------------------------------- generic scene
def _col(pal, c):
    if c is None:
        return pal["fg"]
    if isinstance(c, str):
        return pal[c]
    return c


def scene(d, v, lt, t, pal, gy=None, s=None, bfont=None, alpha=1.0):
    """v: dict(figs=[...], props=[...], bubbles=[...]); pal: fg, bg, acc, acc2, gy, s"""
    gy = gy or pal.get("gy", 820)
    s = s or pal.get("s", 330)
    lw = pal.get("lw")
    for pr in v.get("props", []):
        k = pr[0]
        x = pr[1]
        y = pr[2] if len(pr) > 2 and pr[2] is not None else gy
        sc = pr[3] if len(pr) > 3 else 1.0
        c = _col(pal, pr[4] if len(pr) > 4 else None)
        a_in = ease(lt / 0.5)
        if k == "phone":
            phone(d, x, y, 90 * sc, c, screen=pal.get("screen", (60, 140, 255)), glow=0.6)
        elif k == "door":
            door(d, x, y, 400 * sc, c, fill=pal.get("doorfill"), open_=pr[5] if len(pr) > 5 else 0)
        elif k == "table":
            table(d, x, y, 300 * sc, c)
        elif k == "chair":
            chair(d, x, y, 300 * sc, c, flip=len(pr) > 5 and pr[5])
        elif k == "moon":
            moon(d, x, y, 60 * sc, c, pal["bg"])
        elif k == "heart":
            heart(d, x, y - 10 * math.sin(t * 3) * sc, 120 * sc * (0.6 + 0.4 * back(lt / 0.6)), A(c, alpha))
        elif k == "broken":
            heart(d, x, y, 140 * sc, A(c, alpha), broken=ease((lt - 0.3) / 1.2))
        elif k == "mask":
            mask(d, x, y, 160 * sc, c, eye=pal["bg"], smile=len(pr) <= 5 or pr[5])
        elif k == "chain":
            chain(d, x, y, pr[5], pr[6], c, s=24 * sc)
        elif k == "clock":
            clock(d, x, y, 90 * sc, c, t)
        elif k == "dagger":
            dagger(d, x, y, 120 * sc, c, ang=pr[5] if len(pr) > 5 else 0)
        elif k == "candle":
            candle(d, x, y, 160 * sc, c, t=t)
        elif k == "rain":
            rain(d, t, c, alpha=0.3)
        elif k == "city":
            city(d, y, c, h=(120 * sc, 400 * sc), win=pal.get("win"))
        elif k == "label":
            text(d, (x, y), pr[5], bfont or F("Inter", 40), c, alpha=a_in)
        elif k == "q":
            text(d, (x, y + math.sin(t * 3) * 6), "?", F("archivoblack", int(110 * sc)), c, alpha=a_in)
        elif k == "ex":
            text(d, (x, y + math.sin(t * 3) * 6), "!", F("archivoblack", int(110 * sc)), c, alpha=a_in)
        elif k == "ground":
            d.line([(0, gy), (W, gy)], fill=A(c, 0.5), width=3)
        elif k == "balance":
            balance(d, x, y, 200 * sc, c, tiltv=math.sin(t) * 0.3)
        elif k == "crown":
            cs = 60 * sc
            d.polygon([(x - cs, y), (x - cs, y - cs * 0.8), (x - cs * 0.5, y - cs * 0.35), (x, y - cs), (x + cs * 0.5, y - cs * 0.35),
                       (x + cs, y - cs * 0.8), (x + cs, y)], fill=A(c, 1))
        elif k == "wall":
            d.rectangle((x - 20 * sc, y - 500 * sc, x + 20 * sc, y), fill=A(c, 1))
    for f in v.get("figs", []):
        fx = f.get("x", W / 2)
        if "to" in f:
            dur = f.get("dur", 2.5)
            fx = lerp(f["x"], f["to"], eio(lt / dur))
        delay = f.get("delay", 0)
        a = f.get("a", 1.0) * ease((lt - delay) / 0.4) * alpha
        if a <= 0:
            continue
        pose = f.get("p", "stand")
        if "to" in f and lt < f.get("dur", 2.5) and pose == "stand":
            pose = "walk"
        figure(d, fx, f.get("gy", gy), s * f.get("s", 1.0), pose, _col(pal, f.get("c")), t + fx * 0.01,
               flip=f.get("flip", False), face=f.get("f", "flat"), head_fill=pal.get("headfill", pal["bg"]),
               alpha=a, accent=pal.get("tear") if f.get("tear") else None, hair=_col(pal, f["hair"]) if f.get("hair") else None,
               lw=lw)
    for bb in v.get("bubbles", []):
        x, y, txt = bb[0], bb[1], bb[2]
        delay = bb[3] if len(bb) > 3 else 0.2
        a = ease((lt - delay) / 0.3) * alpha
        if a > 0:
            bubble(d, x, y, txt, bfont or F("Inter", 34), pal.get("bubble", (255, 255, 255)), pal.get("bubtxt", (20, 20, 20)),
                   tail=bb[4] if len(bb) > 4 else (0, 1), alpha=a, maxw=bb[5] if len(bb) > 5 else 460)
