"""Static graphics sweep: thumbnail every unpacked block as tiles, into numbered pages with an index.

gfxsweep.py [4|2]  -> work/gfx/page_NN.png + work/gfx/index.txt. Skips only blocks too small for a tile page
(<0x200 bytes) and the text blocks, and prints them.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
BPP = int(sys.argv[1]) if len(sys.argv) > 1 else 4
TW = 16
CHUNK = TW * TW * 8 * BPP   # 128x128 px per cell
COLS, ROWS = 8, 3
CELL_W, CELL_H = 130, 142
SKIP_TEXT = set(range(212, 303)) | set(range(725, 727)) | set(range(739, 767))


def tile(d, o, px, x0, y0):
    for y in range(8):
        for x in range(8):
            v = 0
            for p in range(BPP // 2):
                base = o + p * 16 + y * 2
                if base + 1 >= len(d):
                    return
                v |= (d[base] >> (7 - x) & 1) << (p * 2) | (d[base + 1] >> (7 - x) & 1) << (p * 2 + 1)
            px[x0 + x, y0 + y] = v * 255 // ((1 << BPP) - 1)


out = ROOT / f"work/gfx{BPP}"
out.mkdir(parents=True, exist_ok=True)
cells, skipped = [], []
for f in sorted((ROOT / "work/blocks").glob("*.bin")):
    d = f.read_bytes()
    i = int(f.stem)
    if i in SKIP_TEXT or len(d) < 0x200:
        skipped.append(i)
        continue
    for k in range(0, len(d), CHUNK):
        cells.append((i, k, d[k:k + CHUNK]))
print("skipped:", skipped)
per = COLS * ROWS
index = []
for pg in range(0, len(cells), per):
    img = Image.new("L", (COLS * CELL_W, ROWS * CELL_H), 40)
    dr = ImageDraw.Draw(img)
    for n, (i, k, d) in enumerate(cells[pg:pg + per]):
        x0, y0 = n % COLS * CELL_W, n // COLS * CELL_H
        dr.text((x0 + 2, y0), f"{i}+{k:X}", fill=255)
        px = img.load()
        for t in range(len(d) // (8 * BPP)):
            tile(d, t * 8 * BPP, px, x0 + t % TW * 8, y0 + 12 + t // TW * 8)
    name = f"page_{pg // per:03d}.png"
    img.save(out / name)
    index.append(f"{name} {' '.join(f'{i}+{k:X}' for i, k, _ in cells[pg:pg + per])}")
(out / "index.txt").write_text("\n".join(index), encoding="utf-8")
print(len(cells), "cells", len(index), "pages")
