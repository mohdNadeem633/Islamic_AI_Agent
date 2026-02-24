#!/usr/bin/env python
"""
Diagnostic script to check background loading and cycling.
"""

import os
import glob
from assets import list_background_paths

# Check what backgrounds are found
backgrounds = list_background_paths()

print("\n" + "="*60)
print("BACKGROUND DIAGNOSTIC")
print("="*60)
print(f"\nTotal backgrounds found: {len(backgrounds)}")
print(f"\nBackground files:")
for i, bg_path in enumerate(backgrounds, 1):
    print(f"  {i:2d}. {os.path.basename(bg_path)}")

print(f"\n{'='*60}")
print("Expected behavior:")
print(f"  - Small ayah (7 verses) in single reel should use:")
print(f"    Ayah 1 → bg_index % {len(backgrounds)} → image 1")
print(f"    Ayah 2 → bg_index % {len(backgrounds)} → image 8")
print(f"    Ayah 3 → bg_index % {len(backgrounds)} → image 16")
print(f"    ... (spread across all {len(backgrounds)} images)")
print("\n" + "="*60 + "\n")
