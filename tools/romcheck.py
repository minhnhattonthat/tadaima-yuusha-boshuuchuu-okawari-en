"""ROM-level gate (skill phase 7): every byte the build changed lies in a range the sources say it may write.

    python -X utf8 tools/romcheck.py [BUILT]     default build/tadaima_en.sfc; build.py runs it after assembling

Allowed ranges come from the inputs, never from the diff: text row spans (raw `r` rows and label rects), the name-entry
grid tables, the LZ block slots (repack.py), the bytes asm/vwf.asm assembles (asar run on blank 0x00 and 0xFF images),
and the expanded banks $20-$3F. Writes build/ranges.txt (one range + reason a line) and runs romdiff.check on it.
shortcut: ranges only, no per-write log (romdiff --writes); overlapping rows are caught by tests/test_extract.py, and the
expanded banks' layout by asserts (insert.Far.number, insert.images, ranges() below). Add the log if a write ever lands on
the wrong original bytes.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import extract  # noqa: E402
import insert  # noqa: E402
import rects  # noqa: E402
import romdiff  # noqa: E402
import unpack  # noqa: E402


def asm_bytes():
    """Offsets asar writes: assembled onto an all-0x00 and an all-0xFF image, a byte either run changed."""
    hit = set()
    with tempfile.TemporaryDirectory() as d:
        for fill in (0x00, 0xFF):
            img = Path(d) / f"blank{fill:02X}.sfc"
            img.write_bytes(bytes([fill]) * insert.ROM_SIZE)
            code = subprocess.call([str(ROOT / "tools/asar/asar.exe"), "--fix-checksum=off", "--no-title-check",
                                    str(ROOT / "asm/vwf.asm"), str(img)], stdout=subprocess.DEVNULL)
            assert code == 0, "asar failed on a blank image"
            hit |= {i for i, b in enumerate(img.read_bytes()) if b != fill}
    return hit


def runs(offsets):
    out, lo = [], None
    for i in sorted(offsets):
        if lo is None or i != hi + 1:
            if lo is not None:
                out.append((lo, hi))
            lo = i
        hi = i
    return out + ([(lo, hi)] if lo is not None else [])


def ranges(rom):
    """[(lo, hi inclusive, reason)]."""
    out = []
    for sec, rows in extract.load(rom).rows.items():
        for i, loc, _ in rows:
            m = insert.LOC.fullmatch(loc)
            if not m[1]:  # raw row in the ROM; b rows live in blocks, covered below
                lo = int(m[2], 16)
                out.append((lo, lo + int(m[3]) - 1, f"row {i}"))
    for i, loc, _ in rects.rows(rom):
        lo, n = int(loc[1:7], 16), int(loc.split(":")[1])
        out.append((lo, lo + n - 1, f"label {i}"))
    for top, low, table in rects.GRID:
        out.append((table, table + 65 * 2 - 1, "name-entry code table"))
        out.append((top, top + 2 + rom[top] * rom[top + 1] - 1, "name-entry grid"))
        out.append((low, low + 2, "name-entry far rect"))
    out.append((rects.ROMAJI_LOW, rects.ROMAJI_LOW + 2, "romaji far rect"))
    out += [(a, a, "name-entry cursor x") for a in rects.CURSOR]
    out.append((rects.TITLE_SET, rects.TITLE_SET + len(rects.TITLE_GLYPHS) - 1, "name-entry title glyph set"))
    for i, src, size, _, _ in unpack.entries(rom):
        off = src & 0x3FFFFF
        used = unpack.load(rom, src, size)[1]
        out.append((off, off + (used or size) - 1, f"block {i}"))
        out.append((unpack.TABLE + i * 8, unpack.TABLE + i * 8 + 2, f"block {i} src (repack.MOVED)"))
    asm = asm_bytes()
    # expanded banks: asm $E0:0000-7FFF, pointer table $21 and image table $22 lower halves (asserted in insert.Far.number),
    # far strings upper halves of $21+, name images lower halves of $23+ (insert.images)
    assert all(i < len(rom) or 0x200000 <= i < 0x208000 for i in asm), "asm/vwf.asm writes past $E0:7FFF in the expanded banks"
    out += [(lo, hi, "asm/vwf.asm") for lo, hi in runs(asm)]
    out.append((0x00FFDC, 0x00FFDF, "header checksum (build.py)"))
    out.append((len(rom), insert.ROM_SIZE - 1, "expanded banks"))
    return out


def main(argv):
    built = Path(argv[0]) if argv else ROOT / "build/tadaima_en.sfc"
    rom = next((ROOT / "rom").glob("*.sfc")).read_bytes()
    rs = ranges(rom)
    (ROOT / "build/ranges.txt").write_text("".join(f"{lo:06X}-{hi:06X}  # {why}\n" for lo, hi, why in rs), encoding="utf-8")
    allowed = set()
    for lo, hi, _ in rs:
        allowed.update(range(lo, hi + 1))
    errs, ok = romdiff.check(rom, built.read_bytes(), allowed, [])
    print("\n".join(errs) if errs else f"romcheck ok: {ok} changed bytes, all inside {len(rs)} allowed ranges")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
