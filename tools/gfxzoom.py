"""Zoom blocks as tile sheets: gfxzoom.py OUT.png BPP ZOOM BLOCK[+HEXOFF[:HEXLEN]]..  (16 tiles wide, grey)"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
out, bpp, zoom = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
parts = []
for a in sys.argv[4:]:
    blk, _, rest = a.partition("+")
    off, _, ln = rest.partition(":")
    d = (ROOT / f"work/blocks/{int(blk):03d}.bin").read_bytes()
    o = int(off or "0", 16)
    parts.append((a, d[o:o + int(ln, 16)] if ln else d[o:]))
W = 128 * zoom + 8
hs = [(len(d) // (8 * bpp) + 15) // 16 * 8 * zoom + 14 for _, d in parts]
cols = max(1, 1100 // W)
rows = [hs[i:i + cols] for i in range(0, len(hs), cols)]
img = Image.new("L", (W * cols, sum(max(r) for r in rows)), 40)
dr = ImageDraw.Draw(img)
y0 = 0
for ri, r in enumerate(rows):
    for ci in range(len(r)):
        name, d = parts[ri * cols + ci]
        x0 = ci * W
        dr.text((x0 + 2, y0), name, fill=255)
        for t in range(len(d) // (8 * bpp)):
            for y in range(8):
                for x in range(8):
                    v = 0
                    o = t * 8 * bpp
                    for p in range(bpp // 2):
                        b = o + p * 16 + y * 2
                        v |= (d[b] >> (7 - x) & 1) << (p * 2) | (d[b + 1] >> (7 - x) & 1) << (p * 2 + 1)
                    c = v * 255 // ((1 << bpp) - 1)
                    px, py = x0 + (t % 16 * 8 + x) * zoom, y0 + 14 + (t // 16 * 8 + y) * zoom
                    dr.rectangle((px, py, px + zoom - 1, py + zoom - 1), fill=c)
    y0 += max(r)
img.save(out)
print(img.size)
