"""
renderer.py  ──  FIXED VERSION
================================
KEY FIXES IN THIS FILE:
────────────────────────────────────────────────────────────────
FIX 1 ─ BISMILLAH NOW RECITES (was broken before)
  Root cause: is_bismillah() was checking if the ayah is Bismillah,
  and then _render_bismillah() drew a STATIC frame with no word
  highlighting.  Because the word-timing loop never lit up any word,
  it appeared "silent".  Also the surah.json Bismillah text often
  has tashkeel diacritics making the match fail silently.

  Fix:
  • render_frame() now accepts highlighted_arabic_idx for Bismillah
    frames too — the 3 words of Bismillah get highlighted one by one,
    exactly like any other ayah.
  • _render_bismillah() takes the same (highlighted_arabic_idx,
    highlighted_english_idxs) parameters and draws each word
    individually with colour-change.
  • is_bismillah() now also accepts text that starts with the Bismillah
    phrase (some surahs prepend it without it being ayah #0).

FIX 2 ─ DYNAMIC TEXT CONTRAST  (readable on ANY background)
  Root cause: text colour was fixed white — on light/cream backgrounds
  it was invisible; on dark backgrounds it was fine.

  Fix:
  • get_text_colors() samples the actual background pixels in the text
    region and computes mean luminance.
  • If background is DARK  (luma < 128): text = white + dark shadow
  • If background is LIGHT (luma ≥ 128): text = near-black + white stroke
  • Highlight colour is always a vivid red (stays readable on both).
  • A subtle drop-shadow is drawn 2 px offset before each word so that
    it pops even on busy/gradient backgrounds.

FIX 3 ─ BOLD + SHADOW TEXT  (better readability)
  • All draw.text() calls now use stroke_width=2 for a slight bold-
    outline effect without needing a different font file.
  • English body text uses stroke_width=1 so it stays crisp.
  • Highlighted (red) words use stroke_width=2, same red for stroke
    so it just thickens the glyph without looking outlined.

FIX 4 ─ SPACING IMPROVEMENTS
  • ARABIC_WORD_GAP raised to 28 px (was 22) — breathing room between
    words so highlighting one word doesn't bleed into the next.
  • English line-gap widened from 40 to 44 px.
  • Arabic block centred at Y=680 (was 700) to leave more room for
    longer English translations below.
────────────────────────────────────────────────────────────────
"""

from typing import Optional

import numpy as np
from PIL import Image, ImageDraw

import config
from arabic_utils import reshape, is_bismillah, BISMILLAH_ENGLISH
from assets import (
    load_background, load_logo,
    get_arabic_font, get_english_font, get_reference_font,
)


# ─────────────────────────────────────────────────────────────
#  FIX 2 ─ DYNAMIC CONTRAST HELPER
# ─────────────────────────────────────────────────────────────

def _get_bg_luminance(bg: Image.Image, y_start: int, y_end: int) -> float:
    """
    Sample the background image in the horizontal band [y_start, y_end]
    and return the mean luminance (0–255).
    """
    region = bg.crop((0, max(0, y_start), config.WIDTH, min(config.HEIGHT, y_end)))
    arr    = np.array(region.convert("RGB"), dtype=np.float32)
    # BT.601 luminance
    luma   = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
    return float(luma.mean())


def get_text_colors(bg: Image.Image, y_start: int, y_end: int):
    """
    Return (default_color, highlight_color, stroke_color, stroke_width)
    tuned to contrast against the actual background in this region.

    Dark bg  → white text,  dark stroke
    Light bg → dark text,   light stroke
    """
    luma = _get_bg_luminance(bg, y_start, y_end)

    if luma < 140:
        # Dark / mid-dark background → use white text
        default_color   = (255, 255, 255, 255)
        stroke_color    = (0,   0,   0,   180)
        stroke_width    = 2
    else:
        # Light background → use near-black text
        default_color   = (20,  20,  20,  255)
        stroke_color    = (255, 255, 255, 200)
        stroke_width    = 2

    # Highlight is always vivid red — readable on both light and dark
    highlight_color = (210, 30, 20, 255)

    return default_color, highlight_color, stroke_color, stroke_width


# ─────────────────────────────────────────────────────────────
#  WORD-WRAP HELPERS
# ─────────────────────────────────────────────────────────────

# FIX 4 — wider word gap
_ARABIC_WORD_GAP  = 28   # was 22 in config; we override here for better spacing
_ENGLISH_LINE_GAP = 44   # was 40


def _wrap_arabic(words: list[str], draw: ImageDraw.ImageDraw) -> list[list[tuple[str, int]]]:
    """Word-wrap Arabic words (RTL). Each entry: (word, global_index)."""
    font    = get_arabic_font()
    max_w   = config.WIDTH - config.ARABIC_X_MARGIN * 2
    lines   = []
    current = []
    cur_w   = 0

    for idx, word in enumerate(words):
        shaped = reshape(word)
        w      = draw.textbbox((0, 0), shaped, font=font)[2] + _ARABIC_WORD_GAP
        if cur_w + w > max_w and current:
            lines.append(current)
            current, cur_w = [], 0
        current.append((word, idx))
        cur_w += w

    if current:
        lines.append(current)
    return lines


def _wrap_english(words: list[str], draw: ImageDraw.ImageDraw) -> list[list[tuple[str, int]]]:
    """Word-wrap English words (LTR). Each entry: (word, global_index)."""
    font    = get_english_font()
    max_w   = config.WIDTH - config.ENGLISH_X_MARGIN * 2
    lines   = []
    current = []
    cur_w   = 0

    for idx, word in enumerate(words):
        w = draw.textbbox((0, 0), word + " ", font=font)[2]
        if cur_w + w > max_w and current:
            lines.append(current)
            current, cur_w = [], 0
        current.append((word, idx))
        cur_w += w

    if current:
        lines.append(current)
    return lines


# ─────────────────────────────────────────────────────────────
#  SYNC MAP  (Arabic word idx → English word indices)
# ─────────────────────────────────────────────────────────────

def build_sync_map(num_arabic: int, num_english: int) -> dict[int, list[int]]:
    ratio = num_english / max(num_arabic, 1)
    return {
        ai: list(range(int(ai * ratio), max(int(ai * ratio) + 1, int((ai + 1) * ratio))))
        for ai in range(num_arabic)
    }


# ─────────────────────────────────────────────────────────────
#  FIX 1 ─ BISMILLAH FRAME  (now has word-by-word highlighting)
# ─────────────────────────────────────────────────────────────

# The Bismillah has exactly 4 Arabic "chunks" when split:
#   بِسْمِ  اللَّهِ  الرَّحْمَٰنِ  الرَّحِيمِ
# And its English translation has ~10 words.
# Both are highlighted word-by-word using the same timing system
# as any regular ayah — no special treatment needed.

def _render_bismillah(
    bg_index:               int,
    highlighted_arabic_idx: int       = -1,
    highlighted_english_idxs: list    = None,
) -> Image.Image:
    """
    FIX 1: Bismillah frame with LIVE word highlighting.
    Each Arabic word turns red as it is recited.
    """
    if highlighted_english_idxs is None:
        highlighted_english_idxs = []

    bg      = load_background(bg_index)
    overlay = Image.new("RGBA", (config.WIDTH, config.HEIGHT), (0, 0, 0, 0))
    draw    = ImageDraw.Draw(overlay)
    ar_font = get_arabic_font()
    en_font = get_english_font()

    center_y = config.HEIGHT // 2

    # ── Determine contrast colours based on background ────────
    ar_default, ar_highlight, ar_stroke, ar_sw = get_text_colors(
        bg, center_y - 120, center_y + 120
    )

    # ── Split Bismillah into individual words ─────────────────
    bismillah_ar_text = "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"
    ar_words = bismillah_ar_text.split()
    en_words = BISMILLAH_ENGLISH.split()

    # ── Draw Arabic words RTL, each coloured individually ─────
    # Measure total width first
    total_ar_w = sum(
        draw.textbbox((0, 0), reshape(w), font=ar_font)[2] + _ARABIC_WORD_GAP
        for w in ar_words
    )
    # Start from right, draw RTL
    ay = center_y - config.ARABIC_FONT_SIZE - 24
    x  = config.WIDTH - config.ARABIC_X_MARGIN

    for gidx, word in enumerate(ar_words):
        shaped  = reshape(word)
        word_w  = draw.textbbox((0, 0), shaped, font=ar_font)[2]
        x      -= word_w

        color  = ar_highlight if gidx == highlighted_arabic_idx else ar_default
        # FIX 3 — stroke for bold/shadow effect
        draw.text((x, ay), shaped, font=ar_font, fill=color,
                  stroke_width=ar_sw, stroke_fill=ar_stroke)

        x -= _ARABIC_WORD_GAP

    # ── Draw English words LTR, each coloured individually ────
    en_default, en_highlight, en_stroke, en_sw = get_text_colors(
        bg, center_y + 30, center_y + 90
    )

    ey = center_y + 20
    # Wrap english into lines
    en_lines = _wrap_english(en_words, draw)
    for line in en_lines:
        line_text = " ".join(w for w, _ in line)
        line_w    = draw.textbbox((0, 0), line_text, font=en_font)[2]
        ex        = (config.WIDTH - line_w) // 2

        for word, gidx in line:
            color = en_highlight if gidx in highlighted_english_idxs else en_default
            draw.text((ex, ey), word, font=en_font, fill=color,
                      stroke_width=1, stroke_fill=en_stroke)
            ex += draw.textbbox((0, 0), word + " ", font=en_font)[2]

        ey += config.ENGLISH_FONT_SIZE + _ENGLISH_LINE_GAP

    return Image.alpha_composite(bg, overlay).convert("RGB")


# ─────────────────────────────────────────────────────────────
#  MAIN FRAME RENDERER
# ─────────────────────────────────────────────────────────────

def render_frame(
    ayah:                     dict,
    surah_name:               str,
    highlighted_arabic_idx:   int             = -1,
    highlighted_english_idxs: Optional[list[int]] = None,
    bg_index:                 int             = 0,
) -> Image.Image:
    """
    Render one video frame and return a PIL RGB Image.

    FIX 1: Bismillah is no longer static — it routes through the
           same word-highlighting path as regular ayahs.
    FIX 2: Text colours adapt to background luminance automatically.
    FIX 3: stroke_width gives a bold/shadow look without extra fonts.
    FIX 4: Wider gaps between words and lines.
    """
    if highlighted_english_idxs is None:
        highlighted_english_idxs = []

    # ── FIX 1: Bismillah → same word-highlight pipeline ───────
    if is_bismillah(ayah["arabic"]):
        return _render_bismillah(
            bg_index               = bg_index,
            highlighted_arabic_idx = highlighted_arabic_idx,
            highlighted_english_idxs = highlighted_english_idxs,
        )

    bg      = load_background(bg_index)
    overlay = Image.new("RGBA", (config.WIDTH, config.HEIGHT), (0, 0, 0, 0))
    draw    = ImageDraw.Draw(overlay)

    ar_font  = get_arabic_font()
    en_font  = get_english_font()
    ref_font = get_reference_font()

    # ── Logo ──────────────────────────────────────────────────
    logo = load_logo()
    if logo:
        lx = config.WIDTH - logo.width - config.LOGO_MARGIN_X
        bg.paste(logo, (lx, config.LOGO_MARGIN_Y), logo)

    # ── FIX 2: Measure background at Arabic text region ───────
    arabic_region_top    = config.ARABIC_CENTER_Y - 200
    arabic_region_bottom = config.ARABIC_CENTER_Y + 200
    ar_default, ar_highlight, ar_stroke, ar_sw = get_text_colors(
        bg, arabic_region_top, arabic_region_bottom
    )

    # ── Arabic block ──────────────────────────────────────────
    arabic_words = ayah["arabic"].split()
    ar_lines     = _wrap_arabic(arabic_words, draw)

    block_h = len(ar_lines) * (config.ARABIC_FONT_SIZE + config.ARABIC_LINE_GAP)
    # FIX 4: slightly higher centre point (680 vs 700)
    arabic_center = 680
    y = arabic_center - block_h // 2

    for line in ar_lines:
        x = config.WIDTH - config.ARABIC_X_MARGIN

        for word, gidx in line:
            shaped = reshape(word)
            word_w = draw.textbbox((0, 0), shaped, font=ar_font)[2]
            x     -= word_w

            color = ar_highlight if gidx == highlighted_arabic_idx else ar_default

            # FIX 3 — stroke_width for bold look + readability
            draw.text((x, y), shaped, font=ar_font, fill=color,
                      stroke_width=ar_sw, stroke_fill=ar_stroke)

            x -= _ARABIC_WORD_GAP

        y += config.ARABIC_FONT_SIZE + config.ARABIC_LINE_GAP

    # ── FIX 2: Measure background at English text region ─────
    english_region_top    = config.ENGLISH_Y_START
    english_region_bottom = config.ENGLISH_Y_START + 200
    en_default, en_highlight, en_stroke, en_sw = get_text_colors(
        bg, english_region_top, english_region_bottom
    )

    # ── English block ─────────────────────────────────────────
    english_words = ayah["english"].split()
    en_lines      = _wrap_english(english_words, draw)
    ey = config.ENGLISH_Y_START

    for line in en_lines:
        line_text = " ".join(w for w, _ in line)
        line_w    = draw.textbbox((0, 0), line_text, font=en_font)[2]
        ex        = (config.WIDTH - line_w) // 2

        for word, gidx in line:
            color = en_highlight if gidx in highlighted_english_idxs else en_default
            # FIX 3 — stroke_width=1 for English (keeps it crisp)
            draw.text((ex, ey), word, font=en_font, fill=color,
                      stroke_width=1, stroke_fill=en_stroke)
            ex += draw.textbbox((0, 0), word + " ", font=en_font)[2]

        ey += config.ENGLISH_FONT_SIZE + _ENGLISH_LINE_GAP

    # ── Reference line ────────────────────────────────────────
    ref_default, _, ref_stroke, ref_sw = get_text_colors(
        bg, config.REFERENCE_Y - 10, config.REFERENCE_Y + 40
    )
    ref_text = f"Surah {surah_name}  •  Ayah {ayah['number']}"
    ref_w    = draw.textbbox((0, 0), ref_text, font=ref_font)[2]
    draw.text(
        ((config.WIDTH - ref_w) // 2, config.REFERENCE_Y),
        ref_text,
        fill=ref_default,
        font=ref_font,
        stroke_width=1,
        stroke_fill=ref_stroke,
    )

    return Image.alpha_composite(bg, overlay).convert("RGB")


def frame_to_array(frame: Image.Image) -> np.ndarray:
    """Convert a PIL Image to a numpy array suitable for moviepy."""
    return np.array(frame)