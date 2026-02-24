"""
arabic_utils.py
===============
Arabic text reshaping and BiDi utilities.

FIX: is_bismillah() now uses a robust contains-check instead of
exact equality, so it works regardless of tashkeel diacritics,
tatweel (U+0640), superscript alef (U+0670) or Unicode variants
returned by different Quran APIs.
"""

import re

import arabic_reshaper
from bidi.algorithm import get_display


_reshaper = arabic_reshaper.ArabicReshaper(
    configuration={
        "delete_harakat":         False,
        "support_ligatures":      True,
        "shift_harakat_position": False,
    }
)


def reshape(text: str) -> str:
    """Reshape + BiDi so PIL renders Arabic correctly."""
    return get_display(_reshaper.reshape(text))


def _strip_arabic_decoration(text: str) -> str:
    """Remove diacritics, tatweel, zero-width chars, superscript alef."""
    cleaned = re.sub(
        r"[\u0610-\u061A\u0640\u064B-\u065F\u0670\u200B-\u200F\uFEFF]",
        "",
        text,
    )
    return re.sub(r"\s+", " ", cleaned).strip()


_BISM_WORDS = ["بسم", "الله", "الرحمن", "الرحيم"]

BISMILLAH_ARABIC_WORDS  = ["بِسْمِ", "اللَّهِ", "الرَّحْمَٰنِ", "الرَّحِيمِ"]
BISMILLAH_ENGLISH_WORDS = ["In the name of Allah,", "the Most Gracious,", "the Most Merciful"]
BISMILLAH_ENGLISH       = "In the name of Allah, the Most Gracious, the Most Merciful"


def is_bismillah(text: str) -> bool:
    """
    Return True if text IS the Bismillah phrase.
    Robust: works regardless of tashkeel, tatweel, Unicode variants.
    """
    stripped = _strip_arabic_decoration(text)
    return all(w in stripped for w in _BISM_WORDS)
