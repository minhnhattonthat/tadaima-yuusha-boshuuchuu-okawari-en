"""Rightmost text-ink column per row band of a shot: inkright.py SHOT.png Y0,H [Y0,H..] [--ink 200].
Ink = a pixel whose brightest channel is >= --ink (white/yellow glyphs over a dark window). For the width gate:
the last column a glyph still shows, read off pixels rather than the engine's cell count."""
import argparse

from PIL import Image


def right(img, y0, h, ink):
    """Runs of ink columns, [(x0, x1)..]: a window border shows as a run of its own at each side."""
    px = img.load()
    cols = sorted({x for x in range(img.width) for y in range(y0, y0 + h) if min(px[x, y][:2]) >= ink})
    runs = []
    for x in cols:
        if runs and x <= runs[-1][1] + 2:
            runs[-1][1] = x
        else:
            runs.append([x, x])
    return [tuple(r) for r in runs]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("shot")
    ap.add_argument("bands", nargs="+")
    ap.add_argument("--ink", type=int, default=200)
    a = ap.parse_args()
    img = Image.open(a.shot).convert("RGB")
    for b in a.bands:
        y0, h = map(int, b.split(","))
        print(b, right(img, y0, h, a.ink))
