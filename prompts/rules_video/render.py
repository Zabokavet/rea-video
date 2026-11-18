"""Render the 'rules' book-and-pen video frames.

usage: python render.py <workdir> <out_video_noaudio.mp4> [--still t1,t2,...]
workdir must contain sents.json (text, rule, sent, dur, words[] from ASR) and timeline.json.
"""
import json, math, os, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

WD = sys.argv[1]
OUT = sys.argv[2]
STILLS = None
if len(sys.argv) > 3 and sys.argv[3] == "--still":
    STILLS = [float(x) for x in sys.argv[4].split(",")]
HERE = os.path.dirname(os.path.abspath(__file__))
FONTDIR = os.environ["REA_FONTS"]
FPS = 30
W, H = 1242, 2208          # scene (supersampled for the camera push-in)
OW, OH = 1080, 1920        # output
PW, PH = 1000, 1880        # right page, page space
INK = (24, 28, 62)         # ballpoint ink
TEXT = (30, 25, 22)
rng = np.random.default_rng(7)


def font(name, size, wght):
    f = ImageFont.truetype(os.path.join(FONTDIR, name), size)
    f.set_variation_by_axes([wght])
    return f

F_HOOK = font("LibreBaskerville[wght].ttf", 70, 700)
F_BODY = font("LibreBaskerville[wght].ttf", 56, 440)
F_CTA = font("LibreBaskerville-Italic[wght].ttf", 56, 480)

sents = json.load(open(f"{WD}/sents.json"))
NR = max(s["rule"] for s in sents) + 1
rules = {}
for i, s in enumerate(sents):
    rules.setdefault(s["rule"], []).append(i)

# ---------------------------------------------------------------- layout
ML, MR, MT, MB = 96, 86, 180, 160
TWID = PW - ML - MR
PARA_GAP = 50


def style(r):
    if r == 0:
        return F_HOOK, 100
    if r == NR - 1:
        return F_CTA, 88
    return F_BODY, 86


def layout_pages():
    pages, y = [[]], MT
    for r in range(NR):
        f, lh = style(r)
        sp = f.getlength(" ")
        lines, x = [[]], 0.0
        for si in rules[r]:
            for w in sents[si]["text"].split():
                wl = f.getlength(w)
                if lines[-1] and x + wl > TWID:
                    lines.append([]); x = 0.0
                lines[-1].append(dict(w=w, si=si, x0=ML + x, x1=ML + x + wl))
                x += wl + sp
        h = len(lines) * lh
        if pages[-1] and (r == NR - 1 or y + h > PH - MB):
            pages.append([]); y = MT
        pages[-1].append(dict(r=r, f=f, lh=lh, y=y,
                              lines=[dict(words=ln, base=y + lh * 0.72 + i * lh) for i, ln in enumerate(lines)]))
        y += h + PARA_GAP
    # vertically centre the closing page
    last = pages[-1]
    top = last[0]["y"]; bot = last[-1]["y"] + len(last[-1]["lines"]) * last[-1]["lh"]
    off = (PH - (bot - top)) / 2 - top - 60
    for p in last:
        for ln in p["lines"]:
            ln["base"] += off
    return pages

PAGES = layout_pages()
# sentence -> page, segments [(x0, x1, ul_y)], words [(seg, x0, x1)]
SENT = [dict(page=None, segs=[], words=[]) for _ in sents]
for pi, pg in enumerate(PAGES):
    for para in pg:
        for ln in para["lines"]:
            ul = ln["base"] + 15
            bysent = {}
            for w in ln["words"]:
                bysent.setdefault(w["si"], []).append(w)
            for si, ws in bysent.items():
                S_ = SENT[si]; S_["page"] = pi
                seg = len(S_["segs"])
                S_["segs"].append((ws[0]["x0"] - 5, ws[-1]["x1"] + 6, ul))
                for w in ws:
                    S_["words"].append((seg, w["x0"], w["x1"]))
# global segment ids per page, in reading order
PAGE_SEGS = [[] for _ in PAGES]
for si, S_ in enumerate(SENT):
    for k, sg in enumerate(S_["segs"]):
        S_.setdefault("gid", []).append(len(PAGE_SEGS[S_["page"]]))
        PAGE_SEGS[S_["page"]].append(sg)

if not os.path.exists(f"{WD}/timeline.json"):
    json.dump([SENT[i]["page"] for i in range(len(sents))], open(f"{WD}/layout.json", "w"))
    print("pages:", len(PAGES), [SENT[i]["page"] for i in range(len(sents))]); sys.exit(0)
TL = json.load(open(f"{WD}/timeline.json"))
for i, s in enumerate(sents):
    s["words_abs"] = [(TL["sent"][i]["t0"] + w["s"], TL["sent"][i]["t0"] + w["e"]) for w in TL["sent"][i]["words"]]

# ---------------------------------------------------------------- geometry
Q = [(176, 158), (1150, 186), (1196, 2072), (138, 2056)]   # right page quad in scene (mild keystone)


def homog(src, dst):
    A, b = [], []
    for (x, y), (u, v) in zip(src, dst):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); b.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); b.append(v)
    h = np.linalg.solve(np.array(A, float), np.array(b, float))
    return np.append(h, 1).reshape(3, 3)

HM = homog([(0, 0), (PW, 0), (PW, PH), (0, PH)], Q)


def P(x, y, M=HM):
    v = M @ np.array([x, y, 1.0])
    return v[0] / v[2], v[1] / v[2]


def T(dx, dy):
    return np.array([[1, 0, dx], [0, 1, dy], [0, 0, 1.0]])


def warp_onto(base, img, M_img2scene, resample=Image.BILINEAR):
    """alpha-composite RGBA img onto RGB base using homography img px -> scene."""
    w, h = img.size
    cs = [P(x, y, M_img2scene) for x, y in [(0, 0), (w, 0), (w, h), (0, h)]]
    bx0 = max(0, int(math.floor(min(c[0] for c in cs))) - 1)
    by0 = max(0, int(math.floor(min(c[1] for c in cs))) - 1)
    bx1 = min(W, int(math.ceil(max(c[0] for c in cs))) + 1)
    by1 = min(H, int(math.ceil(max(c[1] for c in cs))) + 1)
    if bx1 <= bx0 or by1 <= by0:
        return
    M = np.linalg.inv(M_img2scene) @ T(bx0, by0)
    M = M / M[2, 2]
    out = img.transform((bx1 - bx0, by1 - by0), Image.PERSPECTIVE, M.flatten()[:8].tolist(), resample)
    base.paste(out, (bx0, by0), out)


def blur_noise(w, h, scale, seed, sx=None, sy=None):
    r = np.random.default_rng(seed)
    sx = sx or scale; sy = sy or scale
    small = r.standard_normal((max(2, int(h / sy)), max(2, int(w / sx)))).astype(np.float32)
    im = Image.fromarray(((small - small.min()) / (np.ptp(small) + 1e-6) * 255).astype(np.uint8))
    im = im.resize((w, h), Image.BICUBIC)
    a = np.asarray(im, np.float32) / 255.0
    return (a - a.mean()) / (a.std() + 1e-6)

# ---------------------------------------------------------------- paper & desk


def paper(w, h, seed, gutter="left"):
    base = np.array([236, 227, 206], np.float32)
    n = 5.0 * blur_noise(w, h, 140, seed) + 2.5 * blur_noise(w, h, 18, seed + 1) + 2.0 * np.random.default_rng(seed + 2).standard_normal((h, w)).astype(np.float32)
    img = base[None, None, :] + n[..., None] * np.array([1.0, 1.0, 0.9])
    x = np.arange(w, dtype=np.float32)[None, :]
    y = np.arange(h, dtype=np.float32)[:, None]
    gx = x if gutter == "left" else (w - 1 - x)
    shade = 1 - 0.50 * np.exp(-gx / 45) - 0.14 * np.exp(-gx / 240) + 0.025 * np.exp(-((gx - 170) / 120) ** 2)
    edge = np.minimum(np.minimum(w - 1 - gx, y), h - 1 - y)
    shade = shade * (1 - 0.10 * np.exp(-edge / 28))
    img = img * shade[..., None] if shade.ndim == 2 else img * shade[..., None]
    return np.clip(img, 0, 255)


def make_desk():
    x = np.arange(W, dtype=np.float32)[None, :]
    grain = blur_noise(W, H, 0, 11, sx=14, sy=420) * 1.0 + 0.6 * blur_noise(W, H, 0, 12, sx=4, sy=160)
    warp = 30 * blur_noise(W, H, 0, 13, sx=300, sy=600)
    rings = np.sin((x + warp) / 9.0 + grain * 1.3)
    v = 0.55 + 0.18 * rings + 0.22 * grain
    col = np.array([62, 38, 24], np.float32)
    img = col[None, None, :] * (0.75 + 0.5 * v[..., None])
    for sx in (60, 1215):  # plank seams
        img[:, sx:sx + 3] *= 0.45
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


def text_layer(pg):
    im = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for para in pg:
        for ln in para["lines"]:
            for w in ln["words"]:
                d.text((w["x0"], ln["base"]), w["w"], font=para["f"], fill=TEXT + (238,), anchor="ls")
    return im


def page_canvas(pi):
    """right page incl. stacked page edges on right/bottom (RGBA)."""
    cw, ch = PW + 26, PH + 20
    can = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    # stack of page edges
    st = np.zeros((ch, cw, 4), np.uint8)
    for k in range(9):
        c = 214 - (k % 2) * 40 - k * 6
        st[: PH + 2 + 2 * k, PW: PW + 3 + 2 * k + 3, :3] = c
        st[PH: PH + 3 + 2 * k, : PW + 3 + 2 * k, :3] = c
    st[..., 3] = (st[..., :3].sum(-1) > 0) * 255
    can = Image.alpha_composite(can, Image.fromarray(st))
    pap = Image.fromarray(paper(PW, PH, 100 + pi).astype(np.uint8)).convert("RGBA")
    can.paste(pap, (0, 0))
    can = Image.alpha_composite(can, Image.new("RGBA", can.size, (0, 0, 0, 0)))
    tl = text_layer(PAGES[pi]) if pi is not None else None
    if tl is not None:
        can.alpha_composite(tl, (0, 0))
    return can


def back_canvas(pi_front):
    """back of a leaf (shows faint mirrored text of the front)."""
    pap = Image.fromarray(paper(PW, PH, 300 + pi_front, gutter="right").astype(np.uint8)).convert("RGBA")
    if pi_front is not None and pi_front >= 0:
        ghost = text_layer(PAGES[pi_front]).transpose(Image.FLIP_LEFT_RIGHT)
        a = np.asarray(ghost).copy(); a[..., 3] = (a[..., 3] * 0.06).astype(np.uint8)
        pap.alpha_composite(Image.fromarray(a).filter(ImageFilter.GaussianBlur(1.2)))
    return pap


def ink_strip(length, seed):
    s, Hh = 3, 26
    L = int(length) + 24
    r = np.random.default_rng(seed)
    im = Image.new("L", (L * s, Hh * s), 0)
    d = ImageDraw.Draw(im)
    xs = np.linspace(12, 12 + length, max(10, int(length * 1.2)))
    ph = r.uniform(0, 6.3)
    ys = Hh / 2 + r.uniform(0.8, 1.8) * np.sin(xs / r.uniform(70, 120) + ph) + r.uniform(-2.2, 2.2) * (xs - 12) / max(length, 1) \
        + 0.4 * np.sin(xs / 9 + ph * 2)
    wd = 2.5 + 0.5 * np.sin(xs / 41 + ph)
    t = (xs - 12) / max(length, 1)
    wd *= np.clip(np.minimum(t / 0.02, (1 - t) / 0.03), 0.45, 1.0)
    for x, y, w_ in zip(xs, ys, wd):
        d.ellipse([(x - w_) * s, (y - w_) * s, (x + w_) * s, (y + w_) * s], fill=235)
    a = im.resize((L, Hh), Image.LANCZOS)
    rgba = Image.new("RGBA", (L, Hh), INK + (0,))
    rgba.putalpha(a)
    return rgba  # page-space origin = (seg_x0 - 12, ul_y - Hh/2)

# ---------------------------------------------------------------- hand + pen sprite
D = np.array([0.40, 0.9165]); D /= np.linalg.norm(D)
N = np.array([D[1], -D[0]])          # to the right/up of the pen axis
LIGHT = np.array([-0.55, -0.62, 0.86]); LIGHT /= np.linalg.norm(LIGHT)
SS = 2  # supersample for sprite build


def build_hand():
    smax, umin, umax = 1950, -170, 400
    corners = [(s, u) for s in (0, smax) for u in (umin, umax)]
    pts = [(s * D[0] + u * N[0], s * D[1] + u * N[1]) for s, u in corners]
    x0 = min(p[0] for p in pts) - 40; y0 = min(p[1] for p in pts) - 40
    x1 = max(p[0] for p in pts) + 40; y1 = max(p[1] for p in pts) + 40
    w, h = int(x1 - x0), int(y1 - y0)
    tip = np.array([-x0, -y0])
    Wb, Hb = w * SS, h * SS

    def pt(s, u):
        p = (tip + s * D + u * N) * SS
        return (float(p[0]), float(p[1]))

    def capsule(m, a, b, ra, rb, steps=24):
        d_ = ImageDraw.Draw(m)
        for k in range(steps + 1):
            t = k / steps
            s = a[0] + (b[0] - a[0]) * t; u = a[1] + (b[1] - a[1]) * t; r = (ra + (rb - ra) * t) * SS
            c = pt(s, u)
            d_.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=255)

    def poly(m, su):
        ImageDraw.Draw(m).polygon([pt(s, u) for s, u in su], fill=255)

    def newm():
        return Image.new("L", (Wb, Hb), 0)

    yy, xx = np.mgrid[0:Hb, 0:Wb].astype(np.float32) / SS
    rel_x, rel_y = xx - tip[0], yy - tip[1]
    S_loc = rel_x * D[0] + rel_y * D[1]
    U_loc = rel_x * N[0] + rel_y * N[1]

    canvas = np.zeros((Hb, Wb, 3), np.float32)
    alpha = np.zeros((Hb, Wb), np.float32)

    def shade_part(mask, color, rad, amb=0.42, dif=0.78, spec=0.10, shin=18, ao=0.38):
        nonlocal canvas, alpha
        m = np.asarray(mask, np.float32) / 255.0
        if m.max() == 0:
            return
        hgt = np.asarray(mask.filter(ImageFilter.GaussianBlur(rad * SS)), np.float32) / 255.0
        hgt = np.sqrt(np.clip(hgt, 0, 1))
        gy, gx = np.gradient(hgt * rad * SS * 1.4)
        nz = np.ones_like(gx)
        nn = np.sqrt(gx * gx + gy * gy + nz * nz)
        nx, ny, nz = -gx / nn, -gy / nn, nz / nn
        lam = np.clip(nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2], 0, 1)
        hv = LIGHT + np.array([0, 0, 1.0]); hv /= np.linalg.norm(hv)
        sp = np.clip(nx * hv[0] + ny * hv[1] + nz * hv[2], 0, 1) ** shin
        col = np.array(color, np.float32)[None, None, :] * (amb + dif * lam)[..., None] + 255 * spec * sp[..., None]
        # ambient occlusion on what is underneath
        occ = np.asarray(mask.filter(ImageFilter.GaussianBlur(9 * SS)), np.float32) / 255.0
        canvas *= (1 - ao * occ * (1 - m))[..., None]
        canvas = canvas * (1 - m[..., None]) + col * m[..., None]
        alpha = np.maximum(alpha, m)

    SKIN = (176, 128, 102)
    # forearm in a dark suit sleeve, white shirt cuff peeking out
    sl = newm(); capsule(sl, (760, 95), (1800, 230), 132, 150, steps=60)
    shade_part(sl, (34, 36, 44), 60, amb=0.55, dif=0.55, spec=0.03)
    cf = newm(); capsule(cf, (700, 88), (770, 96), 122, 126, steps=12)
    shade_part(cf, (205, 205, 198), 30, amb=0.5, dif=0.55, spec=0.04)
    # wrist + back of hand
    bh = newm()
    capsule(bh, (600, 85), (720, 88), 112, 118, steps=16)
    poly(bh, [(330, -60), (318, 40), (336, 150), (385, 236), (470, 268), (580, 250), (670, 175), (712, 70), (695, -40), (610, -98), (470, -110), (390, -95)])
    # curled ring + little fingers (seen as knuckle rolls from above)
    capsule(bh, (300, 150), (395, 190), 34, 40)
    capsule(bh, (340, 205), (430, 240), 30, 36)
    shade_part(bh, SKIN, 46, amb=0.40, dif=0.70)
    # middle finger tucked under the index (only its upper edge shows)
    mf = newm(); capsule(mf, (190, 44), (300, 70), 22, 27); capsule(mf, (300, 70), (370, 96), 27, 32)
    shade_part(mf, SKIN, 16, amb=0.36, dif=0.66)
    # pen (procedural cylinder shading)
    pen = newm()
    poly(pen, [(4, -3), (42, -11), (42, 11), (4, 3)])
    capsule(pen, (44, 0), (640, -6), 12, 11, steps=140)
    pm = np.asarray(pen, np.float32) / 255.0
    halfw = np.where(S_loc < 42, 3 + (S_loc / 42) * 8, 12.0)
    un = np.clip(U_loc / halfw, -1, 1)
    nzc = np.sqrt(1 - un ** 2)
    Ls, Lu = LIGHT[0] * D[0] + LIGHT[1] * D[1], LIGHT[0] * N[0] + LIGHT[1] * N[1]
    lam = np.clip(un * Lu + nzc * LIGHT[2], 0, 1)
    hv_u, hv_z = Lu, LIGHT[2] + 1; hn = math.hypot(hv_u, hv_z); hv_u /= hn; hv_z /= hn
    spec = np.clip(un * hv_u + nzc * hv_z, 0, 1)
    metal = (S_loc < 42) | ((S_loc > 150) & (S_loc < 157))
    rubber = (S_loc >= 42) & (S_loc <= 150)
    base = np.where(metal, 150.0, np.where(rubber, 26.0, 16.0))
    sp_k = np.where(metal, 230.0, np.where(rubber, 25.0, 200.0)) * spec ** np.where(metal, 12.0, np.where(rubber, 4.0, 40.0))
    pcol = (base * (0.35 + 0.8 * lam))[..., None] * np.array([1.0, 1.0, 1.04]) + sp_k[..., None]
    clip_m = (S_loc > 500) & (S_loc < 615) & (U_loc > -4) & (U_loc < 4)
    pcol = np.where((clip_m & (pm > 0))[..., None], np.array([170.0, 170, 176]) * (0.6 + 0.6 * lam[..., None]), pcol)
    occ = np.asarray(pen.filter(ImageFilter.GaussianBlur(7 * SS)), np.float32) / 255.0
    canvas *= (1 - 0.35 * occ * (1 - pm))[..., None]
    canvas = canvas * (1 - pm[..., None]) + pcol * pm[..., None]
    alpha = np.maximum(alpha, pm)
    # thumb (left of pen) and index finger (resting on top of the pen)
    th = newm(); capsule(th, (122, -21), (240, -40), 24, 30); capsule(th, (240, -40), (390, -66), 30, 44)
    shade_part(th, SKIN, 18, amb=0.38, dif=0.70)
    ix = newm(); capsule(ix, (70, 5), (172, 9), 18, 20); capsule(ix, (172, 9), (268, 22), 20, 24); capsule(ix, (268, 22), (360, 40), 24, 30)
    shade_part(ix, SKIN, 15, amb=0.40, dif=0.72)
    nl = newm(); capsule(nl, (75, 5), (104, 7), 10, 11, steps=8)
    shade_part(nl, (205, 170, 152), 5, spec=0.22, shin=30, ao=0.1)
    tn = newm(); capsule(tn, (127, -31), (146, -34), 7, 8, steps=8)
    shade_part(tn, (205, 170, 152), 4, spec=0.18, shin=30, ao=0.1)
    # knuckle creases
    kn = Image.new("L", (Wb, Hb), 0); dk = ImageDraw.Draw(kn)
    for s0, u0 in [(178, 14), (272, 32), (290, 96)]:
        dk.arc([pt(s0 - 10, u0 - 18)[0] - 14, pt(s0 - 10, u0 - 18)[1] - 14, pt(s0 - 10, u0 - 18)[0] + 14, pt(s0 - 10, u0 - 18)[1] + 14], 200, 320, fill=255, width=SS * 2)
    km = np.asarray(kn.filter(ImageFilter.GaussianBlur(1.5)), np.float32) / 255.0
    canvas *= (1 - 0.25 * km)[..., None]

    canvas *= (1 + 0.035 * blur_noise(Wb, Hb, 3, 77))[..., None]
    rgba = np.dstack([np.clip(canvas, 0, 255), alpha * 255]).astype(np.uint8)
    spr = Image.fromarray(rgba, "RGBA").filter(ImageFilter.GaussianBlur(0.9)).resize((w, h), Image.LANCZOS)
    # contact shadow: shear so it grows with distance from the tip (height above paper)
    v = np.array([0.62, 0.78]); k = 0.075
    Mf = np.eye(2) + k * np.outer(v, D)
    pad = 160
    Mi = np.linalg.inv(Mf)
    # output pixel p' (in padded frame) -> input pixel p
    off = Mf @ tip - tip  # keep tip fixed
    c = -Mi @ (np.array([pad, pad]) + off)
    a_img = spr.getchannel("A")
    sh = a_img.transform((w + 2 * pad, h + 2 * pad), Image.AFFINE, (Mi[0, 0], Mi[0, 1], c[0] + 0 * 0 + Mi[0] @ np.array([0, 0]) + 0, Mi[1, 0], Mi[1, 1], c[1]), Image.BILINEAR)
    # correct affine constant: input = Mi @ (p' - pad - off) ; recompute precisely
    cc = -Mi @ (np.array([pad, pad]) + off)
    sh = a_img.transform((w + 2 * pad, h + 2 * pad), Image.AFFINE, (Mi[0, 0], Mi[0, 1], cc[0], Mi[1, 0], Mi[1, 1], cc[1]), Image.BILINEAR)
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    return spr, tip, sh, tip + pad


# ---------------------------------------------------------------- timeline helpers
def ease(u):
    u = min(1.0, max(0.0, u)); return u * u * (3 - 2 * u)


def head_at(si, t):
    """(segment index, x) of the underline head for sentence si at absolute time t, or None before start."""
    S_ = SENT[si]; ws = sents[si]["words_abs"]
    if t < ws[0][0]:
        return None
    for k, (ws0, we0) in enumerate(ws):
        seg, x0, x1 = S_["words"][k]
        if t < ws0:
            pseg, px0, px1 = S_["words"][k - 1]
            return (pseg, px1)
        if t <= we0:
            u = (t - ws0) / max(we0 - ws0, 1e-3)
            xs = x0 - 5 if k == 0 or S_["words"][k - 1][0] != seg else x0 - 4
            return (seg, xs + (x1 + (6 if k == len(ws) - 1 else 0) - xs) * u)
    seg, x0, x1 = S_["words"][-1]
    return (seg, x1 + 6)


def state_at(t):
    """page shown, completed segs on that page, partial (gid, x), pen tip page-coords, lift, turn."""
    st = dict(page=0, done=0, partial=None, tip=None, lift=0.0, turn=None)
    # turns
    for tr in TL["turns"]:
        if tr["t0"] <= t < tr["t1"]:
            u = (t - tr["t0"]) / (tr["t1"] - tr["t0"])
            st.update(page=tr["to"], done=0, turn=dict(frm=tr["frm"], u=u))
            return st
    # which page are we on
    pg = 0
    for tr in TL["turns"]:
        if t >= tr["t1"]:
            pg = tr["to"]
    st["page"] = pg
    done = 0; partial = None
    for si, S_ in enumerate(SENT):
        if S_["page"] != pg:
            continue
        start, end = TL["sent"][si]["t0"], TL["sent"][si]["t1"]
        if t >= end + 0.05:
            done = S_["gid"][-1] + 1
        elif t >= start:
            hh = head_at(si, t)
            if hh is not None:
                seg, x = hh
                done = S_["gid"][seg]
                partial = (S_["gid"][seg], x)
            break
        else:
            break
    st["done"], st["partial"] = done, partial
    return st


def pen_target(t):
    """pen tip in page coords + lift (or leaf-following during turns)."""
    sp = TL["sent"]
    # during a turn
    for tr in TL["turns"]:
        if tr["t0"] - 0.25 <= t < tr["t1"] + 0.35:
            frm = tr["frm"]
            last = [si for si, S_ in enumerate(SENT) if S_["page"] == frm][-1]
            a = (SENT[last]["segs"][-1][1], SENT[last]["segs"][-1][2])
            nxt = [si for si, S_ in enumerate(SENT) if S_["page"] == tr["to"]][0]
            b = (SENT[nxt]["segs"][0][0] + 4, SENT[nxt]["segs"][0][2])
            corner = (PW - 70, PH * 0.80)
            if t < tr["t0"]:
                u = ease((t - (tr["t0"] - 0.25)) / 0.25)
                return (a[0] + (corner[0] - a[0]) * u, a[1] + (corner[1] - a[1]) * u), 40 * math.sin(math.pi * u) + 6 * u, None
            uu = (t - tr["t0"]) / (tr["t1"] - tr["t0"])
            if uu < 0.5:
                th = math.pi * ease(uu * 1.0) if False else math.pi * leaf_ease(min(uu, 1))
                ex = PW * math.cos(th) - 60
                return (max(ex, -120), corner[1]), 6 + 30 * math.sin(math.pi * uu), dict(follow=True)
            th = math.pi * leaf_ease(0.5)
            ex = PW * math.cos(th) - 60
            u = ease((t - (tr["t0"] + 0.5 * (tr["t1"] - tr["t0"]))) / (tr["t1"] + 0.35 - (tr["t0"] + 0.5 * (tr["t1"] - tr["t0"]))))
            p0 = (max(ex, -120), corner[1])
            return (p0[0] + (b[0] - p0[0]) * u, p0[1] + (b[1] - p0[1]) * u), 36 * math.sin(math.pi * u) * (1 - u) + 30 * (1 - u), None
    # writing / between sentences
    order = list(range(len(sents)))
    for si in order:
        t0, t1 = sp[si]["t0"], sp[si]["t1"]
        if t0 <= t <= t1 + 0.05:
            hh = head_at(si, t)
            S_ = SENT[si]
            if hh is None:
                return (S_["segs"][0][0] + 4, S_["segs"][0][2]), 0.0, None
            seg, x = hh
            return (x, S_["segs"][seg][2]), 0.0, None
    # gaps
    for si in range(len(sents) - 1):
        a_end, b_start = sp[si]["t1"] + 0.05, sp[si + 1]["t0"]
        if a_end < t < b_start:
            A = SENT[si]; B = SENT[si + 1]
            pa = (A["segs"][-1][1], A["segs"][-1][2]); pb = (B["segs"][0][0] + 4, B["segs"][0][2])
            u = ease((t - a_end) / (b_start - a_end))
            return (pa[0] + (pb[0] - pa[0]) * u, pa[1] + (pb[1] - pa[1]) * u), 26 * math.sin(math.pi * u), None
    if t < sp[0]["t0"]:
        B = SENT[0]; return (B["segs"][0][0] + 4, B["segs"][0][2]), 0.0, None
    # tail: lift and retreat
    A = SENT[-1]; pa = (A["segs"][-1][1], A["segs"][-1][2])
    u = ease((t - sp[-1]["t1"] - 0.05) / 1.2)
    return (pa[0] + 90 * u, pa[1] + 160 * u), 70 * u, None


def leaf_ease(u):
    u = min(1.0, max(0.0, u))
    return 0.5 - 0.5 * math.cos(math.pi * u)


# ---------------------------------------------------------------- precompute shared assets
print("building assets...", flush=True)
DESK = make_desk()
SHADOW_BOOK = Image.new("L", (W, H), 0)
ImageDraw.Draw(SHADOW_BOOK).polygon([(q[0] + 20, q[1] + 30) for q in Q] + [], fill=200)
ImageDraw.Draw(SHADOW_BOOK).rectangle([0, 120, 200, 2110], fill=200)
SHADOW_BOOK = SHADOW_BOOK.filter(ImageFilter.GaussianBlur(28))
BASE0 = Image.composite(Image.new("RGB", (W, H), (8, 5, 3)), DESK, SHADOW_BOOK.point(lambda v: int(v * 0.85)))
# left page (back of previous leaf) in the same plane, mirrored gutter
LEFT = back_canvas(-1)
warp_onto(BASE0, LEFT, HM @ T(-PW, 0))
PAGE_IMG = [page_canvas(i) for i in range(len(PAGES))]
BACK_IMG = [back_canvas(i) for i in range(len(PAGES))]
STRIPS = [[ink_strip(sg[1] - sg[0], 1000 * pi + k) for k, sg in enumerate(PAGE_SEGS[pi])] for pi in range(len(PAGES))]
HAND, HAND_TIP, HSHADOW, HSHADOW_TIP = build_hand()
HAND_A = HAND.getchannel("A")

# lamp light (scene space): warm key from the upper-left, cool dark falloff
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
lx, ly = -220.0, 300.0
d2 = ((xx - lx) ** 2 + (yy - ly) ** 2) / (2 * 1350.0 ** 2)
I = 0.10 + 1.08 * np.exp(-d2 * 1.25)
I = 1.12 * I / (1 + 0.12 * I)
warm = np.array([1.0, 0.88, 0.70], np.float32)
cool = np.array([0.70, 0.76, 0.92], np.float32)
mixc = np.clip((I - 0.25) / 0.7, 0, 1)[..., None]
LIGHTMAP = (I[..., None] * (warm * mixc + cool * (1 - mixc))).astype(np.float32)
del xx, yy, d2, I, mixc

base_cache = {}


def page_base(pi, done):
    key = (pi, done)
    if key in base_cache:
        return base_cache[key]
    if done == 0:
        im = BASE0.copy()
        warp_onto(im, PAGE_IMG[pi], HM)
    else:
        im = page_base(pi, done - 1).copy()
        x0, x1, ul = PAGE_SEGS[pi][done - 1]
        warp_onto(im, STRIPS[pi][done - 1], HM @ T(x0 - 12, ul - 13))
    base_cache[key] = im
    return im


def leaf_full(pi):
    k = ("leaf", pi)
    if k not in base_cache:
        im = PAGE_IMG[pi].copy()
        for g, (x0, x1, ul) in enumerate(PAGE_SEGS[pi]):
            im.alpha_composite(STRIPS[pi][g], (int(round(x0 - 12)), int(round(ul - 13))))
        base_cache[k] = im
    return base_cache[k]


def draw_turn(im, frm, u):
    th = math.pi * leaf_ease(u)
    c = math.cos(th); lift = 34 * math.sin(th)
    # shadow of the leaf on the revealed page
    sh = Image.new("L", (W // 2, H // 2), 0)
    ex = PW * c
    shq = [P(0, 0), P(max(ex, 0) + 40 + 60 * math.sin(th), -lift), P(max(ex, 0) + 40 + 60 * math.sin(th), PH + lift), P(0, PH)]
    ImageDraw.Draw(sh).polygon([(x / 2, y / 2) for x, y in shq], fill=int(160 * math.sin(th) + 40))
    sh = sh.filter(ImageFilter.GaussianBlur(18)).resize((W, H), Image.BILINEAR)
    arr = np.asarray(im, np.float32) * (1 - 0.5 * np.asarray(sh, np.float32)[..., None] / 255)
    im.paste(Image.fromarray(arr.astype(np.uint8)))
    if c >= 0:
        src = leaf_full(frm)
        dark = 1 - 0.38 * math.sin(th)
    else:
        src = BACK_IMG[frm].transpose(Image.FLIP_LEFT_RIGHT) if False else BACK_IMG[frm]
        dark = 1 - 0.30 * math.sin(th) + 0.05
    a = np.asarray(src, np.float32).copy()
    # curl shading toward the moving edge
    gx = np.linspace(0, 1, a.shape[1], dtype=np.float32)[None, :]
    curl = (1 - 0.25 * math.sin(th) * gx ** 2) if c >= 0 else (1 - 0.25 * math.sin(th) * (1 - gx) ** 2)
    a[..., :3] *= (dark * curl)[..., None] if np.ndim(curl) else dark
    leaf = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
    lw, lh = leaf.size
    if abs(c) < 0.015:
        return
    if c >= 0:
        dst = [(0, 0), (PW * c, -lift), (PW * c, PH + lift), (0, PH)]
    else:
        dst = [(PW * c, -lift), (0, 0), (0, PH), (PW * c, PH + lift)]
    Mi2p = homog([(0, 0), (lw, 0), (lw, lh), (0, lh)], dst)
    warp_onto(im, leaf, HM @ Mi2p)


# ---------------------------------------------------------------- camera path (sequential)
def precompute_camera(nf):
    cams = []
    cx, cy, z = W / 2, H / 2 + 20, 1.03
    for f in range(nf):
        t = f / FPS
        tip, lift, _ = pen_target(t)
        sx, sy = P(*tip)
        # page-local push in
        pg_start, pg_end = 0.0, TL["end"]
        for tr in TL["turns"]:
            if t >= tr["t1"]:
                pg_start = tr["t1"]
        nxt = [tr["t0"] for tr in TL["turns"] if tr["t0"] > t]
        pg_end = nxt[0] if nxt else TL["end"]
        prog = (t - pg_start) / max(pg_end - pg_start, 1e-3)
        zt = 1.035 + 0.10 * prog
        if any(tr["t0"] <= t < tr["t1"] for tr in TL["turns"]):
            zt = 1.03
        cyt = H / 2 + 0.55 * (sy - H / 2)
        cxt = W / 2 + 0.18 * (sx - W / 2)
        a_c, a_z = 1 - math.exp(-1 / (FPS * 0.9)), 1 - math.exp(-1 / (FPS * 0.45))
        if f == 0:
            cx, cy, z = cxt, cyt, zt
        cx += (cxt - cx) * a_c; cy += (cyt - cy) * a_c; z += (zt - z) * a_z
        cams.append((cx, cy, z))
    return cams


GRAIN = [np.random.default_rng(50 + i).normal(0, 4.2, (OH, OW)).astype(np.float32) for i in range(6)]
VIG_Y, VIG_X = np.mgrid[0:OH, 0:OW].astype(np.float32)
VIG = (1 - 0.32 * (((VIG_X - OW / 2) / (OW * 0.62)) ** 2 + ((VIG_Y - OH / 2) / (OH * 0.62)) ** 2)).clip(0.5, 1)[..., None]
del VIG_X, VIG_Y


def render_frame(f, cam, tipcache):
    t = f / FPS
    st = state_at(t)
    if st["turn"]:
        im = page_base(st["page"], 0).copy()
        draw_turn(im, st["turn"]["frm"], st["turn"]["u"])
    else:
        im = page_base(st["page"], st["done"]).copy()
        if st["partial"]:
            g, x = st["partial"]
            x0, x1, ul = PAGE_SEGS[st["page"]][g]
            strip = STRIPS[st["page"]][g]
            wcrop = int(round(x - (x0 - 12)))
            if wcrop > 2:
                warp_onto(im, strip.crop((0, 0, min(wcrop, strip.size[0]), strip.size[1])), HM @ T(x0 - 12, ul - 13))
    # pen + hand
    tip, lift = tipcache[f]
    jit = 0.0 if lift > 1 else 1.0
    sx, sy = P(tip[0] + jit * 0.9 * math.sin(2 * math.pi * 11 * t), tip[1] + jit * 1.3 * math.sin(2 * math.pi * 7 * t))
    # shadow (multiplied), offset grows with lift
    ox = int(round(sx - HSHADOW_TIP[0] + 0.62 * lift * 1.1)); oy = int(round(sy - HSHADOW_TIP[1] + 0.78 * lift * 1.1))
    arr = np.asarray(im).astype(np.float32)
    shw = np.asarray(HSHADOW, np.float32) / 255.0
    x0, y0 = max(0, ox), max(0, oy); x1, y1 = min(W, ox + shw.shape[1]), min(H, oy + shw.shape[0])
    if x1 > x0 and y1 > y0:
        arr[y0:y1, x0:x1] *= (1 - 0.55 * shw[y0 - oy:y1 - oy, x0 - ox:x1 - ox])[..., None]
    im = Image.fromarray(arr.astype(np.uint8))
    hx = int(round(sx - HAND_TIP[0] - 0.35 * lift)); hy = int(round(sy - HAND_TIP[1] - 0.45 * lift))
    im.paste(HAND, (hx, hy), HAND)
    # light
    arr = np.asarray(im, np.float32) * LIGHTMAP
    # camera
    cx, cy, z = cam
    cw, ch = W / z, H / z
    cx = min(max(cx, cw / 2), W - cw / 2); cy = min(max(cy, ch / 2), H - ch / 2)
    box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).resize((OW, OH), Image.BICUBIC, box=box)
    o = np.asarray(img, np.float32) * VIG + GRAIN[f % 6][..., None]
    # gentle filmic toe: lift blacks slightly, warm highlights
    o = 255 * (np.clip(o, 0, 255) / 255) ** 1.06
    # end fade
    fade = min(1.0, max(0.0, (TL["end"] - t) / 0.45))
    return np.clip(o * fade, 0, 255).astype(np.uint8)


def main():
    nf = int(math.ceil(TL["end"] * FPS))
    cams = precompute_camera(nf)
    tips = []
    for f in range(nf):
        tip, lift, _ = pen_target(f / FPS)
        tips.append((tip, lift))
    # light smoothing of the pen path (critically damped, ~1.5 frames)
    sm = []; px, py = tips[0][0]
    for (tx, ty), l in tips:
        px += (tx - px) * 0.75; py += (ty - py) * 0.75
        sm.append(((px, py), l))
    if STILLS:
        for ts in STILLS:
            f = int(ts * FPS)
            Image.fromarray(render_frame(f, cams[f], sm)).save(f"{WD}/still_{ts:05.2f}.png")
            print("still", ts)
        return
    nproc = 4
    chunk = math.ceil(nf / nproc)
    pids = []
    for w in range(nproc):
        a, b = w * chunk, min(nf, (w + 1) * chunk)
        pid = os.fork()
        if pid == 0:
            seg = f"{WD}/seg{w}.mp4"
            p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                                  "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", seg], stdin=subprocess.PIPE)
            for f in range(a, b):
                p.stdin.write(render_frame(f, cams[f], sm).tobytes())
                if (f - a) % 150 == 0:
                    print(f"worker {w}: {f - a}/{b - a}", flush=True)
            p.stdin.close(); p.wait()
            os._exit(0)
        pids.append(pid)
    for pid in pids:
        os.waitpid(pid, 0)
    with open(f"{WD}/segs.txt", "w") as fh:
        for w in range(nproc):
            fh.write(f"file 'seg{w}.mp4'\n")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", f"{WD}/segs.txt", "-c", "copy", OUT], check=True)
    print("done", OUT)


if __name__ == "__main__":
    main()
