"""
assets.py
=========
Handles loading and caching of all visual assets:
  - Fonts (Arabic, English, Reference)
  - Background images  (auto-discovers background1…N.jpg)
  - Brand logo
"""

import glob
import os
from functools import lru_cache
from typing import Optional

from PIL import Image, ImageFont

import config


# ─────────────────────────────────────────────────────────────
#  FONT LOADING
# ─────────────────────────────────────────────────────────────

def _try_font(paths: list[str], size: int) -> ImageFont.FreeTypeFont:
    """Try each path in order; fall back to PIL default."""
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


@lru_cache(maxsize=1)
def get_arabic_font() -> ImageFont.FreeTypeFont:
    return _try_font(
        [config.ARABIC_FONT_PATH, config.ARABIC_FONT_FALLBACK],
        config.ARABIC_FONT_SIZE,
    )


@lru_cache(maxsize=1)
def get_english_font() -> ImageFont.FreeTypeFont:
    return _try_font(
        [config.ENGLISH_FONT_PATH, config.ENGLISH_FONT_FALLBACK],
        config.ENGLISH_FONT_SIZE,
    )


@lru_cache(maxsize=1)
def get_reference_font() -> ImageFont.FreeTypeFont:
    return _try_font(
        [config.REFERENCE_FONT_PATH, config.ENGLISH_FONT_FALLBACK],
        config.REFERENCE_FONT_SIZE,
    )


# ─────────────────────────────────────────────────────────────
#  BACKGROUND IMAGES
# ─────────────────────────────────────────────────────────────

def list_background_paths() -> list[str]:
    """
    Auto-discover all background images in the images/ folder.
    Supports: background1.jpg, background2.png, bg1.jpg, etc.
    """
    patterns = [
        os.path.join(config.IMAGES_DIR, "background*.jpg"),
        os.path.join(config.IMAGES_DIR, "background*.png"),
        os.path.join(config.IMAGES_DIR, "bg*.jpg"),
        os.path.join(config.IMAGES_DIR, "bg*.png"),
    ]
    found: list[str] = []
    for pat in patterns:
        found.extend(sorted(glob.glob(pat)))
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique = [p for p in found if not (p in seen or seen.add(p))]
    return unique if unique else [os.path.join(config.IMAGES_DIR, "background.jpg")]


_bg_cache: dict[str, Image.Image] = {}


def load_background(index: int = 0) -> Image.Image:
    """
    Return a background Image for the given round-robin index.
    Result is cached per path to avoid repeated disk reads.
    """
    paths = list_background_paths()
    path  = paths[index % len(paths)]

    if path not in _bg_cache:
        if os.path.exists(path):
            img = (
                Image.open(path)
                .convert("RGBA")
                .resize((config.WIDTH, config.HEIGHT), Image.Resampling.LANCZOS)
            )
        else:
            img = Image.new("RGBA", (config.WIDTH, config.HEIGHT), (240, 235, 230, 255))
        _bg_cache[path] = img

    return _bg_cache[path].copy()   # always return a fresh copy


# ─────────────────────────────────────────────────────────────
#  BRAND LOGO
# ─────────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def load_logo() -> Optional[Image.Image]:
    """
    Load the brand logo, scale it to max LOGO_MAX_W wide (aspect preserved).
    Returns None if no logo file is found.
    """
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
