"""
assets.py - FIXED VERSION
=========================
Truly random background selection from ALL available images.
"""

import glob
import os
import random
from functools import lru_cache
from typing import Optional

from PIL import Image, ImageFont

import config


# ─────────────────────────────────────────────────────────────
#  FONT LOADING
# ─────────────────────────────────────────────────────────────

def _try_font(paths, size):
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


@lru_cache(maxsize=1)
def get_arabic_font():
    return _try_font([config.ARABIC_FONT_PATH, config.ARABIC_FONT_FALLBACK],
                     config.ARABIC_FONT_SIZE)

@lru_cache(maxsize=1)
def get_english_font():
    return _try_font([config.ENGLISH_FONT_PATH, config.ENGLISH_FONT_FALLBACK],
                     config.ENGLISH_FONT_SIZE)

@lru_cache(maxsize=1)
def get_reference_font():
    return _try_font([config.REFERENCE_FONT_PATH, config.ENGLISH_FONT_FALLBACK],
                     config.REFERENCE_FONT_SIZE)


# ─────────────────────────────────────────────────────────────
#  BACKGROUND IMAGES - TRULY RANDOM SELECTION
# ─────────────────────────────────────────────────────────────

def list_background_paths():
    """
    Find ALL background images in images/ folder.
    Supports: background*.jpg, background*.png, bg*.jpg, bg*.png
    """
    patterns = [
        os.path.join(config.IMAGES_DIR, "background*.jpg"),
        os.path.join(config.IMAGES_DIR, "background*.png"),
        os.path.join(config.IMAGES_DIR, "bg*.jpg"),
        os.path.join(config.IMAGES_DIR, "bg*.png"),
    ]
    found = []
    for pat in patterns:
        found.extend(glob.glob(pat))
    
    # Deduplicate
    seen = set()
    unique = [p for p in found if not (p in seen or seen.add(p))]
    
    # If no backgrounds found, return default
    if not unique:
        default = os.path.join(config.IMAGES_DIR, "background.jpg")
        return [default] if os.path.exists(default) else []
    
    return unique


# Global shuffle list - ensures every background gets used before repeating
_SHUFFLED_BACKGROUNDS = []
_SHUFFLE_INDEX = 0


def _get_next_random_background():
    """
    Get next background in a shuffled sequence.
    Ensures ALL backgrounds are used before any repeat.
    """
    global _SHUFFLED_BACKGROUNDS, _SHUFFLE_INDEX
    
    paths = list_background_paths()
    if not paths:
        return None
    
    # Reshuffle when we've gone through all backgrounds
    if _SHUFFLE_INDEX >= len(_SHUFFLED_BACKGROUNDS) or not _SHUFFLED_BACKGROUNDS:
        _SHUFFLED_BACKGROUNDS = paths.copy()
        random.shuffle(_SHUFFLED_BACKGROUNDS)
        _SHUFFLE_INDEX = 0
    
    path = _SHUFFLED_BACKGROUNDS[_SHUFFLE_INDEX]
    _SHUFFLE_INDEX += 1
    return path


# Cache keyed by (path, width, height)
_bg_cache: dict = {}


def load_background(index: int = 0,
                    width:  int = None,
                    height: int = None) -> Image.Image:
    """
    Return a background Image scaled to (width, height).
    
    If `index` is provided, select the background deterministically from the
    available list using `index % len(paths)` so callers can control when the
    background changes (e.g. once every `BG_CHANGE_INTERVAL` seconds).
    If `index` is None or negative, fall back to the prior random-shuffle
    behaviour.
    """
    w = width  or config.WIDTH
    h = height or config.HEIGHT
    
    # Check for custom background
    custom_path = getattr(config, "CUSTOM_BACKGROUND_PATH", None)
    if custom_path and os.path.exists(custom_path):
        path = custom_path
    else:
        paths = list_background_paths()
        if not paths:
            # Fallback solid color
            return Image.new("RGBA", (w, h), (240, 235, 230, 255))

        # If caller provided an index, pick deterministically from the list.
        try:
            if index is not None and int(index) >= 0:
                path = paths[int(index) % len(paths)]
            else:
                path = _get_next_random_background()
        except Exception:
            path = _get_next_random_background()
    
    key = (path, w, h)
    
    if key not in _bg_cache:
        if os.path.exists(path):
            img = (Image.open(path)
                       .convert("RGBA")
                       .resize((w, h), Image.Resampling.LANCZOS))
        else:
            img = Image.new("RGBA", (w, h), (240, 235, 230, 255))
        _bg_cache[key] = img
    
    return _bg_cache[key].copy()


# ─────────────────────────────────────────────────────────────
#  LOGO
# ─────────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def load_logo() -> Optional[Image.Image]:
    candidates = [
        os.path.join(config.IMAGES_DIR, "logo.png"),
        os.path.join(config.IMAGES_DIR, "logo.jpg"),
        os.path.join(config.IMAGES_DIR, "brand.png"),
    ]
    for path in candidates:
        if os.path.exists(path):
            logo  = Image.open(path).convert("RGBA")
            scale = config.LOGO_MAX_W / logo.width
            new_h = int(logo.height * scale)
            return logo.resize((config.LOGO_MAX_W, new_h), Image.Resampling.LANCZOS)
    return None
