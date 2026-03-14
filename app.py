"""
app.py
======
Streamlit interface for the Professional Quran Video Generator
"""

import streamlit as st
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

import config
from main_PROFESSIONAL import main as generate_videos

# Surah information (name and ayah count)
surah_info = {
    1: {"surah_name_en": "Al-Fatiha", "number_of_ayahs": 7, "revelation_type": "Meccan"},
    2: {"surah_name_en": "Al-Baqarah", "number_of_ayahs": 286, "revelation_type": "Medinan"},
    3: {"surah_name_en": "Aal-E-Imran", "number_of_ayahs": 200, "revelation_type": "Medinan"},
    4: {"surah_name_en": "An-Nisa", "number_of_ayahs": 176, "revelation_type": "Medinan"},
    5: {"surah_name_en": "Al-Ma'idah", "number_of_ayahs": 120, "revelation_type": "Medinan"},
    6: {"surah_name_en": "Al-An'am", "number_of_ayahs": 165, "revelation_type": "Meccan"},
    7: {"surah_name_en": "Al-A'raf", "number_of_ayahs": 206, "revelation_type": "Meccan"},
    8: {"surah_name_en": "Al-Anfal", "number_of_ayahs": 75, "revelation_type": "Medinan"},
    9: {"surah_name_en": "At-Tawbah", "number_of_ayahs": 129, "revelation_type": "Medinan"},
    10: {"surah_name_en": "Yunus", "number_of_ayahs": 109, "revelation_type": "Meccan"},
    11: {"surah_name_en": "Hud", "number_of_ayahs": 123, "revelation_type": "Meccan"},
    12: {"surah_name_en": "Yusuf", "number_of_ayahs": 111, "revelation_type": "Meccan"},
    13: {"surah_name_en": "Ar-Ra'd", "number_of_ayahs": 43, "revelation_type": "Medinan"},
    14: {"surah_name_en": "Ibrahim", "number_of_ayahs": 52, "revelation_type": "Meccan"},
    15: {"surah_name_en": "Al-Hijr", "number_of_ayahs": 99, "revelation_type": "Meccan"},
    16: {"surah_name_en": "An-Nahl", "number_of_ayahs": 128, "revelation_type": "Meccan"},
    17: {"surah_name_en": "Al-Israa", "number_of_ayahs": 111, "revelation_type": "Meccan"},
    18: {"surah_name_en": "Al-Kahf", "number_of_ayahs": 110, "revelation_type": "Meccan"},
    19: {"surah_name_en": "Maryam", "number_of_ayahs": 98, "revelation_type": "Meccan"},
    20: {"surah_name_en": "Ta-Ha", "number_of_ayahs": 135, "revelation_type": "Meccan"},
    21: {"surah_name_en": "Al-Anbiya", "number_of_ayahs": 112, "revelation_type": "Meccan"},
    22: {"surah_name_en": "Al-Hajj", "number_of_ayahs": 78, "revelation_type": "Medinan"},
    23: {"surah_name_en": "Al-Mu'minun", "number_of_ayahs": 118, "revelation_type": "Meccan"},
    24: {"surah_name_en": "An-Nur", "number_of_ayahs": 64, "revelation_type": "Medinan"},
    25: {"surah_name_en": "Al-Furqan", "number_of_ayahs": 77, "revelation_type": "Meccan"},
    26: {"surah_name_en": "Ash-Shu'ara", "number_of_ayahs": 227, "revelation_type": "Meccan"},
    27: {"surah_name_en": "An-Naml", "number_of_ayahs": 93, "revelation_type": "Meccan"},
    28: {"surah_name_en": "Al-Qasas", "number_of_ayahs": 88, "revelation_type": "Meccan"},
    29: {"surah_name_en": "Al-Ankabut", "number_of_ayahs": 69, "revelation_type": "Meccan"},
    30: {"surah_name_en": "Ar-Rum", "number_of_ayahs": 60, "revelation_type": "Meccan"},
    31: {"surah_name_en": "Luqman", "number_of_ayahs": 34, "revelation_type": "Meccan"},
    32: {"surah_name_en": "As-Sajdah", "number_of_ayahs": 30, "revelation_type": "Meccan"},
    33: {"surah_name_en": "Al-Ahzab", "number_of_ayahs": 73, "revelation_type": "Medinan"},
    34: {"surah_name_en": "Saba", "number_of_ayahs": 54, "revelation_type": "Meccan"},
    35: {"surah_name_en": "Fatir", "number_of_ayahs": 45, "revelation_type": "Meccan"},
    36: {"surah_name_en": "Ya-Sin", "number_of_ayahs": 83, "revelation_type": "Meccan"},
    37: {"surah_name_en": "As-Saffat", "number_of_ayahs": 182, "revelation_type": "Meccan"},
    38: {"surah_name_en": "Sad", "number_of_ayahs": 88, "revelation_type": "Meccan"},
    39: {"surah_name_en": "Az-Zumar", "number_of_ayahs": 75, "revelation_type": "Meccan"},
    40: {"surah_name_en": "Ghafir", "number_of_ayahs": 85, "revelation_type": "Meccan"},
    41: {"surah_name_en": "Fussilat", "number_of_ayahs": 54, "revelation_type": "Meccan"},
    42: {"surah_name_en": "Ash-Shura", "number_of_ayahs": 53, "revelation_type": "Meccan"},
    43: {"surah_name_en": "Az-Zukhruf", "number_of_ayahs": 89, "revelation_type": "Meccan"},
    44: {"surah_name_en": "Ad-Dukhan", "number_of_ayahs": 59, "revelation_type": "Meccan"},
    45: {"surah_name_en": "Al-Jathiyah", "number_of_ayahs": 37, "revelation_type": "Meccan"},
    46: {"surah_name_en": "Al-Ahqaf", "number_of_ayahs": 35, "revelation_type": "Meccan"},
    47: {"surah_name_en": "Muhammad", "number_of_ayahs": 38, "revelation_type": "Medinan"},
    48: {"surah_name_en": "Al-Fath", "number_of_ayahs": 29, "revelation_type": "Medinan"},
    49: {"surah_name_en": "Al-Hujurat", "number_of_ayahs": 18, "revelation_type": "Medinan"},
    50: {"surah_name_en": "Qaf", "number_of_ayahs": 45, "revelation_type": "Meccan"},
    51: {"surah_name_en": "Adh-Dhariyat", "number_of_ayahs": 60, "revelation_type": "Meccan"},
    52: {"surah_name_en": "At-Tur", "number_of_ayahs": 49, "revelation_type": "Meccan"},
    53: {"surah_name_en": "An-Najm", "number_of_ayahs": 62, "revelation_type": "Meccan"},
    54: {"surah_name_en": "Al-Qamar", "number_of_ayahs": 55, "revelation_type": "Meccan"},
    55: {"surah_name_en": "Ar-Rahman", "number_of_ayahs": 78, "revelation_type": "Medinan"},
    56: {"surah_name_en": "Al-Waqi'ah", "number_of_ayahs": 96, "revelation_type": "Meccan"},
    57: {"surah_name_en": "Al-Hadid", "number_of_ayahs": 29, "revelation_type": "Medinan"},
    58: {"surah_name_en": "Al-Mujadilah", "number_of_ayahs": 22, "revelation_type": "Medinan"},
    59: {"surah_name_en": "Al-Hashr", "number_of_ayahs": 24, "revelation_type": "Medinan"},
    60: {"surah_name_en": "Al-Mumtahanah", "number_of_ayahs": 13, "revelation_type": "Medinan"},
    61: {"surah_name_en": "As-Saff", "number_of_ayahs": 14, "revelation_type": "Medinan"},
    62: {"surah_name_en": "Al-Jumu'ah", "number_of_ayahs": 11, "revelation_type": "Medinan"},
    63: {"surah_name_en": "Al-Munafiqun", "number_of_ayahs": 11, "revelation_type": "Medinan"},
    64: {"surah_name_en": "At-Taghabun", "number_of_ayahs": 18, "revelation_type": "Medinan"},
    65: {"surah_name_en": "At-Talaq", "number_of_ayahs": 12, "revelation_type": "Medinan"},
    66: {"surah_name_en": "At-Tahrim", "number_of_ayahs": 12, "revelation_type": "Medinan"},
    67: {"surah_name_en": "Al-Mulk", "number_of_ayahs": 30, "revelation_type": "Meccan"},
    68: {"surah_name_en": "Al-Qalam", "number_of_ayahs": 52, "revelation_type": "Meccan"},
    69: {"surah_name_en": "Al-Haqqah", "number_of_ayahs": 52, "revelation_type": "Meccan"},
    70: {"surah_name_en": "Al-Ma'arij", "number_of_ayahs": 44, "revelation_type": "Meccan"},
    71: {"surah_name_en": "Nuh", "number_of_ayahs": 28, "revelation_type": "Meccan"},
    72: {"surah_name_en": "Al-Jinn", "number_of_ayahs": 28, "revelation_type": "Meccan"},
    73: {"surah_name_en": "Al-Muzzammil", "number_of_ayahs": 20, "revelation_type": "Meccan"},
    74: {"surah_name_en": "Al-Muddaththir", "number_of_ayahs": 56, "revelation_type": "Meccan"},
    75: {"surah_name_en": "Al-Qiyamah", "number_of_ayahs": 40, "revelation_type": "Meccan"},
    76: {"surah_name_en": "Al-Insan", "number_of_ayahs": 31, "revelation_type": "Medinan"},
    77: {"surah_name_en": "Al-Mursalat", "number_of_ayahs": 50, "revelation_type": "Meccan"},
    78: {"surah_name_en": "An-Naba", "number_of_ayahs": 40, "revelation_type": "Meccan"},
    79: {"surah_name_en": "An-Nazi'at", "number_of_ayahs": 46, "revelation_type": "Meccan"},
    80: {"surah_name_en": "Abasa", "number_of_ayahs": 42, "revelation_type": "Meccan"},
    81: {"surah_name_en": "At-Takwir", "number_of_ayahs": 29, "revelation_type": "Meccan"},
    82: {"surah_name_en": "Al-Infitar", "number_of_ayahs": 19, "revelation_type": "Meccan"},
    83: {"surah_name_en": "Al-Mutaffifin", "number_of_ayahs": 36, "revelation_type": "Meccan"},
    84: {"surah_name_en": "Al-Inshiqaq", "number_of_ayahs": 25, "revelation_type": "Meccan"},
    85: {"surah_name_en": "Al-Buruj", "number_of_ayahs": 22, "revelation_type": "Meccan"},
    86: {"surah_name_en": "At-Tariq", "number_of_ayahs": 17, "revelation_type": "Meccan"},
    87: {"surah_name_en": "Al-A'la", "number_of_ayahs": 19, "revelation_type": "Meccan"},
    88: {"surah_name_en": "Al-Ghashiyah", "number_of_ayahs": 26, "revelation_type": "Meccan"},
    89: {"surah_name_en": "Al-Fajr", "number_of_ayahs": 30, "revelation_type": "Meccan"},
    90: {"surah_name_en": "Al-Balad", "number_of_ayahs": 20, "revelation_type": "Meccan"},
    91: {"surah_name_en": "Ash-Shams", "number_of_ayahs": 15, "revelation_type": "Meccan"},
    92: {"surah_name_en": "Al-Layl", "number_of_ayahs": 21, "revelation_type": "Meccan"},
    93: {"surah_name_en": "Ad-Duhaa", "number_of_ayahs": 11, "revelation_type": "Meccan"},
    94: {"surah_name_en": "Ash-Sharh", "number_of_ayahs": 8, "revelation_type": "Meccan"},
    95: {"surah_name_en": "At-Tin", "number_of_ayahs": 8, "revelation_type": "Meccan"},
    96: {"surah_name_en": "Al-Alaq", "number_of_ayahs": 19, "revelation_type": "Meccan"},
    97: {"surah_name_en": "Al-Qadr", "number_of_ayahs": 5, "revelation_type": "Meccan"},
    98: {"surah_name_en": "Al-Bayyinah", "number_of_ayahs": 8, "revelation_type": "Medinan"},
    99: {"surah_name_en": "Az-Zalzalah", "number_of_ayahs": 8, "revelation_type": "Medinan"},
    100: {"surah_name_en": "Al-Adiyat", "number_of_ayahs": 11, "revelation_type": "Meccan"},
    101: {"surah_name_en": "Al-Qari'ah", "number_of_ayahs": 11, "revelation_type": "Meccan"},
    102: {"surah_name_en": "At-Takathur", "number_of_ayahs": 8, "revelation_type": "Meccan"},
    103: {"surah_name_en": "Al-Asr", "number_of_ayahs": 3, "revelation_type": "Meccan"},
    104: {"surah_name_en": "Al-Humazah", "number_of_ayahs": 9, "revelation_type": "Meccan"},
    105: {"surah_name_en": "Al-Fil", "number_of_ayahs": 5, "revelation_type": "Meccan"},
    106: {"surah_name_en": "Quraysh", "number_of_ayahs": 4, "revelation_type": "Meccan"},
    107: {"surah_name_en": "Al-Ma'un", "number_of_ayahs": 7, "revelation_type": "Meccan"},
    108: {"surah_name_en": "Al-Kawthar", "number_of_ayahs": 3, "revelation_type": "Meccan"},
    109: {"surah_name_en": "Al-Kafirun", "number_of_ayahs": 6, "revelation_type": "Meccan"},
    110: {"surah_name_en": "An-Nasr", "number_of_ayahs": 3, "revelation_type": "Medinan"},
    111: {"surah_name_en": "Al-Masad", "number_of_ayahs": 5, "revelation_type": "Meccan"},
    112: {"surah_name_en": "Al-Ikhlas", "number_of_ayahs": 4, "revelation_type": "Meccan"},
    113: {"surah_name_en": "Al-Falaq", "number_of_ayahs": 5, "revelation_type": "Meccan"},
    114: {"surah_name_en": "An-Nas", "number_of_ayahs": 6, "revelation_type": "Meccan"},
}

st.set_page_config(
    page_title="📖 Quran Video Generator",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📖 Professional Quran Video Generator")
st.markdown("""
Generate professional Quran recitation videos with synchronized Arabic and English text.
""")

# Sidebar configuration
st.sidebar.header("⚙️ Settings")

col1, col2 = st.sidebar.columns(2)
with col1:
    surah_num = st.number_input(
        "Surah Number",
        min_value=1,
        max_value=114,
        value=getattr(config, "SURAH_NUMBER", 17),
        help="Select which Surah to generate"
    )

with col2:
    reciter = st.selectbox(
        "Reciter",
        ["alafasy", "basit", "husary"],
        index=0,
        help="Choose the Quranic reciter"
    )

# Display surah info
if surah_num in surah_info:
    info = surah_info[surah_num]
    st.sidebar.info(f"📖 {info['surah_name_en']}\n\nTotal Ayahs: {info['number_of_ayahs']}\nType: {info['revelation_type']}")

# Ayah range
col1, col2 = st.sidebar.columns(2)
with col1:
    ayah_start = st.number_input(
        "Start Ayah",
        min_value=1,
        max_value=info['number_of_ayahs'] if surah_num in surah_info else 286,
        value=getattr(config, "AYAH_START", 1),
        help="First ayah to generate"
    )

with col2:
    ayah_end = st.number_input(
        "End Ayah",
        min_value=1,
        max_value=info['number_of_ayahs'] if surah_num in surah_info else 286,
        value=min(getattr(config, "AYAH_END", 7), info['number_of_ayahs'] if surah_num in surah_info else 7),
        help="Last ayah to generate"
    )

# Background settings
st.sidebar.subheader("🖼️ Background")
uploaded_bg = st.sidebar.file_uploader(
    "Upload Custom Background",
    type=["png", "jpg", "jpeg"],
    help="Upload a custom background image"
)

if uploaded_bg:
    # Save uploaded image
    bg_dir = "custom_backgrounds"
    os.makedirs(bg_dir, exist_ok=True)
    bg_path = os.path.join(bg_dir, uploaded_bg.name)
    with open(bg_path, "wb") as f:
        f.write(uploaded_bg.getbuffer())
    st.sidebar.success(f"Background saved: {uploaded_bg.name}")
    custom_bg_path = bg_path
else:
    custom_bg_path = None
col1, col2 = st.sidebar.columns(2)
with col1:
    do_phone = st.checkbox(
        "📱 Phone Format (9:16)",
        value=getattr(config, "GENERATE_PHONE_FORMAT", True)
    )

with col2:
    do_tv = st.checkbox(
        "🖥️ TV Format (16:9)",
        value=getattr(config, "GENERATE_TV_FORMAT", False)
    )

quality = st.sidebar.radio(
    "Video Quality",
    ["high", "medium", "low"],
    index=0,
    help="Higher quality = larger files, longer processing"
)

fast_mode = st.sidebar.checkbox(
    "⚡ Fast Mode",
    value=getattr(config, "FAST_MODE", False),
    help="Faster preview mode with lower quality"
)

# Font positions
st.sidebar.subheader("📍 Text Positions")
arabic_y = st.sidebar.slider(
    "Arabic Y Position",
    min_value=400,
    max_value=1400,
    value=getattr(config, "ARABIC_CENTER_Y", 1200),
    help="Vertical position of Arabic text"
)
english_y = st.sidebar.slider(
    "English Y Start",
    min_value=1000,
    max_value=1700,
    value=getattr(config, "ENGLISH_Y_START", 1575),
    help="Starting vertical position of English text"
)

# Font colors
st.sidebar.subheader("🎨 Font Colors")
col1, col2 = st.sidebar.columns(2)
with col1:
    arabic_color = st.color_picker(
        "Arabic Text",
        value="#FFFFFF",
        help="Color for Arabic text"
    )
with col2:
    english_color = st.color_picker(
        "English Text",
        value="#FFFFFF",
        help="Color for English text"
    )

# Page settings
st.sidebar.subheader("📄 Page Settings")
words_per_page = st.sidebar.slider(
    "Words Per Page",
    min_value=10,
    max_value=50,
    value=getattr(config, "WORDS_PER_PAGE", 25),
    step=1,
    help="Number of words to display on a single page (20-30 recommended)"
)

# Duration settings
st.sidebar.subheader("⏱️ Duration Settings")
reel_min = st.sidebar.number_input(
    "Min Reel Duration (sec)",
    min_value=10,
    max_value=30,
    value=getattr(config, "REEL_MIN_DURATION", 15)
)
reel_max = st.sidebar.number_input(
    "Max Reel Duration (sec)",
    min_value=30,
    max_value=120,
    value=getattr(config, "REEL_MAX_DURATION", 60)
)
reel_target = st.sidebar.slider(
    "Target Reel Duration (seconds)",
    min_value=reel_min,
    max_value=reel_max,
    value=getattr(config, "REEL_TARGET_DURATION", 30),
    step=5
)
st.divider()

# Display current settings
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Surah", surah_num)
with col2:
    st.metric("Ayahs", f"{ayah_start} - {ayah_end}")
with col3:
    st.metric("Format", "Phone + TV" if (do_phone and do_tv) else ("Phone" if do_phone else "TV"))

st.divider()

# Preview button
if st.button("👀 Preview Layout", use_container_width=True):
    st.info("Preview feature coming soon - will show sample frame layout")

st.divider()

# Generate button
if st.button("🚀 Generate Videos", use_container_width=True, type="primary"):
    # Update config values
    config.SURAH_NUMBER = surah_num
    config.PREFERRED_RECITER = reciter
    config.AYAH_START = ayah_start
    config.AYAH_END = ayah_end
    config.GENERATE_PHONE_FORMAT = do_phone
    config.GENERATE_TV_FORMAT = do_tv
    config.VIDEO_QUALITY = quality
    config.FAST_MODE = fast_mode
    config.REEL_MIN_DURATION = reel_min
    config.REEL_MAX_DURATION = reel_max
    config.REEL_TARGET_DURATION = reel_target
    config.CUSTOM_BACKGROUND_PATH = custom_bg_path
    config.ARABIC_TEXT_COLOR = tuple(int(arabic_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (255,)
    config.ENGLISH_TEXT_COLOR = tuple(int(english_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (255,)
    config.ARABIC_CENTER_Y = arabic_y
    config.ENGLISH_Y_START = english_y
    config.WORDS_PER_PAGE = words_per_page

    with st.spinner("🎬 Generating videos... This may take a few minutes..."):
        try:
            generate_videos()
            st.success("✅ Videos generated successfully!")
            st.balloons()
            
            # Show output locations
            st.info(f"""
            📁 Output locations:
            - **Reels**: `videos/reels/`
            - **YouTube**: `videos/youtube/`
            """)
        except Exception as e:
            st.error(f"❌ Error generating videos: {str(e)}")

st.divider()
st.markdown("""
### 📚 Help
- **Surah**: Select any Surah from 1-114
- **Ayahs**: Choose which ayahs to generate
- **Bismillah**: Traditional Islamic practice to recite Bismillah before each ayah
- **Formats**: Phone format is ideal for social media reels, TV format for YouTube
- **Quality**: Higher quality produces larger files but better visual output
""")
