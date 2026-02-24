"""
FastAPI backend for Quran Video Generator
Provides RESTful endpoints for video generation
"""

from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import json
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import core modules
from main import generate_videos_internal
import config

# Initialize FastAPI app
app = FastAPI(
    title="Quran Video Generator API",
    description="API for generating animated Quran video content",
    version="1.0.0"
)

# ─────────────────────────────────────────────────────────────
#  DATA MODELS
# ─────────────────────────────────────────────────────────────

class GenerationRequest(BaseModel):
    """Request model for video generation"""
    surah_number: int
    reciter: str = "alafasy"
    ayah_start: int = 1
    ayah_end: int = 10
    fast_mode: bool = False
    generate_phone: bool = True
    generate_tv: bool = True
    
    # Layout settings
    arabic_font_size: int = 72
    english_font_size: int = 36
    reference_font_size: int = 29
    arabic_y: int = 800
    english_y: int = 1050
    reference_y: int = 1650
    
    # Timing
    reel_target_sec: int = 16
    youtube_target_min: float = 4.5
    hold_duration: float = 1.5


class GenerationResponse(BaseModel):
    """Response model for generation status"""
    status: str
    message: str
    files_output: Optional[dict] = None
    error: Optional[str] = None


class SurahListResponse(BaseModel):
    """Response model for surah list"""
    total: int
    surahs: List[dict]


class StatusResponse(BaseModel):
    """Response model for generation status polling"""
    status: str  # "pending", "generating", "complete", "error"
    progress: Optional[int] = None
    message: Optional[str] = None

# ─────────────────────────────────────────────────────────────
#  ENDPOINTS
# ─────────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "name": "Quran Video Generator API"
    }


@app.get("/surahs", response_model=SurahListResponse)
async def get_surahs():
    """Get list of all surahs"""
    surahs_data = [
        {"number": i+1, "name": name}
        for i, name in enumerate([
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
        ])
    ]
    return SurahListResponse(total=len(surahs_data), surahs=surahs_data)


@app.post("/generate", response_model=GenerationResponse)
async def generate_videos(request: GenerationRequest, background_tasks: BackgroundTasks):
    """
    Generate Quran videos based on request parameters.
    Returns file paths upon completion.
    """
    try:
        # Validate surah number
        if not (1 <= request.surah_number <= 114):
            return GenerationResponse(
                status="error",
                message="Invalid surah number",
                error="Surah number must be between 1 and 114"
            )
        
        # Validate ayah range
        if request.ayah_start > request.ayah_end:
            return GenerationResponse(
                status="error",
                message="Invalid ayah range",
                error="ayah_start must be <= ayah_end"
            )
        
        # Generate videos
        output_files = generate_videos_internal(
            surah_number=request.surah_number,
            reciter=request.reciter,
            ayah_start=request.ayah_start,
            ayah_end=request.ayah_end,
            fast_mode=request.fast_mode,
            generate_phone=request.generate_phone,
            generate_tv=request.generate_tv
        )
        
        return GenerationResponse(
            status="success",
            message="Videos generated successfully",
            files_output=output_files
        )
    
    except Exception as e:
        return GenerationResponse(
            status="error",
            message="Generation failed",
            error=str(e)
        )


@app.get("/config")
async def get_config():
    """Get current configuration"""
    return {
        "surah_number": config.SURAH_NUMBER,
        "reciter": config.PREFERRED_RECITER,
        "width": config.WIDTH,
        "height": config.HEIGHT,
        "fps": config.FPS,
        "fast_mode": config.FAST_MODE,
        "generate_phone": config.GENERATE_PHONE_FORMAT,
        "generate_tv": config.GENERATE_TV_FORMAT,
    }


@app.get("/output/reels")
async def list_reel_videos():
    """List all generated reel videos"""
    reel_dir = Path(config.REEL_OUTPUT_DIR)
    if not reel_dir.exists():
        return {"reels": []}
    reels = [f.name for f in reel_dir.glob("*.mp4")]
    return {"reels": sorted(reels), "count": len(reels)}


@app.get("/output/youtube")
async def list_youtube_videos():
    """List all generated YouTube videos"""
    yt_dir = Path(config.YOUTUBE_OUTPUT_DIR)
    phone_dir = yt_dir / "phone"
    tv_dir = yt_dir / "tv"
    
    phone_videos = [f.name for f in phone_dir.glob("*.mp4")] if phone_dir.exists() else []
    tv_videos = [f.name for f in tv_dir.glob("*.mp4")] if tv_dir.exists() else []
    
    return {
        "phone": sorted(phone_videos),
        "tv": sorted(tv_videos),
        "phone_count": len(phone_videos),
        "tv_count": len(tv_videos)
    }


# ─────────────────────────────────────────────────────────────
#  ERROR HANDLERS
# ─────────────────────────────────────────────────────────────

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": str(exc)
        },
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
