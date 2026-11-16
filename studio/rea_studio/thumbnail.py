"""Click-worthy thumbnails from a keyframe: punchy grade, readable headline, accent word, safe margins."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from .util import find_font

ACCENTS = {"yellow": (255, 214, 0), "red": (235, 40, 40), "cyan": (0, 220, 255), "green": (60, 220, 90),
           "orange": (255, 140, 0), "white": (255, 255, 255)}


def _fit_lines(draw, words, font_path, max_w, max_h, max_lines=3):
    for size in range(int(max_h / 1.6), 20, -4):
        f = ImageFont.truetype(str(font_path), size)
        lines, cur = [], []
        for w in words:
            trial = " ".join(cur + [w])
            if draw.textlength(trial, font=f) <= max_w or not cur:
                cur.append(w)
            else:
                lines.append(cur)
                cur = [w]
        lines.append(cur)
        widest = max(draw.textlength(" ".join(ln), font=f) for ln in lines)
        if len(lines) <= max_lines and size * 1.12 * len(lines) <= max_h and widest <= max_w:
            return f, lines
    return ImageFont.truetype(str(font_path), 24), [words]


def make(keyframe: Path, text: str, out: Path, aspect: str = "16:9", accent: str = "yellow",
         accent_words: list[str] | None = None, side: str = "auto") -> Path:
    W, H = (1280, 720) if aspect in ("16:9", "21:9") else ((1080, 1920) if aspect == "9:16" else (1080, 1080))
    img = Image.open(keyframe).convert("RGB")
    s = max(W / img.width, H / img.height)
    img = img.resize((int(img.width * s + 1), int(img.height * s + 1)), Image.LANCZOS)
    img = img.crop(((img.width - W) // 2, (img.height - H) // 2, (img.width - W) // 2 + W, (img.height - H) // 2 + H))
    img = ImageEnhance.Contrast(img).enhance(1.18)
    img = ImageEnhance.Color(img).enhance(1.25)
    img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=80, threshold=2))
    # gradient scrim behind the text for legibility
    scrim = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(scrim)
    vertical = H > W
    if side == "auto":
        side = "bottom" if vertical else "left"
    for i in range(W if side == "left" else H):
        if side == "left":
            a = int(200 * max(0, 1 - i / (W * 0.62)) ** 1.4)
            sd.line([(i, 0), (i, H)], fill=a)
        else:
            a = int(210 * max(0, (i - H * 0.45) / (H * 0.55)) ** 1.2)
            sd.line([(0, i), (W, i)], fill=a)
    img = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), img, scrim)
    d = ImageDraw.Draw(img)
    font_path = find_font("title")
    words = text.upper().split()
    if side == "left":
        box = (int(W * 0.05), int(H * 0.1), int(W * 0.58), int(H * 0.8))
    else:
        box = (int(W * 0.06), int(H * 0.58), int(W * 0.88), int(H * 0.3))
    if font_path is None:
        font, lines = ImageFont.load_default(), [words]
    else:
        font, lines = _fit_lines(d, words, font_path, box[2], box[3])
    acc = {w.upper().strip(".,!?") for w in (accent_words or [])}
    if not acc and words:
        acc = {max(words, key=len).strip(".,!?")}  # highlight the longest word by default
    lh = int(font.size * 1.12)
    y = box[1] + (box[3] - lh * len(lines)) // 2
    stroke = max(3, font.size // 14)
    for line in lines:
        x = box[0]
        for w in line:
            col = ACCENTS.get(accent, ACCENTS["yellow"]) if w.strip(".,!?") in acc else (255, 255, 255)
            d.text((x + 4, y + 5), w, font=font, fill=(0, 0, 0))  # drop shadow
            d.text((x, y), w, font=font, fill=col, stroke_width=stroke, stroke_fill=(0, 0, 0))
            x += d.textlength(w + " ", font=font)
        y += lh
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, quality=92)
    return out
