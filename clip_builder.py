"""
clip_builder.py
===============
Converts per-frame rendering into MoviePy video clips.

CHANGE: build_clip() now accepts optional (width, height) so the same
function can render both phone (1080×1920) and TV (1920×1080) clips.
"""

from typing import Optional

import numpy as np
from moviepy.audio.AudioClip import AudioArrayClip
from moviepy.editor import AudioFileClip, ImageSequenceClip, concatenate_audioclips

import config
from renderer import render_frame, frame_to_array, build_sync_map


def _current_arabic_idx(t: float, timings: list) -> int:
    for idx, (start, end) in enumerate(timings):
        if start <= t < end:
            return idx
    if t >= timings[-1][0]:
        return len(timings) - 1
    return -1


def _make_silence(duration_sec: float, audio_clip: AudioFileClip) -> AudioArrayClip:
    n_channels = getattr(audio_clip, "nchannels", 2) or 2
    n_samples  = max(1, int(duration_sec * audio_clip.fps))
    data = (np.zeros(n_samples, dtype=np.float32)
            if n_channels == 1
            else np.zeros((n_samples, n_channels), dtype=np.float32))
    return AudioArrayClip(data, fps=audio_clip.fps)


def build_clip(
    ayah:           dict,
    surah_name:     str,
    audio_clip:     AudioFileClip,
    timings:        list,
    bg_start_index: int            = 0,
    trim_start:     float          = 0.0,
    trim_end:       Optional[float]= None,
    add_hold:       bool           = True,
    width:          int            = None,
    height:         int            = None,
    surah_number:   int            = 0,
) -> ImageSequenceClip:
    """
    Build an ImageSequenceClip for audio window [trim_start, trim_end].

    width / height: leave as None for phone (9:16), pass 1920/1080 for TV.
    """
    W = width  or config.WIDTH
    H = height or config.HEIGHT

    if trim_end is None:
        trim_end = audio_clip.duration

    trim_start = max(0.0, trim_start)
    trim_end   = min(trim_end, audio_clip.duration)

    arabic_words  = ayah["arabic"].split()
    english_words = ayah["english"].split()
    sync_map      = build_sync_map(len(arabic_words), len(english_words))

    total_frames = max(1, int((trim_end - trim_start) * config.FPS))
    frames = []
    
    # Use same background for entire ayah (one background per ayah)
    bg_idx = bg_start_index

    for fi in range(total_frames):
        t      = trim_start + fi / config.FPS
        ar_idx = _current_arabic_idx(t, timings)
        
        en_idxs= sync_map.get(ar_idx, []) if ar_idx >= 0 else []

        frame = render_frame(
            ayah                     = ayah,
            surah_name               = surah_name,
            highlighted_arabic_idx   = ar_idx,
            highlighted_english_idxs = en_idxs,
            bg_index                 = bg_idx,
            width                    = W,
            height                   = H,
            surah_number             = surah_number,
        )
        frames.append(frame_to_array(frame))

    if add_hold and frames:
        hold_n = int(config.HOLD_AT_END * config.FPS)
        frames.extend([frames[-1]] * hold_n)

    sub_audio = audio_clip.subclip(trim_start, trim_end)
    if add_hold:
        silence   = _make_silence(config.HOLD_AT_END, audio_clip)
        sub_audio = concatenate_audioclips([sub_audio, silence])

    video = ImageSequenceClip(frames, fps=config.FPS)
    return video.set_audio(sub_audio)
