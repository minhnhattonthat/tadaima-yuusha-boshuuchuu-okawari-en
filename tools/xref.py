"""Recon: find JSL/JML to a 24-bit address in the code banks, all bank mirrors. xref.py ADDR.."""
import sys
from pathlib import Path

rom = next((Path(__file__).resolve().parents[1] / "rom").glob("*.sfc")).read_bytes()
CODE_END = 0x60000


def hits(pat):
    i = rom.find(pat, 0, CODE_END)
    while i >= 0:
        yield i
        i = rom.find(pat, i + 1, CODE_END)


for t in sys.argv[1:]:
    a = int(t, 16)
    b = a >> 16
    for op, name in ((0x22, "JSL"), (0x5C, "JML")):
        for bank in {b, b & 0x3F, b & 0x3F | 0x80, b & 0x3F | 0x40, b & 0x3F | 0xC0}:
            found = list(hits(bytes([op, a & 255, a >> 8 & 255, bank])))
            if found:
                print(t, name, f"bank {bank:02X} x{len(found)}", " ".join(f"{h:06X}" for h in found[:60]))
