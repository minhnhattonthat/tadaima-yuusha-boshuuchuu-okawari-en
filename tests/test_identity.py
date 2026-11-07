"""Identity build: unpack, recompress every block, rebuild the image, get the dump back byte for byte."""
import random
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import lz  # noqa: E402
import repack  # noqa: E402
import unpack  # noqa: E402

dumps = list((ROOT / "rom").glob("*.sfc"))
rom = dumps[0].read_bytes() if dumps else None
needs_rom = pytest.mark.skipif(rom is None, reason="no dump in rom/")


def unpacks_to(data, dist_code):
    """decompress reads its tables from the image, so the stream goes in a copy of the ROM, junk after it."""
    z = lz.compress(data, dist_code)
    image = bytearray(rom)
    image[repack.BLOCKS:repack.BLOCKS + len(z) + 2] = z + b"\xaa\xaa"
    return lz.decompress(image, repack.BLOCKS)[0] == data


@needs_rom
def test_rebuild_equals_dump():
    assert repack.repack(rom) == rom


@needs_rom
def test_recompressed_blocks_unpack_without_stale_words():
    """Edited blocks compress with no `old`: the stream has to stand on its own."""
    dist_code = lz.dist_codes(rom)
    for _, src, size, _, _ in unpack.entries(rom):
        data, used = unpack.load(rom, src, size)
        if used:
            assert unpacks_to(data, dist_code)


@needs_rom
def test_new_data_round_trips():
    """Matches past both limits, overlaps, no matches at all, and a stream ending on a look-ahead word."""
    dist_code = lz.dist_codes(rom)
    rng = random.Random(1)
    cases = [b"a", b"ab", b"\0" * 1000, b"abc" * 500, rng.randbytes(9000)]
    cases += [rng.randbytes(5000) + rng.randbytes(40) * 3 for _ in range(5)]
    cases += [bytes(rng.choice(b"ab") for _ in range(n)) for n in range(1, 300)]
    for data in cases:
        assert unpacks_to(data, dist_code)
