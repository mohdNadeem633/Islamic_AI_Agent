#!/usr/bin/env python
"""Check how many backgrounds are actually being found"""

import os
import glob

patterns = [
    "images/background*.jpg",
    "images/background*.png",
    "images/bg*.jpg",
    "images/bg*.png",
]

all_found = []
for pattern in patterns:
    found = sorted(glob.glob(pattern))
    if found:
        print(f"\n{pattern}:")
        for f in found:
            print(f"  - {os.path.basename(f)}")
        all_found.extend(found)

# Deduplicate
unique = list(set(all_found))
unique.sort()

print(f"\n{'='*60}")
print(f"TOTAL UNIQUE BACKGROUNDS FOUND: {len(unique)}")
print(f"{'='*60}\n")

# Show actual filenames
if unique:
    print("All backgrounds:")
    for i, path in enumerate(unique, 1):
        print(f"  {i:2d}. {os.path.basename(path)}")
else:
    print("NO BACKGROUNDS FOUND!")
    print("\nFiles in images/ folder:")
    if os.path.exists("images"):
        for f in os.listdir("images"):
            print(f"  - {f}")
