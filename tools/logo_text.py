"""Renders the title logo's English lettering (fonts/TitanOne-Regular.ttf, OFL) to fonts/logo_text.txt, which tools/logo.py
reads at build time (the build stays stdlib). Rerun after a wording change: python -X utf8 tools/logo_text.py

Each zone: a header `zone NAME X Y` (logo-region pixel of the top left), then rows; '.' is no ink, a letter's pixels carry its
number (0-9 a-z) so the build can colour letter by letter. Letters are cut per glyph, scaled to fill the zone's box
proportionally with a 2 px gap (the outline closes it), no antialiasing.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONT = ROOT / "fonts/TitanOne-Regular.ttf"
ZONES = [  # name, text, box (x0, y0, x1, y1) in the logo region (BG2 cols 4-28, rows 0-15), font size
    ("top", "NOW", (62, 30, 126, 45), 30),  # ただいま
    ("left", "HEROES", (4, 52, 91, 80), 40),  # 勇者 募: pal 1 half, x < 96
    ("right", "WANTED", (101, 52, 190, 80), 40),  # 集 中: pal 2 half, x >= 96 (x 192+ is a pal 1 cell again)
]
DIGITS = "0123456789abcdefghijklmnopqrstuvwxyz"


def glyph(c, f, w, h):
    size = f.size
    im = Image.new("L", (size * 2, size * 3), 0)
    d = ImageDraw.Draw(im); d.fontmode = "1"
    d.text((size // 2, size // 2), c, font=f, fill=255)
    return im.crop(im.getbbox()).resize((w, h), Image.NEAREST)


def zone(text, box, fs):
    x0, y0, x1, y1 = box
    f = ImageFont.truetype(str(FONT), fs)
    widths = [f.getbbox(c)[2] - f.getbbox(c)[0] for c in text]
    gap = 2
    k = (x1 - x0 - gap * (len(text) - 1)) / sum(widths)
    grid = [["."] * (x1 - x0) for _ in range(y1 - y0)]
    pen = 0
    for i, c in enumerate(text):
        w = max(1, round(widths[i] * k)) if i < len(text) - 1 else x1 - x0 - pen
        m = glyph(c, f, w, y1 - y0)
        for y in range(m.height):
            for x in range(m.width):
                if m.getpixel((x, y)):
                    grid[y][pen + x] = DIGITS[i]
        pen += w + gap
    return grid


def main():
    out = ["# Rendered by tools/logo_text.py from fonts/TitanOne-Regular.ttf (OFL); read by tools/logo.py\n"]
    for name, text, box, fs in ZONES:
        out.append(f"zone {name} {box[0]} {box[1]} {text}\n")
        out += ["".join(r) + "\n" for r in zone(text, box, fs)]
    (ROOT / "fonts/logo_text.txt").write_text("".join(out), encoding="utf-8")


if __name__ == "__main__":
    main()
