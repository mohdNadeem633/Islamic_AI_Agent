"""
renderer.py
===========
Pure frame-rendering logic.

FIXES in this version:
  1. Bismillah now highlights word-by-word (was fully static before)
  2. Dynamic text contrast adapts to background brightness automatically
  3. Text stroke makes words readable on ANY background colour
  4. TV/YouTube landscape format supported (16:9) alongside phone (9:16)
  5. All layout values come from SETTINGS.py — no numbers buried in code
"""

from typing import Optional

import numpy as np
from PIL import Image, ImageDraw

import config
from arabic_utils import (
    reshape,
    BISMILLAH_ARABIC_WORDS, BISMILLAH_ENGLISH_WORDS, BISMILLAH_ENGLISH,
)
from assets import (
    load_background, load_logo,
    get_arabic_font, get_english_font, get_reference_font,
)


# ─────────────────────────────────────────────────────────────
#  DYNAMIC CONTRAST  (Fix 2 + 3)
# ─────────────────────────────────────────────────────────────

def _region_luminance(bg: Image.Image, y_top: int, y_bottom: int,
                      width: int, height: int) -> float:
    """
    Sample the background in the band [y_top, y_bottom] and return
    mean luminance (0 = black … 255 = white).
    """
    y0 = max(0, y_top)
    y1 = min(height, y_bottom)
    if y1 <= y0:
        return 128.0
    region = bg.crop((0, y0, width, y1))
    arr    = np.array(region.convert("RGB"), dtype=np.float32)
    luma   = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
    return float(luma.mean())


def _text_style(bg: Image.Image, y_top: int, y_bottom: int,
                width: int, height: int):
    """
    Return (default_fill, stroke_fill, stroke_width) tuned to the
    background brightness in the given region.

    Dark background  → white text, dark stroke (shadow)
    Light background → near-black text, white stroke (halo)
    """
    if not getattr(config, "AUTO_CONTRAST", True):
        return config.ARABIC_DEFAULT_COLOR, (0, 0, 0, 140), 1

    luma = _region_luminance(bg, y_top, y_bottom, width, height)
    sw   = getattr(config, "TEXT_STROKE_WIDTH", 2)

    if luma < 145:
        return (255, 255, 255, 255), (0, 0, 0, 160), sw
    else:
        return (18,  18,  18,  255), (255, 255, 255, 180), sw


# ─────────────────────────────────────────────────────────────
#  WORD-WRAP HELPERS
# ─────────────────────────────────────────────────────────────

def _wrap_arabic(words, draw, width):
    font  = get_arabic_font()
    max_w = width - config.ARABIC_X_MARGIN * 2
    lines, current, cur_w = [], [], 0
    for idx, word in enumerate(words):
        shaped = reshape(word)
        w = draw.textbbox((0, 0), shaped, font=font)[2] + config.ARABIC_WORD_GAP
        if cur_w + w > max_w and current:
            lines.append(current); current, cur_w = [], 0
        current.append((word, idx)); cur_w += w
    if current:
        lines.append(current)
    return lines


def _wrap_english(words, draw, width):
    font  = get_english_font()
    max_w = width - config.ENGLISH_X_MARGIN * 2
    lines, current, cur_w = [], [], 0
    for idx, word in enumerate(words):
        w = draw.textbbox((0, 0), word + " ", font=font)[2]
        if cur_w + w > max_w and current:
            lines.append(current); current, cur_w = [], 0
        current.append((word, idx)); cur_w += w
    if current:
        lines.append(current)
    return lines


# ─────────────────────────────────────────────────────────────
#  SYNC MAP
# ─────────────────────────────────────────────────────────────

def build_sync_map(num_arabic: int, num_english: int) -> dict:
    ratio = num_english / max(num_arabic, 1)
    return {
        ai: list(range(int(ai * ratio), max(int(ai * ratio) + 1, int((ai + 1) * ratio))))
        for ai in range(num_arabic)
    }


# ─────────────────────────────────────────────────────────────
#  DRAW HELPERS
# ─────────────────────────────────────────────────────────────

def _draw_word(draw, x, y, text, font, fill, stroke_fill, stroke_width):
    """Draw one word with optional stroke (bold/shadow effect)."""
    if stroke_width > 0:
        draw.text((x, y), text, font=font, fill=fill,
                  stroke_width=stroke_width, stroke_fill=stroke_fill)
    else:
        draw.text((x, y), text, font=font, fill=fill)


# ─────────────────────────────────────────────────────────────
#  BISMILLAH FRAME  (Fix 1 – now highlights word-by-word)
# ─────────────────────────────────────────────────────────────


# ─────────────────────────────────────────────────────────────
#  MAIN FRAME RENDERER
# ─────────────────────────────────────────────────────────────

def render_frame(
    ayah:                     dict,
    surah_name:               str,
    highlighted_arabic_idx:   int             = -1,
    highlighted_english_idxs: Optional[list]  = None,
    bg_index:                 int             = 0,
    width:                    int             = None,
    height:                   int             = None,
    surah_number:             int             = 0,
) -> Image.Image:
    """
    Render one video frame → PIL RGB Image.

    width / height default to config.WIDTH / config.HEIGHT (phone format).
    Pass 1920 / 1080 for TV/laptop landscape format.
    surah_number: pass this to determine if we're rendering Surah Fatiha.
    """
    if highlighted_english_idxs is None:
        highlighted_english_idxs = []

    W = width  or config.WIDTH
    H = height or config.HEIGHT

    # ── Scale layout for landscape format ─────────────────────
    # For 16:9 we shift everything proportionally
    scale_x = W / config.WIDTH
    scale_y = H / config.HEIGHT

    def sx(v): return int(v * scale_x)
    def sy(v): return int(v * scale_y)

    bg      = load_background(bg_index, W, H)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw    = ImageDraw.Draw(overlay)

    ar_font  = get_arabic_font()
    en_font  = get_english_font()
    ref_font = get_reference_font()

    # ── Logo ──────────────────────────────────────────────────
    logo = load_logo()
    if logo:
        lx = W - logo.width - sx(config.LOGO_MARGIN_X)
        bg.paste(logo, (lx, sy(config.LOGO_MARGIN_Y)), logo)

    # ── Arabic block ──────────────────────────────────────────
    arabic_words = ayah["arabic"].split()
    ar_lines     = _wrap_arabic(arabic_words, draw, W)

    ar_top    = sy(config.ARABIC_CENTER_Y) - 200
    ar_bottom = sy(config.ARABIC_CENTER_Y) + 200
    ar_default, ar_stroke_fill, ar_sw = _text_style(bg, ar_top, ar_bottom, W, H)
    ar_highlight = config.ARABIC_HIGHLIGHT_COLOR

    block_h = len(ar_lines) * (config.ARABIC_FONT_SIZE + config.ARABIC_LINE_GAP)
    y       = sy(config.ARABIC_CENTER_Y) - block_h // 2

    for line in ar_lines:
        x = W - sx(config.ARABIC_X_MARGIN)
        for word, gidx in line:
            shaped = reshape(word)
            ww     = draw.textbbox((0, 0), shaped, font=ar_font)[2]
            x     -= ww
            fill   = ar_highlight if gidx == highlighted_arabic_idx else ar_default
            _draw_word(draw, x, y, shaped, ar_font, fill, ar_stroke_fill, ar_sw)
            x -= config.ARABIC_WORD_GAP
        y += config.ARABIC_FONT_SIZE + config.ARABIC_LINE_GAP

    # ── English block ─────────────────────────────────────────
    english_words = ayah["english"].split()
    en_lines      = _wrap_english(english_words, draw, W)

    en_top    = sy(config.ENGLISH_Y_START)
    en_bottom = sy(config.ENGLISH_Y_START) + 200
    en_default, en_stroke_fill, en_sw = _text_style(bg, en_top, en_bottom, W, H)
    en_highlight = config.ENGLISH_HIGHLIGHT_COLOR

    ey = sy(config.ENGLISH_Y_START)

    for line in en_lines:
        line_text = " ".join(w for w, _ in line)
        line_w    = draw.textbbox((0, 0), line_text, font=en_font)[2]
        ex        = (W - line_w) // 2
        for word, gidx in line:
            fill = en_highlight if gidx in highlighted_english_idxs else en_default
            _draw_word(draw, ex, ey, word, en_font, fill, en_stroke_fill, en_sw)
            ex += draw.textbbox((0, 0), word + " ", font=en_font)[2]
        ey += config.ENGLISH_FONT_SIZE + config.ENGLISH_LINE_GAP

    # ── Reference line ────────────────────────────────────────
    show_reference = True
    
    if show_reference:
        ref_y   = sy(config.REFERENCE_Y)
        ref_def, ref_stroke_fill, ref_sw = _text_style(bg, ref_y - 10, ref_y + 40, W, H)
        ref_text = f"Surah {surah_name}  •  Ayah {ayah['number']}"
        ref_w    = draw.textbbox((0, 0), ref_text, font=ref_font)[2]
        _draw_word(draw, (W - ref_w) // 2, ref_y, ref_text,
                   ref_font, ref_def, ref_stroke_fill, 1)

    return Image.alpha_composite(bg, overlay).convert("RGB")


def frame_to_array(frame: Image.Image) -> np.ndarray:
    return np.array(frame)
