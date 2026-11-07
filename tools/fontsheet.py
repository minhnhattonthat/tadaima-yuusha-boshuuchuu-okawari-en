"""Render the 16x16 1bpp dialogue font (block 000, $7E:2000) as labelled sheets: fontsheet.py [FIRST LAST]."""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
FONT = (ROOT / "work/blocks/000.bin").read_bytes()
first = int(sys.argv[1], 16) if len(sys.argv) > 1 else 0
last = int(sys.argv[2], 16) if len(sys.argv) > 2 else 0x1FF
Z, CELL, MARGIN = 3, 56, 34
rows = (last - first) // 16 + 1
img = Image.new("RGB", (MARGIN + 16 * CELL, MARGIN + rows * CELL), (32, 32, 64))
d = ImageDraw.Draw(img)
for c in range(16):
    d.text((MARGIN + c * CELL + 20, 12), f"{c:X}", fill=(255, 255, 0))
for r in range(rows):
    d.text((2, MARGIN + r * CELL + 18), f"{first + r * 16:03X}", fill=(255, 255, 0))
for g in range(first, last + 1):
    x0 = MARGIN + (g - first) % 16 * CELL
    y0 = MARGIN + (g - first) // 16 * CELL
    p = g * 32
    b = FONT[p:p + 32]
    for y in range(16):
        q = (y // 8) * 16 + y % 8
        row = b[q] << 8 | b[q + 8]
        for x in range(16):
            if row >> (15 - x) & 1:
                d.rectangle((x0 + x * Z, y0 + y * Z, x0 + x * Z + Z - 1, y0 + y * Z + Z - 1), fill=(255, 255, 255))
out = ROOT / f"work/font_{first:03X}.png"
img.save(out)
print(out)
