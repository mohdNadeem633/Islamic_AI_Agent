"""
config.py
=========
Central configuration for the Quran Animated Video Generator.
Edit this file to tune every visual and timing parameter.
"""

# ─────────────────────────────────────────────────────────────
#  CANVAS
# ─────────────────────────────────────────────────────────────
WIDTH  = 1080
HEIGHT = 1920

# ─────────────────────────────────────────────────────────────
#  LAYOUT  (Y positions from top, X margins from edges)
# ─────────────────────────────────────────────────────────────
LOGO_MAX_W        = 160       # max logo width in pixels
LOGO_MARGIN_X     = 48
LOGO_MARGIN_Y     = 48

# Arabic block: vertical centre point
ARABIC_CENTER_Y   = 700
# ARABIC_LINE_GAP   = 48        # gap between Arabic lines  (point 2)
ARABIC_WORD_GAP   = 22        # extra horizontal breathing space between words  (point 2)
ARABIC_X_MARGIN   = 80

# English block: starts here and grows downward
ENGLISH_Y_START   = 1130
# ENGLISH_LINE_GAP  = 40        # gap between English lines  (point 2)
# ENGLISH_LINE_GAP  = 20        # gap between English lines  (point 2)
ENGLISH_X_MARGIN  = 90

# Reference sits near the bottom
REFERENCE_Y       = HEIGHT - 110

# ─────────────────────────────────────────────────────────────
#  FONTS
# ─────────────────────────────────────────────────────────────
# ARABIC_FONT_SIZE    = 72
# ENGLISH_FONT_SIZE   = 36
# REFERENCE_FONT_SIZE = 26
ARABIC_FONT_SIZE    = 97
ENGLISH_FONT_SIZE   = 70
REFERENCE_FONT_SIZE = 34

ARABIC_LINE_GAP     = 55
ENGLISH_LINE_GAP    = 26

ARABIC_FONT_PATH    = "fonts/Amiri-Bold.ttf"
ARABIC_FONT_FALLBACK= "fonts/Amiri-Regular.ttf"

ENGLISH_FONT_PATH   = "fonts/NotoSans-SemiBold.ttf"
ENGLISH_FONT_FALLBACK="fonts/dejavu-sans.extralight.ttf"

REFERENCE_FONT_PATH = "fonts/NotoSans-Regular.ttf"

# ─────────────────────────────────────────────────────────────
#  COLOURS
# ─────────────────────────────────────────────────────────────
# ARABIC_DEFAULT_COLOR   = (15,  15,  15,  255)
# ARABIC_HIGHLIGHT_COLOR = (190, 30,  20,  255)   # red when being read  (point 1)

# ENGLISH_DEFAULT_COLOR  = (35,  35,  35,  255)
# ENGLISH_HIGHLIGHT_COLOR= (190, 30,  20,  255)   # red when being read  (point 1)

# REFERENCE_COLOR        = (80,  80,  80,  255)


ARABIC_DEFAULT_COLOR   = (255, 255, 255, 255)   # White
ARABIC_HIGHLIGHT_COLOR = (190, 30, 20, 255)     # Red highlight

ENGLISH_DEFAULT_COLOR  = (255, 255, 255, 255)   # White
ENGLISH_HIGHLIGHT_COLOR= (190, 30, 20, 255)     # Red highlight

REFERENCE_COLOR        = (255, 255, 255, 255)   # White

# ─────────────────────────────────────────────────────────────
#  VIDEO / ANIMATION
# ─────────────────────────────────────────────────────────────
FPS               = 30
HOLD_AT_END       = 1.75       # still-frame pause (seconds) after recitation ends

# Reel length constraints  (point 3)
REEL_TARGET_SEC   = 16        # aim for this duration per reel (15-17 s window)
REEL_MIN_SEC      = 15
REEL_MAX_SEC      = 17

# YouTube video length constraints  (point 3)
YOUTUBE_TARGET_MIN = 4.5      # minutes  →  270 seconds
YOUTUBE_MIN_SEC    = 240      # 4 min
YOUTUBE_MAX_SEC    = 300      # 5 min

# ─────────────────────────────────────────────────────────────
#  AUDIO ANALYSIS
# ─────────────────────────────────────────────────────────────
AUDIO_SR            = 22050
ONSET_DELTA         = 0.07
MIN_WORD_DURATION   = 0.12    # seconds
MIN_ONSET_GAP       = 0.06    # seconds between detected onsets
ENERGY_THRESHOLD    = 0.018

# ─────────────────────────────────────────────────────────────
#  PATHS
# ─────────────────────────────────────────────────────────────
AUDIO_CACHE_DIR   = "audio/recitations"
REEL_OUTPUT_DIR   = "videos/reels"
YOUTUBE_OUTPUT_DIR= "videos/youtube"
IMAGES_DIR        = "images"
CONTENT_FILE      = "content/surah.json"

# Background changes every N seconds during a long clip  (dynamic BG)
BG_CHANGE_INTERVAL = 30       # seconds
