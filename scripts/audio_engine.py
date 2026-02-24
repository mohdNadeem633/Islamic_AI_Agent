"""
audio_engine.py
===============
Two responsibilities:
  1. Download recitation audio from everyayah.com (with caching)
  2. Analyse the audio to produce per-word timestamps via onset detection

The timestamps are used by the renderer to highlight each Arabic word
exactly when it is being recited (point 2 – correct start positions).
"""

import os
from typing import Optional

import librosa
import numpy as np
import requests

import config


# ─────────────────────────────────────────────────────────────
#  AUDIO DOWNLOAD
# ─────────────────────────────────────────────────────────────

_RECITERS = [
    ("Alafasy_128kbps",             "alafasy"),
    ("Abdul_Basit_Murattal_192kbps","basit"),
    ("Husary_128kbps",              "husary"),
]


def download_audio(surah: int, ayah: int) -> Optional[str]:
    """
    Download the recitation MP3 for the given surah/ayah.
    Files are cached in AUDIO_CACHE_DIR so each is downloaded once.
    Returns the local file path, or None if all sources failed.
    """
    os.makedirs(config.AUDIO_CACHE_DIR, exist_ok=True)
    s = str(surah).zfill(3)
    a = str(ayah).zfill(3)

    for url_segment, tag in _RECITERS:
        local = os.path.join(config.AUDIO_CACHE_DIR, f"{s}_{a}_{tag}.mp3")
        if os.path.exists(local):
            return local

        url = f"https://everyayah.com/data/{url_segment}/{s}{a}.mp3"
        try:
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            with open(local, "wb") as f:
                f.write(resp.content)
            print(f"   ✓ Audio cached [{tag}]: {local}")
            return local
        except Exception as exc:
            print(f"   ✗ Download failed [{tag}]: {exc}")

    return None


# ─────────────────────────────────────────────────────────────
#  WORD TIMING ANALYSIS
# ─────────────────────────────────────────────────────────────

def _onset_boundaries(y: np.ndarray, sr: int) -> list[float]:
    """
    Detect onset times and filter to a plausible set of word boundaries.
    Uses librosa onset detection with backtracking for accurate start times.
    """
    raw: np.ndarray = librosa.onset.onset_detect(
        y=y,
        sr=sr,
        units="time",
        backtrack=True,
        delta=config.ONSET_DELTA,
        wait=int(config.MIN_WORD_DURATION * sr / 512),
    )

    filtered: list[float] = []
    for t in raw.tolist():
        if not filtered or (t - filtered[-1]) >= config.MIN_ONSET_GAP:
            filtered.append(float(t))
    return filtered


def _segments_from_onsets(
    onsets: list[float], total_dur: float
) -> list[tuple[float, float]]:
    """Convert onset times to (start, end) segments."""
    segs: list[tuple[float, float]] = []
    for i, t in enumerate(onsets):
        end = onsets[i + 1] if i + 1 < len(onsets) else total_dur
        if end - t >= config.MIN_WORD_DURATION:
            segs.append((t, end))
    return segs


def _fit_to_word_count(
    segs: list[tuple[float, float]], n: int
) -> list[tuple[float, float]]:
    """
    Merge or split segments until we have exactly *n* entries.
    Ensures a 1-to-1 mapping between detected speech bursts and Arabic words.
    """
    segs = list(segs)   # work on a copy

    # ── Too many segments → merge pairs with smallest gap between them ──
    while len(segs) > n:
        gaps = [segs[i + 1][0] - segs[i][1] for i in range(len(segs) - 1)]
        idx  = int(np.argmin(gaps))
        s1, s2 = segs[idx], segs[idx + 1]
        segs = segs[:idx] + [(s1[0], s2[1])] + segs[idx + 2:]

    # ── Too few segments → split the longest one ──
    while len(segs) < n:
        durs = [e - s for s, e in segs]
        idx  = int(np.argmax(durs))
        s, e = segs[idx]
        mid  = (s + e) / 2.0
        segs = segs[:idx] + [(s, mid), (mid, e)] + segs[idx + 1:]

    return segs[:n]


def get_word_timings(
    audio_path: str, num_words: int
) -> list[tuple[float, float]]:
    """
    Public API: analyse *audio_path* and return a list of
    (start_sec, end_sec) tuples – one per Arabic word.

    The list length always equals *num_words*.
    """
    y, sr      = librosa.load(audio_path, sr=config.AUDIO_SR)
    total_dur  = len(y) / sr

    onsets = _onset_boundaries(y, sr)
    segs   = _segments_from_onsets(onsets, total_dur)

    if not segs:
        # Fallback: equally divide audio among words
        dur  = total_dur / num_words
        segs = [(i * dur, (i + 1) * dur) for i in range(num_words)]

    return _fit_to_word_count(segs, num_words)
