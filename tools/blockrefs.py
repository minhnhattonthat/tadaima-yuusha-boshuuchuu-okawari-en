"""List code sites that load a resource block: LDA #block [LDX #dest] JSL $828024. blockrefs.py [FIRST LAST]"""
import re
import sys
from pathlib import Path

rom = next((Path(__file__).resolve().parents[1] / "rom").glob("*.sfc")).read_bytes()[:0x60000]
lo, hi = (int(a) for a in sys.argv[1:3]) if len(sys.argv) > 2 else (0, 862)
for m in re.finditer(rb"\xa9(..)(?:\xa2(..))?\x22\x24\x80\x82", rom, re.S):
    b = int.from_bytes(m.group(1), "little")
    if lo <= b <= hi:
        dest = m.group(2)
        print(f"C{m.start() >> 16:X}:{m.start() & 0xFFFF:04X} block {b}" + (f" x={int.from_bytes(dest, 'little'):04X}" if dest else ""))
