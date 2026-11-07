"""Put English into a ROM image: far strings in banks $A1+, far codes over the Japanese. docs/re/vwf.md.

apply(rom, rows) takes the dump and {row id: English} and returns (image bytes, block edits). Rows not listed stay Japanese.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import extract  # noqa: E402
import font  # noqa: E402
import unpack  # noqa: E402
from tbl import Table  # noqa: E402

FAR, BANK0, ROM_SIZE = 0xF0, 0x21, 0x400000  # file bank of the first far strings, also the table's bank
PAD = 0xF4  # the game's blank glyph: names trim it, list walks skip it
TABLE = 0x210000  # 3 bytes per string, lower half of the bank
LOC = re.compile(r"(?:b(\d+)\+|r)([0-9A-F]+):(\d+)")


def table():
    font.write()
    return Table.load(ROOT / "tbl/en.tbl")


class Far:
    """Far strings in the upper half of file banks $21+, CPU $A1+:8000: DB must keep low RAM in view."""

    def __init__(self, out):
        self.out, self.count, self.pos = out, 0, (BANK0 << 16) + 0x8000

    def number(self):
        """No byte a list walk or a name copy stops on: FF ends, F4+ pads."""
        n = self.count
        while n & 0xFF >= 0xF4 or n >> 8 >= 0xF4:
            n += 1
        self.count = n + 1
        return n

    def put(self, n, data):
        if self.pos & 0xFFFF < 0x8000 or (self.pos & 0xFFFF) + len(data) > 0x10000:
            self.pos = ((self.pos >> 16) + (self.pos & 0xFFFF != 0x8000 or self.pos < 0x10000)) * 0x10000 + 0x8000
        assert self.pos + len(data) <= ROM_SIZE, "far text full"
        self.out[self.pos:self.pos + len(data)] = data
        cpu = self.pos | 0x800000
        self.out[TABLE + n * 3:TABLE + n * 3 + 3] = cpu.to_bytes(3, "little")
        self.pos += len(data)


def place(span, start, n, code):
    """Far code at the front, the rest blanked; a closing FF stays for list walks."""
    keep = span[start + n - 1] == 0xFF
    span[start:start + n] = code + bytes([PAD]) * (n - len(code) - keep) + (b"\xff" if keep else b"")


def apply(rom, english):
    t = table()
    out = bytearray(rom) + b"\xff" * (ROM_SIZE - len(rom))
    blocks = {i: bytearray(unpack.load(rom, src, size)[0]) for i, src, size, _, _ in unpack.entries(rom)}
    rows = [r for sec in extract.load(rom).rows.values() for r in sec]
    far = Far(out)
    number = {}
    at = {}  # (block, start) -> row id, to follow a row with no end code into the next one
    for i, loc, jp in rows:
        m = LOC.fullmatch(loc)
        at[(m[1], int(m[2], 16))] = i
    for i, loc, jp in rows:
        if i in english:
            number[i] = far.number()
    for i, loc, jp in rows:
        if i not in english:
            continue
        m = LOC.fullmatch(loc)
        block, start, n = m[1], int(m[2], 16), int(m[3])
        span = blocks[int(block)] if block else out
        data = t.encode(english[i])
        if span[start + n - 1] != 0xFF and not loc.startswith("r"):  # runs into the next row
            nxt = at.get((block, start + n))
            if nxt in number:
                data += bytes([FAR, number[nxt] & 255, number[nxt] >> 8])
            else:
                data += b"\xff"
        elif not data.endswith(b"\xff"):
            data += b"\xff"
        if len(data) <= n and n < 3:
            span[start:start + len(data)] = data
            continue
        assert n >= 3, (i, n)
        far.put(number[i], data)
        place(span, start, n, bytes([FAR, number[i] & 255, number[i] >> 8]))
    blocks = {b: bytes(d) for b, d in blocks.items() if str(b) in {LOC.fullmatch(loc)[1] for i, loc, _ in rows if i in english}}
    print(f"far strings {far.count}, end {far.pos:06X}")
    return out, blocks


MARK = "The quick brown fox jumps over the lazy dog. "
SPLIT = re.compile(r"(\{[^}]*\}|\[[0-9A-F]{2}\])")


def marker(rows):
    """{id: `<id>` text}: control codes stay where they are, each text run becomes filler twice its length."""
    out = {}
    for i, loc, jp in rows:
        if int(loc.split(":")[1]) < 3:  # too short for a far code; these English rows fit in place
            continue
        first, parts = True, []
        for piece in SPLIT.split(jp):
            if not piece or SPLIT.fullmatch(piece):
                parts.append(piece.replace("[F4]", " "))
            elif first:
                first = False
                parts.append(f"<{i}>")
            else:
                parts.append((MARK * 9)[:len(piece) * 2])
        s = "".join(parts)
        out[i] = s if not first else "<" + i + ">" + s
    return out
