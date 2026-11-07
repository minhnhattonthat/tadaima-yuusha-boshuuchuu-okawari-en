"""Find Japanese text in the ROM and in unpacked blocks: findtext.py PHRASE.. (uses tbl/jp.tbl; run unpack.py first)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))


def table():
    enc = {}
    for line in (ROOT / "tbl/jp.tbl").read_text(encoding="utf-8").splitlines():
        code, _, ch = line.partition("=")
        if len(code) == 2 and len(ch) == 1:
            enc[ch] = bytes.fromhex(code)
        elif len(code) == 4 and len(ch) == 1:
            enc[ch] = bytes.fromhex(code)
    return enc


def encode(enc, s):
    return b"".join(enc[c] for c in s)


if __name__ == "__main__":
    enc = table()
    rom = next((ROOT / "rom").glob("*.sfc")).read_bytes()
    for phrase in sys.argv[1:]:
        try:
            pat = encode(enc, phrase)
        except KeyError as e:
            print(phrase, "not encodable:", e)
            continue
        hits = []
        pos = rom.find(pat)
        while pos >= 0 and pos < 0x60000:
            hits.append(f"C{pos >> 16:X}:{pos & 0xFFFF:04X}")
            pos = rom.find(pat, pos + 1)
        for f in sorted((ROOT / "work/blocks").glob("*.bin")):
            d = f.read_bytes()
            p = d.find(pat)
            while p >= 0:
                hits.append(f"{f.stem}+{p:04X}")
                p = d.find(pat, p + 1)
        print(phrase, pat.hex(), hits[:14], len(hits))
