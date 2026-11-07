"""Recon: find string blocks and raw strings.

    textsweep.py summary          table-headed blocks + raw banks with clean strings
    textsweep.py show BLOCK|rOFF [LEN]   decode a block (or raw ROM from file offset, prefix r) as FF-ended strings
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from tbl import Table  # noqa: E402

T = Table.load(ROOT / "tbl/jp.tbl")
HIRA = re.compile(r"[ぁ-ん]")
KANJI = re.compile(r"[一-龥]")
KATA = re.compile(r"[ァ-ヴー]")
NOISE = re.compile(r"[0-9A-Z🅐-🅡Ⓐ-Ⓨ♂♀／％．＆]")


def table_block(data):
    """u16 offset table at +0 whose entries are increasing and each string ends in FF. Returns offsets or None."""
    if len(data) < 6:
        return None
    first = data[0] | data[1] << 8
    if first < 2 or first & 1 or first >= len(data):
        return None
    offs = [data[i] | data[i + 1] << 8 for i in range(0, first, 2)]
    if any(a > b for a, b in zip(offs, offs[1:])) or offs[-1] >= len(data):
        return None
    if any(data[o - 1] != 0xFF for o in offs[1:]) or data[-1] != 0xFF and data[-2] != 0xFF:
        return None
    return offs


def clean(s):
    """A real string: kana heavy, no mix of latin/symbols with kana that random data makes."""
    plain = re.sub(r"\{[^}]*\}", "", s)
    n = len(plain)
    if n < 2:
        return False
    jp = len(HIRA.findall(plain)) + len(KATA.findall(plain)) + len(KANJI.findall(plain))
    return jp >= 2 and len(NOISE.findall(plain)) * 8 <= n and jp * 10 >= n * 8


def strings(data, base=0):
    pos, n = 0, len(data)
    while pos < n:
        end = data.find(b"\xff", pos)
        if end < 0:
            break
        if end - pos >= 2:
            try:
                s, used = T.decode(data, pos, length=end - pos + 1)
            except Exception:
                s = "["
            if "[" not in s and clean(s):
                yield base + pos, s
        pos = end + 1


if __name__ == "__main__":
    rom = next((ROOT / "rom").glob("*.sfc")).read_bytes()
    if sys.argv[1] == "summary":
        for b in range(0x20):
            hits = list(strings(rom[b * 0x10000:(b + 1) * 0x10000]))
            print(f"bank {b:02X}: {len(hits):4d} strings {sum(len(s) for _, s in hits):6d} chars  "
                  + " / ".join(s[:14] for _, s in hits[:4]))
        for f in sorted((ROOT / "work/blocks").glob("*.bin")):
            data = f.read_bytes()
            offs = table_block(data)
            hits = list(strings(data))
            if offs and hits:
                print(f"tbl {f.stem}: n={len(offs):3d} size={len(data):04X} clean={len(hits):3d} "
                      f"chars={sum(len(s) for _, s in hits):5d}  {hits[0][1][:24]}")
            elif len(hits) >= 5:
                print(f"blk {f.stem}: size={len(data):04X} clean={len(hits):3d} "
                      f"chars={sum(len(s) for _, s in hits):5d}  {hits[0][1][:24]}")
    else:
        a = sys.argv[2]
        if a.startswith("r"):
            off = int(a[1:], 16)
            n = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0x400
            data, base = rom[off:off + n], off
        else:
            data, base = (ROOT / f"work/blocks/{int(a):03d}.bin").read_bytes(), 0
            n = int(sys.argv[3], 16) if len(sys.argv) > 3 else len(data)
            data = data[:n]
        for p, s in strings(data, base):
            print(f"{p:06X} {s}")
