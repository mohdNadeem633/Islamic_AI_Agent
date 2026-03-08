"""
Quran Animated Reel & YouTube Video Generator
==============================================
Improvements over v1:
  1.  Larger, bolder Arabic font  +  bolder English font
  2.  Red underline bar ONLY under the currently-spoken Arabic word (precise alignment)
  3.  Background rotates through images/background1.jpg … backgroundN.jpg per ayah
  4.  Background changes dynamically every N seconds during long videos
  5.  Bismillah shown centred in Arabic + English translation
  6.  Brand logo scaled correctly (max 160 px wide) – upper-right corner
  7.  Ayah reference number displayed bottom-centre
  8.  Words highlighted ONE-AT-A-TIME (only the word being spoken turns red)
  9.  Red highlight fixed – colour actually changes; was cumulative, now single-word
 10.  Audio sync improved: onset detection → word-level timestamps via DTW-like approach
 11a. SHORT reel  ≤ 120 s  → videos/reels/<name>_ayah_<n>.mp4   (Instagram / Facebook)
 11b. LONG video  (full)   → videos/youtube/<name>_ayah_<n>.mp4  (YouTube, no split)
      If ayah > 120 s it is also split into ≤120 s parts under videos/reels/.
"""

from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import AudioFileClip, ImageSequenceClip, concatenate_videoclips
import json, os, re, glob
import arabic_reshaper
from bidi.algorithm import get_display
import requests
import librosa
import numpy as np

# =============================================================
# ========================= CONFIG ============================
# =============================================================

WIDTH, HEIGHT = 1080, 1920

# --- Layout -------------------------------------------------
LOGO_MAX_W         = 160          # pt 6 – logo capped at 160 px wide
LOGO_MARGIN        = 48
LOGO_Y             = 48

BRAND_TEXT_FONT_SIZE = 32

ARABIC_TEXT_CENTER_Y  = 720       # vertical centre of Arabic block
ENGLISH_Y_START       = 1080
REFERENCE_Y           = HEIGHT - 110

ARABIC_X_MARGIN    = 80
ENGLISH_X_MARGIN   = 80

# --- Fonts --------------------------------------------------
ARABIC_FONT_SIZE   = 72           # pt 1 – bigger & bolder
ENGLISH_FONT_SIZE  =            # pt 1 – bigger
REFERENCE_FONT_SIZE = 26

# --- Colours ------------------------------------------------
BG_COLOR           = (240, 235, 230, 255)

ARABIC_COLOR       = (15, 15, 15, 255)
ARABIC_HIGHLIGHT   = (180, 30, 20, 255)    # pt 8/9 – single-word red highlight

ENGLISH_COLOR      = (35, 35, 35, 255)
ENGLISH_HIGHLIGHT  = (180, 30, 20, 255)

REFERENCE_COLOR    = (80, 80, 80, 255)

# Underline bar beneath highlighted Arabic word – pt 2
UNDERLINE_H        = 5
UNDERLINE_PAD      = 4            # extra px left/right

# --- Animation ----------------------------------------------
FPS                = 30
HOLD_AT_END        = 2.5          # seconds of still frame at end

# --- Audio analysis -----------------------------------------
ENERGY_THRESHOLD   = 0.018
MIN_WORD_DURATION  = 0.12
MIN_GAP            = 0.06

# --- Reel split threshold -----------------------------------
REEL_MAX_DURATION  = 120          # seconds – pt 11

# =============================================================
# ==================== ARABIC RESHAPER ========================
# =============================================================

reshaper = arabic_reshaper.ArabicReshaper(configuration={
    "delete_harakat": False,
    "support_ligatures": True,
    "shift_harakat_position": False,
})

def reshape_arabic(text):
    return get_display(reshaper.reshape(text))

def is_bismillah(text):
    clean = re.sub(r'[\u064B-\u0652\u0670]', '', text)
    return clean.strip() == "بسم الله الرحمن الرحيم"

# =============================================================
# ====================== FONT LOADING =========================
# =============================================================

def load_fonts():
    """Load fonts; fall back to default if files missing."""
    try:
        # pt 1 – try Bold variants first
        ar  = ImageFont.truetype("fonts/Amiri-Bold.ttf",          ARABIC_FONT_SIZE)
    except Exception:
        try:
            ar = ImageFont.truetype("fonts/Amiri-Regular.ttf",    ARABIC_FONT_SIZE)
        except Exception:
            ar = ImageFont.load_default()

    try:
        en  = ImageFont.truetype("fonts/NotoSans-SemiBold.ttf",   ENGLISH_FONT_SIZE)
    except Exception:
        try:
            en = ImageFont.truetype("fonts/dejavu-sans.extralight.ttf", ENGLISH_FONT_SIZE)
        except Exception:
            en = ImageFont.load_default()

    try:
        ref = ImageFont.truetype("fonts/NotoSans-Regular.ttf",    REFERENCE_FONT_SIZE)
    except Exception:
        try:
            ref = ImageFont.truetype("fonts/dejavu-sans.extralight.ttf", REFERENCE_FONT_SIZE)
        except Exception:
            ref = ImageFont.load_default()

    return ar, en, ref

# =============================================================
# =================== BACKGROUND LOADING ======================
# =============================================================

# def list_backgrounds():
#     """Return sorted list of background image paths (pt 3/4)."""
#     patterns = ["images/background*.jpg", "images/background*.png",
#                 "images/bg*.jpg",         "images/bg*.png"]
#     found = []
#     for p in patterns:
#         found.extend(sorted(glob.glob(p)))
#     if not found:
#         found = ["images/background.jpg"]
#     return found

# _BG_CACHE: dict = {}

# def load_background(index: int = 0) -> Image.Image:
#     """Load background by round-robin index (pt 3)."""
#     paths = list_backgrounds()
#     path  = paths[index % len(paths)]
#     if path in _BG_CACHE:
#         return _BG_CACHE[path].copy()
#     if os.path.exists(path):
#         bg = Image.open(path).convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
#     else:
#         bg = Image.new("RGBA", (WIDTH, HEIGHT), BG_COLOR)
#     _BG_CACHE[path] = bg
#     return bg.copy()

def list_backgrounds():
    """Return sorted list of background image paths (pt 3/4)."""
    patterns = ["images/background*.jpg", "images/background*.png",
                "images/bg*.jpg",         "images/bg*.png"]
    found = []
    for p in patterns:
        found.extend(sorted(glob.glob(p)))
    if not found:
        found = ["images/background.jpg"]
    return found


_BG_CACHE: dict = {}

def load_background() -> Image.Image:
    """Load random background image."""
    paths = list_backgrounds()

    if not paths:
        return Image.new("RGBA", (WIDTH, HEIGHT), BG_COLOR)

    path = random.choice(paths)   # ✅ RANDOM IMAGE

    if path in _BG_CACHE:
        return _BG_CACHE[path].copy()

    if os.path.exists(path):
        bg = Image.open(path).convert("RGBA").resize(
            (WIDTH, HEIGHT),
            Image.Resampling.LANCZOS
        )
    else:
        bg = Image.new("RGBA", (WIDTH, HEIGHT), BG_COLOR)

    _BG_CACHE[path] = bg
    return bg.copy()

def load_logo():
    """Load brand logo; scale to LOGO_MAX_W (pt 6)."""
    for p in ["images/logo.png", "images/logo.jpg", "images/brand.png"]:
        if os.path.exists(p):
            logo = Image.open(p).convert("RGBA")
            ratio = LOGO_MAX_W / logo.width
            new_h = int(logo.height * ratio)
            return logo.resize((LOGO_MAX_W, new_h), Image.Resampling.LANCZOS)
    return None

# =============================================================
# ==================== AUDIO FUNCTIONS ========================
# =============================================================

def download_recitation_audio(surah: int, ayah: int):
    os.makedirs("audio/recitations", exist_ok=True)
    s, a = str(surah).zfill(3), str(ayah).zfill(3)
    reciters = [
        ("Alafasy_128kbps",            "alafasy"),
        ("Abdul_Basit_Murattal_192kbps","basit"),
        ("Husary_128kbps",             "husary"),
    ]
    for path_seg, name in reciters:
        fpath = f"audio/recitations/{s}_{a}_{name}.mp3"
        if os.path.exists(fpath):
            return fpath
        url = f"https://everyayah.com/data/{path_seg}/{s}{a}.mp3"
        try:
            r = requests.get(url, timeout=20)
            r.raise_for_status()
            with open(fpath, "wb") as f:
                f.write(r.content)
            print(f"   [OK] Audio downloaded: {name}")
            return fpath
        except Exception:
            continue
    return None

def analyze_audio_for_words(audio_path: str, num_words: int):
    """
    Improved word-timing analysis (pt 10):
    Uses onset detection + energy to assign one timestamp per Arabic word.
    Returns list of (start_sec, end_sec) tuples of length == num_words.
    """
    y, sr = librosa.load(audio_path, sr=22050)
    total_dur = len(y) / sr

    # --- onset detection for word boundaries ---
    onset_frames = librosa.onset.onset_detect(
        y=y, sr=sr,
        units="time",
        backtrack=True,
        delta=0.07,
        wait=int(MIN_WORD_DURATION * sr / 512)
    )

    # Filter out onsets that are too close together
    filtered = []
    for t in onset_frames:
        if not filtered or t - filtered[-1] >= MIN_GAP:
            filtered.append(float(t))

    # Build word segments from onsets
    segments = []
    for i, t in enumerate(filtered):
        end = filtered[i + 1] if i + 1 < len(filtered) else total_dur
        if end - t >= MIN_WORD_DURATION:
            segments.append((t, end))

    if not segments:
        # Fallback: equal division
        dur = total_dur / num_words
        segments = [(i * dur, (i + 1) * dur) for i in range(num_words)]

    # Map segments → exactly num_words slots
    # If too many segments, merge shortest gaps; if too few, subdivide longest
    while len(segments) > num_words:
        # merge the two adjacent segments with smallest combined gap
        gaps = [segments[i+1][0] - segments[i][1] for i in range(len(segments)-1)]
        idx  = int(np.argmin(gaps))
        s1, s2 = segments[idx], segments[idx+1]
        segments = segments[:idx] + [(s1[0], s2[1])] + segments[idx+2:]

    while len(segments) < num_words:
        # subdivide the longest segment
        durs = [e - s for s, e in segments]
        idx  = int(np.argmax(durs))
        s, e = segments[idx]
        mid  = (s + e) / 2
        segments = segments[:idx] + [(s, mid), (mid, e)] + segments[idx+1:]

    return segments[:num_words]

# =============================================================
# ==================== FRAME GENERATOR ========================
# =============================================================

def _draw_arabic_line_rtl(draw, words, word_indices, y, ar_font,
                           highlighted_idx, word_boxes: dict):
    """
    Draw one line of Arabic words RTL.
    Stores bounding box of EACH word in word_boxes[global_idx] for underline use.
    pt 2 – underline bar aligned under the highlighted word.
    pt 8/9 – only ONE word highlighted at a time.
    """
    # Measure total line width first for centring option, but we use RTL layout
    x = WIDTH - ARABIC_X_MARGIN
    for word, idx in zip(words, word_indices):
        shaped = reshape_arabic(word)
        bbox   = draw.textbbox((0, 0), shaped + " ", font=ar_font)
        w_px   = bbox[2] - bbox[0]
        x -= w_px

        color = ARABIC_HIGHLIGHT if idx == highlighted_idx else ARABIC_COLOR

        # Draw word
        draw.text((x, y), shaped, font=ar_font, fill=color)

        # Store word box for underline
        actual_bbox = draw.textbbox((x, y), shaped, font=ar_font)
        word_boxes[idx] = actual_bbox  # (x0,y0,x1,y1)


def create_frame(ayah: dict, surah_name: str,
                 highlighted_arabic_idx: int = -1,
                 highlighted_english_idxs: list = None,
                 bg_index: int = 0,
                 is_bism: bool = False):
    """
    Render one video frame.
    highlighted_arabic_idx : index of single Arabic word being spoken (pt 8/9)
    highlighted_english_idxs : list of English word indices to colour (roughly synced)
    bg_index : which background image to use (pt 3/4)
    """
    if highlighted_english_idxs is None:
        highlighted_english_idxs = []

    bg      = load_background(bg_index)
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw    = ImageDraw.Draw(overlay)
    ar_font, en_font, ref_font = load_fonts()

    # ---- Logo (pt 6) ----------------------------------------
    logo = load_logo()
    if logo:
        lx = WIDTH - logo.width - LOGO_MARGIN
        bg.paste(logo, (lx, LOGO_Y), logo)

    # ---- Bismillah frame (pt 5) -----------------------------
    if is_bism:
        ar_text = reshape_arabic(ayah["arabic"])
        en_text = "In the name of Allah, the Most Gracious, the Most Merciful"

        # Arabic centred
        ar_bbox = draw.textbbox((0, 0), ar_text, font=ar_font)
        ar_w    = ar_bbox[2] - ar_bbox[0]
        ax      = (WIDTH - ar_w) // 2
        ay      = HEIGHT // 2 - ARABIC_FONT_SIZE - 20
        draw.text((ax, ay), ar_text, font=ar_font, fill=ARABIC_HIGHLIGHT,
                  stroke_width=1, stroke_fill=(255, 255, 255, 40))

        # English centred below
        en_bbox = draw.textbbox((0, 0), en_text, font=en_font)
        en_w    = en_bbox[2] - en_bbox[0]
        ex      = (WIDTH - en_w) // 2
        draw.text((ex, ay + ARABIC_FONT_SIZE + 20), en_text,
                  font=en_font, fill=ENGLISH_HIGHLIGHT)

        return Image.alpha_composite(bg, overlay).convert("RGB")

    # ---- Arabic text (pt 1, 2, 8, 9) -----------------------
    arabic_words = ayah["arabic"].split()
    max_w = WIDTH - ARABIC_X_MARGIN * 2

    # Word-wrap RTL
    lines: list[list] = []          # each item is list of (word, global_idx)
    line: list        = []
    w_sum             = 0
    for i, word in enumerate(arabic_words):
        shaped = reshape_arabic(word)
        ww     = draw.textbbox((0, 0), shaped + " ", font=ar_font)[2]
        if w_sum + ww <= max_w:
            line.append((word, i))
            w_sum += ww
        else:
            if line:
                lines.append(line)
            line  = [(word, i)]
            w_sum = ww
    if line:
        lines.append(line)

    total_arabic_h = len(lines) * (ARABIC_FONT_SIZE + 28)
    y = ARABIC_TEXT_CENTER_Y - total_arabic_h // 2

    word_boxes: dict = {}
    for ln in lines:
        words_in_line   = [w for w, _ in ln]
        indices_in_line = [i for _, i in ln]
        _draw_arabic_line_rtl(draw, words_in_line, indices_in_line, y,
                               ar_font, highlighted_arabic_idx, word_boxes)
        y += ARABIC_FONT_SIZE + 28

    # ---- Red underline under highlighted word (pt 2) --------
    if highlighted_arabic_idx in word_boxes:
        x0, y0, x1, y1 = word_boxes[highlighted_arabic_idx]
        uy = y1 + UNDERLINE_PAD
        draw.rectangle(
            [x0 - UNDERLINE_PAD, uy, x1 + UNDERLINE_PAD, uy + UNDERLINE_H],
            fill=ARABIC_HIGHLIGHT
        )

    # ---- English text (pt 1) --------------------------------
    english_words = ayah["english"].split()
    max_ew = WIDTH - ENGLISH_X_MARGIN * 2
    e_lines: list = []
    e_line: list  = []
    ew_sum        = 0
    for i, word in enumerate(english_words):
        ww = draw.textbbox((0, 0), word + " ", font=en_font)[2]
        if ew_sum + ww <= max_ew:
            e_line.append((word, i))
            ew_sum += ww
        else:
            if e_line:
                e_lines.append(e_line)
            e_line  = [(word, i)]
            ew_sum  = ww
    if e_line:
        e_lines.append(e_line)

    ey = ENGLISH_Y_START
    for ln in e_lines:
        text = " ".join(w for w, _ in ln)
        lw   = draw.textbbox((0, 0), text, font=en_font)[2]
        ex   = (WIDTH - lw) // 2
        for word, i in ln:
            color = ENGLISH_HIGHLIGHT if i in highlighted_english_idxs else ENGLISH_COLOR
            draw.text((ex, ey), word, font=en_font, fill=color)
            ex += draw.textbbox((0, 0), word + " ", font=en_font)[2]
        ey += ENGLISH_FONT_SIZE + 18

    # ---- Reference (pt 7) ----------------------------------
    ref_text = f"Surah {surah_name}  -  Ayah {ayah['number']}"
    rw       = draw.textbbox((0, 0), ref_text, font=ref_font)[2]
    draw.text(((WIDTH - rw) // 2, REFERENCE_Y), ref_text,
              fill=REFERENCE_COLOR, font=ref_font)

    return Image.alpha_composite(bg, overlay).convert("RGB")

# =============================================================
# ================== SYNC MAPPING =============================
# =============================================================

def build_english_sync(timings, num_arabic, num_english):
    """
    Map arabic word index -> english word indices (roughly proportional).
    Returns dict: arabic_idx -> [english_idx, ...]
    """
    mapping = {}
    ratio   = num_english / max(num_arabic, 1)
    for ai in range(num_arabic):
        ei_start = int(ai * ratio)
        ei_end   = int((ai + 1) * ratio)
        mapping[ai] = list(range(ei_start, max(ei_start + 1, ei_end)))
    return mapping

# =============================================================
# ================ VIDEO CLIP BUILDER =========================
# =============================================================

def build_video_clip(ayah, surah_name, audio_clip, timings, bg_index=0,
                     trim_start=0.0, trim_end=None):
    """
    Build an ImageSequenceClip for the given audio window [trim_start, trim_end].
    bg_index controls which background is used (pt 3/4).
    """
    arabic_words  = ayah["arabic"].split()
    english_words = ayah["english"].split()
    sync_map      = build_english_sync(timings, len(arabic_words), len(english_words))
    is_bism       = is_bismillah(ayah["arabic"])

    if trim_end is None:
        trim_end = audio_clip.duration

    clip_dur   = trim_end - trim_start
    total_frames = int(clip_dur * FPS)

    frames = []
    # Cache of last frame index to avoid redrawing identical frames
    last_ar_idx = -2

    for fi in range(total_frames):
        t = trim_start + fi / FPS

        # pt 8/9: find the SINGLE word being spoken right now
        ar_idx = -1
        for j, (s, e) in enumerate(timings):
            if s <= t < e:
                ar_idx = j
                break
        # If past all timings, keep last word highlighted until hold-end
        if ar_idx == -1 and t >= timings[-1][0]:
            ar_idx = len(timings) - 1

        en_idxs = sync_map.get(ar_idx, []) if ar_idx >= 0 else []

        # pt 4: change background every 30 s during long clips
        dynamic_bg = bg_index + int(t // 30)

        frame = create_frame(
            ayah, surah_name,
            highlighted_arabic_idx   = ar_idx,
            highlighted_english_idxs = en_idxs,
            bg_index                 = dynamic_bg,
            is_bism                  = is_bism,
        )
        frames.append(np.array(frame))

    # Hold last frame for HOLD_AT_END if this is the tail clip
    if trim_end >= audio_clip.duration - 0.1:
        hold_frames = int(HOLD_AT_END * FPS)
        frames.extend([frames[-1]] * hold_frames)

    video_clip = ImageSequenceClip(frames, fps=FPS)

    # Trim audio to window
    sub_audio = audio_clip.subclip(trim_start, min(trim_end, audio_clip.duration))
    if trim_end >= audio_clip.duration - 0.1:
        from moviepy.audio.AudioClip import AudioArrayClip
        silence = np.zeros((int(HOLD_AT_END * sub_audio.fps), 2))
        sil_clip = AudioArrayClip(silence, fps=sub_audio.fps)
        from moviepy.editor import concatenate_audioclips
        sub_audio = concatenate_audioclips([sub_audio, sil_clip])

    return video_clip.set_audio(sub_audio)

# =============================================================
# ================== MAIN VIDEO GENERATOR =====================
# =============================================================

def generate_ayah_videos(ayah: dict, surah_name: str, surah_number: int,
                          ayah_bg_index: int = 0):
    """
    Generate both the short reel(s) and the full YouTube video (pt 11).
    """
    os.makedirs("videos/reels",   exist_ok=True)
    os.makedirs("videos/youtube", exist_ok=True)

    audio_path = download_recitation_audio(surah_number, ayah["number"])
    if not audio_path:
        print(f"   [FAIL] Could not download audio for ayah {ayah['number']}")
        return

    audio      = AudioFileClip(audio_path)
    total_dur  = audio.duration
    words      = ayah["arabic"].split()
    timings    = analyze_audio_for_words(audio_path, len(words))

    base_name  = f"{surah_name}_ayah_{ayah['number']}"

    # ---- pt 11b: Full YouTube video (no split) ---------------
    yt_out  = f"videos/youtube/{base_name}.mp4"
    yt_clip = build_video_clip(ayah, surah_name, audio, timings,
                                bg_index=ayah_bg_index)
    yt_clip.write_videofile(
        yt_out, codec="libx264", audio_codec="aac",
        bitrate="8000k", audio_bitrate="320k",
        ffmpeg_params=["-crf", "18"], logger=None
    )
    yt_clip.close()
    print(f"   [OK] YouTube video: {yt_out}  ({total_dur:.1f}s)")

    # ---- pt 11a: Reel(s) ≤ 120 s for Instagram / Facebook ---
    if total_dur <= REEL_MAX_DURATION:
        # Single reel (same as YouTube clip, just different folder)
        reel_out = f"videos/reels/{base_name}.mp4"
        # Re-use the same file (copy or re-render)
        reel_clip = build_video_clip(ayah, surah_name, audio, timings,
                                      bg_index=ayah_bg_index)
        reel_clip.write_videofile(
            reel_out, codec="libx264", audio_codec="aac",
            bitrate="8000k", audio_bitrate="320k",
            ffmpeg_params=["-crf", "18"], logger=None
        )
        reel_clip.close()
        print(f"   [OK] Reel (single): {reel_out}")
    else:
        # Split into ≤120 s parts
        num_parts = int(np.ceil(total_dur / REEL_MAX_DURATION))
        part_dur  = total_dur / num_parts
        for part_idx in range(num_parts):
            t_start = part_idx * part_dur
            t_end   = min((part_idx + 1) * part_dur, total_dur)
            reel_out = f"videos/reels/{base_name}_part{part_idx+1}.mp4"
            part_clip = build_video_clip(
                ayah, surah_name, audio, timings,
                bg_index   = ayah_bg_index + part_idx,   # pt 4 – different bg per part
                trim_start = t_start,
                trim_end   = t_end
            )
            part_clip.write_videofile(
                reel_out, codec="libx264", audio_codec="aac",
                bitrate="8000k", audio_bitrate="320k",
                ffmpeg_params=["-crf", "18"], logger=None
            )
            part_clip.close()
            print(f"   [OK] Reel part {part_idx+1}/{num_parts}: {reel_out}")

    audio.close()

# =============================================================
# ========================= MAIN ==============================
# =============================================================

def generate_all():
    with open("content/surah.json", encoding="utf-8") as f:
        surah = json.load(f)

    surah_name   = surah["surah_name_en"]
    surah_number = surah["surah_number"]
    backgrounds  = list_backgrounds()
    print(f"\n[INFO] Surah: {surah_name}  ({len(surah['ayahs'])} ayahs)")
    print(f"[INFO] Backgrounds available: {len(backgrounds)}")

    for idx, ayah in enumerate(surah["ayahs"]):
        print(f"\n── Ayah {ayah['number']} ──────────────────────────────")
        # pt 3: each ayah gets the next background, cycling
        generate_ayah_videos(
            ayah,
            surah_name,
            surah_number,
            ayah_bg_index=idx,
        )

    print("\n[DONE] ALL VIDEOS GENERATED SUCCESSFULLY!")
    print("   [OUTPUT] Reels  (<=120 s)  -> videos/reels/")
    print("   [OUTPUT] YouTube (full)   -> videos/youtube/")

if __name__ == "__main__":
    generate_all()