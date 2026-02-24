#!/usr/bin/env python
"""
Quick fix to verify background spreading for small ayahs.
For a Surah with 7 ayahs and 55 backgrounds:

Old method: Backgrounds 1-7 only
New method: Use ayah number * 8 to spread across all 55

Example - Fatihah (7 ayahs):
Ayah 1: bg_index = (1-1)*8 = 0 → image 0 % 55 = 0
Ayah 2: bg_index = (2-1)*8 = 8 → image 8 % 55 = 8
Ayah 3: bg_index = (3-1)*8 = 16 → image 16 % 55 = 16
Ayah 4: bg_index = (4-1)*8 = 24 → image 24 % 55 = 24
Ayah 5: bg_index = (5-1)*8 = 32 → image 32 % 55 = 32
Ayah 6: bg_index = (6-1)*8 = 40 → image 40 % 55 = 40
Ayah 7: bg_index = (7-1)*8 = 48 → image 48 % 55 = 48

This spreads across images 0, 8, 16, 24, 32, 40, 48 - much better!
"""
total_bg = 55

print("\nBackground distribution test for Fatihah (7 ayahs):")
print("="*50)
for ayah_num in range(1, 8):
    bg_idx = (ayah_num - 1) * 8
    image_num = bg_idx % total_bg
    print(f"Ayah {ayah_num}: bg_index={bg_idx:2d} → image {image_num:2d}")

print("\n" + "="*50)
print("\nTo apply this fix, update video_exporter.py line ~141:")
print("Change: bgspread_index = bg_start + int((i * total_bg) / max(1, len(batch)))")
print("To:     bgspread_index = (ayah['number'] - 1) * 8 + bg_start")
print("\nOr use: bgspread_index = (ayah['number'] - 1) * ((total_bg // 114) or 1)")
print("        This automatically scales based on total available backgrounds")
