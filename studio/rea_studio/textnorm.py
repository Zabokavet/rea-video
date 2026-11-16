"""Text normalisation for engines that cannot read digits (MMS-TTS vocabularies are letters only).

Haitian Creole numbers follow the standard Kreyòl orthography (IPN). Best practice is still to write numbers as
words in Kreyòl scripts; this converter covers 0-999,999,999 so years like 1804 are never silently dropped.
"""
from __future__ import annotations

import re

_HT_UNITS = ["zewo", "en", "de", "twa", "kat", "senk", "sis", "sèt", "uit", "nèf", "dis", "onz", "douz", "trèz",
             "katòz", "kenz", "sèz", "disèt", "dizuit", "diznèf"]
_HT_TENS = {20: "ven", 30: "trant", 40: "karant", 50: "senkant", 60: "swasant"}
_HT_TENS_PREFIX = {20: "venn", 30: "trann", 40: "karann", 50: "senkann", 60: "swasann"}
_HT_HUNDREDS = {1: "san", 2: "desan", 3: "twasan", 4: "katsan", 5: "senksan", 6: "sisan", 7: "sètsan", 8: "uisan",
                9: "nèfsan"}


def _ht_below_100(n: int) -> str:
    if n < 20:
        return _HT_UNITS[n]
    if n < 70:
        t, u = n // 10 * 10, n % 10
        if u == 0:
            return _HT_TENS[t]
        if u == 1:
            return _HT_TENS_PREFIX[t] + "teyen"
        if u in (8, 9):  # ventuit, ventnèf
            return _HT_TENS[t] + _HT_UNITS[u]
        return _HT_TENS_PREFIX[t] + _HT_UNITS[u]
    if n < 80:
        return "swasann" + _HT_UNITS[n - 60]
    if n == 80:
        return "katreven"
    return "katreven" + _HT_UNITS[n - 80]


def ht_number(n: int) -> str:
    if n < 100:
        return _ht_below_100(n)
    if n < 1000:
        h, r = divmod(n, 100)
        return _HT_HUNDREDS[h] + ("" if r == 0 else " " + _ht_below_100(r))
    if n < 1_000_000:
        th, r = divmod(n, 1000)
        head = "mil" if th == 1 else ht_number(th) + " mil"
        return head + ("" if r == 0 else " " + ht_number(r))
    if n < 1_000_000_000:
        m, r = divmod(n, 1_000_000)
        return ht_number(m) + " milyon" + ("" if r == 0 else " " + ht_number(r))
    return " ".join(_HT_UNITS[int(d)] for d in str(n))


def normalize(text: str, lang: str) -> str:
    if lang == "ht":
        text = re.sub(r"(\d+)%", lambda m: m.group(1) + " pousan", text)
        text = re.sub(r"\$\s?(\d+)", lambda m: m.group(1) + " dola", text)
        text = re.sub(r"(\d{1,3})(?:[ ,.](\d{3}))+", lambda m: m.group(0).replace(",", "").replace(" ", "").replace(".", ""), text)
        text = re.sub(r"\d+", lambda m: ht_number(int(m.group(0))), text)
    return text
