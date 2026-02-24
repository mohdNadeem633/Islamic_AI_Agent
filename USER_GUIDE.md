# 📖 Quran Video Generator - User Guide
## Simple. Beautiful. No Technical Skills Required.

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install
Open terminal/command prompt in the project folder and run:

```bash
pip install -r requirements.txt
```

### Step 2: Launch the App
```bash
streamlit run app.py
```

Your browser will open automatically to `http://localhost:8501`

### Step 3: Generate!
1. Choose your Surah
2. Upload background images
3. Adjust settings if you want
4. Click "GENERATE VIDEOS"
5. Done! ✨

---

## 📚 Complete Walkthrough

### Left Sidebar - Main Settings

#### 📖 Select Surah
Three easy ways to choose:
- **By Name:** Dropdown list of all 114 Surahs
- **By Number:** Enter 1-114
- **Random:** Let the app pick one

#### 📄 Ayah Range (Optional)
- Check "Specific ayahs only" if you want just certain verses
- Otherwise, the whole Surah will be used

#### 🎙️ Reciter
Choose your favorite:
- **Alafasy** - Very clear, most popular
- **Abdul Basit** - Beautiful classical style
- **Husary** - Clear Tajweed pronunciation

#### 📱 Video Formats
- **Phone / Reels (9:16)** - For Instagram, Facebook, TikTok, YouTube Shorts
- **TV / YouTube (16:9)** - For watching on TV, laptop, desktop YouTube

#### ⏱️ Video Length
- **Reel target** - How long each short clip should be (10-30 seconds)
- **YouTube target** - How long each full video should be (2-10 minutes)
- **End pause** - How long to hold the last frame (0.5-5 seconds)

---

### Tab 1: 🎨 Style

#### Font Sizes
Move the sliders to make text bigger or smaller:
- **Arabic:** 40-120 (default 72)
- **English:** 20-60 (default 36)
- **Reference:** 16-40 (default 29)
- **Text stroke:** 0-5 (default 2) - Makes text bolder

#### Colors
- **Auto-adapt to background** ✅ (Recommended)
  - Automatically picks light or dark text based on your background
  - Smart and hassle-free!

- If unchecked, you can manually pick colors:
  - Click the color boxes to choose exact colors
  - Set different colors for normal text and highlighted words

---

### Tab 2: 🖼️ Backgrounds

#### Upload Images
1. Click "Browse files"
2. Select as many images as you want (JPG or PNG)
3. Click "Upload"
4. Done! The app will cycle through them randomly

**💡 Pro Tip:** Upload 50-100 diverse images for best variety!

#### Current Backgrounds
- See all your uploaded backgrounds
- Preview thumbnails
- Delete all if you want to start fresh

**⚠️ Important:** Make sure to upload at least one background before generating videos.

---

### Tab 3: 📐 Layout

Position text exactly where you want it on the screen.

#### How the Screen Works
- **Width:** 1080 pixels (left to right)
- **Height:** 1920 pixels (top to bottom)
- **Y=0:** Very top
- **Y=1920:** Very bottom

#### Arabic Text Position
- **Vertical center:** Where the Arabic text block sits (400-1200)
  - Lower number = higher on screen
  - Higher number = lower on screen
- **Side margins:** Space from left/right edges
- **Line spacing:** Gap between Arabic lines
- **Word spacing:** Gap between Arabic words

#### English Text Position
- **Start position:** Where English translation begins (800-1600)
- **Side margins:** Space from edges
- **Line spacing:** Gap between lines

#### Reference Line
- The "Surah Name • Ayah Number" text at bottom
- Adjust how far from top (1400-1880)

#### Logo
If you have a `images/logo.png` file:
- **Max width:** How big the logo should be
- **From right:** Distance from right edge
- **From top:** Distance from top

---

### Tab 4: ▶️ Generate

#### Preview Settings
Click "👁️ Preview Settings" to:
- Make sure the Surah loaded correctly
- See the first Ayah as a preview
- Check number of Ayahs

#### Generate Videos
1. Click the big **"🎬 GENERATE VIDEOS"** button
2. Wait (this can take 5-30 minutes depending on Surah length)
3. Watch the progress in real-time
4. When done, your videos will be in:
   - `videos/reels/` - Short clips
   - `videos/youtube/phone/` - Phone format full videos
   - `videos/youtube/tv/` - TV format full videos

---

## 🎨 Design Tips

### For Best Results:

1. **Backgrounds:**
   - Use high-quality images (1080x1920 or larger)
   - Mix different styles (nature, abstract, patterns)
   - Avoid images with too much text or busy details

2. **Colors:**
   - Keep "Auto-adapt" ON for automatic text contrast
   - Red highlight works on all backgrounds
   - If using custom colors, test with dark AND light backgrounds

3. **Positioning:**
   - Default positions work great for most cases
   - If text overlaps, increase line spacing
   - If text is cut off, adjust side margins

4. **Duration:**
   - Reels: 15-17 seconds is perfect for Instagram/Facebook
   - YouTube: 4-5 minutes keeps viewers engaged

---

## 🐛 Troubleshooting

### "No background images found"
→ Upload at least one image in the Backgrounds tab

### "Generation failed"
→ Check the error log in the expander
→ Make sure you have fonts folder with required fonts
→ Check internet connection (needed to fetch Surah text)

### Text is cut off or overlapping
→ Adjust positions in the Layout tab
→ Decrease font sizes in the Style tab
→ Increase margins

### Videos are too long/short
→ Adjust "Reel target" and "YouTube target" in sidebar

### Can't see generated videos
→ Check the file paths shown after generation
→ Look in `videos/reels/` and `videos/youtube/` folders

---

## 📁 Project Structure

```
your-project/
├── app.py                    ← Launch this with Streamlit
├── main.py                   ← Video generator (runs automatically)
├── SETTINGS.py               ← Auto-generated from UI
├── requirements.txt          ← Install dependencies
│
├── fonts/                    ← Font files (include these)
│   ├── Amiri-Bold.ttf
│   ├── Amiri-Regular.ttf
│   ├── NotoSans-SemiBold.ttf
│   └── NotoSans-Regular.ttf
│
├── images/                   ← Your background images
│   ├── background1.jpg
│   ├── background2.jpg
│   └── logo.png             ← Optional logo
│
├── audio/                    ← Auto-created
│   └── recitations/         ← Cached MP3s (never re-downloaded)
│
└── videos/                   ← Auto-created
    ├── reels/               ← Short clips (15-17s)
    └── youtube/
        ├── phone/           ← 9:16 format (4-5 min)
        └── tv/              ← 16:9 format (4-5 min)
```

---

## ⚡ Advanced Tips

### Batch Processing
Want to generate multiple Surahs?
1. Generate first Surah
2. Change Surah selection
3. Click Generate again
4. Repeat!

### Custom Fonts
Want different fonts?
1. Download .ttf font files
2. Place in `fonts/` folder
3. Edit `SETTINGS.py` font paths (or edit app.py to add dropdown)

### Editing After Generation
All settings are saved in `SETTINGS.py`. You can:
1. Edit values manually in a text editor
2. Run `python main.py` from terminal to regenerate without the UI

---

## 🎬 Uploading to Social Media

### Instagram Reels / Facebook Reels
- Use files from `videos/reels/`
- Perfect length (15-17 seconds)
- 9:16 format

### YouTube Shorts
- Use files from `videos/reels/`
- Under 60 seconds

### YouTube (Regular)
- **For mobile viewers:** Use `videos/youtube/phone/`
- **For TV/desktop:** Use `videos/youtube/tv/`
- Both are 4-5 minutes long

### TikTok
- Use files from `videos/reels/`
- May need to trim to under 60 seconds

---

## 💡 Need Help?

- **Installation issues:** Make sure Python 3.8+ is installed
- **Generation is slow:** Normal! Each ayah takes 15-60 seconds
- **Out of memory:** Try generating shorter Surahs first
- **Audio won't download:** Check your internet connection

---

## ✨ You're Ready!

1. Install dependencies
2. Launch the app
3. Upload backgrounds
4. Choose your Surah
5. Generate
6. Share beautiful Quran videos!

May your videos bring benefit to many. 🤲
