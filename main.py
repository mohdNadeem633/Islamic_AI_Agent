import json
import os
import sys
import requests

import config
from assets import list_background_paths
from video_exporter import export_reels, export_youtube


def fetch_surah_online(surah_number: int) -> dict:
    print(f"   Fetching Surah #{surah_number} from internet...")

    base = "https://api.alquran.cloud/v1/surah"

    try:
        ar_resp = requests.get(f"{base}/{surah_number}", timeout=20)
        ar_resp.raise_for_status()
        ar_data = ar_resp.json()["data"]

        en_resp = requests.get(f"{base}/{surah_number}/en.sahih", timeout=20)
        en_resp.raise_for_status()
        en_data = en_resp.json()["data"]

    except requests.exceptions.ConnectionError:
        print("   No internet connection.")
        return _load_local_cache()
    except requests.exceptions.Timeout:
        print("   Request timed out.")
        return _load_local_cache()
    except Exception as exc:
        print(f"   Download error: {exc}")
        return _load_local_cache()

    surah = {
        "surah_number":  surah_number,
        "surah_name_ar": ar_data["name"],
        "surah_name_en": ar_data["englishName"],
        "revelation_type": ar_data.get("revelationType", ""),
        "number_of_ayahs": ar_data["numberOfAyahs"],
        "ayahs": []
    }

    for ar, en in zip(ar_data["ayahs"], en_data["ayahs"]):
        surah["ayahs"].append({
            "number":  ar["numberInSurah"],
            "arabic":  ar["text"],
            "english": en["text"],
        })

    os.makedirs("content", exist_ok=True)
    with open(config.CONTENT_FILE, "w", encoding="utf-8") as f:
        json.dump(surah, f, ensure_ascii=False, indent=2)

    print(f"   {ar_data['englishName']} — {ar_data['numberOfAyahs']} ayahs fetched.")
    return surah


def _load_local_cache() -> dict:
    if os.path.exists(config.CONTENT_FILE):
        print(f"   Using cached file: {config.CONTENT_FILE}")
        with open(config.CONTENT_FILE, encoding="utf-8") as f:
            return json.load(f)

    print("\nERROR: No internet and no local cache found.")
    sys.exit(1)


def main() -> None:
    print("\n" + "=" * 54)
    print("  QURAN VIDEO GENERATOR")
    print("=" * 54)

    surah_number = getattr(config, "SURAH_NUMBER", 100)
    surah = fetch_surah_online(surah_number)

    surah_name = surah["surah_name_en"]
    ayahs = surah["ayahs"]
    
    # Filter ayahs by range if specified
    ayah_start = getattr(config, "AYAH_START", 1)
    ayah_end = getattr(config, "AYAH_END", len(ayahs))
    
    # Ensure valid range
    ayah_start = max(1, min(ayah_start, len(ayahs)))
    ayah_end = max(ayah_start, min(ayah_end, len(ayahs)))
    
    ayahs = [a for a in ayahs if ayah_start <= a["number"] <= ayah_end]
    
    backgrounds = list_background_paths()

    print(f"\n  Surah       : {surah_name} (#{surah_number})")
    print(f"  Ayahs       : {ayah_start} to {ayah_end} ({len(ayahs)} total)")
    print(f"  Backgrounds : {len(backgrounds)}")

    do_phone = getattr(config, "GENERATE_PHONE_FORMAT", True)
    do_tv = getattr(config, "GENERATE_TV_FORMAT", True)

    print(f"\n  Phone reels (9:16) : {'YES' if do_phone else 'NO'}")
    print(f"  TV YouTube  (16:9) : {'YES' if do_tv else 'NO'}\n")

    if do_phone:
        print("Generating REELS...")
        export_reels(
            ayahs=ayahs,
            surah_name=surah_name,
            surah_number=surah_number,
            bg_start=0,
        )

    print("\nGenerating YOUTUBE videos...")
    export_youtube(
        ayahs=ayahs,
        surah_name=surah_name,
        surah_number=surah_number,
        bg_start=10,
    )

    print("\n" + "=" * 54)
    print("  ALL DONE!")
    if do_phone:
        print(f"  Reels         -> {config.REEL_OUTPUT_DIR}/")
        print(f"  YouTube phone -> {config.YOUTUBE_OUTPUT_DIR}/phone/")
    if do_tv:
        print(f"  YouTube TV    -> {config.YOUTUBE_OUTPUT_DIR}/tv/")
    print("=" * 54 + "\n")


def generate_videos_internal(
    surah_number: int,
    reciter: str = "alafasy",
    ayah_start: int = 1,
    ayah_end: int = 10,
    fast_mode: bool = False,
    generate_phone: bool = True,
    generate_tv: bool = True,
) -> dict:
    """
    Internal function for API to call.
    Returns dict with output file paths.
    """
    # Update config
    import SETTINGS as s
    s.SURAH_NUMBER = surah_number
    s.PREFERRED_RECITER = reciter
    s.AYAH_START = ayah_start
    s.AYAH_END = ayah_end
    s.FAST_MODE = fast_mode
    s.GENERATE_PHONE_FORMAT = generate_phone
    s.GENERATE_TV_FORMAT = generate_tv
    
    # Reload config
    import importlib
    importlib.reload(config)
    
    # Run main logic
    surah = fetch_surah_online(surah_number)
    ayahs = surah["ayahs"]
    surah_name = surah["surah_name_en"]
    
    # Filter by range
    ayahs = [a for a in ayahs if ayah_start <= a["number"] <= ayah_end]
    backgrounds = list_background_paths()
    
    output_files = {"phone_reels": [], "youtube_phone": [], "youtube_tv": []}
    
    if generate_phone:
        export_reels(
            ayahs=ayahs,
            surah_name=surah_name,
            surah_number=surah_number,
            bg_start=0,
        )
        # Collect output files
        reel_files = [f for f in os.listdir(config.REEL_OUTPUT_DIR) if f.endswith(".mp4")]
        output_files["phone_reels"] = reel_files
    
    if generate_tv or generate_phone:
        export_youtube(
            ayahs=ayahs,
            surah_name=surah_name,
            surah_number=surah_number,
            bg_start=10,
        )
        # Collect YouTube files
        if generate_phone:
            phone_dir = os.path.join(config.YOUTUBE_OUTPUT_DIR, "phone")
            if os.path.exists(phone_dir):
                output_files["youtube_phone"] = [f for f in os.listdir(phone_dir) if f.endswith(".mp4")]
        if generate_tv:
            tv_dir = os.path.join(config.YOUTUBE_OUTPUT_DIR, "tv")
            if os.path.exists(tv_dir):
                output_files["youtube_tv"] = [f for f in os.listdir(tv_dir) if f.endswith(".mp4")]
    
    return output_files


if __name__ == "__main__":
    main()
