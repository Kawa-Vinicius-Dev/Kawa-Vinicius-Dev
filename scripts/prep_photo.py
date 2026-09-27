"""Remove background, crop to head+shoulders, boost contrast.

Usage: python scripts/prep_photo.py source-photo.jpg [x0 y0 x1 y1]
Writes source-prepped.png (grayscale + alpha). Run locally only when the photo changes.
"""
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import new_session, remove

src = sys.argv[1]
box = tuple(map(int, sys.argv[2:6])) if len(sys.argv) >= 6 else (350, 610, 770, 1080)
ERASE = [(635, 900, 800, 1120), (595, 1000, 800, 1120)]  # original-photo coords to blank out (the hand left over once the phone is removed)

session = new_session("u2net_human_seg")  # ~170MB; rembg's default model is 1GB
cut = remove(Image.open(src).convert("RGB"), session=session)  # segment on full frame, then crop
alpha = np.array(cut)[:, :, 3].astype(np.float32) / 255
for ex0, ey0, ex1, ey1 in ERASE:
    alpha[ey0:ey1, ex0:ex1] = 0
x0, y0, x1, y1 = box
rgb, alpha = np.array(cut.convert("RGB"))[y0:y1, x0:x1], alpha[y0:y1, x0:x1]

gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
gray = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8)).apply(gray)
out = np.dstack([gray, (alpha * 255).astype(np.uint8)])  # keep alpha: it decides what's background

Image.fromarray(out, "LA").save("source-prepped.png")
print("wrote source-prepped.png", out.shape)
