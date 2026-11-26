"""Descriptive, filesystem-safe download names built from the story title."""
from __future__ import annotations

import re
import unicodedata
from datetime import datetime
from urllib.parse import quote

_MAX_STEM = 80


def title_stem(title: str) -> str:
    """'The Lighthouse Keeper: Part 2' -> 'The-Lighthouse-Keeper-Part-2'. Keeps non-Latin letters."""
    t = unicodedata.normalize("NFKC", title or "").strip()
    t = re.sub(r"[^\w\s-]", " ", t, flags=re.UNICODE)
    t = re.sub(r"[\s_-]+", "-", t).strip("-")
    return t[:_MAX_STEM].rstrip("-") or "narration"


def ascii_stem(stem: str) -> str:
    """ASCII-only fallback for old clients. A title with no Latin letters becomes 'narration'."""
    m = re.fullmatch(r"(.*?)(_\d{4}-\d\d-\d\d_\d{4})?", stem)
    title, stamp = m.group(1), m.group(2) or ""
    a = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    a = re.sub(r"[^A-Za-z0-9]+", "-", a).strip("-")
    if not re.search(r"[A-Za-z]", a):
        a = "narration"
    return a + stamp


def download_name(title: str, created_at: str, ext: str) -> str:
    try:
        stamp = datetime.fromisoformat(created_at).strftime("%Y-%m-%d_%H%M")
    except (TypeError, ValueError):
        stamp = ""
    stem = title_stem(title)
    return f"{stem}_{stamp}.{ext}" if stamp else f"{stem}.{ext}"


def content_disposition(filename: str, attachment: bool = True) -> str:
    """RFC 6266 header with an ASCII fallback and a UTF-8 ``filename*`` for non-Latin titles."""
    stem, _, ext = filename.rpartition(".")
    fallback = f"{ascii_stem(stem)}.{ext}"
    kind = "attachment" if attachment else "inline"
    return f"{kind}; filename=\"{fallback}\"; filename*=UTF-8''{quote(filename)}"
