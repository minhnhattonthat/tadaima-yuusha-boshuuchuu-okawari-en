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
import rects  # noqa: E402
import unpack  # noqa: E402
from tbl import Table  # noqa: E402

FAR, BANK0, ROM_SIZE = 0xF0, 0x21, 0x400000  # file bank of the first far strings, also the table's bank
CALL = 0xF1  # far string, then the text goes on after the code (asm/vwf.asm far_read .call)
PAD = 0xF4  # the game's blank glyph: names trim it, list walks skip it
TABLE = 0x210000  # 3 bytes per string, lower half of the bank
LOC = re.compile(r"(?:b(\d+)\+|r)([0-9A-F]+):(\d+)")
IMG, IMG_DATA = 0x220000, 0x230000  # lower halves of banks: far strings keep to the upper ones
NAMES = ("item", "equip", "spell", "char")  # rows shown through the tilemap path
LINES = {"desc_item": 10, "desc_equip": 10, "desc_spell": 10, "bio": 10}  # the same path, a far code per line: section -> cells a line
CODE = re.compile(r"\{[^}]*\}|\[[0-9A-F]{2}\]")
CODE_NL = re.compile(r"\{nl\}")
COST = re.compile(r"(?:\[F4\]|[0-9])*／.*")  # spell record: the cost after the name stays the game's bytes, so it lines up


def table():
    font.write()
    return Table.load(ROOT / "tbl/en.tbl")


class Far:
    """Far strings in the upper half of file banks $21+, CPU $A1+:8000: DB must keep low RAM in view."""

    def __init__(self, out):
        self.out, self.count, self.pos = out, 0, (BANK0 << 16) + 0x8000

    def number(self):
        """No byte a list walk or a name copy stops on (FF ends, F4+ pads), nor one the tilemap path reads as a code (F0, F1)."""
        n = self.count
        while n & 0xFF >= 0xF0 or n >> 8 >= 0xF0:
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
    secs = extract.load(rom).rows
    by_line = {r[0]: LINES[sec] for sec in LINES for r in secs[sec]}
    shop = {r[0] for r in secs["shop"]}
    shown = {}  # far number -> (text, cells) for images()
    extra = []  # (far number, row id) of list records, for far.tsv
    for i, loc, jp in rows:
        m = LOC.fullmatch(loc)
        at[(m[1], int(m[2], 16))] = i
    for i, loc, jp in rows:
        if i in english and i not in by_line:
            number[i] = far.number()
    for i, loc, jp in rows:
        if i not in english:
            continue
        if i in by_line:
            lines_in(out, far, shown, t, i, loc, jp, english[i], by_line[i])
            continue
        if i.startswith("spell") and COST.search(jp):
            keep = len(extract.T.encode(COST.search(jp)[0]))
            loc = f"{loc.split(':')[0]}:{int(loc.split(':')[1]) - keep}"
            shown[number[i]] = (english[i], int(loc.split(":")[1]))
            data = t.encode(english[i]) + b"\xff"
            far.put(number[i], data)
            start = int(LOC.fullmatch(loc)[2], 16)
            out[start:start + 3] = bytes([FAR, number[i] & 255, number[i] >> 8])
            n = int(loc.split(":")[1])
            out[start + 3:start + n] = bytes([PAD]) * (n - 3)
            continue
        m = LOC.fullmatch(loc)
        block, start, n = m[1], int(m[2], 16), int(m[3])
        span = blocks[int(block)] if block else out
        if i in shop and extract.fixed_list(span, start, start + n) == start + n:
            records_in(span, far, extra, shown, t, i, start, n, english[i])
            continue
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
    rects.apply(out, english, far)
    blocks[1] = bytearray(font.small_sheet(bytes(blocks[1])))
    shown |= {number[i]: (english[i], int(loc.split(":")[1])) for i, loc, _ in rows if i in english and i.startswith(NAMES) and number[i] not in shown}
    images(out, far.count, shown)
    edited = {LOC.fullmatch(loc)[1] for i, loc, _ in rows if i in english} | {"1"}
    blocks = {b: bytes(d) for b, d in blocks.items() if str(b) in edited}
    print(f"far strings {far.count}, end {far.pos:06X}")
    (ROOT / "build/far.tsv").write_text("".join(f"{n}\t{i}\n" for i, n in [*number.items(), *extra]), encoding="utf-8")  # for tools/windows.py
    return out, blocks


def records_in(span, far, extra, shown, t, i, start, n, en):
    """A place list: `name FE` records of 10 bytes, copied 10 at a time into a slot ($C2:D4DE, $C2:D22C). A call code per
    record: $C2:D4AB appends FE 危険度 ★ after the 10 bytes, so the text must go on after the name."""
    names = en.split("{nl}")
    for k in range(n // 11):
        s = names[k].strip() if k < len(names) else ""
        q = start + k * 11
        code = b""
        if s:
            f = far.number()
            far.put(f, t.encode(s) + b"\xff")
            extra.append((i, f))
            shown[f] = (s, 10)
            code = bytes([CALL, f & 255, f >> 8])
        span[q:q + 10] = code + bytes([PAD]) * (10 - len(code))


def lines_in(out, far, shown, t, i, loc, jp, en, cells):
    """A description in a raw range: `F0 a b FE F0 c d .. F4.. FF`, one far code per line, in the row's own bytes. 4 bytes a line."""
    m = LOC.fullmatch(loc)
    start, size = int(m[2], 16), int(m[3])
    text = en.removesuffix("{end}").split("{nl}")
    # the box is blitted as tall as its lines: a line dropped (even an empty one) leaves the last description's tiles there
    text += [""] * (jp.count("{nl}") + 1 - len(text))
    while text and not text[-1] and len(text) > jp.count("{nl}") + 1:
        text.pop()
    cost = lambda ls: sum(3 if s else 0 for s in ls) + len(ls) - 1
    if cost(text) > size - 1:
        print(f"{i}: {size} bytes hold fewer than {len(text)} lines")
        while cost(text) > size - 1:
            text.pop()
    code = bytearray()
    for k, s in enumerate(text):
        if s:
            n = far.number()
            far.put(n, t.encode(s) + b"\xff")
            shown[n] = (s, cells)
            code += bytes([FAR, n & 255, n >> 8])
        code += b"\xfe" if k < len(text) - 1 else b""
    out[start:start + size - 1] = code + bytes([PAD]) * (size - 1 - len(code))


def images(out, count, rows):
    """Far numbers shown on the tilemap path: each gets its text as tiles. Table entry: u24 source, tile count. docs/re/vwf.md."""
    pos = IMG_DATA
    blank = pos
    pos += 3 * 32
    for n in range(count):
        at, tiles = blank, 3
        if n in rows:
            text, cells = rows[n]
            data = font.small_tiles(CODE.sub("", text), cells)
            if (pos & 0xFFFF) + len(data) > 0x8000:
                pos = (pos >> 16) + 1 << 16
            at, tiles = pos, len(data) // 32
            assert tiles <= 10, (n, text)  # asm/vwf.asm !ROOM: each pool ring keeps room for 10 tiles
            out[pos:pos + len(data)] = data
            pos += len(data)
        out[IMG + n * 4:IMG + n * 4 + 4] = (at | 0xC00000).to_bytes(3, "little") + bytes([tiles])
    assert pos < ROM_SIZE
    print(f"name images {len(rows)}, end {pos:06X}")


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
