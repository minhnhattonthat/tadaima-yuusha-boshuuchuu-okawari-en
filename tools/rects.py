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
MARK = {0x27: "゙", 0x28: "゚", 0xE8: "゙", 0xE9: "゚"}  # tile on the row above; E8, E9 are for windows that fill with E7
BLANK = (0x00, 0x26, 0xE7)
# File offsets. COPIED: code copies these to RAM and patches numbers in, so they can't take a far code: English stays inside W.
RECTS = [0x00A0DA, 0x00A14C, 0x0480F7, 0x0499DB, 0x04B4A0, 0x04B4AA, *range(0x04B596, 0x04B607, 14), 0x04B7BF, 0x04B80C, 0x04B814, 0x04B819,
         0x04B837, 0x04B845, 0x04B859, 0x04B863, 0x04B871, 0x04CBD1, 0x04CBE2, 0x04CC06, 0x04CC16, 0x04CC1C, 0x04CC24, 0x04CC2E, 0x04CC34,
         *range(0x04CC46, 0x04CCA1, 18), 0x0597CC, 0x0597F0, 0x0597FA, 0x059804, *range(0x0598A6, 0x059941, 14), 0x05BC09, 0x05BC11, 0x05BC19]
COPIED = {0x00A0DA, 0x00A14C, 0x0499DB, 0x04B4AA, 0x04B871}


def text_tile(t):
    return 0x30 <= t < 0x99


def runs(rom, p):
    """Kana runs of the rect at p: (row, first col, end col, jp)."""
    w, h = rom[p], rom[p + 1]
    body = rom[p + 2:p + 2 + w * h]
    out = []
    for y in range(h):
        x = 0
        while x < w:
            if not text_tile(body[y * w + x]) and not (body[y * w + x] == 0x29 and x):
                x += 1
                continue
            a = x
            while x < w and (text_tile(body[y * w + x]) or body[y * w + x] == 0x29):
                x += 1
            s = "".join(TILE.get(body[y * w + i], "?") + (MARK.get(body[(y - 1) * w + i], "") if y else "") for i in range(a, x))
            out.append((y, a, x, unicodedata.normalize("NFC", s)))
    return out


def rows(rom):
    return [(f"rect{p:06X}", f"r{p:06X}:{2 + rom[p] * rom[p + 1]}", "{nl}".join(r[3] for r in runs(rom, p))) for p in RECTS]


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


def apply(out, english, far):
    """Far rects take a number from `far`, the same table as far strings."""
    for p in RECTS:
        en = english.get(f"rect{p:06X}")
        if en is None:
            continue
        w, h, body = rebuild(out, p, en)
        if w == out[p]:
            out[p + 2:p + 2 + len(body)] = body
            continue
        assert p not in COPIED, (hex(p), en, f"{w} tiles, room for {out[p]}")
        n = far.number()
        far.put(n, bytes([w, h]) + body)
        out[p:p + 3] = bytes([0xF0, n & 255, n >> 8])


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
