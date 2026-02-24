"""
main.py
=======
Entry point for the Quran Animated Video Generator.

Run:
    python main.py

Outputs:
    videos/reels/    → 15-17 s clips  (Instagram / Facebook)
    videos/youtube/  → 4-5 min files  (YouTube)
"""

import json
import sys

import config
from assets import list_background_paths
from video_exporter import export_reels, export_youtube


# ─────────────────────────────────────────────────────────────
#  LOAD CONTENT
# ─────────────────────────────────────────────────────────────

def load_surah(path: str = config.CONTENT_FILE) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Content file not found: {path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in {path}: {e}")
        sys.exit(1)


# ─────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────

def main() -> None:
    surah        = load_surah()
    surah_name   = surah["surah_name_en"]
    surah_number = surah["surah_number"]
    ayahs        = surah["ayahs"]
    backgrounds  = list_background_paths()

    print(f"\n{'='*52}")
    print(f"  📖  Surah : {surah_name}  (#{surah_number})")
    print(f"  📜  Ayahs : {len(ayahs)}")
    print(f"  🖼️   Backgrounds : {len(backgrounds)}")
    print(f"{'='*52}\n")

    # ── Reels (15-17 s) ──────────────────────────────────────
    print("▶  Generating REELS (15-17 s each) …")
    export_reels(
        ayahs        = ayahs,
        surah_name   = surah_name,
        surah_number = surah_number,
        bg_start     = 0,
    )

    # ── YouTube (4-5 min) ────────────────────────────────────
    print("\n▶  Generating YOUTUBE videos (4-5 min each) …")
    export_youtube(
        ayahs        = ayahs,
        surah_name   = surah_name,
        surah_number = surah_number,
        bg_start     = 10,   # offset so YouTube uses different backgrounds than reels
    )

    print(f"\n{'='*52}")
    print("  ✨  ALL DONE!")
    print(f"  📱  Reels   → {config.REEL_OUTPUT_DIR}/")
    print(f"  ▶️   YouTube → {config.YOUTUBE_OUTPUT_DIR}/")
    print(f"{'='*52}\n")


if __name__ == "__main__":
    main()
