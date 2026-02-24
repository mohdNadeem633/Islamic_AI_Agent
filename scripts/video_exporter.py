"""
video_exporter.py
=================
Handles the two output streams:

  REELS   → videos/reels/    (15-17 s per clip, Instagram / Facebook)
  YOUTUBE → videos/youtube/  (4-5 min per file, YouTube)

ROOT CAUSE FIX (AttributeError: 'NoneType' has no attribute 'get_frame')
─────────────────────────────────────────────────────────────────────────
MoviePy reads audio *lazily* — the AudioFileClip reader stays open until
write_videofile() finishes.  The old code called audio.close() immediately
after build_clip(), which destroyed the reader before writing started.

Fix: _build_ayah_clip() now returns BOTH (clip, audio_handle).
The caller collects all audio handles and closes them ONLY AFTER
write_videofile() has fully completed.

SECOND FIX (silence shape crash for mono audio)
───────────────────────────────────────────────
Moved silence generation into clip_builder._make_silence() which reads
the actual channel count instead of always assuming stereo (N, 2).
"""

import os
from typing import Optional

import numpy as np
from moviepy.editor import (
    AudioFileClip,
    ImageSequenceClip,
    concatenate_videoclips,
)

import config
from audio_engine import download_audio, get_word_timings
from clip_builder import build_clip


# ─────────────────────────────────────────────────────────────
#  ENCODE SETTINGS
# ─────────────────────────────────────────────────────────────

_ENCODE_PARAMS = dict(
    codec         = "libx264",
    audio_codec   = "aac",
    bitrate       = "8000k",
    audio_bitrate = "320k",
    ffmpeg_params = ["-crf", "18"],
    logger        = None,
)


# ─────────────────────────────────────────────────────────────
#  WRITE HELPER  –  write first, THEN close everything
# ─────────────────────────────────────────────────────────────

def _write_and_close(
    clip:          ImageSequenceClip,
    path:          str,
    audio_handles: list[AudioFileClip],
) -> None:
    """
    Write *clip* to *path*.
    After writing completes, close the clip then all audio handles.
    Audio MUST NOT be closed before this function is called.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    clip.write_videofile(path, **_ENCODE_PARAMS)   # audio read happens here

    try:
        clip.close()
    except Exception:
        pass
    for handle in audio_handles:
        try:
            handle.close()
        except Exception:
            pass

    print(f"   💾  Saved: {path}")


# ─────────────────────────────────────────────────────────────
#  DURATION HELPER
# ─────────────────────────────────────────────────────────────

def _get_duration(surah_number: int, ayah_number: int) -> float:
    """Return audio duration for one ayah in seconds, or 0.0 on failure."""
    path = download_audio(surah_number, ayah_number)
    if not path:
        return 0.0
    try:
        a = AudioFileClip(path)
        d = float(a.duration)
        a.close()
        return d
    except Exception:
        return 0.0


# ─────────────────────────────────────────────────────────────
#  SINGLE AYAH → (clip, audio_handle)
# ─────────────────────────────────────────────────────────────

def _build_ayah_clip(
    ayah:         dict,
    surah_name:   str,
    surah_number: int,
    bg_index:     int,
    trim_start:   float = 0.0,
    trim_end:     Optional[float] = None,
    add_hold:     bool = False,
) -> tuple[Optional[ImageSequenceClip], Optional[AudioFileClip]]:
    """
    Build a video clip for one ayah.

    Returns (clip, audio_handle).
    The caller MUST close audio_handle only AFTER write_videofile() finishes.
    Returns (None, None) if audio download failed.
    """
    audio_path = download_audio(surah_number, ayah["number"])
    if not audio_path:
        print(f"   ✗ No audio for ayah {ayah['number']}")
        return None, None

    audio   = AudioFileClip(audio_path)
    words   = ayah["arabic"].split()
    timings = get_word_timings(audio_path, len(words))

    clip = build_clip(
        ayah           = ayah,
        surah_name     = surah_name,
        audio_clip     = audio,        # NOT closed here — caller owns it
        timings        = timings,
        bg_start_index = bg_index,
        trim_start     = trim_start,
        trim_end       = trim_end if trim_end is not None else audio.duration,
        add_hold       = add_hold,
    )

    return clip, audio


# ─────────────────────────────────────────────────────────────
#  BATCH FLUSH  (shared by reels + YouTube)
# ─────────────────────────────────────────────────────────────

def _flush_batch(
    batch:        list[dict],
    out_path:     str,
    surah_name:   str,
    surah_number: int,
    bg_start:     int,
) -> None:
    """
    Build clips for every ayah in *batch*, concatenate them, write to
    *out_path*, then close clips + audio in the correct order.
    """
    clips:         list[ImageSequenceClip] = []
    audio_handles: list[AudioFileClip]     = []

    for i, ayah in enumerate(batch):
        is_last = (i == len(batch) - 1)
        clip, audio = _build_ayah_clip(
            ayah         = ayah,
            surah_name   = surah_name,
            surah_number = surah_number,
            bg_index     = bg_start + i,
            add_hold     = is_last,
        )
        if clip is not None:
            clips.append(clip)
        if audio is not None:
            audio_handles.append(audio)

    if not clips:
        for h in audio_handles:
            try:
                h.close()
            except Exception:
                pass
        return

    final = concatenate_videoclips(clips) if len(clips) > 1 else clips[0]
    _write_and_close(final, out_path, audio_handles)


# ─────────────────────────────────────────────────────────────
#  REEL EXPORTER  (15-17 s per file)
# ─────────────────────────────────────────────────────────────

def export_reels(
    ayahs:        list[dict],
    surah_name:   str,
    surah_number: int,
    bg_start:     int = 0,
) -> None:
    """
    Batch ayahs into 15-17 s reels → REEL_OUTPUT_DIR.

    Strategy
    --------
    • Accumulate consecutive ayahs until total >= REEL_TARGET_SEC, then flush.
    • A single ayah longer than REEL_MAX_SEC is time-sliced into separate reels.
    """
    os.makedirs(config.REEL_OUTPUT_DIR, exist_ok=True)
    print(f"\n📱  Building reels  →  {config.REEL_OUTPUT_DIR}/")

    durations = [_get_duration(surah_number, a["number"]) for a in ayahs]

    reel_num:  int        = 1
    batch:     list[dict] = []
    batch_dur: float      = 0.0

    def _flush_reel(b: list[dict], bg_idx: int) -> None:
        nonlocal reel_num
        path = os.path.join(
            config.REEL_OUTPUT_DIR,
            f"{surah_name}_reel_{reel_num:03d}.mp4",
        )
        print(f"\n── Reel {reel_num:03d}  ({len(b)} ayah(s)) ──────────────")
        _flush_batch(b, path, surah_name, surah_number, bg_idx)
        reel_num += 1

    for ayah, dur in zip(ayahs, durations):
        if dur <= 0:
            continue

        # ── Long ayah: slice into reel-sized parts ─────────────
        if dur > config.REEL_MAX_SEC:
            if batch:
                _flush_reel(batch, bg_start + reel_num)
                batch, batch_dur = [], 0.0

            audio_path = download_audio(surah_number, ayah["number"])
            audio      = AudioFileClip(audio_path)
            words      = ayah["arabic"].split()
            timings    = get_word_timings(audio_path, len(words))
            n_parts    = int(np.ceil(dur / config.REEL_TARGET_SEC))
            part_dur   = dur / n_parts

            # Build all part clips, collecting handles
            part_clips:   list[ImageSequenceClip] = []
            for part in range(n_parts):
                t0 = part * part_dur
                t1 = min((part + 1) * part_dur, dur)
                c  = build_clip(
                    ayah           = ayah,
                    surah_name     = surah_name,
                    audio_clip     = audio,
                    timings        = timings,
                    bg_start_index = bg_start + reel_num + part,
                    trim_start     = t0,
                    trim_end       = t1,
                    add_hold       = (part == n_parts - 1),
                )
                part_clips.append(c)

            # Write each part, but close audio only after the last one
            for idx, c in enumerate(part_clips):
                out = os.path.join(
                    config.REEL_OUTPUT_DIR,
                    f"{surah_name}_reel_{reel_num:03d}.mp4",
                )
                print(f"\n── Reel {reel_num:03d}  (part {idx+1}/{n_parts}) ──────────────")
                handles = [audio] if idx == len(part_clips) - 1 else []
                _write_and_close(c, out, handles)
                reel_num += 1

            continue

        # ── Normal: accumulate ─────────────────────────────────
        batch.append(ayah)
        batch_dur += dur

        if batch_dur >= config.REEL_TARGET_SEC:
            _flush_reel(batch, bg_start + reel_num)
            batch, batch_dur = [], 0.0

    if batch:
        _flush_reel(batch, bg_start + reel_num)


# ─────────────────────────────────────────────────────────────
#  YOUTUBE EXPORTER  (4-5 min per file)
# ─────────────────────────────────────────────────────────────

def export_youtube(
    ayahs:        list[dict],
    surah_name:   str,
    surah_number: int,
    bg_start:     int = 0,
) -> None:
    """
    Batch ayahs into 4-5 minute YouTube videos → YOUTUBE_OUTPUT_DIR.
    """
    os.makedirs(config.YOUTUBE_OUTPUT_DIR, exist_ok=True)
    print(f"\n▶️   Building YouTube videos  →  {config.YOUTUBE_OUTPUT_DIR}/")

    durations  = [_get_duration(surah_number, a["number"]) for a in ayahs]
    target_sec = config.YOUTUBE_TARGET_MIN * 60

    yt_num:    int        = 1
    batch:     list[dict] = []
    batch_dur: float      = 0.0

    def _flush_yt(b: list[dict], bg_idx: int) -> None:
        nonlocal yt_num
        total = sum(_get_duration(surah_number, a["number"]) for a in b)
        path  = os.path.join(
            config.YOUTUBE_OUTPUT_DIR,
            f"{surah_name}_youtube_{yt_num:03d}.mp4",
        )
        print(f"\n── YouTube {yt_num:03d}  ({len(b)} ayah(s), ~{total:.0f}s) ──────────────")
        _flush_batch(b, path, surah_name, surah_number, bg_idx)
        yt_num += 1

    for ayah, dur in zip(ayahs, durations):
        if dur <= 0:
            continue

        batch.append(ayah)
        batch_dur += dur

        if batch_dur >= target_sec:
            _flush_yt(batch, bg_start + yt_num)
            batch, batch_dur = [], 0.0

    if batch:
        _flush_yt(batch, bg_start + yt_num)
