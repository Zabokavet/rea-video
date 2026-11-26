"""Split long stories into pieces that fit a voice provider's per-request limit.

Splits happen at paragraph, then sentence, then clause, then word boundaries, so the
joined narration has no audible cuts mid-word. No text is ever dropped.
"""
from __future__ import annotations

import re

_SENTENCE_END = re.compile(r"(?<=[.!?…。！？])[\"'”’»）)]*\s+|(?<=[。！？])")
_CLAUSE_END = re.compile(r"(?<=[,;:，；：、—])\s*")


def _pieces(text: str, pattern: re.Pattern) -> list[str]:
    parts, start = [], 0
    for m in pattern.finditer(text):
        end = m.end()
        if end > start:
            parts.append(text[start:end])
            start = end
    if start < len(text):
        parts.append(text[start:])
    return [p for p in parts if p]


def _split_oversized(unit: str, limit: int) -> list[str]:
    if len(unit) <= limit:
        return [unit]
    for pattern in (_SENTENCE_END, _CLAUSE_END):
        parts = _pieces(unit, pattern)
        if len(parts) > 1:
            out: list[str] = []
            for p in parts:
                out.extend(_split_oversized(p, limit))
            return out
    # Fall back to word boundaries, then a hard cut for e.g. very long unspaced text.
    words = re.findall(r"\S+\s*", unit)
    if len(words) > 1:
        out, cur = [], ""
        for w in words:
            if cur and len(cur) + len(w) > limit:
                out.append(cur)
                cur = ""
            cur += w
            while len(cur) > limit:
                out.append(cur[:limit])
                cur = cur[limit:]
        if cur:
            out.append(cur)
        return out
    return [unit[i:i + limit] for i in range(0, len(unit), limit)]


def split_text(text: str, limit: int) -> list[str]:
    """Return chunks of at most ``limit`` characters that together hold all of ``text``."""
    if limit < 1:
        raise ValueError("limit must be positive")
    text = text.replace("\r\n", "\n").strip()
    if not text:
        return []
    units: list[str] = []
    for para in re.split(r"\n\s*\n", text):
        para = para.strip()
        if not para:
            continue
        for sentence in _pieces(para, _SENTENCE_END):
            units.extend(_split_oversized(sentence, limit))
        units[-1] = units[-1].rstrip() + "\n\n"

    chunks, cur = [], ""
    for u in units:
        if cur and len(cur) + len(u.rstrip()) > limit:
            chunks.append(cur.strip())
            cur = ""
        cur += u
    if cur.strip():
        chunks.append(cur.strip())
    return chunks
