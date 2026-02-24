from moviepy.editor import VideoFileClip
import numpy as np
from PIL import Image
import sys

path = "videos/reels/Al-Faatiha_reel_001.mp4"
try:
    clip = VideoFileClip(path)
except Exception as e:
    print("ERROR_OPEN", e)
    sys.exit(2)

duration = clip.duration
# sample rate (frames per second) for analysis
sample_rate = 5
times = np.arange(0, duration, 1.0/sample_rate)
frames = []
for t in times:
    try:
        frame = clip.get_frame(t)
    except Exception as e:
        # if get_frame fails near end, break
        break
    img = Image.fromarray(frame).convert("L").resize((160, 160))
    arr = np.asarray(img, dtype=np.float32)
    frames.append(arr)

if len(frames) < 2:
    print("NO_FRAMES")
    clip.close()
    sys.exit(3)

# compute mean absolute difference between consecutive frames
diffs = []
events = []
for i in range(1, len(frames)):
    d = float(np.mean(np.abs(frames[i] - frames[i-1])))
    diffs.append(d)
    if d > 18.0:  # threshold for significant change
        events.append(times[i])

print(f"DURATION:{duration:.2f}")
print(f"SAMPLED_FRAMES:{len(frames)} (rate={sample_rate}fps)")
print(f"MEAN_DIFF:{np.mean(diffs):.2f}")
print(f"STD_DIFF:{np.std(diffs):.2f}")
print(f"EVENT_COUNT:{len(events)}")
if events:
    intervals = np.diff(events)
    print("EVENT_TIMES:", ",".join([f"{e:.2f}s" for e in events]))
    if len(intervals) > 0:
        print(f"AVG_INTERVAL:{np.mean(intervals):.2f}s")
    else:
        print("AVG_INTERVAL:N/A (single event)")
else:
    print("EVENT_TIMES:NONE")

clip.close()
