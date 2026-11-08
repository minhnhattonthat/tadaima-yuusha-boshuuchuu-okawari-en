"""The English font (fonts/vwf.txt) -> tbl/en.tbl and build/vwf_*.bin. Code map in docs/re/vwf.md.

Codes: A-Z keep the game's 0A-23, a-z take 24-3D, digits for text 60-69, the rest of ASCII from 3E. 00-09 stay the game's fixed
digits (code-drawn numbers line up by cell). asm/vwf.asm draws 0A-69 from this font, anything else the old way.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIRST, END, TOP = 0x0A, 0x6A, 2  # first code, end code, blank rows above the art
MAX_INK = 8  # asm/vwf.asm spreads a glyph over 3 tile columns: 8 px and the shadow


def load():
    """{char: (rows, advance)}. Rows: ints, bit 7 = left pixel."""
    glyphs, cur = {}, None
    for line in (ROOT / "fonts/vwf.txt").read_text(encoding="utf-8").splitlines():
        if line.startswith("== "):
            parts = line[3:].split()
            cur = " " if parts[0] == r"\s" else parts[0]
            glyphs[cur] = [[], int(parts[1]) if len(parts) > 1 else None]
        elif cur and line:  # '#' lines before the first glyph are comments, after it they are ink
            glyphs[cur][0].append(line)
    out = {}
    for ch, (art, adv) in glyphs.items():
        ink = max((len(r.rstrip(".")) for r in art), default=0)
        assert ink <= MAX_INK, (ch, ink)
        rows = [sum(0x80 >> x for x, c in enumerate(r) if c == "#") for r in art]
        out[ch] = (rows, adv if adv is not None else ink + 1)
    return out


def codes():
    """{char: code}"""
    m = {chr(65 + i): 0x0A + i for i in range(26)} | {chr(97 + i): 0x24 + i for i in range(26)} | {chr(48 + i): 0x60 + i for i in range(10)}
    rest = [c for c in map(chr, range(32, 127)) if c not in m]
    return m | {c: 0x3E + i for i, c in enumerate(rest)}


SMALL_BG, SMALL_LOWER, POOL_START, POOL_END = 0x26, 0x30, 0x4A, 0xA0  # blank tile, a-z tiles, tiles names are sent to (asm/vwf.asm)
SMALL_DOT = 0x2A  # the game's ・, only in the rank label NO・1 ($C2:B778): redrawn as a full stop for "No.1"


def small():
    """Names on the tilemap path: {char: (8 rows, advance)} from fonts/spleen-5x8.bdf, trimmed to proportional."""
    out, code, rows = {}, None, None
    for line in (ROOT / "fonts/spleen-5x8.bdf").read_text(encoding="ascii").splitlines():
        if line.startswith("ENCODING "):
            code = int(line.split()[1])
        elif line == "BITMAP":
            rows = []
        elif line == "ENDCHAR":
            if 32 <= code < 127:
                ink = max((8 - (r & -r).bit_length() + 1 for r in rows if r), default=0)
                left = min((8 - r.bit_length() for r in rows if r), default=0)
                out[chr(code)] = ([r << left & 0xFF for r in rows], ink - left + 1 if ink else 3)
            rows = None
        elif rows is not None:
            rows.append(int(line, 16))
    return out


def planar(px):
    """8x8 pixel values -> 32 bytes of SNES 4bpp."""
    t = bytearray(32)
    for y, row in enumerate(px):
        for x, v in enumerate(row):
            for p in range(4):
                t[(p >> 1) * 16 + y * 2 + (p & 1)] |= (v >> p & 1) << (7 - x)
    return bytes(t)


def small_width(text):
    g = small()
    return sum(g[c][1] for c in text)


def small_tiles(text, cells):
    """Text as 4bpp tiles, ink 15 and shadow 14 like the game's small font: at least 3 tiles, clipped to `cells`."""
    g, w = small(), cells * 8
    px = [[0] * w for _ in range(8)]
    pen = 0
    for c in text:
        rows, adv = g[c]
        for y, r in enumerate(rows):
            for x in range(8):
                if r >> (7 - x) & 1:
                    for dx, dy in ((1, 0), (0, 1), (1, 1)):
                        if pen + x + dx < w and y + dy < 8 and not px[y + dy][pen + x + dx]:
                            px[y + dy][pen + x + dx] = 14
                    if pen + x < w:
                        px[y][pen + x] = 15
        pen += adv
    n = max(3, min(cells, (min(pen, w) + 7) // 8))
    return b"".join(planar([r[i * 8:i * 8 + 8] for r in px]) for i in range(n))


def small_sheet(sheet):
    """Block 001 with a-z at the tiles asm/vwf.asm maps them to and the name tiles blanked. A kana left in the script can't pass for a word."""
    out = bytearray(sheet)
    g = small()
    for i, ch in [*enumerate(map(chr, range(97, 123))), (SMALL_DOT - SMALL_LOWER, ".")]:
        rows = g[ch][0]
        px = [[0] * 8 for _ in range(8)]
        for y, r in enumerate(rows):
            for x in range(7):
                if r >> (7 - x) & 1:
                    px[y][x] = 15
                    if y < 7 and not px[y + 1][x + 1]:
                        px[y + 1][x + 1] = 14
                    if not px[y][x + 1]:
                        px[y][x + 1] = 14
        out[(SMALL_LOWER + i) * 32:(SMALL_LOWER + i + 1) * 32] = planar(px)
    out[POOL_START * 32:POOL_END * 32] = bytes((POOL_END - POOL_START) * 32)
    return bytes(out)


def advances():
    return {ch: adv for ch, (_, adv) in load().items()}


def write():
    glyphs, code = load(), codes()
    assert len(code) == 95 and max(code.values()) < END
    by_code = {v: k for k, v in code.items()}
    font, width = bytearray(16 * (END - FIRST)), bytearray(END - FIRST)
    for c, ch in by_code.items():
        rows, adv = glyphs[ch]
        i = c - FIRST
        font[i * 16 + TOP:i * 16 + TOP + len(rows)] = bytes(rows)
        width[i] = adv
    out = ROOT / "build"
    out.mkdir(exist_ok=True)
    (out / "vwf_font.bin").write_bytes(font)
    (out / "vwf_width.bin").write_bytes(width)
    ctrl = [ln for ln in (ROOT / "tbl/jp.tbl").read_text(encoding="utf-8").splitlines() if "={" in ln and not ln.startswith("#")]
    rows = ["# generated by tools/font.py; do not edit", "F0={far:2}", "F1={call:2}","F5={cell}", *ctrl]
    rows += [f"{c:02X}=" + (r"\s" if ch == " " else ch) for c, ch in sorted(by_code.items())]
    (ROOT / "tbl/en.tbl").write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    sys.exit(write())
