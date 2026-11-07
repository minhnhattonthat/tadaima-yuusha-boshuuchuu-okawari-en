"""Relative search for a tile-number run in the ROM and every LZ block: findtiles.py 7D 88 63 3B [--stride N] (delta match, any offset)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import unpack  # noqa: E402


def hits(data, want, stride):
    d = [(b - want[0]) & 0xFF for b in want]
    for p in range(len(data) - stride * len(want)):
        if all((data[p + i * stride] - data[p]) & 0xFF == x for i, x in enumerate(d)):
            yield p, (data[p] - want[0]) & 0xFF


rom = next((ROOT / "rom").glob("*.sfc")).read_bytes()
args = sys.argv[1:]
stride = 1
if "--stride" in args:
    i = args.index("--stride")
    stride = int(args[i + 1])
    del args[i:i + 2]
want = [int(a, 16) for a in args]
for p, off in hits(rom, want, stride):
    print(f"rom {p:06X} offset {off:02X}")
for i, src, size, _, _ in unpack.entries(rom):
    for p, off in hits(unpack.load(rom, src, size)[0], want, stride):
        print(f"block {i}+{p:X} offset {off:02X}")
