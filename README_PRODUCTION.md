# Quran Video Generator - Production Setup

## Project Structure

```
Islamic-ai-agent/
├── src/                      # Core logic (move existing modules here)
│   ├── video_exporter.py    # Export video files
│   ├── clip_builder.py      # Build video clips
│   ├── renderer.py          # Frame rendering
│   ├── audio_engine.py      # Audio processing
│   ├── assets.py            # Asset loading
│   ├── arabic_utils.py      # Arabic text processing
│   └── __init__.py
│
├── api/                      # FastAPI backend
│   ├── main_api.py          # Main API server
│   └── __init__.py
│
├── app/                      # Streamlit frontend
│   ├── app_v2.py            # Production web interface
│   └── __init__.py
│
├── config/                   # Configuration
│   ├── settings.py          # Settings management
│   └── __init__.py
│
├── data/                     # Static data
│   ├── content/             # Content files (surah.json, quotes.json)
│   ├── fonts/               # Font files
│   └── images/              # Background images
│
├── videos/                   # Output directory (generated)
│   ├── reels/               # Phone reel format
│   └── youtube/             # YouTube format
│       ├── phone/           # 9:16 vertical
│       └── tv/              # 16:9 horizontal
│
├── audio/                    # Audio cache
│   └── recitations/         # Cached audio files
│
├── main.py                  # CLI interface
├── config.py                # Config loader
├── SETTINGS.py              # Auto-generated settings
├── requirements.txt         # Dependencies
├── README.md                # This file
└── .env.example             # Environment variables template
```

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Additional API Dependencies

```bash
pip install fastapi uvicorn gunicorn python-multipart
```

## Running the Application

### Option A: Full Stack (API + Streamlit)

**Terminal 1: Start the API Server**
```bash
python -m uvicorn api.main_api:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2: Start the Streamlit Frontend**
```bash
streamlit run app/app_v2.py
```

The frontend will be available at: http://localhost:8501

### Option B: CLI Only

```bash
python main.py
```

## API Documentation

Once the API is running, access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | API health check |
| `/surahs` | GET | Get list of all surahs |
| `/generate` | POST | Generate videos |
| `/config` | GET | Get current configuration |
| `/output/reels` | GET | List generated reels |
| `/output/youtube` | GET | List YouTube videos |

### Example API Call

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "surah_number": 1,
    "reciter": "alafasy",
    "ayah_start": 1,
    "ayah_end": 5,
    "fast_mode": false,
    "generate_phone": true,
    "generate_tv": false
  }'
```

## Configuration

Edit `SETTINGS.py` or use the API endpoints to configure:
- Video dimensions (WIDTH, HEIGHT)
- FPS and playback speed
- Fast Mode encoding
- Reciter selection
- Output formats

## Performance Notes

- **Fast Mode**: Reduced quality, ~40% faster encoding
- **Audio Caching**: First run downloads audio; subsequent runs use cache
- **Background Changes**: Backgrounds now change only with each new ayah (not timer-based)

## Troubleshooting

### API not responding
- Ensure the API server is running: `python -m uvicorn api.main_api:app --reload`
- Check that port 8000 is not in use

### Video generation errors
- Verify fonts are in `fonts/` directory
- Check that background images exist in `images/`
- Ensure ffmpeg is installed and in PATH

### Memory issues with large surahs
- Use Fast Mode to reduce memory usage
- Generate smaller ayah ranges
- Increase system RAM

## Production Deployment

### Using Gunicorn (recommended for production)

```bash
# API
gunicorn -w 4 -b 0.0.0.0:8000 api.main_api:app

# Streamlit (in separate terminal)
streamlit run app/app_v2.py --server.port=8501
```

### Using Docker (coming soon)

```bash
docker build -t quran-video-generator .
docker run -p 8000:8000 -p 8501:8501 quran-video-generator
```

## File Output Locations

- **Phone Reels (9:16)**: `videos/reels/*.mp4`  
- **YouTube Phone (9:16)**: `videos/youtube/phone/*.mp4`
- **YouTube TV (16:9)**: `videos/youtube/tv/*.mp4`

## Features

✅ Support for all 114 surahs  
✅ Multiple reciters (Alafasy, Abdul Basit, Husary)  
✅ Dynamic text highlighting with audio sync  
✅ Automatic contrast adaptation to background  
✅ Multiple output formats (Reels, YouTube)  
✅ Fast mode for quick generation  
✅ Audio caching for performance  
✅ Background change on ayah change only  
✅ RESTful API interface  
✅ Web-based UI  

## License

Proprietary - All rights reserved

## Support

For issues or feature requests, contact support@quranvideogenerator.local
