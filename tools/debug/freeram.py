"""WRAM no scene of a tour ever wrote: union of lowmap.txt files (tools/debug/lowmap.lua). freeram.py DIR.. [--min 16]
Prints runs of watched, unwritten bytes, longest first."""
import argparse
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("dirs", nargs="+")
ap.add_argument("--min", type=int, default=16)
args = ap.parse_args()
maps = [t for d in args.dirs for p in Path(d).glob("*/lowmap.txt") if len(t := p.read_text()) == 0x20000]
assert maps, "no full-size lowmap.txt: run the tour with tools/debug/lowmap.lua"
free = [all(m[i] == "0" for m in maps) for i in range(0x20000)]
runs, start = [], None
for i, f in enumerate(free + [False]):
    if f and start is None:
        start = i
    elif not f and start is not None:
        runs.append((i - start, start))
        start = None
print(len(maps), "runs")
for n, a in sorted(runs, reverse=True):
    if n >= args.min:
        print(f"${0x7E + (a >> 16):02X}:{a & 0xFFFF:04X}-{(a + n - 1) & 0xFFFF:04X} {n} bytes")
