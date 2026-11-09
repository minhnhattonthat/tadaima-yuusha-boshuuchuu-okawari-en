"""repack.py: an edited block whose stream outgrows its slot moves to repack.MOVED, its table src repointed, and unpacks the same."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import insert  # noqa: E402
import repack  # noqa: E402
import unpack  # noqa: E402

ROM = next((ROOT / "rom").glob("*.sfc"), None)
pytestmark = pytest.mark.skipif(ROM is None, reason="no dump in rom/")


def test_trim_keeps_7f_fe00():
    rom = ROM.read_bytes()
    out = repack.repack(rom, trim=repack.TRIM)
    for i, n in repack.TRIM.items():
        src, size = next((s, k) for j, s, k, _, _ in unpack.entries(rom) if j == i)
        assert dict((j, k) for j, _, k, _, _ in unpack.entries(out))[i] == n
        assert unpack.load(out, src, n)[0] == unpack.load(rom, src, size)[0][:n]


def test_grown_block_moves():
    rom = ROM.read_bytes()
    i, src, size = next((i, s, n) for i, s, n, _, _ in unpack.entries(rom) if i == 603)
    data = bytearray(unpack.load(rom, src, size)[0])
    data[:] = bytes((k * 2654435761 >> 13) & 0xFF for k in range(size))  # incompressible: the stream outgrows the slot
    image = rom + b"\xff" * (insert.ROM_SIZE - len(rom))
    out = repack.repack(rom, {i: bytes(data)}, image)
    moved = dict((k, s) for k, s, _, _, _ in unpack.entries(out))[i]
    assert moved & 0x3FFFFF == repack.MOVED and moved >> 22 == src >> 22
    assert unpack.load(out, moved, size)[0] == bytes(data)
    assert dict((k, s) for k, s, _, _, _ in unpack.entries(out))[i + 1] == dict((k, s) for k, s, _, _, _ in unpack.entries(rom))[i + 1]
