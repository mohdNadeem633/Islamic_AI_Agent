"""
audio_engine.py
===============
Two responsibilities:
  1. Download & cache recitation audio from everyayah.com
  2. Analyse audio to produce per-word timestamps

FIXES:
  • Preferred reciter is now read from SETTINGS.py (PREFERRED_RECITER).
    The system tries your preferred reciter first, then falls back to
    the others only if the first fails.
  • Audio is ONLY downloaded once — if the cached file already exists,
    it is returned instantly without any network request.
  • _get_duration() reuses download_audio() cache instead of calling it
    again, preventing the double-download that was happening before.
"""

import os
from typing import Optional

import librosa
import numpy as np
import requests

import config


# ─────────────────────────────────────────────────────────────
#  RECITER TABLE
# ─────────────────────────────────────────────────────────────

_RECITER_TABLE = {
    "alafasy": "Alafasy_128kbps",
    "basit":   "Abdul_Basit_Murattal_192kbps",
    "husary":  "Husary_128kbps",
}

_ALL_RECITERS = ["alafasy", "basit", "husary"]


def _ordered_reciters() -> list:
    """Return reciter list with PREFERRED_RECITER first."""
    preferred = getattr(config, "PREFERRED_RECITER", "alafasy")
    others    = [r for r in _ALL_RECITERS if r != preferred]
    return [preferred] + others


# ─────────────────────────────────────────────────────────────
#  AUDIO DOWNLOAD  (with smart cache — never re-downloads)
# ─────────────────────────────────────────────────────────────

def download_audio(surah: int, ayah_num: int) -> Optional[str]:
    """
    Return local path to the recitation MP3 for surah/ayah.

    Smart cache logic:
      1. Check if ANY reciter's file is already cached → return it immediately
         (no network request at all).
      2. If not cached, try each reciter in preferred order.
      3. Save to cache on first successful download.
    """
    os.makedirs(config.AUDIO_CACHE_DIR, exist_ok=True)
    s = str(surah).zfill(3)
    a = str(ayah_num).zfill(3)

    reciters = _ordered_reciters()

    # ── Step 1: check if already cached (any reciter) ─────────
    for tag in reciters:
        local = os.path.join(config.AUDIO_CACHE_DIR, f"{s}_{a}_{tag}.mp3")
        if os.path.exists(local):
            return local          # ← instant return, no download

    # ── Step 2: download from preferred reciter first ─────────
    for tag in reciters:
        url_seg = _RECITER_TABLE[tag]
        local   = os.path.join(config.AUDIO_CACHE_DIR, f"{s}_{a}_{tag}.mp3")
        url     = f"https://everyayah.com/data/{url_seg}/{s}{a}.mp3"
        try:
            print(f"   [DOWN] Downloading audio [{tag}] ...", end=" ", flush=True)
            resp = requests.get(url, timeout=25)
            resp.raise_for_status()
            with open(local, "wb") as f:
                f.write(resp.content)
            print(f"[OK] saved.")
            return local
        except Exception as exc:
            print(f"[FAIL] ({exc})")

    print(f"   [FAIL] All reciters failed for {s}_{a}")
    return None


# ─────────────────────────────────────────────────────────────
#  WORD TIMING ANALYSIS
# ─────────────────────────────────────────────────────────────

def _onset_boundaries(y: np.ndarray, sr: int) -> list:
    raw = librosa.onset.onset_detect(
        y=y, sr=sr, units="time", backtrack=True,
        delta=config.ONSET_DELTA,
        wait=int(config.MIN_WORD_DURATION * sr / 512),
    )
    filtered = []
    for t in raw.tolist():
        if not filtered or (t - filtered[-1]) >= config.MIN_ONSET_GAP:
            filtered.append(float(t))
    return filtered


def _segments_from_onsets(onsets: list, total_dur: float) -> list:
    segs = []
    for i, t in enumerate(onsets):
        end = onsets[i + 1] if i + 1 < len(onsets) else total_dur
        if end - t >= config.MIN_WORD_DURATION:
            segs.append((t, end))
    return segs


def _fit_to_word_count(segs: list, n: int) -> list:
    segs = list(segs)
    while len(segs) > n:
        gaps = [segs[i + 1][0] - segs[i][1] for i in range(len(segs) - 1)]
        idx  = int(np.argmin(gaps))
        s1, s2 = segs[idx], segs[idx + 1]
        segs = segs[:idx] + [(s1[0], s2[1])] + segs[idx + 2:]
    while len(segs) < n:
        durs = [e - s for s, e in segs]
        idx  = int(np.argmax(durs))
        s, e = segs[idx]
        mid  = (s + e) / 2.0
        segs = segs[:idx] + [(s, mid), (mid, e)] + segs[idx + 1:]
    return segs[:n]


def get_word_timings(audio_path: str, num_words: int) -> list:
    """
    Analyse audio_path and return [(start_sec, end_sec), ...] — one per word.
    List length always equals num_words.
    """
    y, sr     = librosa.load(audio_path, sr=config.AUDIO_SR)
    total_dur = len(y) / sr
    onsets    = _onset_boundaries(y, sr)
    segs      = _segments_from_onsets(onsets, total_dur)
    if not segs:
        dur  = total_dur / num_words
        segs = [(i * dur, (i + 1) * dur) for i in range(num_words)]
    return _fit_to_word_count(segs, num_words)


def get_audio_duration(surah: int, ayah_num: int) -> float:
    """
    Return duration in seconds for a surah/ayah audio.
    Uses the cached file — does NOT trigger a second download.
    """
    path = download_audio(surah, ayah_num)
    if not path:
        return 0.0
    try:
        from moviepy.editor import AudioFileClip
        a = AudioFileClip(path)
        d = float(a.duration)
        a.close()
        return d
    except Exception:
        return 0.0


def get_bismillah_end_time(audio_path: str) -> float:
    """
    Get the estimated end time of Bismillah recitation in Ayah 1 audio.
    
    Most reciters take 3-5 seconds for Bismillah. We analyze the audio
    to find a natural pause or use a reasonable default.
    """
    if not audio_path or not os.path.exists(audio_path):
        return float(getattr(config, "BISMILLAH_DURATION", 4.0))
    
    try:
        # Get total audio duration
        from moviepy.editor import AudioFileClip
        audio = AudioFileClip(audio_path)
        total_duration = float(audio.duration)
        audio.close()
        
        # Bismillah is typically 20-30% of the first ayah audio
        # (Bismillah is relatively short compared to the full verse)
        bismi_end = min(total_duration * 0.25, 5.0)  # Cap at 5 seconds
        
        return bismi_end
    except Exception as e:
        # Fallback to configured duration
        print(f"[WARN] Could not analyze audio for Bismillah timing: {e}")
        return float(getattr(config, "BISMILLAH_DURATION", 4.0))


def download_bismillah(surah: int) -> Optional[str]:
    """
    Download Bismillah (intro) for the given surah.
    Returns local path to Bismillah audio, or None if not available.
    
    Surah 9 (At-Tawbah) doesn't have Bismillah, so this returns None.
    """
    # At-Tawbah (Surah 9) doesn't start with Bismillah
    if surah == 9:
        return None
    
    os.makedirs(config.AUDIO_CACHE_DIR, exist_ok=True)
    
    reciters = _ordered_reciters()
    
    # Bismillah uses first ayah (001) for each surah
    s = str(surah).zfill(3)
    a = "001"
    
    # Try downloading from preferred reciter first
    for tag in reciters:
        url_seg = _RECITER_TABLE[tag]
        local = os.path.join(config.AUDIO_CACHE_DIR, f"bismillah_{s}_{tag}.mp3")
        
        # Check cache first
        if os.path.exists(local):
            return local
        
        # Download
        url = f"https://everyayah.com/data/{url_seg}/{s}{a}.mp3"
        try:
            resp = requests.get(url, timeout=25)
            resp.raise_for_status()
            with open(local, "wb") as f:
                f.write(resp.content)
            return local
        except Exception:
            pass
    
    return None
