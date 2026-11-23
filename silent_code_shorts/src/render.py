"""Renders the single static top-down scene: parchment book on a dark wooden desk,
gold serif lines appearing one by one, a right hand (dark suit sleeve, white cuff,
gold cufflink) whose index finger reads each line left to right with a gold underline."""
import json, math, os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

W, H = 1080, 1920
FPS = 30
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.environ.get("SC_FONT_DIR", os.path.join(HERE, "..", "assets", "fonts"))
F_REG = os.path.join(FONT_DIR, "cormorant-garamond-latin-600-normal.woff")
F_BOLD = os.path.join(FONT_DIR, "cormorant-garamond-latin-700-normal.woff")

# page geometry
PAGE = (78, 150, 1032, 1790)          # x0, y0, x1, y1 of the right-hand page
TEXT_X0, TEXT_X1 = 168, 948
TEXT_Y0, TEXT_Y1 = 300, 1610

NUM_WORDS = {"One:", "Two:", "Three:", "Four:", "Five:", "Six:", "Seven:", "Eight:", "Nine:", "Ten:"}


# ----------------------------------------------------------------------------- helpers
def smooth_noise(h, w, scale, rng, octaves=4):
    out = np.zeros((h, w), np.float32)
    amp = 1.0; tot = 0
    for o in range(octaves):
        sh, sw = max(2, int(h / scale) + 2), max(2, int(w / scale) + 2)
        small = Image.fromarray((rng.random((sh, sw)) * 255).astype(np.uint8))
        big = np.asarray(small.resize((w, h), Image.BICUBIC), np.float32) / 255
        out += big * amp; tot += amp
        amp *= 0.5; scale /= 2
    return out / tot


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


# ----------------------------------------------------------------------------- background
def make_background(seed=3):
    rng = np.random.default_rng(seed)
    # dark wood desk: long horizontal grain
    g1 = smooth_noise(H // 8, W // 1, 1, rng, 1)
    grain = np.asarray(Image.fromarray((g1 * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255
    grain = Image.fromarray((grain * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur((0.5)))
    grain = np.asarray(grain, np.float32) / 255
    low = smooth_noise(H, W, 300, rng, 3)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rings = 0.5 + 0.5 * np.sin(yy / 23.0 + low * 9 + np.sin(xx / 400) * 2)
    wood = 0.55 * grain + 0.25 * rings + 0.2 * low
    base = np.array([78, 46, 26], np.float32); dark = np.array([20, 11, 7], np.float32)
    img = dark + (base - dark) * wood[..., None]
    # vignette to black
    d = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.58)) ** 2)
    vig = np.clip(1.15 - d ** 1.6, 0.18, 1)
    img *= vig[..., None]

    canvas = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
    x0, y0, x1, y1 = PAGE

    # book shadow on desk
    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).rounded_rectangle((x0 - 60, y0 + 10, x1 + 40, y1 + 60), 30, fill=200)
    sh = sh.filter(ImageFilter.GaussianBlur(40))
    canvas = Image.alpha_composite(canvas, Image.merge("RGBA", (*[Image.new("L", (W, H), 0)] * 3, sh)))

    # leather cover edge peeking out
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle((x0 - 70, y0 - 22, x1 + 22, y1 + 24), 14, fill=(52, 22, 14, 255))
    d.rounded_rectangle((x0 - 70, y0 - 22, x1 + 22, y1 + 24), 14, outline=(78, 38, 22, 255), width=3)
    # stacked page edges (right & bottom)
    for i in range(9, 0, -1):
        c = 205 - i * 9
        d.rectangle((x0 + i, y0 + i * 1.2, x1 + i * 1.3, y1 + i * 1.5), fill=(c, c - 14, c - 42, 255))
    # sliver of left page
    d.rectangle((x0 - 64, y0 + 4, x0, y1 + 4), fill=(214, 196, 158, 255))

    # parchment
    pw, ph = x1 - x0, y1 - y0
    n1 = smooth_noise(ph, pw, 260, rng, 5)
    n2 = smooth_noise(ph, pw, 40, rng, 3)
    fib = rng.random((ph, pw)).astype(np.float32)
    fib = np.asarray(Image.fromarray((fib * 255).astype(np.uint8)).resize((pw // 3, ph)).resize((pw, ph)).filter(
        ImageFilter.GaussianBlur(0.8)), np.float32) / 255
    cream = np.array([238, 224, 192], np.float32)
    aged = np.array([196, 164, 112], np.float32)
    py, px = np.mgrid[0:ph, 0:pw].astype(np.float32)
    edge = np.minimum.reduce([px / pw, (pw - px) / pw, py / ph * 1.6, (ph - py) / ph * 1.6])
    edge_age = np.clip(1 - edge / 0.12, 0, 1) ** 1.8
    blot = np.clip((n1 - 0.55) * 3, 0, 1) * 0.35
    t = np.clip(0.18 + 0.4 * edge_age + blot + (n2 - 0.5) * 0.18 + (fib - 0.5) * 0.06, 0, 1)
    paper = cream + (aged - cream) * t[..., None]
    # gutter shadow (left) + page curl highlight
    gut = np.exp(-px / 70.0) * 0.55 + np.exp(-px / 260.0) * 0.12
    hl = np.exp(-((px - 210) / 160.0) ** 2) * 0.05
    paper *= (1 - gut + hl)[..., None]
    page = Image.fromarray(np.clip(paper, 0, 255).astype(np.uint8)).convert("RGBA")
    # slightly irregular page corners
    m = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, pw - 1, ph - 1), 10, fill=255)
    canvas.paste(page, (x0, y0), m)

    # decorative gold double frame + small ornaments (no text)
    d = ImageDraw.Draw(canvas)
    gold = (150, 108, 40, 255); gold2 = (172, 128, 52, 200)
    fx0, fy0, fx1, fy1 = x0 + 52, y0 + 58, x1 - 46, y1 - 58
    d.rectangle((fx0, fy0, fx1, fy1), outline=gold, width=3)
    d.rectangle((fx0 + 12, fy0 + 12, fx1 - 12, fy1 - 12), outline=gold2, width=1)
    for cx, cy in ((fx0, fy0), (fx1, fy0), (fx0, fy1), (fx1, fy1)):
        d.regular_polygon((cx, cy, 11), 4, rotation=45, fill=gold)
        d.regular_polygon((cx, cy, 5), 4, rotation=45, fill=(230, 210, 160, 255))
    # top flourish
    mx = (fx0 + fx1) // 2
    d.line((mx - 170, fy0 + 70, mx - 20, fy0 + 70), fill=gold, width=2)
    d.line((mx + 20, fy0 + 70, mx + 170, fy0 + 70), fill=gold, width=2)
    d.regular_polygon((mx, fy0 + 70, 10), 4, rotation=45, fill=gold)
    d.ellipse((mx - 186, fy0 + 66, mx - 178, fy0 + 74), fill=gold)
    d.ellipse((mx + 178, fy0 + 66, mx + 186, fy0 + 74), fill=gold)
    return canvas


# ----------------------------------------------------------------------------- text layout
def layout(lines):
    """Word-wrap all lines; shrink font until everything fits on the page."""
    for size in range(48, 26, -1):
        f_reg = ImageFont.truetype(F_REG, size)
        f_bold = ImageFont.truetype(F_BOLD, size)
        lh = int(size * 1.22); gap = int(size * 0.55)
        space = f_reg.getlength(" ")
        y = TEXT_Y0
        out = []
        for li, line in enumerate(lines):
            words = line.split(" ")
            rows = []; cur = []; x = TEXT_X0
            for w in words:
                font = f_bold if (w in NUM_WORDS and not cur and not rows) else f_reg
                wl = font.getlength(w)
                if cur and x + wl > TEXT_X1:
                    rows.append(cur); cur = []; x = TEXT_X0
                cur.append((w, x, font, wl)); x += wl + space
            rows.append(cur)
            row_objs = []
            for r in rows:
                row_objs.append({"y": y, "words": r, "x0": r[0][1], "x1": r[-1][1] + r[-1][3],
                                 "chars": sum(len(w[0]) + 1 for w in r)})
                y += lh
            out.append(row_objs)
            y += gap
        if y - gap <= TEXT_Y1:
            # vertically center the block inside the text area
            off = ((TEXT_Y1 - (y - gap)) // 2)
            for rows in out:
                for r in rows:
                    r["y"] += off
            return out, size
    raise RuntimeError("text does not fit")


def render_line_layer(rows, size):
    """Gold embossed text for one script line on a transparent layer."""
    ys = [r["y"] for r in rows]
    top = min(ys) - 20; bot = max(ys) + int(size * 1.4)
    hh = bot - top
    mask = Image.new("L", (W, hh), 0)
    d = ImageDraw.Draw(mask)
    for r in rows:
        for w, x, font, _ in r["words"]:
            d.text((x, r["y"] - top), w, font=font, fill=255)
    # metallic gold gradient per row
    grad = np.zeros((hh, W, 3), np.float32)
    lo = np.array([104, 68, 14], np.float32); hi = np.array([168, 122, 38], np.float32); spec = np.array([206, 162, 72], np.float32)
    yy = np.arange(hh)[:, None].astype(np.float32)
    phase = np.zeros((hh, 1), np.float32)
    for r in rows:
        ry = r["y"] - top
        inside = (yy >= ry) & (yy < ry + size * 1.25)
        p = np.clip((yy - ry) / (size * 1.05), 0, 1)
        phase = np.where(inside, p, phase)
    tcol = np.where(phase < 0.45, lo + (hi - lo) * (phase / 0.45), hi + (spec - hi) * np.clip((phase - 0.45) / 0.2, 0, 1))
    tcol = np.where(phase > 0.65, spec + (lo - spec) * np.clip((phase - 0.65) / 0.35, 0, 1), tcol)
    grad[:] = tcol[:, :, :] if tcol.ndim == 3 else tcol[:, None, :]
    layer = Image.new("RGBA", (W, hh), (0, 0, 0, 0))
    # soft dark impression (ink sinking into paper) + tiny highlight for an embossed look
    shadow = mask.filter(ImageFilter.GaussianBlur(0.9)).point(lambda v: int(v * 0.38))
    layer.paste(Image.new("RGBA", (W, hh), (60, 36, 10, 255)), (1, 1), shadow)
    hl = mask.filter(ImageFilter.GaussianBlur(0.5)).point(lambda v: int(v * 0.22))
    layer.paste(Image.new("RGBA", (W, hh), (255, 240, 200, 255)), (-1, -1), hl)
    gold = Image.fromarray(np.clip(grad, 0, 255).astype(np.uint8)).convert("RGBA")
    layer.paste(gold, (0, 0), mask)
    return layer, top


# ----------------------------------------------------------------------------- hand sprite
SKIN = np.array([222, 170, 138], np.float32)


def _shade(mask, base, light=(-0.55, -0.8), blur=26, dark=0.42, hi=0.18):
    """Fake 3D: interior brighter, rims darker, light from upper-left."""
    m = np.asarray(mask, np.float32) / 255
    b = np.asarray(mask.filter(ImageFilter.GaussianBlur(blur)), np.float32) / 255
    # directional term: gradient of blurred mask
    gy, gx = np.gradient(b)
    nl = -(gx * light[0] + gy * light[1]) * blur * 1.6
    s = (1 - dark) + dark * np.clip(b * 1.6, 0, 1) + np.clip(nl, -0.35, 0.35) * 0.9
    rgb = base[None, None, :] * s[..., None] + 255 * hi * np.clip(nl, 0, 1)[..., None]
    rgba = np.dstack([np.clip(rgb, 0, 255), m * 255]).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


def _capsule(d, p0, p1, r0, r1, fill=255, steps=40):
    for i in range(steps + 1):
        t = i / steps
        x = p0[0] + (p1[0] - p0[0]) * t; y = p0[1] + (p1[1] - p0[1]) * t
        r = r0 + (r1 - r0) * t
        d.ellipse((x - r, y - r, x + r, y + r), fill=fill)


def _gb(a, sig):
    from scipy.ndimage import gaussian_filter
    return gaussian_filter(a.astype(np.float32), sig)


def _lit(height, alpha, base, k, spec=0.22, shin=18, amb=0.38, rim=None):
    """Lambert + Blinn lighting of a height field (light from upper-left, above)."""
    gy, gx = np.gradient(height)
    nx, ny, nz = -gx * k, -gy * k, np.ones_like(height)
    n = np.sqrt(nx * nx + ny * ny + nz * nz); nx /= n; ny /= n; nz /= n
    L = np.array([-0.45, -0.6, 0.66]); L /= np.linalg.norm(L)
    Hh = L + np.array([0, 0, 1.0]); Hh /= np.linalg.norm(Hh)
    diff = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    sp = np.clip(nx * Hh[0] + ny * Hh[1] + nz * Hh[2], 0, 1) ** shin
    col = base[None, None, :] * (amb + (1 - amb) * 1.15 * diff)[..., None] + 255 * spec * sp[..., None]
    if rim is not None:  # warm subsurface tint at the rims
        col = col * (1 - rim[..., None]) + col * np.array([1.05, 0.86, 0.80]) * rim[..., None]
    return Image.fromarray(np.dstack([np.clip(col, 0, 255), np.clip(alpha, 0, 1) * 255]).astype(np.uint8), "RGBA")


def make_hand(S=2, K=1.22):
    """Right hand seen from above, palm down, index finger pointing straight up.
    Built from a lit height field so the hand reads as one organic form."""
    w, h = int(820 * S * K), int(2300 * S)
    cx = int(320 * S * K)
    oy = int(40 * S)
    def P(x, y):
        return (cx + x * S * K, oy + y * S * K)
    def R(v):
        return v * S * K
    def mask(draw_fn):
        m = Image.new("L", (w, h), 0); draw_fn(ImageDraw.Draw(m)); return np.asarray(m, np.float32) / 255

    # ---------------- skin height field
    mf = mask(lambda d: _capsule(d, P(0, 24), P(10, 300), R(24), R(36), steps=110))
    mt = mask(lambda d: _capsule(d, P(-50, 452), P(-46, 318), R(30), R(25), steps=70))
    mb = mask(lambda d: d.polygon([P(-36, 236), P(20, 222), P(100, 228), P(168, 252), P(198, 310), P(192, 400),
                                   P(168, 478), P(-20, 486), P(-52, 410), P(-50, 300)], fill=255))
    knuck = [(60, 236, 42), (112, 248, 39), (158, 272, 34)]
    mks = [mask(lambda d, kx=kx, ky=ky, r=r: d.ellipse([*P(kx - r, ky - r * 0.9), *P(kx + r, ky + r * 1.35)], fill=255))
           for kx, ky, r in knuck]
    hf = _gb(mf, R(13)) * 0.95; ht = _gb(mt, R(14)) * 0.8
    hb = (_gb(mb, R(25)) * 0.35 + _gb(mb, R(60)) * 0.5 + _gb(mb, R(110)) * 0.6) * 1.05
    hk = [_gb(m, R(15)) * 0.98 for m in mks]
    height = np.maximum.reduce([hf, ht, hb, *hk]) + 0.12 * (hf + hb)
    sil = np.clip(mf + mt + mb + sum(mks), 0, 1)
    sil = _gb(sil, R(3.5)); sil = np.clip((sil - 0.5) * 6 + 0.5, 0, 1)
    rim = np.clip(1 - _gb(sil, R(10)) * 1.4, 0, 1) * sil
    skin = _lit(height * R(30), sil, SKIN, k=1.0, spec=0.16, shin=14, amb=0.45, rim=rim * 0.8)
    # subtle skin texture
    arr = np.asarray(skin).astype(np.float32)
    rng = np.random.default_rng(11)
    tex = _gb(rng.standard_normal((h, w)), S * 1.2) * 18
    arr[..., :3] = np.clip(arr[..., :3] + tex[..., None], 0, 255)
    skin = Image.fromarray(arr.astype(np.uint8), "RGBA")
    # soft creases + nails
    det = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(det)
    dk = (130, 78, 60, 120)
    for y in (100, 172):
        d.arc([*P(-17, y - 8), *P(23, y + 8)], 205, 335, fill=dk, width=int(R(3)))
    det = det.filter(ImageFilter.GaussianBlur(R(1.6)))
    skin = Image.alpha_composite(skin, det)
    d = ImageDraw.Draw(skin)
    d.rounded_rectangle([*P(-15, 30), *P(18, 78)], R(15), fill=(232, 194, 178, 235), outline=(186, 136, 116, 255), width=int(S))
    d.ellipse([*P(-8, 36), *P(3, 50)], fill=(250, 232, 220, 160))

    # ---------------- suit sleeve
    ms = mask(lambda d: (d.polygon([P(-70, 532), P(222, 522), P(280, 1880), P(-110, 1880)], fill=255),
                         d.ellipse([*P(-72, 496), *P(224, 564)], fill=255)))
    folds = np.zeros_like(ms)
    for (a, b, c) in [((-30, 640), (20, 820), (-10, 1000)), ((170, 600), (150, 800), (190, 980)), ((70, 1100), (95, 1300), (55, 1500))]:
        folds += mask(lambda d, a=a, b=b, c=c: d.line([P(*a), P(*b), P(*c)], fill=255, width=int(R(22)), joint="curve"))
    hs = _gb(ms, R(60)) + _gb(folds, R(12)) * 0.25
    sleeve = _lit(hs * R(30), ms, np.array([34, 37, 50], np.float32), k=1.0, spec=0.05, shin=8, amb=0.42)
    arr = np.asarray(sleeve).astype(np.float32)
    arr[..., :3] = np.clip(arr[..., :3] + rng.normal(0, 2.5, (h, w))[..., None], 0, 255)
    sleeve = Image.fromarray(arr.astype(np.uint8), "RGBA")

    # ---------------- white shirt cuff + gold cufflink
    mc = mask(lambda d: (d.polygon([P(-50, 462), P(196, 454), P(212, 556), P(-64, 564)], fill=255),
                         d.ellipse([*P(-52, 436), *P(198, 488)], fill=255)))
    mc = np.clip((_gb(mc, S) - 0.5) * 4 + 0.5, 0, 1)
    cuff = _lit(_gb(mc, R(22)) * R(22), mc, np.array([236, 236, 232], np.float32), k=1.0, spec=0.06, amb=0.55)
    cd = ImageDraw.Draw(cuff)
    cd.line([P(-56, 540), P(208, 532)], fill=(196, 196, 192, 255), width=int(S * 1.5))
    ccx, ccy = 172, 508
    cd.ellipse([*P(ccx - 24, ccy - 21), *P(ccx + 24, ccy + 21)], fill=(104, 72, 20, 255))
    cd.ellipse([*P(ccx - 20, ccy - 18), *P(ccx + 20, ccy + 18)], fill=(192, 146, 56, 255))
    cd.ellipse([*P(ccx - 14, ccy - 13), *P(ccx + 11, ccy + 9)], fill=(230, 196, 110, 255))
    cd.ellipse([*P(ccx - 9, ccy - 9), *P(ccx - 2, ccy - 3)], fill=(255, 246, 210, 255))

    # hand casts a soft contact shadow onto the cuff
    hand_a = np.asarray(skin.split()[3], np.float32) / 255
    cs = np.roll(_gb(hand_a, R(8)), int(R(10)), axis=0) * 0.35
    carr = np.asarray(cuff).astype(np.float32)
    carr[..., :3] *= (1 - cs)[..., None]
    cuff = Image.fromarray(carr.astype(np.uint8), "RGBA")

    sprite = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for part in (sleeve, cuff, skin):
        sprite = Image.alpha_composite(sprite, part)
    sprite = sprite.resize((w // S, h // S), Image.LANCZOS)
    return sprite, (cx // S, oy // S)


def rotated_hands(sprite, tip, angles):
    """Pre-rotate sprite (+ shadow) for a few arm angles. Returns list of (img, shadow, tip)."""
    out = []
    for a in angles:
        r = sprite.rotate(a, resample=Image.BICUBIC, expand=True, center=tip)
        # tip location after rotation with expand: compute by rotating a marker
        mk = Image.new("L", sprite.size, 0)
        ImageDraw.Draw(mk).ellipse((tip[0] - 3, tip[1] - 3, tip[0] + 3, tip[1] + 3), fill=255)
        mr = np.asarray(mk.rotate(a, resample=Image.BILINEAR, expand=True, center=tip))
        ys, xs = np.nonzero(mr > 60)
        t = (int(xs.mean()), int(ys.mean()))
        alpha = r.split()[3]
        sh = alpha.filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(v * 0.5))
        shadow = Image.new("RGBA", r.size, (20, 10, 4, 255))
        shadow.putalpha(sh)
        out.append((r, shadow, t))
    return out


# ----------------------------------------------------------------------------- animation
def finger_path(rows_by_line, timeline, duration):
    """Returns f(t) -> (x, y, line_index, row_index, progress_x) for the fingertip."""
    segs = []  # (t0, t1, (x0,y0), (x1,y1), kind, li, ri)
    lines = timeline["lines"]
    for li, (rows, tl) in enumerate(zip(rows_by_line, lines)):
        tot = sum(r["chars"] for r in rows)
        dur = tl["end"] - tl["start"]
        t = tl["start"]
        for ri, r in enumerate(rows):
            rd = dur * r["chars"] / tot
            y = r["y"] + 0
            if ri > 0:  # quick return to start of the next row of the same line
                ret = min(0.28, rd * 0.25)
                prev = rows[ri - 1]
                segs.append((t, t + ret, (prev["x1"], prev["y"]), (r["x0"], r["y"]), "move", li, ri))
                t += ret; rd -= ret
            segs.append((t, t + rd, (r["x0"], r["y"]), (r["x1"], r["y"]), "read", li, ri))
            t += rd
    return segs


def finger_at(segs, t, size):
    ybase = int(size * 1.08)  # fingertip sits just under the glyph baseline
    if t <= segs[0][0]:
        s = segs[0]
        return s[2][0] - 6, s[2][1] + ybase, s[5], s[6], s[2][0], False
    for i, s in enumerate(segs):
        t0, t1, a, b, kind, li, ri = s
        if t0 <= t <= t1:
            u = (t - t0) / max(1e-6, t1 - t0)
            u = ease(u) if kind == "move" else (u * 0.94 + 0.06 * ease(u))
            x = a[0] + (b[0] - a[0]) * u
            y = a[1] + (b[1] - a[1]) * u
            return x, y + ybase, li, ri, x, kind == "read"
        if i + 1 < len(segs) and t1 < t < segs[i + 1][0]:
            nxt = segs[i + 1]
            u = ease((t - t1) / (nxt[0] - t1))
            # lift slightly while travelling to the next line
            x = b[0] + (nxt[2][0] - b[0]) * u
            y = b[1] + (nxt[2][1] - b[1]) * u - math.sin(u * math.pi) * 10
            return x, y + ybase, li, ri, b[0], False
    s = segs[-1]
    return s[3][0], s[3][1] + ybase, s[5], s[6], s[3][0], False


def render_video(timeline_path, audio_path, out_path, lines, preview_png=None):
    with open(timeline_path) as f:
        tl = json.load(f)
    duration = tl["duration"]
    bg = make_background()
    rows_by_line, size = layout(lines)
    layers = [render_line_layer(rows, size) for rows in rows_by_line]
    sprite, tip = make_hand()
    angles = [12, 15, 18, 21, 24, 27, 30]  # degrees CCW: arm from lower right
    hands = rotated_hands(sprite, tip, angles)
    segs = finger_path(rows_by_line, tl, duration)

    starts = [l["start"] for l in tl["lines"]]
    ends = [l["end"] for l in tl["lines"]]
    FADE = 0.45

    cache = {"n": -1, "img": None}

    def base_with(n_done):
        if cache["n"] != n_done:
            img = bg.copy()
            for i in range(n_done):
                lay, top = layers[i]
                img.alpha_composite(lay, (0, top))
            cache["n"], cache["img"] = n_done, img
        return cache["img"]

    nframes = int(round(duration * FPS))
    only = None
    if out_path is None:
        only = sorted(preview_png)
    proc = None if only is not None else subprocess.Popen([
        "ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
        "-i", "-", "-i", audio_path, "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-profile:v", "high",
        "-tune", "stillimage", "-g", "60", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-t", f"{duration:.3f}", "-movflags", "+faststart", out_path], stdin=subprocess.PIPE)

    for fi in (only if only is not None else range(nframes)):
        t = fi / FPS
        # lines fully visible
        n_done = sum(1 for s in starts if t >= s - 0.3 + FADE)
        frame = base_with(n_done).copy()
        # line currently fading in
        for i, s in enumerate(starts):
            a = (t - (s - 0.3)) / FADE
            if 0 < a < 1:
                lay, top = layers[i]
                al = lay.copy()
                al.putalpha(lay.split()[3].point(lambda v, k=ease(a): int(v * k)))
                frame.alpha_composite(al, (0, top))
        fx, fy, li, ri, ux, reading = finger_at(segs, t, size)
        # gold underline following the fingertip (current line, fades after the line ends)
        rows = rows_by_line[li]
        ua = 1.0
        if t > ends[li]:
            ua = 1 - ease((t - ends[li]) / 0.5)
        if t < starts[li] - 0.05:
            ua = 0
        if ua > 0:
            d = ImageDraw.Draw(frame)
            col = (178, 132, 44, int(235 * ua))
            for rj, r in enumerate(rows):
                uy = r["y"] + int(size * 1.02)
                if rj < ri:
                    xa, xb = r["x0"], r["x1"]
                elif rj == ri:
                    xa, xb = r["x0"], min(max(ux, r["x0"]), r["x1"])
                else:
                    continue
                if xb > xa + 1:
                    ov = Image.new("RGBA", (int(xb - xa) + 4, 6), (0, 0, 0, 0))
                    ImageDraw.Draw(ov).line((1, 2, int(xb - xa) + 1, 2), fill=col, width=3)
                    frame.alpha_composite(ov, (int(xa) - 1, uy))
        # natural micro-motion
        fx += math.sin(t * 1.7) * 1.2
        fy += math.sin(t * 1.1 + 0.6) * 1.5
        # arm angle depends on horizontal position (pivot is the elbow, lower right)
        ang_u = (fx - TEXT_X0) / (TEXT_X1 - TEXT_X0)
        ai = int(round((1 - min(max(ang_u, 0), 1)) * (len(angles) - 1)))
        himg, hsh, htip = hands[ai]
        ox, oy = int(fx - htip[0]), int(fy - htip[1])
        _paste_clip(frame, hsh, ox + 22, oy + 30)
        _paste_clip(frame, himg, ox, oy)
        if preview_png and fi in preview_png:
            frame.convert("RGB").save(preview_png[fi])
        if proc is None:
            continue
        proc.stdin.write(frame.convert("RGB").tobytes())
    if proc is None:
        return
    proc.stdin.close()
    proc.wait()
    if proc.returncode:
        raise RuntimeError("ffmpeg failed")


def _paste_clip(dst, src, x, y):
    sx0, sy0 = max(0, -x), max(0, -y)
    dx0, dy0 = max(0, x), max(0, y)
    w = min(src.width - sx0, dst.width - dx0); h = min(src.height - sy0, dst.height - dy0)
    if w <= 0 or h <= 0:
        return
    dst.alpha_composite(src.crop((sx0, sy0, sx0 + w, sy0 + h)), (dx0, dy0))
