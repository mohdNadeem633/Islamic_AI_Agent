"""
Quran Video Generator - Production Web Interface
================================================
Calls FastAPI backend for video generation.

Run with:
    streamlit run app_v2.py
    
(API server should be running: python -m uvicorn api.main_api:app --reload)
"""

import streamlit as st
import requests
import os
from pathlib import Path

API_BASE_URL = os.getenv("API_URL", "http://localhost:8000")

# Must be first Streamlit command
st.set_page_config(
    page_title="Quran Video Generator",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    .success-box {
        padding: 1rem;
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        color: #155724;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def get_surah_list():
    """Fetch surah list from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/surahs", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return [(s["number"], s["name"]) for s in data["surahs"]]
    except Exception as e:
        st.error(f"Failed to fetch surahs: {e}")
    return []

def generate_videos_api(request_data: dict) -> dict:
    """Call API to generate videos"""
    try:
        response = requests.post(f"{API_BASE_URL}/generate", json=request_data, timeout=3600)
        return response.json()
    except Exception as e:
        return {"status": "error", "message": "API call failed", "error": str(e)}

def get_video_outputs() -> dict:
    """Fetch list of generated video files"""
    try:
        reels = requests.get(f"{API_BASE_URL}/output/reels", timeout=5).json()
        youtube = requests.get(f"{API_BASE_URL}/output/youtube", timeout=5).json()
        return {"reels": reels, "youtube": youtube}
    except Exception as e:
        return {"reels": {"reels": []}, "youtube": {"phone": [], "tv": []}}

# Main UI
st.markdown('<div class="main-header"><h1>📖 Quran Video Generator</h1><p>Create beautiful animated Quran videos</p></div>', unsafe_allow_html=True)

# Initialize session state
if 'generated' not in st.session_state:
    st.session_state.generated = False

# Sidebar
with st.sidebar:
    st.header("⚙️ Video Settings")
    
    st.subheader("📚 Select Surah")
    surahs = get_surah_list()
    if surahs:
        surah_choice = st.selectbox("Surah:", surahs, format_func=lambda x: f"{x[0]}. {x[1]}")
        surah_number = surah_choice[0]
    else:
        st.error("Could not load surahs. Is the API running?")
        st.stop()
    
    st.subheader("🎙️ Reciter")
    reciter = st.selectbox("Reciter:", ["alafasy", "basit", "husary"],
                          format_func=lambda x: {"alafasy": "Alafasy", "basit": "Abdul Basit", "husary": "Husary"}[x])
    
    st.markdown("---")
    st.subheader("📱 Video Formats")
    generate_phone = st.checkbox("Phone/Reels (9:16)", value=True)
    generate_tv = st.checkbox("TV/YouTube (16:9)", value=False)
    
    st.markdown("---")
    st.subheader("⚡ Speed Mode")
    fast_mode = st.checkbox("Fast Mode (lower quality, faster)", value=False)
    
    st.markdown("---")
    st.subheader("📖 Ayah Range")
    col1, col2 = st.columns(2)
    with col1:
        ayah_start = st.number_input("Start Ayah:", value=1, min_value=1)
    with col2:
        ayah_end = st.number_input("End Ayah:", value=10, min_value=1)

# Main content
st.header("Generate Videos")

col1, col2 = st.columns([3, 1])
with col1:
    if st.button("🎬 GENERATE VIDEOS", type="primary", use_container_width=True):
        if not generate_phone and not generate_tv:
            st.error("❌ Select at least one format")
        elif ayah_start > ayah_end:
            st.error("❌ Start Ayah must be <= End Ayah")
        else:
            # Prepare request
            request_data = {
                "surah_number": surah_number,
                "reciter": reciter,
                "ayah_start": int(ayah_start),
                "ayah_end": int(ayah_end),
                "fast_mode": fast_mode,
                "generate_phone": generate_phone,
                "generate_tv": generate_tv,
            }
            
            # Show progress
            progress_placeholder = st.empty()
            status_placeholder = st.empty()
            
            with progress_placeholder.container():
                progress_bar = st.progress(0)
                status_placeholder.info("🔄 Sending request to server...")
            
            # Call API
            result = generate_videos_api(request_data)
            
            if result.get("status") == "success":
                progress_bar.progress(1.0)
                st.success("✅ Videos generated successfully!")
                
                if result.get("files_output"):
                    files = result["files_output"]
                    with st.expander("📁 Generated Files"):
                        if files.get("phone_reels"):
                            st.write("**Phone Reels:**")
                            for f in files["phone_reels"]:
                                st.write(f"  • {f}")
                        if files.get("youtube_phone"):
                            st.write("**YouTube Phone:**")
                            for f in files["youtube_phone"]:
                                st.write(f"  • {f}")
                        if files.get("youtube_tv"):
                            st.write("**YouTube TV:**")
                            for f in files["youtube_tv"]:
                                st.write(f"  • {f}")
            else:
                st.error(f"❌ Generation failed: {result.get('error', result.get('message'))}")

with col2:
    if st.button("🎬 API Docs", help="Open API documentation"):
        st.info(f"API Documentation: [Swagger UI]({API_BASE_URL}/docs)")

# Show generated files
st.markdown("---")
st.header("📺 Generated Videos")

tabs = st.tabs(["All Reels", "YouTube Phone", "YouTube TV"])

with tabs[0]:
    outputs = get_video_outputs()
    reels = outputs.get("reels", {}).get("reels", [])
    if reels:
        st.success(f"✅ {len(reels)} reel files Found")
        for reel in reels[:10]:  # Show first 10
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"📹 {reel}")
            with col2:
                if st.button("▶️ Play", key=f"reel_{reel}"):
                    st.write(f"[Open: videos/reels/{reel}]()")
    else:
        st.info("No reel videos generated yet")

with tabs[1]:
    outputs = get_video_outputs()
    yt_phone = outputs.get("youtube", {}).get("phone", [])
    if yt_phone:
        st.success(f"✅ {len(yt_phone)} phone videos found")
        for vid in yt_phone[:10]:
            st.write(f"📹 {vid}")
    else:
        st.info("No YouTube phone videos generated yet")

with tabs[2]:
    outputs = get_video_outputs()
    yt_tv = outputs.get("youtube", {}).get("tv", [])
    if yt_tv:
        st.success(f"✅ {len(yt_tv)} TV videos found")
        for vid in yt_tv[:10]:
            st.write(f"📹 {vid}")
    else:
        st.info("No YouTube TV videos generated yet")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #999;'>
    <p>Quran Video Generator API v1.0 | Ready for Production</p>
</div>
""", unsafe_allow_html=True)
