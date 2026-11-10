"""Label rects: `W H tiles` records for the blit $C21CF0, tile numbers of block 001, kana that no string table holds. docs/re/vwf.md.

rows(rom) gives script/label.tsv rows: id, loc, jp, one {nl}-separated piece per kana run. apply() writes English as tiles from the sheet: in place
when it fits, else a far rect (`F0 lo hi`, wider copy in far banks). rects.py LOG -> kana rects in a tools/debug/rectlog.lua log.
"""
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOJUON = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんっゃゅょ"
KATA = "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモ"
TILE = {0x30 + i: c for i, c in enumerate(GOJUON)} | {0x62 + i: c for i, c in enumerate(KATA)}
TILE |= dict(zip(range(0x85, 0x99), "ラリルレロヤユヨワヲンッャュョァィゥェォ"))
TILE |= {0x29: "ー", 0x2B: "／"} | {i + 1: c for i, c in enumerate("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")}
YEAR, YEAR_RECT = 0xF7, 0x04CBDF  # 年 (G4) is text only in its own rect, the config play time "1 年" (in the status box code fills it)
TILE[YEAR] = "年"
MARK = {0x27: "゙", 0x28: "゚", 0xE8: "゙", 0xE9: "゚"}  # tile on the row above; E8, E9 are for windows that fill with E7
BLANK = (0x00, 0x26, 0xE7)
# File offsets. COPIED: code copies these to RAM and patches numbers in, so they can't take a far code: English stays inside W.
RECTS = [0x00A0DA, 0x00A14C, 0x0480F7, 0x0499DB, 0x04B4A0, 0x04B4AA, *range(0x04B596, 0x04B607, 14), 0x04B7BF, 0x04B80C, 0x04B814, 0x04B819,
         0x04B837, 0x04B845, 0x04B859, 0x04B863, 0x04B871, 0x04CBD1, 0x04CBDF, 0x04CBE2, 0x04CC06, 0x04CC16, 0x04CC1C, 0x04CC24, 0x04CC2E, 0x04CC34,
         *range(0x04CC46, 0x04CCA1, 18), 0x0597CC, 0x0597F0, 0x0597FA, 0x059804, *range(0x0598A6, 0x059941, 14), 0x05BC09, 0x05BC11, 0x05BC19]
COPIED = {0x00A0DA, 0x00A14C, 0x0499DB, 0x04B4AA, 0x04B871}


def text_tile(t):
    return 0x30 <= t < 0x99


def runs(rom, p):
    """Kana runs of the rect at p: (row, first col, end col, jp)."""
    w, h = rom[p], rom[p + 1]
    body = rom[p + 2:p + 2 + w * h]
    text = lambda t: text_tile(t) or (p == YEAR_RECT and t == YEAR)
    out = []
    for y in range(h):
        x = 0
        while x < w:
            if not text(body[y * w + x]) and not (body[y * w + x] == 0x29 and x):
                x += 1
                continue
            a = x
            while x < w and (text(body[y * w + x]) or body[y * w + x] == 0x29):
                x += 1
            s = "".join(TILE.get(body[y * w + i], "?") + (MARK.get(body[(y - 1) * w + i], "") if y else "") for i in range(a, x))
            out.append((y, a, x, unicodedata.normalize("NFC", s)))
    return out


def rows(rom):
    return [(f"rect{p:06X}", f"r{p:06X}:{2 + rom[p] * rom[p + 1]}", "{nl}".join(r[3] for r in runs(rom, p))) for p in RECTS] + cell_rows(rom)


# Recruit status box: $C2:B3DD copies rect $A0DA to $1111 and patches in headerless cell tables (no W H): race at $C0:A056 + 12 * race
# (6 cells x 2 rows), job at $C0:A09E + 10 * job (5 x 2), upper row dakuten. Entry 0 of each is a ????? placeholder. English is lower
# row only, from the entry's first byte: asm/vwf.asm makes the code read 7 race / 6 job cells there (found from a player bug report).
CELLS = {0x00A056: (12, 6, 7), 0x00A09E: (10, 5, 6)}  # table: (stride, JP cells a row, English cells)


def cell_rows(rom):
    out = []
    for t, (stride, w, _) in CELLS.items():
        for p in range(t + stride, t + 6 * stride, stride):
            top, low = rom[p:p + w], rom[p + w:p + 2 * w]
            s = "".join(TILE[b] + MARK.get(a, "") for a, b in zip(top, low) if b not in BLANK)
            out.append((f"cell{p:06X}", f"r{p:06X}:{stride}", unicodedata.normalize("NFC", s)))
    return out


def cells(out, english):
    for i, _, _ in cell_rows(out):
        if i not in english:
            continue
        p = int(i[4:], 16)
        stride, _, room = next(v for t, v in CELLS.items() if t < p < t + 6 * v[0])
        t = tiles(english[i], 0)
        assert len(t) <= room, (i, english[i], f"room for {room}")
        out[p:p + stride] = bytes(t + [0] * (stride - len(t)))


def tiles(s, fill):
    """English as sheet tiles: capitals and digits are the game's, a-z are put in by font.small_sheet."""
    out = []
    for c in s:
        if c == " ":
            out.append(fill)
        elif c.isdigit():
            out.append(1 + int(c))
        elif "A" <= c <= "Z":
            out.append(0x0B + ord(c) - 65)
        elif "a" <= c <= "z":
            out.append(0x30 + ord(c) - 97)
        else:
            out.append({"/": 0x2B, "-": 0x29}[c])
    return out


def rebuild(rom, p, en):
    """The rect with its kana runs replaced by the {nl}-separated English pieces: (W, H, body)."""
    w, h = rom[p], rom[p + 1]
    body = list(rom[p + 2:p + 2 + w * h])
    fill = 0x26 if 0x26 in body else 0
    found = runs(rom, p)
    parts = en.split("{nl}")
    assert len(parts) == len(found), (hex(p), parts)
    grid = [body[y * w:y * w + w] for y in range(h)]
    for (y, a, b, _), s in zip(found, parts):
        for x in range(a, b):
            grid[y][x] = fill
            if y and grid[y - 1][x] in MARK:
                grid[y - 1][x] = 0xE7 if grid[y - 1][x] >= 0xE8 else 0
        t = tiles(s, fill)
        grid[y].extend([fill] * (a + len(t) - len(grid[y])))
        assert all(v in BLANK for v in grid[y][b:a + len(t)]), (hex(p), s, "runs into a number")
        grid[y][a:a + len(t)] = t
    width = max(len(r) for r in grid)
    for r in grid:
        r.extend([r[-1] if r[-1] in BLANK else fill] * (width - len(r)))
    return width, h, bytes(v for r in grid for v in r)


# Status box, 21x2, copied to $1111 by $C2:B7CF. The code writes money (5 digits), years and months (2 each) into it; asm/vwf.asm moves
# those writes to the cells below (row 0 at $1113, row 1 at $1128). JP: のこり over 1年 0ヶ月 (年 ヶ月 are G4 tiles F7-F9), money + シリング
# under it. English: money + "Shillings" on row 0, "<time left> 1yr 0mo" on row 1. yr/mo: flagged D4 abbreviation, "years"/"months" don't fit.
STATUS = 0x04B4AA
# party panel job rects: pointers $C4:B520, each 8x2 tiles (6 job tiles + 2 icon), job cells from the 04B485/04B492 sheets.
# Mage's two rows (rect $C4:B54E) used 魔 術 + 戦士's 士 (player bug report: "Mage ght").
JOB_MAGE = (0x04B550, 0x04B558)
STATUS_CELLS = {"money": (0, 2, 5), "years": (1, 11, 2), "months": (1, 16, 2)}  # row, col, digits: asm writes at $1113 + 21 * row + col


def status(rom, en):
    left, money = en.split("{nl}")
    w, h = rom[STATUS], rom[STATUS + 1]
    grid = [[0x26] * w for _ in range(h)]
    grid[0][:2], grid[1][:2] = rom[STATUS + 2:STATUS + 4], rom[STATUS + 2 + w:STATUS + 4 + w]  # the purse icon
    for y, x, n in STATUS_CELLS.values():
        grid[y][x:x + n] = [0] * n
    for y, x, s in ((0, 8, money), (1, 2, left), (1, 13, "yr"), (1, 18, "mo")):
        t = tiles(s, 0x26)
        assert all(v == 0x26 for v in grid[y][x:x + len(t)]) and x + len(t) <= w, (s, "status box: no room")
        grid[y][x:x + len(t)] = t
    return bytes(v for r in grid for v in r)


def apply(out, english, far):
    """Far rects take a number from `far`, the same table as far strings."""
    if f"rect{RECTS[0]:06X}" in english:
        grid(out, far)
    cells(out, english)
    for p in JOB_MAGE:  # 魔術士: the 士 cell is 戦士's, "ght" of Knight in English; centred on blanks like the 2-cell jobs
        assert out[p:p + 6] in (bytes([0xDC, 0xDD, 0xE0, 0xE1, 0xC8, 0xC9]), bytes([0xDE, 0xDF, 0xE2, 0xE3, 0xCA, 0xCB])), hex(p)
        out[p:p + 6] = bytes([0xEC, *out[p:p + 4], 0xEC])
    for p in RECTS:
        en = english.get(f"rect{p:06X}")
        if en is None:
            continue
        if p == STATUS:
            out[p + 2:p + 2 + out[p] * out[p + 1]] = status(out, en)
            continue
        w, h, body = rebuild(out, p, en)
        if w == out[p]:
            out[p + 2:p + 2 + len(body)] = body
            continue
        assert p not in COPIED, (hex(p), en, f"{w} tiles, room for {out[p]}")
        n = far.number()
        far.put(n, bytes([w, h]) + body)
        out[p:p + 3] = bytes([0xF0, n & 255, n >> 8])


# Name entry: pages 0, 1 (hiragana, katakana) become capitals and small letters. Grid = two rects, 7 rows of 10 cells; code table = 68 u16, code + a
# dakuten flag, the same order. The romaji page stays. The last 3 cells are the commands すすむ, もどる, おわる (Next, Back, Done). docs/re/vwf.md.
GRID = ((0x059A8B, 0x059B19, 0x0595F9), (0x059B84, 0x059C12, 0x059681))
GRID_COLS = (0, 2, 4, 6, 8, 11, 13, 15, 17, 19)
NO_CHAR = 0xF4
ROMAJI_LOW = 0x059D0B
DOT_MARK = 0x059D78  # body of the 1x1 rect $85:9D76 (drawn by $C1:4AB8): ゛ over もどる's と, left as a stray mark before "Done"
CURSOR, CURSOR_X = (0x05959C, 0x05959E, 0x0595A0), (0x78, 0xA0, 0xC8)  # cursor x of the three commands: the words are longer, so they sit further left
TITLE = (0x0594C6, 0x0594D8, 0x0594EA)  # the page's name: 4 big cells each of the glyph set below (cells 4p..4p+3)
# Glyph set ひらがなカタカナローマ字 (12 cells in the old 16 px font, drawn one per cell: asm fixed_check) the titles pick from.
# The tabs L and R name the pages, so every page's title reads NAME. Codes 0A-23 are the old font's capitals.
TITLE_SET, TITLE_GLYPHS = 0x05947C, bytes([0x17, 0x0A, 0x16, 0x0E] * 3 + [0xF4, 0xFF])


def grid_chars(base, first_code):
    """(chars, codes) for 60 cells: letters, then digits, then nothing."""
    chars = [chr(base + i) for i in range(26)] + list("0123456789")
    codes = [first_code + i for i in range(26)] + list(range(10))
    return chars + [" "] * (60 - len(chars)), codes + [NO_CHAR] * (60 - len(codes))


def grid(out, far):
    for page, (top, low, table) in enumerate(GRID):
        chars, codes = grid_chars(65 + 32 * page, 0x24 if page else 0x0A)
        for k, c in enumerate(codes + [NO_CHAR] * 5):
            out[table + k * 2:table + k * 2 + 2] = bytes([c, 0])
        w, h = out[top], out[top + 1]
        body = bytearray(w * h)
        for r in range(4):
            for k, x in enumerate(GRID_COLS):
                body[r * 2 * w + x] = tiles(chars[r * 10 + k], 0)[0]
        out[top + 2:top + 2 + w * h] = body
        lw, lh = 23, out[low + 1]
        body = bytearray(lw * lh)
        for r in range(2):
            for k, x in enumerate(GRID_COLS):
                body[r * 2 * lw + x] = tiles(chars[(4 + r) * 10 + k], 0)[0]
        commands(body, lw)
        n = far.number()
        far.put(n, bytes([lw, lh]) + body)
        out[low:low + 3] = bytes([0xF0, n & 255, n >> 8])
    w, h = out[ROMAJI_LOW], out[ROMAJI_LOW + 1]
    body = bytearray(out[ROMAJI_LOW + 2:ROMAJI_LOW + 2 + w * h])
    for x in range(10, w):  # すすむ もどる おわる, the same words as the other pages
        body[4 * w + x] = 0
    commands(body, w)
    n = far.number()
    far.put(n, bytes([w, h]) + body)
    out[ROMAJI_LOW:ROMAJI_LOW + 3] = bytes([0xF0, n & 255, n >> 8])
    assert out[DOT_MARK - 2:DOT_MARK + 1] == b"\x01\x01\x27"
    out[DOT_MARK] = 0
    for at, x in zip(CURSOR, CURSOR_X):
        out[at] = x
    assert out[TITLE_SET + len(TITLE_GLYPHS) - 1] == 0xFF
    out[TITLE_SET:TITLE_SET + len(TITLE_GLYPHS)] = TITLE_GLYPHS


def commands(body, w):
    for word, x in (("Next", 6), ("Back", 11), ("Done", 16)):
        body[4 * w + x:4 * w + x + 4] = bytes(tiles(word, 0))


def marker(rom):
    """Each run shows the rect's offset, cut to the room a copied rect has."""
    out = {}
    for p in RECTS:
        parts = []
        for k, (y, a, b, _) in enumerate(runs(rom, p)):
            s = f"{p & 0xFFFF:04X}{k}"
            parts.append(s[:b - a] if p in COPIED else s)
        out[f"rect{p:06X}"] = "{nl}".join(parts)
    return out


if __name__ == "__main__":
    seen = {}
    for line in Path(sys.argv[1]).read_text().splitlines():
        ret, src, w, h, *b = line.split()
        b = [int(x, 16) for x in b]
        w, h = int(w), int(h)
        n = sum(text_tile(t) for t in b)
        if n >= 2 and n * 6 >= len(b) and not re.match("85:9[89]", src):
            seen.setdefault((src, tuple(b)), (ret, w, h))
    for (src, b), (ret, w, h) in sorted(seen.items()):
        print(ret, src, f"{w}x{h}", " / ".join("".join(TILE.get(t, ".") for t in b[y * w:y * w + w]) for y in range(h)))
