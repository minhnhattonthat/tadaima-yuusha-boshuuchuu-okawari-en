"""Print a BG tilemap from a VRAM dump as hex tile numbers: mapdump.py VRAM.bin BYTE_ADDR_HEX W H. Rows of blanks ($00, $26) are dropped."""
import sys

v = open(sys.argv[1], "rb").read()
at, w, h = int(sys.argv[2], 16), int(sys.argv[3]), int(sys.argv[4])
for y in range(h):
    r = [v[at + (y * w + x) * 2] | v[at + (y * w + x) * 2 + 1] << 8 for x in range(w)]
    if any(t & 0x3FF not in (0, 0x26) for t in r):
        print(f"{y:2d}", " ".join(f"{t & 0x3FF:02X}" for t in r), " attr", hex(max(r) & 0xFC00))
