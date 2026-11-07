"""Far strings: every translated row leaves a far code that resolves to its English, in a bank where low RAM stays visible."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import extract  # noqa: E402
import insert  # noqa: E402

ROM = next((ROOT / "rom").glob("*.sfc"), None)
pytestmark = pytest.mark.skipif(ROM is None, reason="no dump in rom/")


@pytest.fixture(scope="module")
def built():
    rom = ROM.read_bytes()
    rows = [r for sec in extract.load(rom).rows.values() for r in sec]
    english = insert.marker(rows)
    image, blocks = insert.apply(rom, english)
    return rom, rows, english, image, blocks


def test_far_codes_resolve(built):
    rom, rows, english, image, blocks = built
    t = insert.table()
    for i, loc, _ in rows:
        if i not in english:
            continue
        m = insert.LOC.fullmatch(loc)
        span = blocks[int(m[1])] if m[1] else image
        start, n = int(m[2], 16), int(m[3])
        assert span[start] == insert.FAR, i
        num = span[start + 1] | span[start + 2] << 8
        assert span[start + 1] < 0xF4 and span[start + 2] < 0xF4, i
        cpu = int.from_bytes(image[insert.TABLE + num * 3:insert.TABLE + num * 3 + 3], "little")
        assert 0xA1 <= cpu >> 16 <= 0xBF and cpu & 0xFFFF >= 0x8000, i
        data = t.encode(english[i])
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


def test_blocks_keep_size(built):
    rom, _, _, _, blocks = built
    sizes = {i: size for i, _, size, _, _ in insert.unpack.entries(rom)}
    assert all(len(d) == sizes[b] for b, d in blocks.items())
