"""
Quran Video Generator - Web Interface
======================================
Beautiful, simple UI for non-technical users.

Run with:
    streamlit run app.py
"""

import streamlit as st
import os
import json
import random
from pathlib import Path
import requests
from PIL import Image
import subprocess
import config
from audio_engine import download_audio

# Must be first Streamlit command
st.set_page_config(
    page_title="Quran Video Generator",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'ayah_start_val' not in st.session_state:
    st.session_state.ayah_start_val = 1
if 'ayah_end_val' not in st.session_state:
    st.session_state.ayah_end_val = 10

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def get_surah_list():
    surahs = [
        "Al-Fatihah", "Al-Baqarah", "Aal-E-Imran", "An-Nisa", "Al-Ma'idah",
        "Al-An'am", "Al-A'raf", "Al-Anfal", "At-Tawbah", "Yunus",
        "Hud", "Yusuf", "Ar-Ra'd", "Ibrahim", "Al-Hijr",
        "An-Nahl", "Al-Isra", "Al-Kahf", "Maryam", "Ta-Ha",
        "Al-Anbiya", "Al-Hajj", "Al-Mu'minun", "An-Nur", "Al-Furqan",
        "Ash-Shu'ara", "An-Naml", "Al-Qasas", "Al-Ankabut", "Ar-Rum",
        "Luqman", "As-Sajdah", "Al-Ahzab", "Saba", "Fatir",
        "Ya-Sin", "As-Saffat", "Sad", "Az-Zumar", "Ghafir",
        "Fussilat", "Ash-Shura", "Az-Zukhruf", "Ad-Dukhan", "Al-Jathiyah",
        "Al-Ahqaf", "Muhammad", "Al-Fath", "Al-Hujurat", "Qaf",
        "Adh-Dhariyat", "At-Tur", "An-Najm", "Al-Qamar", "Ar-Rahman",
        "Al-Waqi'ah", "Al-Hadid", "Al-Mujadila", "Al-Hashr", "Al-Mumtahanah",
        "As-Saff", "Al-Jumu'ah", "Al-Munafiqun", "At-Taghabun", "At-Talaq",
        "At-Tahrim", "Al-Mulk", "Al-Qalam", "Al-Haqqah", "Al-Ma'arij",
        "Nuh", "Al-Jinn", "Al-Muzzammil", "Al-Muddaththir", "Al-Qiyamah",
        "Al-Insan", "Al-Mursalat", "An-Naba", "An-Nazi'at", "Abasa",
        "At-Takwir", "Al-Infitar", "Al-Mutaffifin", "Al-Inshiqaq", "Al-Buruj",
        "At-Tariq", "Al-A'la", "Al-Ghashiyah", "Al-Fajr", "Al-Balad",
        "Ash-Shams", "Al-Layl", "Ad-Duhaa", "Ash-Sharh", "At-Tin",
        "Al-Alaq", "Al-Qadr", "Al-Bayyinah", "Az-Zalzalah", "Al-Adiyat",
        "Al-Qari'ah", "At-Takathur", "Al-Asr", "Al-Humazah", "Al-Fil",
        "Quraysh", "Al-Ma'un", "Al-Kawthar", "Al-Kafirun", "An-Nasr",
        "Al-Masad", "Al-Ikhlas", "Al-Falaq", "An-Nas"
    ]
    return [(i+1, name) for i, name in enumerate(surahs)]


def rgb_to_tuple(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4)) + (255,)


def save_settings(settings):
    # include optional preview/resolution settings (width, height, fps)
    width = settings.get('width', 1080)
    height = settings.get('height', 1920)
    fps = settings.get('fps', 30)

    content = f'''"""
QURAN VIDEO GENERATOR - AUTO-GENERATED SETTINGS
"""

SURAH_NUMBER = {settings['surah_number']}
PREFERRED_RECITER = "{settings['reciter']}"
AYAH_START = {settings['ayah_start']}
AYAH_END = {settings['ayah_end']}
FAST_MODE = {settings.get('fast_mode', False)}

ARABIC_CENTER_Y = {settings['arabic_y']}
ARABIC_X_MARGIN = {settings['arabic_margin']}
ARABIC_LINE_GAP = {settings['arabic_line_gap']}
ARABIC_WORD_GAP = {settings['arabic_word_gap']}

ENGLISH_Y_START = {settings['english_y']}
ENGLISH_X_MARGIN = {settings['english_margin']}
ENGLISH_LINE_GAP = {settings['english_line_gap']}
REFERENCE_Y = {settings['reference_y']}

ARABIC_FONT_SIZE = {settings['arabic_font_size']}
ENGLISH_FONT_SIZE = {settings['english_font_size']}
REFERENCE_FONT_SIZE = {settings['reference_font_size']}

AUTO_CONTRAST = {settings['auto_contrast']}
ARABIC_DEFAULT_COLOR = {settings['arabic_default_color']}
ENGLISH_DEFAULT_COLOR = {settings['english_default_color']}
REFERENCE_COLOR = {settings['reference_color']}
ARABIC_HIGHLIGHT_COLOR = {settings['arabic_highlight_color']}
ENGLISH_HIGHLIGHT_COLOR = {settings['english_highlight_color']}
TEXT_STROKE_WIDTH = {settings['text_stroke_width']}

LOGO_MAX_W = {settings['logo_width']}
LOGO_MARGIN_X = {settings['logo_margin_x']}
LOGO_MARGIN_Y = {settings['logo_margin_y']}

REEL_TARGET_SEC = {settings['reel_target']}
REEL_MIN_SEC = {settings['reel_min']}
REEL_MAX_SEC = {settings['reel_max']}
YOUTUBE_TARGET_MIN = {settings['youtube_target_min']}
YOUTUBE_MIN_SEC = {settings['youtube_min']}
YOUTUBE_MAX_SEC = {settings['youtube_max']}
HOLD_AT_END = {settings['hold_duration']}

GENERATE_PHONE_FORMAT = {settings['generate_phone']}
GENERATE_TV_FORMAT = {settings['generate_tv']}

FPS = {fps}
BG_CHANGE_INTERVAL = {settings['bg_change_interval']}

ARABIC_FONT_PATH = "fonts/Amiri-Bold.ttf"
ARABIC_FONT_FALLBACK = "fonts/Amiri-Regular.ttf"
ENGLISH_FONT_PATH = "fonts/NotoSans-SemiBold.ttf"
ENGLISH_FONT_FALLBACK = "fonts/dejavu-sans.extralight.ttf"
REFERENCE_FONT_PATH = "fonts/NotoSans-Regular.ttf"

AUDIO_CACHE_DIR = "audio/recitations"
REEL_OUTPUT_DIR = "videos/reels"
YOUTUBE_OUTPUT_DIR = "videos/youtube"
IMAGES_DIR = "images"
CONTENT_FILE = "content/surah.json"

AUDIO_SR = 22050
ONSET_DELTA = 0.07
MIN_WORD_DURATION = 0.12
MIN_ONSET_GAP = 0.06
ENERGY_THRESHOLD = 0.018

WIDTH = {width}
HEIGHT = {height}
'''
    with open("SETTINGS.py", "w", encoding="utf-8") as f:
        f.write(content)


# Main UI
st.markdown('<div class="main-header"><h1>📖 Quran Video Generator</h1><p>Create beautiful animated Quran videos</p></div>', unsafe_allow_html=True)

if 'generated' not in st.session_state:
    st.session_state.generated = False

# Sidebar
with st.sidebar:
    st.header("⚙️ Video Settings")
    
    st.subheader("📚 Select Surah")
    selection_mode = st.radio("Choose by:", ["Surah Name", "Surah Number", "Random"], horizontal=True)
    
    if selection_mode == "Surah Name":
        surahs = get_surah_list()
        surah_choice = st.selectbox("Surah:", surahs, format_func=lambda x: f"{x[0]}. {x[1]}")
        surah_number = surah_choice[0]
    elif selection_mode == "Surah Number":
        surah_number = st.number_input("Surah Number:", 1, 114, 100)
    else:
        surah_number = random.randint(1, 114)
        st.info(f"🎲 Random: Surah #{surah_number}")
    
    # Determine max ayahs for the selected surah (use local content if available)
    surah_max_ayahs = 286
    try:
        with open("content/surah.json", encoding="utf-8") as f:
            sd = json.load(f)
            if sd.get("surah_number") == surah_number:
                surah_max_ayahs = sd.get("number_of_ayahs", surah_max_ayahs)
    except Exception:
        pass

    # Ensure session_state defaults are within bounds to avoid Streamlit widget errors
    try:
        ss_start = int(st.session_state.get('ayah_start_val', 1))
    except Exception:
        ss_start = 1
    try:
        ss_end = int(st.session_state.get('ayah_end_val', 10))
    except Exception:
        ss_end = 10

    ss_start = max(1, min(ss_start, surah_max_ayahs))
    ss_end = max(ss_start, min(ss_end, surah_max_ayahs))
    st.session_state['ayah_start_val'] = ss_start
    st.session_state['ayah_end_val'] = ss_end

    st.subheader("🎙️ Reciter")
    reciter = st.selectbox("Reciter:", ["alafasy", "basit", "husary"],
                          format_func=lambda x: {"alafasy": "Alafasy", "basit": "Abdul Basit", "husary": "Husary"}[x])
    
    st.markdown("---")
    st.subheader("📱 Video Formats")
    generate_phone = st.checkbox("Phone/Reels (9:16)", value=True)
    generate_tv = st.checkbox("TV/YouTube (16:9)", value=True)
    
    st.markdown("---")
    st.subheader("⚡ Generation Speed")
    fast_mode = st.checkbox("Fast Mode (lower quality, faster generation)", value=False)
    reel_target = st.slider("Reel (seconds):", 10, 30, 16)
    youtube_target_min = st.slider("YouTube (minutes):", 2.0, 10.0, 4.5, 0.5)
    hold_duration = st.slider("End pause (seconds):", 0.5, 5.0, 1.5, 0.5)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🎨 Style", "🖼️ Backgrounds", "📐 Layout", "▶️ Generate"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔤 Font Sizes")
        arabic_font_size = st.slider("Arabic:", 40, 120, 72)
        english_font_size = st.slider("English:", 20, 60, 36)
        reference_font_size = st.slider("Reference:", 16, 40, 29)
        text_stroke_width = st.slider("Text stroke:", 0, 5, 2)
    
    with col2:
        st.subheader("🎨 Colors")
        auto_contrast = st.checkbox("Auto-adapt", value=True)
        if not auto_contrast:
            arabic_default = st.color_picker("Arabic:", "#FFFFFF")
            english_default = st.color_picker("English:", "#FFFFFF")
            reference = st.color_picker("Reference:", "#DCDCDC")
        else:
            arabic_default = english_default = "#FFFFFF"
            reference = "#DCDCDC"
        arabic_highlight = st.color_picker("Arabic highlight:", "#DC2814")
        english_highlight = st.color_picker("English highlight:", "#DC2814")

with tab2:
    st.header("Background Images")
    os.makedirs("images", exist_ok=True)
    
    uploaded_files = st.file_uploader("Upload images:", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    if uploaded_files:
        for uploaded_file in uploaded_files:
            img = Image.open(uploaded_file)
            filename = f"background{random.randint(1000, 9999)}.jpg"
            img.save(os.path.join("images", filename))
        st.success(f"✅ Uploaded {len(uploaded_files)} images")
    
    bg_files = list(Path("images").glob("background*.jpg")) + list(Path("images").glob("background*.png"))
    if bg_files:
        st.info(f"📊 {len(bg_files)} backgrounds available")

with tab3:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📝 Arabic")
        arabic_y = st.slider("Vertical center:", 400, 1200, 800, 10)
        arabic_margin = st.slider("Side margins:", 40, 200, 89, 5)
        arabic_line_gap = st.slider("Line spacing:", 20, 100, 52, 4)
        arabic_word_gap = st.slider("Word spacing:", 10, 60, 28, 2)
    with col2:
        st.subheader("🔤 English")
        english_y = st.slider("Start position:", 800, 1600, 1050, 10)
        english_margin = st.slider("Side margins:", 40, 200, 95, 5)
        english_line_gap = st.slider("Line spacing:", 20, 80, 44, 4)
    
    reference_y = st.slider("Reference position:", 1400, 1880, 1650, 10)
    col1, col2, col3 = st.columns(3)
    with col1:
        logo_width = st.number_input("Logo width:", 80, 300, 160, 10)
    with col2:
        logo_margin_x = st.number_input("From right:", 20, 150, 48, 5)
    with col3:
        logo_margin_y = st.number_input("From top:", 20, 150, 48, 5)
    
    st.markdown("---")
    
    st.subheader("🎬 Video Playback")
    bg_change_interval = st.slider("Background change (seconds):", 0.5, 10.0, 2.0, 0.5)
    
    st.markdown("---")
    
    st.subheader("📖 Ayah Range")
    st.caption("Quick select or enter custom range")
    
    # Quick selection buttons
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("First 5", use_container_width=True):
            st.session_state.ayah_start_val = 1
            st.session_state.ayah_end_val = 5
    with col2:
        if st.button("First 10", use_container_width=True):
            st.session_state.ayah_start_val = 1
            st.session_state.ayah_end_val = 10
    with col3:
        if st.button("First 20", use_container_width=True):
            st.session_state.ayah_start_val = 1
            st.session_state.ayah_end_val = 20
    with col4:
        if st.button("Full Surah", use_container_width=True):
            st.session_state.ayah_start_val = 1
            st.session_state.ayah_end_val = surah_max_ayahs  # Max ayahs for selected surah
    
    # Manual range input
    col1, col2 = st.columns(2)
    with col1:
        ayah_start = st.number_input(
            "Start Ayah:", 
            value=st.session_state.get('ayah_start_val', 1), 
            min_value=1, 
            max_value=surah_max_ayahs,
            step=1
        )
    with col2:
        ayah_end = st.number_input(
            "End Ayah:", 
            value=st.session_state.get('ayah_end_val', 10), 
            min_value=1, 
            max_value=surah_max_ayahs,
            step=1
        )

with tab4:
    st.header("Generate Videos")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("🎬 GENERATE VIDEOS", type="primary", use_container_width=True):
            if not generate_phone and not generate_tv:
                st.error("❌ Select at least one format")
            elif not bg_files:
                st.error("❌ Upload at least one background image")
            elif ayah_start > ayah_end:
                st.error("❌ Start Ayah must be <= End Ayah")
            else:
                settings = {
                    'surah_number': surah_number, 'reciter': reciter,
                    'ayah_start': int(ayah_start), 'ayah_end': int(ayah_end),
                    'fast_mode': fast_mode,
                    'arabic_y': arabic_y, 'arabic_margin': arabic_margin,
                    'arabic_line_gap': arabic_line_gap, 'arabic_word_gap': arabic_word_gap,
                    'english_y': english_y, 'english_margin': english_margin,
                    'english_line_gap': english_line_gap, 'reference_y': reference_y,
                    'arabic_font_size': arabic_font_size, 'english_font_size': english_font_size,
                    'reference_font_size': reference_font_size, 'auto_contrast': auto_contrast,
                    'arabic_default_color': rgb_to_tuple(arabic_default),
                    'english_default_color': rgb_to_tuple(english_default),
                    'reference_color': rgb_to_tuple(reference),
                    'arabic_highlight_color': rgb_to_tuple(arabic_highlight),
                    'english_highlight_color': rgb_to_tuple(english_highlight),
                    'text_stroke_width': text_stroke_width,
                    'logo_width': logo_width, 'logo_margin_x': logo_margin_x,
                    'logo_margin_y': logo_margin_y,
                    'reel_target': reel_target,
                    'reel_min': max(10, reel_target - 2),
                    'reel_max': min(30, reel_target + 2),
                    'youtube_target_min': youtube_target_min,
                    'youtube_min': int(youtube_target_min * 60 - 30),
                    'youtube_max': int(youtube_target_min * 60 + 30),
                    'hold_duration': hold_duration,
                    'generate_phone': generate_phone,
                    'generate_tv': generate_tv,
                    'bg_change_interval': int(bg_change_interval),
                }
                
                save_settings(settings)

                # Pre-cache audio for selected ayah range to speed generation
                # Defensive clamp: ensure requested ayah range doesn't exceed surah length
                try:
                    with open("content/surah.json", encoding="utf-8") as f:
                        sd = json.load(f)
                        if sd.get("surah_number") == surah_number:
                            max_ayahs = sd.get("number_of_ayahs", None)
                            if max_ayahs is not None:
                                ayah_start = max(1, min(int(ayah_start), max_ayahs))
                                ayah_end = max(ayah_start, min(int(ayah_end), max_ayahs))
                except Exception:
                    pass
                total_ayahs = int(ayah_end) - int(ayah_start) + 1
                precache_container = st.container()
                with precache_container:
                    pre_progress = st.progress(0)
                    pre_status = st.empty()
                    cached_count = 0
                    try:
                        for i, ay in enumerate(range(int(ayah_start), int(ayah_end) + 1), start=1):
                            pre_status.info(f"Downloading audio for ayah {ay} ({i}/{total_ayahs})...")
                            path = download_audio(surah_number, ay)
                            if path:
                                cached_count += 1
                            pre_progress.progress(i / max(total_ayahs, 1))
                        pre_status.success(f"Audio pre-cache complete: {cached_count}/{total_ayahs} files available")
                    except Exception as e:
                        pre_status.error(f"Audio pre-cache error: {e}")

                # Create containers for real-time updates
                progress_container = st.container()
                status_container = st.container()
                log_container = st.container()
                
                with progress_container:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    percent_text = st.empty()
                
                total_ayahs = int(ayah_end) - int(ayah_start) + 1
                
                try:
                    status_text.info(f"Starting video generation for {total_ayahs} ayahs...")
                    percent_text.write("")
                    
                    # Real-time subprocess streaming
                    process = subprocess.Popen(
                        ["python", "main.py"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        bufsize=1
                    )
                    
                    progress_count = 0
                    output_lines = []
                    
                    # Read output line by line in real-time
                    for line in iter(process.stdout.readline, ''):
                        if not line:
                            break
                        
                        output_lines.append(line)
                        
                        # Look for [PROGRESS] messages
                        if "[PROGRESS]" in line:
                            progress_count += 1
                            progress = min(progress_count / max(total_ayahs * 1.5, 5), 1.0)
                            progress_bar.progress(progress)
                            percent_text.write(f"**{int(progress*100)}% Complete** • {line.replace('[PROGRESS]', '').strip()}")
                            status_text.info(f"Processing... {line.replace('[PROGRESS]', '').strip()}")
                    
                    # Wait for process to complete
                    returncode = process.wait()
                    
                    # Get any remaining stderr
                    stderr = process.stderr.read()
                    
                    # Show completion
                    progress_bar.progress(1.0)
                    
                    if returncode == 0:
                        percent_text.write("**✅ 100% Complete**")
                        status_text.success("✅ All videos generated successfully!")
                        st.session_state.generated = True
                        with log_container.expander("📄 Generation Log"):
                            st.code('\n'.join(output_lines))
                    else:
                        status_text.error(f"❌ Generation failed (Exit code: {returncode})")
                        with log_container.expander("❌ Error Details"):
                            st.code("STDOUT:\n" + '\n'.join(output_lines))
                            if stderr:
                                st.code("STDERR:\n" + stderr)
                            
                except Exception as e:
                    status_text.error(f"❌ Error: {e}")
    
    with col2:
        if st.button("📂 Open Output", help="Open videos folder"):
            import webbrowser
            import pathlib
            output_dir = pathlib.Path(config.REEL_OUTPUT_DIR).absolute()
            webbrowser.open(f'file:///{output_dir}')
