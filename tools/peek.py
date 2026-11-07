"""Recon: dump a ROM range as hex + gojuon guess. peek.py OFFSET [LEN]"""
import sys
from pathlib import Path

ROM = next((Path(__file__).resolve().parents[1] / "rom").glob("*.sfc")).read_bytes()
H = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん"
off = int(sys.argv[1], 16)
n = int(sys.argv[2], 16) if len(sys.argv) > 2 else 0x100
for i in range(off, off + n, 16):
    row = ROM[i:i + 16]
    txt = "".join(H[b - 0x24] if 0x24 <= b < 0x24 + len(H) else "." for b in row)
    print(f"{i:06X} {row.hex(' ')}  {txt}")
