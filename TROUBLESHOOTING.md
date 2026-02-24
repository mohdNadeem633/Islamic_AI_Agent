# 🔧 Troubleshooting Guide

## ⚡ Quick Diagnosis

Run this command first to check everything:

```bash
python test_system.py
```

This will tell you exactly what's wrong!

---

## 🐛 Common Issues & Solutions

### Issue 1: "Module not found" error

**Symptoms:**
```
ModuleNotFoundError: No module named 'requests'
ModuleNotFoundError: No module named 'PIL'
ModuleNotFoundError: No module named 'streamlit'
```

**Solution:**
```bash
pip install -r requirements.txt
```

If that doesn't work:
```bash
python -m pip install -r requirements.txt
```

---

### Issue 2: Wrong Surah being generated

**Symptoms:**
- UI shows Surah 114 but generates Surah 100
- Different Surah than selected

**Root Cause:**
The `SETTINGS.py` file stores the last selection. When you change it in the UI, it updates `SETTINGS.py`.

**Solution:**

**Option A - Use the UI** (Recommended):
1. Open `streamlit run app.py`
2. Change Surah in sidebar
3. Click "Generate Videos"
4. Settings are auto-saved

**Option B - Edit manually:**
1. Open `SETTINGS.py` in text editor
2. Find line: `SURAH_NUMBER = 114`
3. Change to your desired number (1-114)
4. Save file
5. Run `python main.py`

---

### Issue 3: Bismillah not reciting / highlighting

**Symptoms:**
- Bismillah appears but doesn't change color word-by-word
- Static Bismillah frame

**Root Cause:**
Old `arabic_utils.py` has Unicode encoding issues

**Solution:**
1. Replace `arabic_utils.py` with `FIXED_arabic_utils.py`
2. Make sure file is saved with UTF-8 encoding

**Test Bismillah detection:**
```python
python -c "from arabic_utils import is_bismillah; print(is_bismillah('بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ'))"
```

Should print: `True`

---

### Issue 4: Same backgrounds repeating

**Symptoms:**
- Have 100 backgrounds but only see 5-10 different ones
- Backgrounds repeat in same order

**Root Cause:**
Old `assets.py` uses modulo round-robin instead of true random

**Solution:**
Replace `assets.py` with the fixed version that has:
```python
def _get_next_random_background():
    """Ensures ALL backgrounds used before repeating"""
```

---

### Issue 5: Text not readable on some backgrounds

**Symptoms:**
- White text on white background
- Dark text on dark background
- Can't read some ayahs

**Solution:**
In UI or SETTINGS.py:
```python
AUTO_CONTRAST = True  # Must be True
```

This automatically picks light/dark text based on background brightness.

---

### Issue 6: No internet / API fails

**Symptoms:**
```
ConnectionError: No internet connection
ERROR: No internet and no local cache found
```

**Solutions:**

**If you have internet:**
1. Check firewall isn't blocking Python
2. Try: `python -c "import requests; print(requests.get('https://api.alquran.cloud/v1/surah/1').status_code)"`
3. Should print: `200`

**If no internet:**
1. Pre-download Surah with internet on another computer
2. Place `content/surah.json` in project folder
3. System will use cached file automatically

---

### Issue 7: "No background images found"

**Symptoms:**
```
ERROR: No background images found
Upload at least one background image
```

**Solution:**
1. Create `images/` folder if it doesn't exist:
   ```bash
   mkdir images
   ```

2. Add at least 1 image to `images/` folder:
   - Name it: `background1.jpg` or `bg1.png`
   - Can also use: `background001.jpg`, `background_1.png`, etc.

3. Verify:
   ```bash
   ls images/background*
   ```

---

### Issue 8: Fonts not found / ugly text

**Symptoms:**
- Text looks wrong
- Error: "Font not found"
- Using system default font

**Solution:**
Download required fonts:

1. **Amiri Bold** (for Arabic):
   - Download: https://fonts.google.com/specimen/Amiri
   - File: `Amiri-Bold.ttf`
   - Place in: `fonts/Amiri-Bold.ttf`

2. **Noto Sans** (for English):
   - Download: https://fonts.google.com/specimen/Noto+Sans
   - Files: `NotoSans-SemiBold.ttf`, `NotoSans-Regular.ttf`
   - Place in: `fonts/` folder

**Verify fonts:**
```bash
ls fonts/*.ttf
```

Should show:
```
fonts/Amiri-Bold.ttf
fonts/Amiri-Regular.ttf
fonts/NotoSans-Regular.ttf
fonts/NotoSans-SemiBold.ttf
```

---

### Issue 9: Audio won't download

**Symptoms:**
```
Downloading audio [alafasy] ... ✗
All reciters failed
```

**Solutions:**

1. **Check internet:**
   ```bash
   ping everyayah.com
   ```

2. **Test manually:**
   ```bash
   curl https://everyayah.com/data/Alafasy_128kbps/001001.mp3 -o test.mp3
   ```

3. **Try different reciter:**
   In `SETTINGS.py`:
   ```python
   PREFERRED_RECITER = "basit"  # or "husary"
   ```

4. **Check audio cache folder:**
   ```bash
   ls audio/recitations/
   ```
   If files exist, they won't re-download.

---

### Issue 10: Generation is very slow

**Symptoms:**
- Takes 30+ minutes for short Surah
- Computer freezes
- High CPU/RAM usage

**Solutions:**

1. **Start with short Surah:**
   - Surah 103 (Al-Asr) - only 3 ayahs
   - Surah 108 (Al-Kawthar) - only 3 ayahs
   - Surah 112 (Al-Ikhlas) - only 4 ayahs

2. **Check RAM:**
   - Need at least 4GB free RAM
   - Close other programs

3. **Disable one format:**
   ```python
   GENERATE_TV_FORMAT = False  # Only make phone videos
   ```

4. **First generation is always slower:**
   - Downloading audio takes time
   - Subsequent generations use cached audio (much faster!)

---

### Issue 11: Streamlit won't start

**Symptoms:**
```
streamlit: command not found
ModuleNotFoundError: No module named 'streamlit'
```

**Solution:**
```bash
pip install streamlit
```

Then:
```bash
streamlit run app.py
```

**If browser doesn't open automatically:**
Manually go to: `http://localhost:8501`

---

### Issue 12: Unicode / encoding errors

**Symptoms:**
- Weird characters like `â€"` instead of proper symbols
- Arabic text appears as boxes or question marks

**Solutions:**

1. **Re-save files with UTF-8:**
   - Open file in VS Code or Notepad++
   - Save As → Encoding: UTF-8
   - NOT UTF-8 BOM or ANSI

2. **Check terminal encoding:**
   ```bash
   python -c "import sys; print(sys.stdout.encoding)"
   ```
   Should print: `utf-8`

3. **Windows users:**
   Add to beginning of Python files:
   ```python
   # -*- coding: utf-8 -*-
   ```

---

### Issue 13: Videos stuck at "Generating..."

**Symptoms:**
- Progress shows but no output
- Terminal shows no errors
- Videos folder empty

**Solutions:**

1. **Check terminal output:**
   Look for actual error messages (not just in Streamlit UI)

2. **Run main.py directly:**
   ```bash
   python main.py
   ```
   Easier to see errors

3. **Check disk space:**
   ```bash
   # Linux/Mac
   df -h .
   
   # Windows
   dir
   ```
   Videos need ~50MB each

4. **Check write permissions:**
   Make sure `videos/` folder is writable

---

## 🧪 Testing Individual Components

### Test 1: Check imports
```bash
python -c "import PIL, moviepy, librosa, requests; print('OK')"
```

### Test 2: Check Surah fetch
```bash
python -c "import requests; print(requests.get('https://api.alquran.cloud/v1/surah/1').json()['data']['englishName'])"
```

### Test 3: Check audio download
```python
from audio_engine import download_audio
path = download_audio(1, 1)
print(f"Downloaded to: {path}")
```

### Test 4: Check background images
```python
from assets import list_background_paths
paths = list_background_paths()
print(f"Found {len(paths)} backgrounds")
```

### Test 5: Check fonts
```python
from assets import get_arabic_font, get_english_font
print("Arabic font:", get_arabic_font())
print("English font:", get_english_font())
```

---

## 📞 Still Having Issues?

1. **Run the test script:**
   ```bash
   python test_system.py
   ```

2. **Check the error message carefully:**
   - Note the exact error text
   - Note which file/line it occurs

3. **Verify file structure:**
   ```bash
   ls -la
   ```
   Make sure all `.py` files are in root folder, not in subdirectories

4. **Try a clean install:**
   ```bash
   # 1. Delete virtual environment if you have one
   rm -rf venv/
   
   # 2. Reinstall everything
   pip install -r requirements.txt
   
   # 3. Test
   python test_system.py
   ```

---

## ✅ Success Checklist

Before generating videos, verify:

- [ ] All Python modules installed (`pip list | grep -E "pillow|moviepy|librosa|streamlit"`)
- [ ] All `.py` files in root folder
- [ ] `fonts/` folder with 4 `.ttf` files
- [ ] `images/` folder with at least 1 background
- [ ] Internet connection working
- [ ] `SETTINGS.py` has correct `SURAH_NUMBER`
- [ ] `test_system.py` passes all tests

Then you're ready to:
```bash
streamlit run app.py
```

🎉 Happy video generating!
