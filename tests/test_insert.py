"""Far strings: every translated row leaves a far code that resolves to its English, in a bank where low RAM stays visible."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import extract  # noqa: E402
import insert  # noqa: E402
import rects  # noqa: E402

ROM = next((ROOT / "rom").glob("*.sfc"), None)
pytestmark = pytest.mark.skipif(ROM is None, reason="no dump in rom/")


@pytest.fixture(scope="module")
def built():
    rom = ROM.read_bytes()
    rows = [r for sec in extract.load(rom).rows.values() for r in sec]
    english = insert.marker(rows)
    image, blocks = insert.apply(rom, english)
    return rom, rows, english, image, blocks


def test_rects():
    """Labels: English in place when it fits, a far rect when wider, numbers in a copied rect untouched."""
    rom = ROM.read_bytes()
    assert all(r[2] for r in rects.rows(rom)), "a rect with no kana"
    out = bytearray(rom) + b"\xff" * (insert.ROM_SIZE - len(rom))
    p = 0x04CBD1  # プレイじかん, 6 wide
    wide, short = f"rect{p:06X}", "rect04CC16"
    far = insert.Far(out)
    rects.apply(out, {wide: "Play Time", short: "Fast"}, far)
    assert out[p] == insert.FAR
    cpu = int.from_bytes(out[insert.TABLE:insert.TABLE + 3], "little")
    assert out[cpu & 0x3FFFFF:(cpu & 0x3FFFFF) + 2] == bytes([9, 2])
    assert out[0x04CC16:0x04CC18] == rom[0x04CC16:0x04CC18] and out[0x04CC18] == 0x10  # F of Fast, in place
    with pytest.raises(AssertionError):
        rects.apply(bytearray(rom), {"rect04B4AA": "Remaining{nl}Shillings and more of them here"}, far)


def test_far_codes_resolve(built):
    rom, rows, english, image, blocks = built
    t = insert.table()
    secs = extract.load(rom).rows
    lined = {r[0] for sec in insert.LINES for r in secs[sec]} | {r[0] for r in secs["shop"] if is_list(rom, r[1])}
    for i, loc, _ in rows:
        if i not in english:
            continue
        m = insert.LOC.fullmatch(loc)
        span = blocks[int(m[1])] if m[1] else image
        start, n = int(m[2], 16), int(m[3])
        assert span[start] in (insert.FAR, insert.CALL), i
        num = span[start + 1] | span[start + 2] << 8
        assert span[start + 1] < 0xF0 and span[start + 2] < 0xF0, i
        cpu = int.from_bytes(image[insert.TABLE + num * 3:insert.TABLE + num * 3 + 3], "little")
        assert 0xA1 <= cpu >> 16 <= 0xBF and cpu & 0xFFFF >= 0x8000, i
        data = t.encode(english[i].split("{nl}")[0] if i in lined else english[i])  # descriptions: a far code per line
        assert image[cpu & 0x3FFFFF:(cpu & 0x3FFFFF) + len(data)] == data, i


def test_end_bytes_survive(built):
    """List walks count FF FF: only text may change, never a terminator."""
    rom, rows, english, image, blocks = built
    for i, loc, _ in rows:
        if i not in english:
            continue
        m = insert.LOC.fullmatch(loc)
        start, n = int(m[2], 16), int(m[3])
        if not m[1]:
            assert (rom[start + n - 1] == 0xFF) <= (image[start + n - 1] == 0xFF), i


def test_lines_keep_count(built):
    """A description keeps every line the Japanese had, an empty one as a bare FE: the box is blitted as tall as its lines."""
    rom, _, _, image, _ = built
    secs = extract.load(rom).rows
    for i, loc, jp in (r for sec in insert.LINES for r in secs[sec]):
        start, n = int(insert.LOC.fullmatch(loc)[2], 16), int(loc.split(":")[1])
        code, k, fe = image[start:start + n - 1], 0, 0
        while k < len(code):  # a far number byte may be FE: walk the codes
            fe += code[k] == 0xFE
            k += 3 if code[k] == insert.FAR else 1
        assert fe == jp.count("{nl}"), i
    p = 0x00B5F0  # てきにのろいをかける{nl}{end}: line 2 empty
    assert image[p] == insert.FAR and image[p + 3] == 0xFE


def is_list(rom, loc):
    m = insert.LOC.fullmatch(loc)
    data = insert.unpack.load(rom, *next((s, z) for b, s, z, _, _ in insert.unpack.entries(rom) if b == int(m[1])))[0]
    start, n = int(m[2], 16), int(m[3])
    return extract.fixed_list(data, start, start + n) == start + n


def test_place_lists_keep_records(built):
    """Place names are copied 10 bytes at a time ($C2:D4DE): every record gets its own far code and keeps its FE."""
    rom, rows, english, image, blocks = built
    lists = [(i, loc) for i, loc, _ in extract.load(rom).rows["shop"] if is_list(rom, loc)]
    assert len(lists) == 12
    for i, loc in lists:
        m = insert.LOC.fullmatch(loc)
        span, start = blocks[int(m[1])], int(m[2], 16)
        for k in range(int(m[3]) // 11):
            q = start + k * 11
            assert span[q] == insert.CALL and span[q + 10] == 0xFE, (i, k)


def test_blocks_keep_size(built):
    rom, _, _, _, blocks = built
    sizes = {i: size for i, _, size, _, _ in insert.unpack.entries(rom)}
    assert all(len(d) == sizes[b] for b, d in blocks.items())
