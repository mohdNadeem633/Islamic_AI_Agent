import os
from typing import Optional

import numpy as np
from moviepy.editor import AudioFileClip, concatenate_videoclips, CompositeAudioClip

import config
from audio_engine import download_audio, get_word_timings, get_audio_duration, download_bismillah
from clip_builder import build_clip
from assets import list_background_paths


# ─────────────────────────────────────────────────────────────
#  FORMAT SIZES
# ─────────────────────────────────────────────────────────────
_PHONE_W, _PHONE_H = 1080, 1920
_TV_W,    _TV_H    = 1920, 1080


# ─────────────────────────────────────────────────────────────
#  ENCODE SETTINGS
# ─────────────────────────────────────────────────────────────
_ENCODE_PHONE = dict(
    codec="libx264",
    audio_codec="aac",
    bitrate="8000k",
    audio_bitrate="320k",
    ffmpeg_params=["-crf", "18"],
    logger=None,
)

_ENCODE_TV = dict(
    codec="libx264",
    audio_codec="aac",
    bitrate="12000k",
    audio_bitrate="320k",
    ffmpeg_params=["-crf", "17", "-preset", "slow"],
    logger=None,
)

# Fast mode for quick testing/preview
_ENCODE_PHONE_FAST = dict(
    codec="libx264",
    audio_codec="aac",
    bitrate="4000k",
    audio_bitrate="128k",
    ffmpeg_params=["-crf", "28", "-preset", "superfast"],
    logger=None,
)

_ENCODE_TV_FAST = dict(
    codec="libx264",
    audio_codec="aac",
    bitrate="6000k",
    audio_bitrate="128k",
    ffmpeg_params=["-crf", "28", "-preset", "superfast"],
    logger=None,
)


# ─────────────────────────────────────────────────────────────
#  WRITE HELPER
# ─────────────────────────────────────────────────────────────
def _write_and_close(clip, path: str, audio_handles: list, enc: dict) -> None:
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

    print(f"Saved: {path}")


# ─────────────────────────────────────────────────────────────
#  DURATION
# ─────────────────────────────────────────────────────────────
def _dur(surah_number: int, ayah_number: int) -> float:
    return get_audio_duration(surah_number, ayah_number)


# ─────────────────────────────────────────────────────────────
#  SINGLE AYAH CLIP
# ─────────────────────────────────────────────────────────────
def _build_ayah_clip(
    ayah,
    surah_name,
    surah_number,
    bg_index,
    trim_start=0.0,
    trim_end=None,
    add_hold=False,
    width=None,
    height=None,
):
    audio_path = download_audio(surah_number, ayah["number"])
    if not audio_path:
        print(f"No audio for ayah {ayah['number']}")
        return None, None

    audio = AudioFileClip(audio_path)
    words = ayah["arabic"].split()
    timings = get_word_timings(audio_path, len(words))

    clip = build_clip(
        ayah=ayah,
        surah_name=surah_name,
        audio_clip=audio,
        timings=timings,
        bg_start_index=bg_index,
        trim_start=trim_start,
        trim_end=trim_end if trim_end is not None else audio.duration,
        add_hold=add_hold,
        width=width,
        height=height,
    )

    return clip, audio


# ─────────────────────────────────────────────────────────────
#  BATCH FLUSH
# ─────────────────────────────────────────────────────────────
def _flush_batch(batch, out_path, surah_name, surah_number,
                 bg_start, width, height, enc, bismillah_audio_path=None):

    clips, handles = [], []
    
    # Get total available backgrounds
    total_bg = len(list_background_paths())
    if total_bg == 0:
        total_bg = 1

    for i, ayah in enumerate(batch):
        # Spread backgrounds evenly across all available images
        # For small batches (few ayahs), this distributes them across all 52+ images
        # Example: 7-ayah surah with 52 backgrounds:
        #   i=0: 0 + int(0*52/7) = 0
        #   i=1: 0 + int(1*52/7) = 7
        #   i=2: 0 + int(2*52/7) = 14
        #   i=3: 0 + int(3*52/7) = 22
        #   i=4: 0 + int(4*52/7) = 29
        #   i=5: 0 + int(5*52/7) = 37
        #   i=6: 0 + int(6*52/7) = 44
        bgspread_index = bg_start + int((i * total_bg) / max(1, len(batch)))
        
        clip, audio = _build_ayah_clip(
            ayah=ayah,
            surah_name=surah_name,
            surah_number=surah_number,
            bg_index=bgspread_index,
            add_hold=(i == len(batch) - 1),
            width=width,
            height=height,
        )

        if clip:
            # For first clip, prepend Bismillah audio if available
            if i == 0 and bismillah_audio_path and os.path.exists(bismillah_audio_path):
                try:
                    bismillah_audio = AudioFileClip(bismillah_audio_path)
                    if audio:
                        # Combine Bismillah + ayah audio
                        combined_audio = concatenate_videoclips([bismillah_audio, audio])
                        clip = clip.set_audio(combined_audio)
                    else:
                        # Use preset duration for video if no audio
                        clip_with_bismillah = clip.set_duration(clip.duration + bismillah_audio.duration)
                        clip_with_bismillah = clip_with_bismillah.set_audio(bismillah_audio)
                        clip = clip_with_bismillah
                    handles.append(bismillah_audio)
                except Exception as e:
                    print(f"  [WARN] Could not prepend Bismillah: {e}")
            
            clips.append(clip)
        if audio:
            handles.append(audio)

    if not clips:
        for h in handles:
            try:
                h.close()
            except:
                pass
        return

    final = concatenate_videoclips(clips) if len(clips) > 1 else clips[0]
    _write_and_close(final, out_path, handles, enc)


# ─────────────────────────────────────────────────────────────
#  REEL EXPORTER
# ─────────────────────────────────────────────────────────────
def export_reels(ayahs, surah_name, surah_number, bg_start=0):

    if not getattr(config, "GENERATE_PHONE_FORMAT", True):
        return

    os.makedirs(config.REEL_OUTPUT_DIR, exist_ok=True)
    print(f"\nReels (9:16) -> {config.REEL_OUTPUT_DIR}/")

    # Use fast mode if enabled
    fast_mode = getattr(config, "FAST_MODE", False)
    encode_settings = _ENCODE_PHONE_FAST if fast_mode else _ENCODE_PHONE
    
    # Download Bismillah for this surah (returns None for Surah 9)
    bismillah_audio_path = download_bismillah(surah_number)

    durations = [_dur(surah_number, a["number"]) for a in ayahs]
    total_duration = sum(durations)
    
    # If surah is small (< 2 min), keep entire surah in one reel
    # regardless of REEL_TARGET_SEC setting
    force_single_reel = total_duration < 120
    
    reel_num = [1]
    batch, batch_dur = [], 0.0
    ayah_index = [0]
    first_reel = [True]

    def _flush_reel(b, bg_idx):
        path = os.path.join(
            config.REEL_OUTPUT_DIR,
            f"{surah_name}_reel_{reel_num[0]:03d}.mp4"
        )
        progress_text = f"[PROGRESS] Reel {reel_num[0]:03d}: Ayah(s) {b[0]['number']}-{b[-1]['number']}"
        print(progress_text)
        
        # Pass Bismillah only to the first reel
        bismillah_for_reel = bismillah_audio_path if first_reel[0] else None
        first_reel[0] = False

        _flush_batch(
            b, path, surah_name, surah_number,
            bg_idx, _PHONE_W, _PHONE_H, encode_settings,
            bismillah_audio_path=bismillah_for_reel
        )

        reel_num[0] += 1

    for ayah, dur in zip(ayahs, durations):
        if dur <= 0:
            continue

        batch.append(ayah)
        batch_dur += dur
        ayah_index[0] += 1

        # Split reels only if surah is NOT small (>= 120 seconds)
        # Small surahs stay in one reel
        if not force_single_reel and batch_dur >= config.REEL_TARGET_SEC:
            _flush_reel(batch, bg_start + reel_num[0])
            batch[:] = []
            batch_dur = 0.0

    if batch:
        _flush_reel(batch, bg_start + reel_num[0])


# ─────────────────────────────────────────────────────────────
#  YOUTUBE EXPORTER
# ─────────────────────────────────────────────────────────────
def export_youtube(ayahs, surah_name, surah_number, bg_start=0):

    do_phone = getattr(config, "GENERATE_PHONE_FORMAT", True)
    do_tv    = getattr(config, "GENERATE_TV_FORMAT", True)
    
    # Use fast mode if enabled
    fast_mode = getattr(config, "FAST_MODE", False)
    encode_phone = _ENCODE_PHONE_FAST if fast_mode else _ENCODE_PHONE
    encode_tv = _ENCODE_TV_FAST if fast_mode else _ENCODE_TV

    if not do_phone and not do_tv:
        print("Both YouTube formats disabled in SETTINGS.py")
        return

    phone_dir = os.path.join(config.YOUTUBE_OUTPUT_DIR, "phone")
    tv_dir = os.path.join(config.YOUTUBE_OUTPUT_DIR, "tv")

    if do_phone:
        os.makedirs(phone_dir, exist_ok=True)
    if do_tv:
        os.makedirs(tv_dir, exist_ok=True)

    print(f"\nYouTube -> {config.YOUTUBE_OUTPUT_DIR}/")

    if do_phone:
        print(f"  Phone (9:16) -> {phone_dir}/")
    if do_tv:
        print(f"  TV (16:9)    -> {tv_dir}/")
    
    # Download Bismillah for this surah (returns None for Surah 9)
    bismillah_audio_path = download_bismillah(surah_number)

    durations = [_dur(surah_number, a["number"]) for a in ayahs]
    total_duration = sum(durations)
    target_sec = config.YOUTUBE_TARGET_MIN * 60
    
    # If surah is small (< 2 min), keep entire surah in one YouTube file
    force_single_yt = total_duration < 120

    yt_num = [1]
    batch, batch_dur = [], 0.0
    first_yt = [True]

    def _flush_yt(b, bg_idx):
        total = sum(_dur(surah_number, a["number"]) for a in b)

        progress_text = f"[PROGRESS] YouTube {yt_num[0]:03d}: Ayah(s) {b[0]['number']}-{b[-1]['number']} (~{total:.0f}s)"
        print(progress_text)
        
        # Pass Bismillah only to the first YouTube file
        bismillah_for_yt = bismillah_audio_path if first_yt[0] else None
        first_yt[0] = False

        if do_phone:
            path = os.path.join(
                phone_dir,
                f"{surah_name}_youtube_{yt_num[0]:03d}.mp4"
            )
            _flush_batch(b, path, surah_name, surah_number,
                         bg_idx, _PHONE_W, _PHONE_H, encode_phone,
                         bismillah_audio_path=bismillah_for_yt)

        if do_tv:
            path = os.path.join(
                tv_dir,
                f"{surah_name}_youtube_{yt_num[0]:03d}_tv.mp4"
            )
            _flush_batch(b, path, surah_name, surah_number,
                         bg_idx, _TV_W, _TV_H, encode_tv,
                         bismillah_audio_path=bismillah_for_yt)

        yt_num[0] += 1

    for ayah, dur in zip(ayahs, durations):
        if dur <= 0:
            continue

        batch.append(ayah)
        batch_dur += dur

        # Split YouTube files only if surah is NOT small (>= 120 seconds)
        # Small surahs stay in one YouTube file
        if not force_single_yt and batch_dur >= target_sec:
            _flush_yt(batch, bg_start + yt_num[0])
            batch[:] = []
            batch_dur = 0.0

    if batch:
        _flush_yt(batch, bg_start + yt_num[0])
