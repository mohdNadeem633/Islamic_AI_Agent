"""
clip_builder.py
===============
Converts per-frame rendering into MoviePy video clips.

Responsibilities:
  • Iterate over time, call renderer.render_frame() for each frame
  • Handle background changes every BG_CHANGE_INTERVAL seconds
  • Append hold-frames at the end of each clip
  • Attach (sub-clipped) audio

BUG FIXES vs previous version:
  • Silence array now uses the actual channel count of the source audio
    (mono MP3s have 1 channel, not 2) — previously crashed with shape error
  • Audio object is NO LONGER closed inside this function; ownership stays
    with the caller so MoviePy can read it lazily during write_videofile
"""

from typing import Optional

import numpy as np
from moviepy.audio.AudioClip import AudioArrayClip
from moviepy.editor import AudioFileClip, ImageSequenceClip, concatenate_audioclips

import config
from renderer import render_frame, frame_to_array, build_sync_map


# ─────────────────────────────────────────────────────────────
#  ACTIVE WORD LOOKUP
# ─────────────────────────────────────────────────────────────

def _current_arabic_idx(
    t: float,
    timings: list[tuple[float, float]],
) -> int:
    """
    Return the index of the Arabic word being recited at time *t*.
      -1  → before recitation starts
      N-1 → after recitation ends (hold last word highlighted)
    """
    for idx, (start, end) in enumerate(timings):
        if start <= t < end:
            return idx
    if t >= timings[-1][0]:
        return len(timings) - 1
    return -1


# ─────────────────────────────────────────────────────────────
#  SILENCE HELPER
# ─────────────────────────────────────────────────────────────

def _make_silence(duration_sec: float, audio_clip: AudioFileClip) -> AudioArrayClip:
    """
    Create a silent AudioArrayClip that matches the channel count of *audio_clip*.
    Handles both mono (1 ch) and stereo (2 ch) sources safely.
    """
    n_channels = getattr(audio_clip, "nchannels", 2) or 2
    n_samples  = max(1, int(duration_sec * audio_clip.fps))

    if n_channels == 1:
        data = np.zeros(n_samples, dtype=np.float32)
    else:
        data = np.zeros((n_samples, n_channels), dtype=np.float32)

    return AudioArrayClip(data, fps=audio_clip.fps)


# ─────────────────────────────────────────────────────────────
#  SINGLE CLIP BUILDER
# ─────────────────────────────────────────────────────────────

def build_clip(
    ayah:           dict,
    surah_name:     str,
    audio_clip:     AudioFileClip,
    timings:        list[tuple[float, float]],
    bg_start_index: int   = 0,
    trim_start:     float = 0.0,
    trim_end:       Optional[float] = None,
    add_hold:       bool  = True,
) -> ImageSequenceClip:
    """
    Build and return an ImageSequenceClip for the audio window
    [trim_start, trim_end].

    IMPORTANT: The caller must keep *audio_clip* open until AFTER
    write_videofile() has finished.  Do NOT close it before writing.

    Parameters
    ----------
    bg_start_index : background index at trim_start
                     (auto-increments every BG_CHANGE_INTERVAL seconds)
    trim_start     : clip window start in seconds
    trim_end       : clip window end in seconds  (None = full audio duration)
    add_hold       : append HOLD_AT_END still-frames + silence at the end
    """
    if trim_end is None:
        trim_end = audio_clip.duration

    trim_start = max(0.0, trim_start)
    trim_end   = min(trim_end, audio_clip.duration)

    arabic_words  = ayah["arabic"].split()
    english_words = ayah["english"].split()
    sync_map      = build_sync_map(len(arabic_words), len(english_words))

    total_frames = max(1, int((trim_end - trim_start) * config.FPS))
    frames: list[np.ndarray] = []

    for fi in range(total_frames):
        t = trim_start + fi / config.FPS

        bg_idx = bg_start_index + int(
            (t - trim_start) // config.BG_CHANGE_INTERVAL
        )

        ar_idx  = _current_arabic_idx(t, timings)
        en_idxs = sync_map.get(ar_idx, []) if ar_idx >= 0 else []

        frame = render_frame(
            ayah                     = ayah,
            surah_name               = surah_name,
            highlighted_arabic_idx   = ar_idx,
            highlighted_english_idxs = en_idxs,
            bg_index                 = bg_idx,
        )
        frames.append(frame_to_array(frame))

    # ── Append hold frames (still image) ──────────────────────
    if add_hold and frames:
        hold_n = int(config.HOLD_AT_END * config.FPS)
        frames.extend([frames[-1]] * hold_n)

    # ── Build audio sub-clip ───────────────────────────────────
    # subclip() returns a lazy view — audio_clip MUST stay open
    sub_audio = audio_clip.subclip(trim_start, trim_end)

    if add_hold:
        silence   = _make_silence(config.HOLD_AT_END, audio_clip)
        sub_audio = concatenate_audioclips([sub_audio, silence])

    video = ImageSequenceClip(frames, fps=config.FPS)
    return video.set_audio(sub_audio)
