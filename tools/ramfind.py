"""Recon: find a kana word (gojuon code order, あ=0x24) in RAM dumps. ramfind.py WORD DUMP.."""
import sys
from pathlib import Path

H = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをん"
pat = bytes(0x24 + H.index(c) for c in sys.argv[1])
for f in sys.argv[2:]:
    d = Path(f).read_bytes()
    i = d.find(pat)
    while i >= 0:
        print(f, f"{0x7E0000 + i:06X}", d[max(i - 8, 0):i + 24].hex(" "))
        i = d.find(pat, i + 1)
