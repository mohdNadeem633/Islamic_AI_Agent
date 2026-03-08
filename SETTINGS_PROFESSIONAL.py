"""
PROFESSIONAL QURAN VIDEO GENERATOR - SETTINGS
==============================================
Complete control over timing, layout, and video quality
"""

# ═══════════════════════════════════════════════════════════
# 📚 SURAH & AYAH SELECTION
# ═══════════════════════════════════════════════════════════

SURAH_NUMBER = 17  # Al-Israa
PREFERRED_RECITER = "alafasy"  # Options: "alafasy", "basit", "husary"

# Ayah range to generate
AYAH_START = 1
AYAH_END = 7

# ═══════════════════════════════════════════════════════════
# 🎬 BISMILLAH SETTINGS
# ═══════════════════════════════════════════════════════════
# 🎬 BISMILLAH SETTINGS
# ═══════════════════════════════════════════════════════════

# Add Bismillah at the start of the surah (once). Surah 1 & 9 handled
# specially (Fatiha already includes it; At-Tawbah has none).
BISMILLAH_AT_START = False

# Legacy option (ignored if BISMILLAH_AT_START enabled).
BISMILLAH_BEFORE_EVERY_AYAH = False  # kept for backwards compatibility

# How long the Bismillah display page should last (seconds)
# This is used when rendering Bismillah as a separate clip
BISMILLAH_DURATION = 4.0

# How long to hold on Bismillah before transitioning (seconds)
BISMILLAH_HOLD_TIME = 0.5

# ═══════════════════════════════════════════════════════════
# ⏱️ TIMING CONTROL (PROFESSIONAL SETTINGS)
# ═══════════════════════════════════════════════════════════

# Reel length control
REEL_MIN_DURATION = 15  # Minimum reel length (seconds)
REEL_MAX_DURATION = 60  # Maximum reel length (seconds)
REEL_TARGET_DURATION = 30  # Target reel length (seconds)

# YouTube video length control
YOUTUBE_MIN_DURATION = 180  # 3 minutes minimum
YOUTUBE_MAX_DURATION = 600  # 10 minutes maximum
YOUTUBE_TARGET_DURATION = 270  # 4.5 minutes target

# Timing adjustments for sync
WORD_TIMING_PRECISION = "high"  # Options: "low", "medium", "high", "ultra"
# - low: Fast, less accurate
# - medium: Balanced
# - high: Accurate, slower
# - ultra: Most accurate, slowest

# Add extra time per word (seconds) - helps with sync
WORD_PADDING = 0.05  # 0.05 = 50ms extra per word

# Pause at end of each ayah (seconds)
HOLD_AT_END = 2.0  # How long to hold final frame

# Transition between ayahs (seconds)
AYAH_TRANSITION_TIME = 0.3  # Smooth fade between ayahs

# ═══════════════════════════════════════════════════════════
# 🎨 TEXT APPEARANCE (PROFESSIONAL LOOK)
# ═══════════════════════════════════════════════════════════

# Font sizes
ARABIC_FONT_SIZE = 72
ENGLISH_FONT_SIZE = 36
REFERENCE_FONT_SIZE = 29

# Text positioning
ARABIC_CENTER_Y = 800   # Vertical center of Arabic text
ARABIC_X_MARGIN = 89    # Side margins
ARABIC_LINE_GAP = 52    # Space between lines
ARABIC_WORD_GAP = 28    # Space between words

ENGLISH_Y_START = 1050  # Where English starts
ENGLISH_X_MARGIN = 95
ENGLISH_LINE_GAP = 44

REFERENCE_Y = 1650  # Reference line position

# ═══════════════════════════════════════════════════════════
# 🌈 COLORS (PROFESSIONAL PALETTE)
# ═══════════════════════════════════════════════════════════

# Auto-adapt text color to background
AUTO_CONTRAST = True  # Recommended: True

# Default text colors (when not highlighted)
ARABIC_DEFAULT_COLOR = (255, 255, 255, 255)  # White
ENGLISH_DEFAULT_COLOR = (255, 255, 255, 255)  # White
REFERENCE_COLOR = (220, 220, 220, 255)  # Light gray

# Custom colors (user-settable)
ARABIC_TEXT_COLOR = (255, 255, 255, 255)  # Default white
ENGLISH_TEXT_COLOR = (255, 255, 255, 255)  # Default white

# Highlight colors (when word is being recited) - THE RED COLOR
ARABIC_HIGHLIGHT_COLOR = (220, 40, 20, 255)  # Red
ENGLISH_HIGHLIGHT_COLOR = (220, 40, 20, 255)  # Red

# Text stroke (outline) for readability
TEXT_STROKE_WIDTH = 2  # Thickness of text outline

# ═══════════════════════════════════════════════════════════
# 🖼️ BACKGROUND SETTINGS (PROFESSIONAL LOOK)
# ═══════════════════════════════════════════════════════════

# Background change strategy
BG_CHANGE_MODE = "per_ayah"  # Options:
# - "per_ayah": One background per ayah (RECOMMENDED)
# - "per_reel": One background per video
# - "timed": Change every N seconds
# - "random": Random for each frame

# If using "timed" mode, how often to change (seconds)
BG_CHANGE_INTERVAL = 30

# Background effects
BG_BLUR_AMOUNT = 0  # 0-10, 0=no blur, 10=heavy blur
BG_DARKEN_PERCENT = 0  # 0-50, 0=normal, 50=very dark
BG_BRIGHTNESS_ADJUST = 0  # -50 to +50

# Custom background (user-uploaded)
CUSTOM_BACKGROUND_PATH = None  # Path to custom background image

# ═══════════════════════════════════════════════════════════
# 🎥 VIDEO QUALITY (PROFESSIONAL OUTPUT)
# ═══════════════════════════════════════════════════════════

# Formats to generate
GENERATE_PHONE_FORMAT = True  # 9:16 phone/reels
GENERATE_TV_FORMAT = False  # 16:9 TV/YouTube

# Encoding quality
FAST_MODE = False  # True = faster but lower quality
VIDEO_QUALITY = "high"  # Options: "draft", "medium", "high", "ultra"
# - draft: Fast preview, low quality
# - medium: Balanced
# - high: Recommended for publishing
# - ultra: Best quality, very slow

# Frame rate
FPS = 30  # Frames per second (30 recommended, 60 for ultra-smooth)

# ═══════════════════════════════════════════════════════════
# 🎭 ANIMATION & EFFECTS
# ═══════════════════════════════════════════════════════════

# Word highlighting animation
HIGHLIGHT_TRANSITION = "instant"  # Options:
# - "instant": Immediate color change
# - "fade": Smooth fade transition
# - "grow": Word grows slightly when highlighted

# Text entrance animation
TEXT_ENTRANCE_EFFECT = "none"  # Options:
# - "none": Appear immediately
# - "fade_in": Fade in over 0.3s
# - "slide_up": Slide up from below

# Background transitions
BG_TRANSITION_EFFECT = "fade"  # Options:
# - "fade": Smooth crossfade
# - "cut": Instant change
# - "slide": Slide transition

# ═══════════════════════════════════════════════════════════
# 🏷️ BRANDING
# ═══════════════════════════════════════════════════════════

# Logo settings
LOGO_MAX_W = 160  # Maximum logo width (pixels)
LOGO_MARGIN_X = 48  # Distance from right edge
LOGO_MARGIN_Y = 48  # Distance from top
LOGO_OPACITY = 255  # 0-255, 0=invisible, 255=fully visible

# Watermark text (optional)
WATERMARK_TEXT = ""  # Leave empty to disable
WATERMARK_POSITION = "bottom_right"  # Options: "top_left", "top_right", "bottom_left", "bottom_right"
WATERMARK_OPACITY = 128  # 0-255

# ═══════════════════════════════════════════════════════════
# 🎯 ADVANCED SYNC SETTINGS
# ═══════════════════════════════════════════════════════════

# Audio analysis precision
AUDIO_SR = 22050  # Sample rate (higher = more accurate, slower)
ONSET_DELTA = 0.05  # Sensitivity: 0.03=very sensitive, 0.10=less sensitive
MIN_WORD_DURATION = 0.15  # Minimum word length (seconds)
MIN_ONSET_GAP = 0.08  # Minimum gap between words

# Sync correction
AUTO_SYNC_CORRECTION = True  # Automatically adjust timing if off
SYNC_OFFSET = 0.0  # Manual offset (seconds): negative=earlier, positive=later

# ═══════════════════════════════════════════════════════════
# 📁 FILE PATHS & SYSTEM
# ═══════════════════════════════════════════════════════════

# Font paths
ARABIC_FONT_PATH = "fonts/Amiri-Regular.ttf"
ARABIC_FONT_FALLBACK = "fonts/AmiriQuran.ttf"
ENGLISH_FONT_PATH = "fonts/NotoSans-Regular.ttf"
ENGLISH_FONT_FALLBACK = "fonts/dejavu-sans.extralight.ttf"
REFERENCE_FONT_PATH = "fonts/NotoSans-Regular.ttf"

# Output directories
AUDIO_CACHE_DIR = "audio/recitations"
REEL_OUTPUT_DIR = "videos/reels"
YOUTUBE_OUTPUT_DIR = "videos/youtube"
IMAGES_DIR = "images"
CONTENT_FILE = "content/surah.json"

# Performance
MAX_MEMORY_MB = 2000  # Maximum RAM usage (MB)
ENABLE_CACHING = True  # Cache frames for faster generation
PARALLEL_PROCESSING = False  # Use multiple CPU cores (experimental)

# ═══════════════════════════════════════════════════════════
# 🎬 PROFESSIONAL PRESETS
# ═══════════════════════════════════════════════════════════

# Quick preset modes (uncomment one to use)
# PRESET = "instagram_reels"  # Optimized for Instagram
# PRESET = "youtube_shorts"   # Optimized for YouTube Shorts
# PRESET = "tiktok"           # Optimized for TikTok
# PRESET = "facebook_reels"   # Optimized for Facebook
# PRESET = "professional"     # High quality for all platforms
PRESET = "custom"  # Use settings above

# Preset configurations (applied automatically)
if PRESET == "instagram_reels":
    REEL_TARGET_DURATION = 30
    VIDEO_QUALITY = "high"
    BISMILLAH_BEFORE_EVERY_AYAH = True
    FPS = 30
elif PRESET == "youtube_shorts":
    REEL_TARGET_DURATION = 45
    VIDEO_QUALITY = "high"
    FPS = 30
elif PRESET == "tiktok":
    REEL_TARGET_DURATION = 60
    VIDEO_QUALITY = "medium"
    FPS = 30
elif PRESET == "professional":
    REEL_TARGET_DURATION = 30
    VIDEO_QUALITY = "ultra"
    BISMILLAH_BEFORE_EVERY_AYAH = True
    FPS = 60

# ═══════════════════════════════════════════════════════════
# 📊 DERIVED SETTINGS (DO NOT EDIT)
# ═══════════════════════════════════════════════════════════

WIDTH = 1080
HEIGHT = 1920

# Quality presets
QUALITY_PRESETS = {
    "draft": {"bitrate": "2000k", "crf": "28", "preset": "superfast"},
    "medium": {"bitrate": "5000k", "crf": "23", "preset": "medium"},
    "high": {"bitrate": "8000k", "crf": "18", "preset": "slow"},
    "ultra": {"bitrate": "12000k", "crf": "15", "preset": "veryslow"},
}

CURRENT_QUALITY = QUALITY_PRESETS.get(VIDEO_QUALITY, QUALITY_PRESETS["high"])
