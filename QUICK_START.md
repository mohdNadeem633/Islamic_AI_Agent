# 🚀 Quick Start Guide - Quran Video Generator

## ⚡ 60 Seconds to First Video

### 1. Install Dependencies
```bash
pip install -r requirements_production.txt
```

### 2. Terminal 1: Start API Server
```bash
python -m uvicorn api.main_api:app --reload
```
✅ API running at: http://localhost:8000

### 3. Terminal 2: Start Web Interface
```bash
streamlit run app/app_v2.py
```
✅ Web UI available at: http://localhost:8501

### 4. Generate Your First Video
- Select a Surah (e.g., Al-Fatihah)
- Choose Reciter (Alafasy, Abdul Basit, or Husary)
- Set Ayah Range (e.g., 1-5)
- Click "GENERATE VIDEOS"

✅ Videos saved to: `videos/reels/` and `videos/youtube/`

---

## 📋 Generated Files

Last generation (Al-Israa Surah):
- ✅ `Al-Israa_reel_001.mp4` (6.5 MB)
- ✅ `Al-Israa_reel_002.mp4` (5.1 MB)

Located in: `C:\Users\Admin\Desktop\Islamic-ai-agent\videos\reels\`

---

## 🎯 Production Deployment

### Using Gunicorn (Recommended)
```bash
# Terminal 1: API with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 api.main_api:app

# Terminal 2: Streamlit for web
streamlit run app/app_v2.py --server.port=8501
```

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔧 Configuration

Environment variables (copy `.env.example` to `.env`):
```bash
API_URL=http://localhost:8000
FAST_MODE=false
DEFAULT_RECITER=alafasy
```

---

## 📊 Features

✅ All 114 Surahs  
✅ 3 Different Reciters  
✅ Multiple Output Formats (9:16 Reels, 16:9 YouTube)  
✅ Fast Mode (40% faster encoding)  
✅ Audio Pre-caching  
✅ Background Changes on Ayah Change Only  
✅ RESTful API  
✅ Web-based UI  

---

## 🚨 Troubleshooting

### API won't start
```bash
# Make sure port 8000 is free
netstat -ano | findstr :8000

# Kill process if needed
taskkill /PID <PID> /F
```

### Streamlit connection error
- Ensure API is running first
- Check API_URL in environment

### Video generation fails
- Verify fonts exist in `fonts/` directory
- Check background images in `images/`
- Ensure ffmpeg is installed

---

## 📝 Project Structure

```
Islamic-ai-agent/
├── api/
│   └── main_api.py          ← FastAPI backend
├── app/
│   └── app_v2.py             ← Streamlit frontend
├── videos/
│   ├── reels/                ← Phone videos (9:16)
│   └── youtube/              ← YouTube videos
│       ├── phone/ (9:16)
│       └── tv/    (16:9)
├── main.py                   ← CLI runner
├── SETTINGS.py               ← Auto-generated config
└── README_PRODUCTION.md      ← Full documentation
```

---

## 🤝 Ready to Sell?

The app is production-ready:
- ✅ RESTful API with documentation
- ✅ Web-based UI (no technical knowledge needed)
- ✅ Background change logic corrected
- ✅ Proper folder structure
- ✅ Easy deployment with Gunicorn

### Next Steps:
1. Setup `.env` with your production settings
2. Deploy API to cloud (AWS, GCP, Azure, etc.)
3. Deploy Streamlit to Streamlit Cloud or your server
4. Test all endpoints via API docs

---

## 📞 API Example

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "surah_number": 1,
    "reciter": "alafasy",
    "ayah_start": 1,
    "ayah_end": 7,
    "fast_mode": false,
    "generate_phone": true,
    "generate_tv": false
  }'
```

---

**Version**: 1.0.0  
**Status**: Production Ready  
**Last Updated**: 2026-02-20
