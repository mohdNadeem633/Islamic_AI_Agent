"""
test_system.py
==============
Test script to verify everything is working correctly.

Run this BEFORE generating videos to check:
- Internet connectivity
- API access
- Font files
- Background images
- Audio download
- All modules import correctly
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported."""
    print("=" * 60)
    print("TEST 1: Checking Python modules...")
    print("=" * 60)
    
    required_modules = [
        'PIL', 'moviepy', 'librosa', 'arabic_reshaper', 'bidi',
        'requests', 'numpy', 'streamlit'
    ]
    
    failed = []
    for module_name in required_modules:
        try:
            __import__(module_name)
            print(f"[OK] {module_name}")
        except ImportError as e:
            print(f"[FAIL] {module_name} - {e}")
            failed.append(module_name)
    
    if failed:
        print(f"\n[ERROR] Missing modules: {', '.join(failed)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("\n[PASS] All required modules installed!\n")
    return True


def test_project_files():
    """Test that all project files exist."""
    print("=" * 60)
    print("TEST 2: Checking project files...")
    print("=" * 60)
    
    required_files = [
        'app.py', 'main.py', 'SETTINGS.py', 'config.py',
        'arabic_utils.py', 'assets.py', 'audio_engine.py',
        'clip_builder.py', 'renderer.py', 'video_exporter.py',
        'requirements.txt'
    ]
    
    missing = []
    for filename in required_files:
        if os.path.exists(filename):
            print(f"[OK] {filename}")
        else:
            print(f"[FAIL] {filename} - NOT FOUND")
            missing.append(filename)
    
    if missing:
        print(f"\n[ERROR] Missing files: {', '.join(missing)}")
        return False
    
    print("\n[PASS] All project files present!\n")
    return True


def test_fonts():
    """Test that font files exist."""
    print("=" * 60)
    print("TEST 3: Checking fonts...")
    print("=" * 60)
    
    required_fonts = [
        'fonts/Amiri-Bold.ttf',
        'fonts/Amiri-Regular.ttf',
        'fonts/NotoSans-SemiBold.ttf',
        'fonts/NotoSans-Regular.ttf',
    ]
    
    missing = []
    for font_path in required_fonts:
        if os.path.exists(font_path):
            print(f"[OK] {font_path}")
        else:
            print(f"[FAIL] {font_path} - NOT FOUND")
            missing.append(font_path)
    
    if missing:
        print(f"\n[ERROR] Missing fonts: {', '.join(missing)}")
        print("Download from:")
        print("  Amiri: https://fonts.google.com/specimen/Amiri")
        print("  Noto Sans: https://fonts.google.com/specimen/Noto+Sans")
        return False
    
    print("\n[PASS] All fonts present!\n")
    return True


def test_images():
    """Test that background images exist."""
    print("=" * 60)
    print("TEST 4: Checking background images...")
    print("=" * 60)
    
    if not os.path.exists('images'):
        print("[FAIL] images/ folder not found")
        print("\n[ERROR] Create images/ folder and add background images!")
        return False
    
    import glob
    bg_files = (glob.glob('images/background*.jpg') + 
                glob.glob('images/background*.png') +
                glob.glob('images/bg*.jpg') +
                glob.glob('images/bg*.png'))
    
    if not bg_files:
        print("[FAIL] No background images found")
        print("\n[ERROR] Add at least one background image to images/ folder!")
        return False
    
    print(f"[OK] Found {len(bg_files)} background images")
    for img in bg_files[:5]:  # Show first 5
        print(f"  - {img}")
    if len(bg_files) > 5:
        print(f"  ... and {len(bg_files) - 5} more")
    
    print("\n[PASS] Background images ready!\n")
    return True


def test_internet():
    """Test internet connectivity and API access."""
    print("=" * 60)
    print("TEST 5: Checking internet & API...")
    print("=" * 60)
    
    try:
        import requests
        
        # Test API
        response = requests.get("https://api.alquran.cloud/v1/surah/1", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'data' in data:
            print(f"[OK] API accessible")
            print(f"  Test: Retrieved Surah {data['data']['englishName']}")
        else:
            print("[FAIL] API returned unexpected format")
            return False
            
    except requests.exceptions.ConnectionError:
        print("[FAIL] No internet connection")
        print("\n[ERROR] Connect to internet to download Surah text!")
        return False
    except Exception as e:
        print(f"[FAIL] API error: {e}")
        return False
    
    print("\n[PASS] Internet & API working!\n")
    return True


def test_settings():
    """Test that SETTINGS.py is configured correctly."""
    print("=" * 60)
    print("TEST 6: Checking SETTINGS.py...")
    print("=" * 60)
    
    try:
        import config
        
        surah_num = getattr(config, 'SURAH_NUMBER', None)
        reciter = getattr(config, 'PREFERRED_RECITER', None)
        
        if surah_num is None:
            print("[FAIL] SURAH_NUMBER not set")
            return False
        
        if not (1 <= surah_num <= 114):
            print(f"[FAIL] SURAH_NUMBER = {surah_num} (must be 1-114)")
            return False
        
        print(f"[OK] SURAH_NUMBER = {surah_num}")
        print(f"[OK] PREFERRED_RECITER = {reciter}")
        print(f"[OK] GENERATE_PHONE_FORMAT = {getattr(config, 'GENERATE_PHONE_FORMAT', True)}")
        print(f"[OK] GENERATE_TV_FORMAT = {getattr(config, 'GENERATE_TV_FORMAT', True)}")
        
    except Exception as e:
        print(f"[FAIL] Error loading SETTINGS: {e}")
        return False
    
    print("\n[PASS] Settings configured!\n")
    return True


def test_audio_download():
    """Test audio download functionality."""
    print("=" * 60)
    print("TEST 7: Testing audio download...")
    print("=" * 60)
    
    try:
        from audio_engine import download_audio
        
        # Test download Surah 1, Ayah 1
        print("Attempting to download test audio (Surah 1, Ayah 1)...")
        audio_path = download_audio(1, 1)
        
        if audio_path and os.path.exists(audio_path):
            print(f"[OK] Audio downloaded successfully")
            print(f"  Path: {audio_path}")
        else:
            print("[FAIL] Audio download failed")
            return False
            
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False
    
    print("\n[PASS] Audio download working!\n")
    return True


def main():
    """Run all tests."""
    print("\n")
    print("[" + "=" * 58 + "]")
    print("|" + " " * 10 + "QURAN VIDEO GENERATOR - SYSTEM TEST" + " " * 13 + "|")
    print("[" + "=" * 58 + "]")
    print()
    
    tests = [
        ("Imports", test_imports),
        ("Project Files", test_project_files),
        ("Fonts", test_fonts),
        ("Images", test_images),
        ("Internet", test_internet),
        ("Settings", test_settings),
        ("Audio Download", test_audio_download),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} test crashed: {e}\n")
            results.append((test_name, False))
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} - {test_name}")
    
    all_passed = all(passed for _, passed in results)
    
    print()
    if all_passed:
        print("[" + "=" * 58 + "]")
        print("|" + " " * 15 + "*** ALL TESTS PASSED! ***" + " " * 19 + "|")
        print("|" + " " * 10 + "You're ready to generate videos!" + " " * 16 + "|")
        print("|" + " " * 15 + "Run: streamlit run app.py" + " " * 18 + "|")
        print("[" + "=" * 58 + "]")
        print()
        return 0
    else:
        print("[" + "=" * 58 + "]")
        print("|" + " " * 12 + "WARNING: SOME TESTS FAILED" + " " * 19 + "|")
        print("|" + " " * 8 + "Fix the issues above before generating" + " " * 11 + "|")
        print("[" + "=" * 58 + "]")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
