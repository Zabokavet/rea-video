"""Haitian Creole text preparation: numbers become words so every voice reads them in Kreyòl.

Spelling follows common Haitian orthography; the words are what the voice pronounces,
so a phonetic spelling matters more than a single "correct" form.
"""
from __future__ import annotations

import re

_UNITS = ["zewo", "en", "de", "twa", "kat", "senk", "sis", "sèt", "uit", "nèf",
          "dis", "onz", "douz", "trèz", "katòz", "kenz", "sèz", "disèt", "dizuit", "diznèf"]
# tens: (alone, before "eyen" for 1, before a consonant, before a vowel)
_TENS = {2: ("ven", "venteyen", "venn", "vent"), 3: ("trant", "tranteyen", "trann", "trant"),
         4: ("karant", "karanteyen", "karann", "karant"), 5: ("senkant", "senkanteyen", "senkann", "senkant"),
         6: ("swasant", "swasanteyen", "swasann", "swasant")}


def _below_100(n: int) -> str:
    if n < 20:
        return _UNITS[n]
    t, u = divmod(n, 10)
    if t in _TENS:
        alone, one, cons, vowel = _TENS[t]
        if u == 0:
            return alone
        if u == 1:
            return one
        word = _UNITS[u]
        return (vowel if word[0] in "aeiouè" else cons) + word
    if t == 7:  # 70-79: swasann + 10..19
        return "swasanteonz" if u == 1 else "swasann" + _UNITS[10 + u]
    if t == 8:
        return "katreven" if u == 0 else "katreven " + _UNITS[u]
    return "katreven" + _UNITS[10 + u]  # 90-99


def _below_1000(n: int) -> str:
    h, r = divmod(n, 100)
    parts = []
    if h:
        parts.append("san" if h == 1 else f"{_UNITS[h]} san")
    if r or not h:
        parts.append(_below_100(r))
    return " ".join(parts)


def number_to_words(n: int) -> str:
    if n < 0:
        return "mwens " + number_to_words(-n)
    if n < 1000:
        return _below_1000(n)
    for size, name in ((10**9, "milya"), (10**6, "milyon"), (1000, "mil")):
        if n >= size:
            q, r = divmod(n, size)
            head = name if (q == 1 and size == 1000) else f"{number_to_words(q)} {name}"
            return head if r == 0 else f"{head} {number_to_words(r)}"
    return str(n)


def _replace_number(m: re.Match) -> str:
    raw = m.group(0)
    if re.fullmatch(r"\d{1,3}(?:[.,]\d{3})+", raw):  # 1,000 or 1.000 = one thousand
        raw = re.sub(r"[.,]", "", raw)
    whole, _, frac = raw.replace(" ", "").partition(",") if "," in raw and "." not in raw else raw.partition(".")
    whole = whole.replace(",", "").replace(".", "")
    if len(whole) > 12:  # e.g. a phone or ID number: read digit by digit
        return " ".join(_UNITS[int(d)] for d in raw if d.isdigit())
    words = number_to_words(int(whole))
    if frac:
        words += " pwen " + " ".join(_UNITS[int(d)] for d in frac)
    return words


def expand_numbers(text: str) -> str:
    """'3 ti kochon ak 25 goud' -> 'twa ti kochon ak vennsenk goud'."""
    text = re.sub(r"(\d+)\s*%", r"\1 pousan", text)
    return re.sub(r"\d{1,3}(?:[.,]\d{3})+(?!\d)|\d+(?:[.,]\d+)?", _replace_number, text)
