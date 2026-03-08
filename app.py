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

# Ayah range
col1, col2 = st.sidebar.columns(2)
with col1:
    ayah_start = st.number_input(
        "Start Ayah",
        min_value=1,
        value=getattr(config, "AYAH_START", 2),
        help="First ayah to generate"
    )

with col2:
    ayah_end = st.number_input(
        "End Ayah",
        min_value=1,
        value=getattr(config, "AYAH_END", 7),
        help="Last ayah to generate"
    )

# Video settings
st.sidebar.subheader("📺 Video Settings")
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

# Target duration
st.sidebar.subheader("⏱️ Duration Settings")
reel_duration = st.sidebar.slider(
    "Target Reel Duration (seconds)",
    min_value=15,
    max_value=60,
    value=getattr(config, "REEL_TARGET_DURATION", 30),
    step=5
)

# Main content area
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
    config.REEL_TARGET_DURATION = reel_duration

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
