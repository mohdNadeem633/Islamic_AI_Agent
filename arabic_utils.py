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
    import unicodedata
    # Normalize to NFD to separate base characters and diacritics
    normalized = unicodedata.normalize('NFD', text)
    # Remove non-spacing marks (diacritics)
    cleaned = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    # Remove other decorations
    cleaned = re.sub(r"[\u0610-\u061A\u0640\u0670\u200B-\u200F\uFEFF]", "", cleaned)
    # Normalize alif variants
    cleaned = cleaned.replace('ٱ', 'ا')
    # Normalize yeh variants
    cleaned = cleaned.replace('ی', 'ي')
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


def starts_with_bismillah(text: str) -> bool:
    """Return True if *text* begins with the Bismillah phrase.

    The check ignores diacritics and other decoration by normalizing both
    the input text and the canonical Bismillah words before comparison.
    """
    # strip decorations to avoid mismatches
    stripped = _strip_arabic_decoration(text)
    words = stripped.split()
    if len(words) < 4:
        return False
    # compare against stripped canonical words
    canonical = [ _strip_arabic_decoration(w) for w in BISMILLAH_ARABIC_WORDS ]
    return words[:4] == canonical


def remove_leading_bismillah(text: str) -> str:
    """Strip leading Bismillah words from *text* if they appear.

    The comparison uses the same normalization as :func:`starts_with_bismillah`.
    Only the first four words are removed; the remainder of the verse is
    returned with leading whitespace trimmed.  If no match is found, *text*
    is returned unmodified.
    """
    if starts_with_bismillah(text):
        # remove first four words from the original text (not stripped) to
        # preserve diacritics/spacing in the remainder
        parts = text.split()
        return " ".join(parts[4:]).lstrip()
    return text
