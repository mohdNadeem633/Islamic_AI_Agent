"""
main_PROFESSIONAL.py
====================
Professional Quran Video Generator - Main Entry Point

KEY FEATURES:
- Bismillah before EVERY ayah (if enabled)
- Perfect audio/text sync
- One background per ayah
- Professional output quality
"""

import json
import os
import sys
import requests

import config
from assets import list_background_paths
from video_exporter_PROFESSIONAL import export_reels, export_youtube


def fetch_surah_online(surah_number: int) -> dict:
    """Fetch surah from Quran API."""
    print(f"   📖 Fetching Surah #{surah_number} from internet...")

    base = "https://api.alquran.cloud/v1/surah"

    try:
        ar_resp = requests.get(f"{base}/{surah_number}", timeout=20)
        ar_resp.raise_for_status()
        ar_data = ar_resp.json()["data"]

        en_resp = requests.get(f"{base}/{surah_number}/en.sahih", timeout=20)
        en_resp.raise_for_status()
        en_data = en_resp.json()["data"]

    except requests.exceptions.ConnectionError:
        print("   ❌ No internet connection.")
        return _load_local_cache()
    except requests.exceptions.Timeout:
        print("   ⏱️ Request timed out.")
        return _load_local_cache()
    except Exception as exc:
        print(f"   ❌ Download error: {exc}")
        return _load_local_cache()

    surah = {
        "surah_number": surah_number,
        "surah_name_ar": ar_data["name"],
        "surah_name_en": ar_data["englishName"],
        "revelation_type": ar_data.get("revelationType", ""),
        "number_of_ayahs": ar_data["numberOfAyahs"],
        "ayahs": []
    }

    for ar, en in zip(ar_data["ayahs"], en_data["ayahs"]):
        surah["ayahs"].append({
            "number": ar["numberInSurah"],
            "arabic": ar["text"],
            "english": en["text"],
        })

    os.makedirs("content", exist_ok=True)
    with open(config.CONTENT_FILE, "w", encoding="utf-8") as f:
        json.dump(surah, f, ensure_ascii=False, indent=2)

    print(f"   ✅ {ar_data['englishName']} — {ar_data['numberOfAyahs']} ayahs fetched.")
    return surah


def _load_local_cache() -> dict:
    """Load cached surah if available."""
    if os.path.exists(config.CONTENT_FILE):
        print(f"   📂 Using cached file: {config.CONTENT_FILE}")
        with open(config.CONTENT_FILE, encoding="utf-8") as f:
            return json.load(f)

    print("\n❌ ERROR: No internet and no local cache found.")
    sys.exit(1)


def _prepare_ayahs_with_bismillah(ayahs: list, surah_number: int) -> list:
    """
    Remove Bismillah from the first ayah of surahs that start with it.

    Rules:
      * Surah 9 (At-Tawbah) has none.
      * Surah 1 (Al-Fatiha) already includes Bismillah in verse 1; leave as-is.
      * For all other surahs, strip Bismillah from the start of the first ayah.
    """
    from arabic_utils import (
        BISMILLAH_ARABIC_WORDS, BISMILLAH_ENGLISH,
        starts_with_bismillah, remove_leading_bismillah,
    )

    # Handle special surahs
    if surah_number == 9:
        return ayahs
    if surah_number == 1:
        # Fatiha: first verse already includes Bismillah, do nothing
        return ayahs

    prepared = [dict(a) for a in ayahs]

    # Always strip any embedded bismillah from first ayah's text
    if prepared and starts_with_bismillah(prepared[0]["arabic"]):
        prepared[0]["arabic"] = remove_leading_bismillah(prepared[0]["arabic"])
        if prepared[0].get("english", "").startswith(BISMILLAH_ENGLISH):
            prepared[0]["english"] = prepared[0]["english"][len(BISMILLAH_ENGLISH) :].lstrip()
        # Mark that this ayah had Bismillah removed so audio can be trimmed
        prepared[0]["has_bismillah_prefix"] = True

    return prepared


def _split_ayahs_into_pages(ayahs: list) -> list:
    """
    Split ayahs that exceed word limit into multiple pages.
    
    Each page is treated as a separate clip with the same ayah number.
    Audio timing remains unchanged (will be divided proportionally across pages).
    """
    words_per_page = getattr(config, "WORDS_PER_PAGE", 25)
    pages = []
    
    for ayah in ayahs:
        arabic_words = ayah["arabic"].split()
        english_words = ayah["english"].split()
        
        total_words = len(arabic_words)
        
        if total_words <= words_per_page:
            # Ayah fits in one page
            pages.append(ayah)
        else:
            # Split into multiple pages
            num_pages = (total_words + words_per_page - 1) // words_per_page
            
            for page_num in range(num_pages):
                start_idx = page_num * words_per_page
                end_idx = min((page_num + 1) * words_per_page, total_words)
                
                page_arabic = " ".join(arabic_words[start_idx:end_idx])
                page_english = " ".join(english_words[start_idx:end_idx])
                
                # Create a page entry
                page_ayah = {
                    "number": ayah["number"],
                    "arabic": page_arabic,
                    "english": page_english,
                    "is_page": True,
                    "page_num": page_num + 1,
                    "total_pages": num_pages,
                    "original_word_count": total_words,
                }
                
                # Preserve metadata
                if ayah.get("has_bismillah_prefix"):
                    page_ayah["has_bismillah_prefix"] = True
                
                pages.append(page_ayah)
    
    return pages


# def main() -> None:
#     """Main execution function."""
#     print("\n" + "=" * 60)
#     print("  📖 PROFESSIONAL QURAN VIDEO GENERATOR")
#     print("=" * 60)

#     # Get settings
#     surah_number = getattr(config, "SURAH_NUMBER", 1)
#     surah = fetch_surah_online(surah_number)

#     surah_name = surah["surah_name_en"]
#     ayahs = surah["ayahs"]
    
#     # Filter ayahs by range
#     ayah_start = getattr(config, "AYAH_START", 1)
#     ayah_end = getattr(config, "AYAH_END", len(ayahs))
    
#     ayah_start = max(1, min(ayah_start, len(ayahs)))
#     ayah_end = max(ayah_start, min(ayah_end, len(ayahs)))
    
#     ayahs = [a for a in ayahs if ayah_start <= a["number"] <= ayah_end]
    
#     # CRITICAL: Optionally prepend Bismillah clip at start of surah
#     ayahs = _prepare_ayahs_with_bismillah(ayahs, surah_number)
    
#     # Split ayahs into pages based on word count
#     ayahs = _split_ayahs_into_pages(ayahs)
    
#     backgrounds = list_background_paths()

#     # Display configuration
#     print(f"\n  📕 Surah       : {surah_name} (#{surah_number})")
    
#     bismillah_mode = getattr(config, "BISMILLAH_AT_START", False)
#     if bismillah_mode:
#         original_count = ayah_end - ayah_start + 1
#         total_clips = len(ayahs)
#         extra = total_clips - original_count
#         print(f"  📄 Ayahs       : {ayah_start} to {ayah_end} ({original_count} ayahs)")
#         if extra > 0:
#             print(f"  🎬 With Bismillah: {total_clips} total clips ({extra} added for Bismillah)")
#         else:
#             print(f"  🎬 With Bismillah: {total_clips} total clips")
#     else:
#         print(f"  📄 Ayahs       : {ayah_start} to {ayah_end} ({len(ayahs)} total)")
    
#     print(f"  🖼️  Backgrounds : {len(backgrounds)}")
    
#     # Quality settings
#     quality = getattr(config, "VIDEO_QUALITY", "high")
#     fast_mode = getattr(config, "FAST_MODE", False)
#     print(f"  ⚙️  Quality     : {quality.upper()} {'(Fast Mode)' if fast_mode else ''}")

#     # Format settings
#     do_phone = getattr(config, "GENERATE_PHONE_FORMAT", True)
#     do_tv = getattr(config, "GENERATE_TV_FORMAT", False)

#     print(f"\n  📱 Phone reels (9:16) : {'✅ YES' if do_phone else '❌ NO'}")
#     print(f"  🖥️  TV YouTube  (16:9) : {'✅ YES' if do_tv else '❌ NO'}")
    
#     # Timing info
#     target_duration = getattr(config, "REEL_TARGET_DURATION", 30)
#     print(f"  ⏱️  Target reel length: {target_duration}s")
#     print()

#     # Generate videos
#     if do_phone:
#         print("▶️  Generating REELS...")
#         export_reels(
#             ayahs=ayahs,
#             surah_name=surah_name,
#             surah_number=surah_number,
#             bg_start=0,
#         )

#     print("\n▶️  Generating YOUTUBE videos...")
#     export_youtube(
#         ayahs=ayahs,
#         surah_name=surah_name,
#         surah_number=surah_number,
#         bg_start=10,
#     )

#     # Summary
#     print("\n" + "=" * 60)
#     print("  ✨ ALL DONE!")
#     if do_phone:
#         print(f"  📱 Reels         → {config.REEL_OUTPUT_DIR}/")
#         print(f"  📱 YouTube phone → {config.YOUTUBE_OUTPUT_DIR}/phone/")
#     if do_tv:
#         print(f"  🖥️  YouTube TV    → {config.YOUTUBE_OUTPUT_DIR}/tv/")
#     print("=" * 60 + "\n")


# if __name__ == "__main__":
#     main()
def main() -> None:
    """Main function to generate Quran videos."""
    print("\n" + "=" * 60)
    print("📖 PROFESSIONAL QURAN VIDEO GENERATOR")
    print("=" * 60)

    # Load settings
    surah_number = getattr(config, "SURAH_NUMBER", 17)
    ayah_start = getattr(config, "AYAH_START", 1)
    ayah_end = getattr(config, "AYAH_END", 7)
    reciter = getattr(config, "PREFERRED_RECITER", "alafasy")

    print(f"\n  📖 Surah       : #{surah_number}")
    print(f"  🎤 Reciter     : {reciter}")

    # Fetch surah data
    surah = fetch_surah_online(surah_number)
    surah_name = surah["surah_name_en"]

    # Extract ayahs
    all_ayahs = surah["ayahs"]
    ayahs = [a for a in all_ayahs if ayah_start <= a["number"] <= ayah_end]

    # Prepare ayahs (handle Bismillah)
    ayahs = _prepare_ayahs_with_bismillah(ayahs, surah_number)

    # Split long ayahs into pages
    ayahs = _split_ayahs_into_pages(ayahs)

    # Load backgrounds
    backgrounds = list_background_paths()

    print(f"  📄 Ayahs       : {ayah_start} to {ayah_end} ({len(ayahs)} total)")
    print(f"  🖼️  Backgrounds : {len(backgrounds)}")

    # Quality settings
    quality = getattr(config, "VIDEO_QUALITY", "high")
    fast_mode = getattr(config, "FAST_MODE", False)
    print(f"  ⚙️  Quality     : {quality.upper()} {'(Fast Mode)' if fast_mode else ''}")

    # Format settings
    do_phone = getattr(config, "GENERATE_PHONE_FORMAT", True)
    do_tv = getattr(config, "GENERATE_TV_FORMAT", False)

    print(f"\n  📱 Phone reels (9:16) : {'✅ YES' if do_phone else '❌ NO'}")
    print(f"  🖥️  TV YouTube  (16:9) : {'✅ YES' if do_tv else '❌ NO'}")

    # Timing info
    target_duration = getattr(config, "REEL_TARGET_DURATION", 30)
    print(f"  ⏱️  Target reel length: {target_duration}s")
    print()

    # Generate videos
    if do_phone:
        print("▶️  Generating REELS...")
        export_reels(
            ayahs=ayahs,
            surah_name=surah_name,
            surah_number=surah_number,
            bg_start=0,
        )

    if do_tv:
        print("\n▶️  Generating YOUTUBE videos...")
        export_youtube(
            ayahs=ayahs,
            surah_name=surah_name,
            surah_number=surah_number,
            bg_start=10,
        )

    # Summary
    print("\n" + "=" * 60)
    print("✅ VIDEO GENERATION COMPLETE!")
    print("=" * 60)
    print(f"📁 Output folders:")
    if do_phone:
        print(f"   📱 Reels: videos/reels/")
    if do_tv:
        print(f"   🖥️  YouTube: videos/youtube/")
    print()
    print("🎉 Enjoy your professional Quran videos!")
    print("=" * 60)


if __name__ == "__main__":
    main()