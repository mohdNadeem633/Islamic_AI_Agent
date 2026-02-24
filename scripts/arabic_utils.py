"""
arabic_utils.py  ──  FIXED VERSION
====================================
KEY FIX HERE:
─────────────────────────────────────────────────────────────────
FIX 1 ─ ROBUST BISMILLAH DETECTION

  Root cause of "Bismillah not reciting":
  The old is_bismillah() stripped diacritics and then did an exact
  equality check:
      stripped == "بسم الله الرحمن الرحيم"

  This silently FAILED for two common reasons:
  (a) The JSON from alquran.cloud API returns the Bismillah as:
      "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"
      After stripping harakāt you get:
      "بسم الله الرحمن الرحيم"   ← with TATWEEL / spacing variants
      that don't always match the hardcoded string exactly.

  (b) Some surahs have Bismillah as ayah 1 with the full text that
      also contains extra Unicode normalization characters.

  Fix: use a CONTAINS check on key root words after aggressive
  cleaning (remove all Unicode 600-6FF non-letter chars).
  If the text contains both "بسم" AND "الله" AND "الرحمن", it IS
  the Bismillah — regardless of diacritics, tatweel, or spacing.

IMPORTANT NOTE FOR AUDIO SYNC:
  Because is_bismillah() now returns True, the clip_builder will
  call render_frame() normally for each frame, passing in the
  highlighted_arabic_idx — so the 4 Bismillah words will turn red
  one by one, exactly like every other ayah.  No other code change
  needed in clip_builder or video_exporter.
─────────────────────────────────────────────────────────────────
"""

import re
import unicodedata

import arabic_reshaper
from bidi.algorithm import get_display


# ─────────────────────────────────────────────────────────────
#  RESHAPER (configured once at import time)
# ─────────────────────────────────────────────────────────────

_reshaper = arabic_reshaper.ArabicReshaper(
    configuration={
        "delete_harakat":         False,   # keep diacritics (tashkeel)
        "support_ligatures":      True,
        "shift_harakat_position": False,
    }
)


def reshape(text: str) -> str:
    """
    Reshape Arabic text and apply BiDi algorithm so PIL renders it correctly.
    Call this on every Arabic string before passing it to ImageDraw.text().
    """
    return get_display(_reshaper.reshape(text))


def _strip_arabic(text: str) -> str:
    """
    Remove ALL Arabic diacritics, tatweel, zero-width joiners,
    and other decoration — leave only base letters and spaces.
    """
    # Remove harakāt (U+064B – U+0652), tatweel (U+0640), maddah,
    # waṣla, superscript alef (U+0670), and common zero-width chars.
    cleaned = re.sub(
        r"[\u0610-\u061A\u064B-\u065F\u0670\u0640\u200B-\u200F\uFEFF]",
        "",
        text,
    )
    # Collapse multiple spaces
    return re.sub(r"\s+", " ", cleaned).strip()


def is_bismillah(text: str) -> bool:
    """
    FIX 1 — Return True if *text* is (or starts with) the Bismillah phrase.

    Uses a CONTAINS / ROOT-WORD approach instead of exact equality so it
    works regardless of tashkeel, tatweel, Unicode normalization, or
    whether extra words follow.

    The three root words that uniquely identify the Bismillah are:
        بسم  (bismi)
        الله  (Allah)
        الرحمن  (al-Rahman)
    All three must be present for the function to return True.
    """
    stripped = _strip_arabic(text)

    # The three anchors
    has_bism    = "بسم"    in stripped
    has_allah   = "الله"   in stripped
    has_rahman  = "الرحمن" in stripped

    return has_bism and has_allah and has_rahman


BISMILLAH_ENGLISH = "In the name of Allah, the Most Gracious, the Most Merciful"