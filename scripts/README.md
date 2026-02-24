# Quran Animated Video Generator  –  v3
### Modular • Clean • Fully Refactored

---

## What changed in this version

| # | Point | Fix |
|---|-------|-----|
| 1 | **No underline** – colour only | `UNDERLINE` code fully removed. Only the word's **colour** changes to red while it is being recited. Works for both Arabic and English. |
| 2 | **Better spacing & reading flow** | `ARABIC_LINE_GAP = 48`, `ARABIC_WORD_GAP = 22`, `ENGLISH_LINE_GAP = 40`. Arabic starts centred around `ARABIC_CENTER_Y = 700`; English starts at `ENGLISH_Y_START = 1130`. Both positions ensure words never overlap other elements. |
| 3 | **Correct reel & YouTube lengths** | Reels: **15-17 s** (multiple ayahs batched). YouTube: **4-5 min** (multiple ayahs batched). |
| 4 | **Fully separated, clean modules** | See architecture below. Every concern is in its own file. |

---

## Architecture

```
project/
│
├── main.py              ← Entry point – load JSON, call exporters
│
├── config.py            ← ALL constants (sizes, colours, timings, paths)
│
├── assets.py            ← Font / background / logo loading & caching
│
├── arabic_utils.py      ← Arabic reshaping, BiDi, Bismillah detection
│
├── audio_engine.py      ← Download recitation audio + onset-based word timing
│
├── renderer.py          ← Frame drawing (PIL) → returns PIL Image
│                           • No underline (point 1)
│                           • Proper spacing (point 2)
│
├── clip_builder.py      ← Converts frames → MoviePy clip with audio
│
├── video_exporter.py    ← Batches ayahs → reel files OR YouTube files
│                           • Reel: 15-17 s (point 3)
│                           • YouTube: 4-5 min (point 3)
│
├── content/
│   └── surah.json
│
├── fonts/
│   ├── Amiri-Bold.ttf          ← Arabic (preferred)
│   ├── Amiri-Regular.ttf       ← Arabic (fallback)
│   ├── NotoSans-SemiBold.ttf   ← English (preferred)
│   ├── NotoSans-Regular.ttf    ← Reference line
│   └── dejavu-sans.extralight.ttf  ← universal fallback
│
├── images/
│   ├── background1.jpg         ← backgrounds auto-discovered
│   ├── background2.jpg
│   ├── background3.jpg         ← add as many as you like
│   └── logo.png                ← brand logo (transparent PNG)
│
├── audio/
│   └── recitations/            ← auto-created; cached MP3s
│
└── videos/
    ├── reels/                  ← auto-created; 15-17 s clips
    └── youtube/                ← auto-created; 4-5 min videos
```

---

## surah.json format

```json
{
  "surah_name_en": "Al-Aadiyaat",
  "surah_number": 100,
  "ayahs": [
    { "number": 1, "arabic": "وَٱلْعَٰدِيَٰتِ ضَبْحًا",      "english": "By the racers, panting," },
    { "number": 2, "arabic": "فَٱلْمُورِيَٰتِ قَدْحًا",       "english": "And the producers of sparks [when] striking" }
  ]
}
```

---

## Installation

```bash
pip install pillow moviepy librosa arabic-reshaper python-bidi requests numpy
```

**Fonts (free download):**
- [Amiri Bold](https://fonts.google.com/specimen/Amiri) → `fonts/Amiri-Bold.ttf`
- [Noto Sans SemiBold](https://fonts.google.com/noto/specimen/Noto+Sans) → `fonts/NotoSans-SemiBold.ttf`

---

## Run

```bash
python main.py
```

**Example output:**
```
====================================================
  📖  Surah : Al-Aadiyaat  (#100)
  📜  Ayahs : 11
  🖼️   Backgrounds : 5
====================================================

▶  Generating REELS (15-17 s each) …
   ✓ Audio cached [alafasy]: audio/recitations/100_001_alafasy.mp3
   💾  Saved: videos/reels/Al-Aadiyaat_reel_001.mp4
   💾  Saved: videos/reels/Al-Aadiyaat_reel_002.mp4

▶  Generating YOUTUBE videos (4-5 min each) …
   💾  Saved: videos/youtube/Al-Aadiyaat_youtube_001.mp4

====================================================
  ✨  ALL DONE!
  📱  Reels   → videos/reels/
  ▶️   YouTube → videos/youtube/
====================================================
```

---

## Upload guide

| Platform | Folder | Notes |
|----------|--------|-------|
| **Instagram Reels** | `videos/reels/` | 15-17 s, 1080×1920 |
| **Facebook Reels** | `videos/reels/` | 15-17 s, 1080×1920 |
| **YouTube Shorts** | `videos/reels/` | use clips ≤ 60 s |
| **YouTube** | `videos/youtube/` | 4-5 min, 1080×1920 |

---

## Tuning guide

All numbers live in `config.py` — no other file needs editing for tweaks.

| Constant | Default | Controls |
|----------|---------|----------|
| `ARABIC_FONT_SIZE` | 72 | Arabic text size |
| `ENGLISH_FONT_SIZE` | 36 | English text size |
| `ARABIC_LINE_GAP` | 48 | Space between Arabic lines |
| `ARABIC_WORD_GAP` | 22 | Extra space between Arabic words |
| `ENGLISH_LINE_GAP` | 40 | Space between English lines |
| `ARABIC_CENTER_Y` | 700 | Vertical centre of Arabic block |
| `ENGLISH_Y_START` | 1130 | Top of English block |
| `REEL_TARGET_SEC` | 16 | Target reel duration (seconds) |
| `REEL_MIN_SEC` | 15 | Min reel duration |
| `REEL_MAX_SEC` | 17 | Max reel duration |
| `YOUTUBE_TARGET_MIN` | 4.5 | Target YouTube duration (minutes) |
| `HOLD_AT_END` | 2.5 | Still-frame pause at end of each clip |
| `LOGO_MAX_W` | 160 | Logo maximum width in pixels |
| `BG_CHANGE_INTERVAL` | 30 | Background switches every N seconds |
