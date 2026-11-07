"""Recon: ROM map. Marks resource-table blocks, then lists what's left, FF/00 runs and raw string ranges."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import unpack  # noqa: E402
from textsweep import strings  # noqa: E402

rom = next((ROOT / "rom").glob("*.sfc")).read_bytes()
used = bytearray(len(rom))
spans = []
for i, src, size, dst, bank in unpack.entries(rom):
    data, n = unpack.load(rom, src, size)
    off = src & 0x3FFFFF
    n = n or size
    used[off:off + n] = b"\x01" * n
    spans.append((off, off + n, i))
spans.sort()
print(f"blocks: {spans[0][0]:06X}..{spans[-1][1]:06X}, {sum(used)} bytes")

# uncovered gaps
i = 0
while i < len(rom):
    if used[i]:
        i += 1
        continue
    j = i
    while j < len(rom) and not used[j]:
        j += 1
    if j - i >= 0x100:
        fill = rom[i:j]
        print(f"gap {i:06X}..{j:06X} len={j - i:05X} 00={fill.count(0) * 100 // (j - i)}% FF={fill.count(255) * 100 // (j - i)}%")
    i = j

# trailing fill per 64K bank
for b in range(0x20):
    s = rom[b << 16:(b + 1) << 16]
    for v in (0x00, 0xFF):
        k = 0x10000
        while k and s[k - 1] == v:
            k -= 1
        if 0x10000 - k >= 0x40:
            print(f"bank {b:02X} ends in {v:02X} x {0x10000 - k:04X} from {(b << 16) + k:06X}")

# raw string ranges outside blocks: merge hits closer than 0x40 bytes
hits = [(p, s) for p, s in strings(rom) if not used[p]]
ranges = []
for p, s in hits:
    if ranges and p - ranges[-1][1] < 0x40:
        ranges[-1][1] = p + len(s)
        ranges[-1][2] += 1
    else:
        ranges.append([p, p + len(s), 1])
for a, b, n in ranges:
    if n >= 3:
        print(f"raw text {a:06X}..{b:06X} strings={n}")
