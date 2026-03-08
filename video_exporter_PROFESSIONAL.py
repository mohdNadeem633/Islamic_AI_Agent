"""
video_exporter_PROFESSIONAL.py
===============================
Professional video exporter with:
- Bismillah before EVERY ayah
- Perfect sync
- One background per ayah
- Smooth transitions
"""

import os
from moviepy.editor import AudioFileClip, concatenate_videoclips
import config
from audio_engine import download_audio, get_word_timings, get_audio_duration, get_bismillah_end_time
from clip_builder import build_clip
from assets import list_background_paths


# Format sizes
_PHONE_W, _PHONE_H = 1080, 1920
_TV_W, _TV_H = 1920, 1080


def _get_encode_settings(quality: str, fast_mode: bool):
    """Get encoding settings based on quality preset."""
    if fast_mode:
        return {
            "codec": "libx264",
            "audio_codec": "aac",
            "bitrate": "4000k",
            "audio_bitrate": "128k",
            "ffmpeg_params": ["-crf", "28", "-preset", "superfast"],
            "logger": None,
        }
    
    quality_presets = {
        "draft": {"bitrate": "2000k", "crf": "28", "preset": "superfast"},
        "medium": {"bitrate": "5000k", "crf": "23", "preset": "medium"},
        "high": {"bitrate": "8000k", "crf": "18", "preset": "slow"},
        "ultra": {"bitrate": "12000k", "crf": "15", "preset": "veryslow"},
    }
    
    preset = quality_presets.get(quality, quality_presets["high"])
    
    return {
        "codec": "libx264",
        "audio_codec": "aac",
        "bitrate": preset["bitrate"],
        "audio_bitrate": "320k",
        "ffmpeg_params": ["-crf", preset["crf"], "-preset", preset["preset"]],
        "logger": None,
    }


def _write_video(clip, path: str, audio_handles: list, enc: dict) -> None:
    """Write video file and cleanup."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    clip.write_videofile(path, **enc)

    try:
        clip.close()
    except Exception:
        pass

    for h in audio_handles:
        try:
            h.close()
        except Exception:
            pass

    print(f"✅ Saved: {path}")


def _get_ayah_duration(surah_number: int, ayah: dict) -> float:
    """Get duration for an ayah."""
    duration = get_audio_duration(surah_number, ayah["number"])
    if ayah.get("has_bismillah_prefix", False):
        # Subtract Bismillah duration from ayah 1
        from audio_engine import get_bismillah_end_time
        audio_path = download_audio(surah_number, 1)
        if audio_path:
            bismillah_dur = get_bismillah_end_time(audio_path)
            duration -= bismillah_dur
    return duration



def _build_ayah_clip(
    ayah: dict,
    surah_name: str,
    surah_number: int,
    bg_index: int,
    add_hold: bool = False,
    width: int = None,
    height: int = None,
):
    """
    Build clip for ONE ayah.
    
    For Ayah 1, if Bismillah was stripped, trim the audio to skip Bismillah.
    """
    from audio_engine import get_bismillah_end_time
    
    # Regular ayah
    audio_path = download_audio(surah_number, ayah["number"])
    
    # If this is Ayah 1 with Bismillah stripped, skip the Bismillah audio
    if ayah["number"] == 1 and ayah.get("has_bismillah_prefix", False):
        # Skip the Bismillah portion at the start
        bismillah_duration = get_bismillah_end_time(audio_path)
        trim_start_ms = bismillah_duration
        trim_end_ms = None  # Go to end of audio
    else:
        trim_start_ms = 0.0
        trim_end_ms = None
    
    if not audio_path:
        print(f"⚠️  No audio for ayah {ayah.get('number', '?')}")
        return None, []

    audio = AudioFileClip(audio_path)
    handles = [audio]
    
    words = ayah["arabic"].split()
    timings = get_word_timings(audio_path, len(words))

    clip = build_clip(
        ayah=ayah,
        surah_name=surah_name,
        audio_clip=audio,
        timings=timings,
        bg_start_index=bg_index,
        trim_start=trim_start_ms,
        trim_end=trim_end_ms,
        add_hold=add_hold,
        width=width,
        height=height,
        surah_number=surah_number,
    )

    return clip, handles


def _flush_batch(
    batch: list,
    out_path: str,
    surah_name: str,
    surah_number: int,
    bg_start: int,
    width: int,
    height: int,
    enc: dict
):
    """
    Build and save a batch of ayahs as one video.
    
    KEY FIX: Uses ONE background per ayah (not changing mid-ayah).
    """
    from moviepy.editor import VideoFileClip
    
    clips = []
    handles = []
    
    total_bg = len(list_background_paths())
    if total_bg == 0:
        total_bg = 1
    
    bg_change_mode = getattr(config, "BG_CHANGE_MODE", "per_ayah")
    
    # Prepend Bismillah reel if this batch starts with ayah 1 and not Surah 9
    if batch and batch[0]["number"] == 1 and surah_number != 9:
        bismillah_path = os.path.join(os.getcwd(), "Bismillah_Reel.mp4")
        if os.path.exists(bismillah_path):
            bismillah_clip = VideoFileClip(bismillah_path)
            clips.append(bismillah_clip)
            handles.append(bismillah_clip)
    
    for i, ayah in enumerate(batch):
        # Determine background index
        if bg_change_mode == "per_ayah":
            # One background per ayah (PROFESSIONAL)
            bg_idx = (bg_start + i) % total_bg
        elif bg_change_mode == "per_reel":
            # Same background for entire video
            bg_idx = bg_start % total_bg
        else:
            # Default: spread across all backgrounds
            bg_idx = bg_start + int((i * total_bg) / max(1, len(batch)))
        
        # Build clip
        is_last = (i == len(batch) - 1)
        clip, audio = _build_ayah_clip(
            ayah=ayah,
            surah_name=surah_name,
            surah_number=surah_number,
            bg_index=bg_idx,
            add_hold=is_last,
            width=width,
            height=height,
        )

        if clip:
            clips.append(clip)
        if audio:
            handles.extend(audio)

    if not clips:
        for h in handles:
            try:
                h.close()
            except:
                pass
        return

    # Concatenate all clips
    final = concatenate_videoclips(clips, method="compose") if len(clips) > 1 else clips[0]
    _write_video(final, out_path, handles, enc)


def export_reels(ayahs: list, surah_name: str, surah_number: int, bg_start: int = 0):
    """
    Export phone reels (9:16).
    
    FIXED: Respects REEL_TARGET_DURATION setting.
    """
    if not getattr(config, "GENERATE_PHONE_FORMAT", True):
        return

    os.makedirs(config.REEL_OUTPUT_DIR, exist_ok=True)
    print(f"\n📱 Generating phone reels (9:16) → {config.REEL_OUTPUT_DIR}/")

    # Get quality settings
    quality = getattr(config, "VIDEO_QUALITY", "high")
    fast_mode = getattr(config, "FAST_MODE", False)
    enc = _get_encode_settings(quality, fast_mode)

    # Get target duration
    target_sec = getattr(config, "REEL_TARGET_DURATION", 30)
    min_sec = getattr(config, "REEL_MIN_DURATION", 15)
    max_sec = getattr(config, "REEL_MAX_DURATION", 60)

    # Calculate durations
    durations = [_get_ayah_duration(surah_number, a) for a in ayahs]
    
    reel_num = 1
    batch = []
    batch_dur = 0.0

    def _flush_reel(b, bg_idx):
        nonlocal reel_num
        path = os.path.join(
            config.REEL_OUTPUT_DIR,
            f"{surah_name}_reel_{reel_num:03d}.mp4"
        )
        
        total_dur = sum(_get_ayah_duration(surah_number, a) for a in b)
        print(f"\n🎬 Reel {reel_num:03d}: {len(b)} clips, ~{total_dur:.1f}s")

        _flush_batch(b, path, surah_name, surah_number, bg_idx, _PHONE_W, _PHONE_H, enc)
        reel_num += 1

    # Batch ayahs by duration
    for ayah, dur in zip(ayahs, durations):
        if dur <= 0:
            continue

        # Check if adding this ayah exceeds max
        if batch and (batch_dur + dur) > max_sec:
            _flush_reel(batch, bg_start + reel_num)
            batch = []
            batch_dur = 0.0

        batch.append(ayah)
        batch_dur += dur

        # Check if we've hit target
        if batch_dur >= target_sec:
            _flush_reel(batch, bg_start + reel_num)
            batch = []
            batch_dur = 0.0

    # Flush remaining
    if batch:
        _flush_reel(batch, bg_start + reel_num)


def export_youtube(ayahs: list, surah_name: str, surah_number: int, bg_start: int = 0):
    """Export longer YouTube videos."""
    do_phone = getattr(config, "GENERATE_PHONE_FORMAT", True)
    do_tv = getattr(config, "GENERATE_TV_FORMAT", False)

    if not do_phone and not do_tv:
        print("⏭️  Skipping YouTube (both formats disabled)")
        return

    phone_dir = os.path.join(config.YOUTUBE_OUTPUT_DIR, "phone")
    tv_dir = os.path.join(config.YOUTUBE_OUTPUT_DIR, "tv")

    if do_phone:
        os.makedirs(phone_dir, exist_ok=True)
    if do_tv:
        os.makedirs(tv_dir, exist_ok=True)

    print(f"\n📺 Generating YouTube videos → {config.YOUTUBE_OUTPUT_DIR}/")

    # Get settings
    quality = getattr(config, "VIDEO_QUALITY", "high")
    fast_mode = getattr(config, "FAST_MODE", False)
    enc = _get_encode_settings(quality, fast_mode)

    target_sec = getattr(config, "YOUTUBE_TARGET_DURATION", 270)
    durations = [_get_ayah_duration(surah_number, a) for a in ayahs]

    yt_num = 1
    batch = []
    batch_dur = 0.0

    def _flush_yt(b, bg_idx):
        nonlocal yt_num
        total = sum(_get_ayah_duration(surah_number, a) for a in b)
        print(f"\n🎥 YouTube {yt_num:03d}: {len(b)} clips, ~{total:.1f}s")

        if do_phone:
            path = os.path.join(phone_dir, f"{surah_name}_youtube_{yt_num:03d}.mp4")
            _flush_batch(b, path, surah_name, surah_number, bg_idx, _PHONE_W, _PHONE_H, enc)

        if do_tv:
            path = os.path.join(tv_dir, f"{surah_name}_youtube_{yt_num:03d}_tv.mp4")
            _flush_batch(b, path, surah_name, surah_number, bg_idx, _TV_W, _TV_H, enc)

        yt_num += 1

    for ayah, dur in zip(ayahs, durations):
        if dur <= 0:
            continue

        batch.append(ayah)
        batch_dur += dur

        if batch_dur >= target_sec:
            _flush_yt(batch, bg_start + yt_num)
            batch = []
            batch_dur = 0.0

    if batch:
        _flush_yt(batch, bg_start + yt_num)
