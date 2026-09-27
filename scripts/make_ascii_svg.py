"""source-prepped.png -> kawa-ascii.svg: monochrome ASCII portrait that types itself in once.

Usage: python scripts/make_ascii_svg.py [source-prepped.png]
"""
import sys
from html import escape

import numpy as np
from PIL import Image

RAMP = " .`:-=+*cs#%@"  # light-on-dark: dark pixel -> sparse, bright pixel -> dense; background -> space
COLS = 90
CW, LH, FS = 6.6, 11, 11  # char width, line height, font size (px)
PAD = 14
FG, BG, CURSOR = "#c9d1d9", "#0d1117", "#39d353"
ROW_DUR, ROW_STEP = 0.35, 0.045  # seconds per row wipe, stagger between rows

img = Image.open(sys.argv[1] if len(sys.argv) > 1 else "source-prepped.png").convert("LA")
rows = round(COLS * img.height / img.width * CW / LH)
px = np.asarray(img.resize((COLS, rows), Image.LANCZOS), dtype=np.float32) / 255
lum, alpha = px[:, :, 0], px[:, :, 1]
lo, hi = np.percentile(lum[alpha >= 0.5], [3, 97])  # stretch contrast over the subject only
lum = np.clip((lum - lo) / (hi - lo), 0, 1)
idx = (1 + lum * (len(RAMP) - 2)).round().astype(int)  # subject never drops to a space...
idx[alpha < 0.5] = 0  # ...only the background does
lines = ["".join(RAMP[i] for i in row) for row in idx]

W, H = COLS * CW + PAD * 2, rows * LH + PAD * 2
lw = COLS * CW
# Each row is revealed by a BG-colored cover sliding right in COLS steps, with a cursor on its edge.
# CSS keyframes, not SMIL: SMIL clip animations stayed frozen inside <img> in Chromium.
out = [
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" width="{W:.0f}" height="{H:.0f}">',
    f"<style>.v{{animation:type {ROW_DUR}s steps({COLS}) forwards}}"
    f".k{{opacity:0;animation:cur {ROW_DUR}s steps({COLS}) forwards}}"
    f"@keyframes type{{to{{transform:translateX({lw}px)}}}}"
    f"@keyframes cur{{0%,99%{{opacity:1}}to{{opacity:0;transform:translateX({lw}px)}}}}</style>",
    f'<rect width="100%" height="100%" rx="8" fill="{BG}"/>',
    f'<g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="{FS}" fill="{FG}">',
]
for r, line in enumerate(lines):
    if not line.strip():
        continue
    y, t = PAD + r * LH, f"animation-delay:{r * ROW_STEP:.3f}s"
    out.append(
        f'<text x="{PAD}" y="{y + LH - 2.5}" textLength="{lw}" lengthAdjust="spacing">{escape(line).replace(" ", "&#160;")}</text>'  # nbsp: renderers collapse plain spaces
        f'<rect class="v" style="{t}" x="{PAD}" y="{y}" width="{lw + PAD}" height="{LH}" fill="{BG}"/>'
        f'<rect class="k" style="{t}" x="{PAD}" y="{y + 1}" width="{CW}" height="{LH - 2}" fill="{CURSOR}"/>'
    )
out += ["</g>", "</svg>"]

open("kawa-ascii.svg", "w", encoding="utf-8").write("\n".join(out))
print(f"wrote kawa-ascii.svg ({COLS}x{rows})")
