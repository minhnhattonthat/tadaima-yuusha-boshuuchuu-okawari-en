"""Rebuild the block area from unpacked blocks, every LZ block recompressed. See docs/re/compression.md."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import lz  # noqa: E402
import unpack  # noqa: E402

BLOCKS = 0x060010  # first block


def repack(rom):
    """Blanks every block first, so a test against the dump proves the rebuild. Bytes the table doesn't reach stay:
    the five gaps between blocks are not padding (docs/re/memory.md)."""
    out = bytearray(rom)
    streams = []
    dist_code = lz.dist_codes(rom)
    for _, src, size, _, _ in unpack.entries(rom):
        data, used = unpack.load(rom, src, size)
        off = src & 0x3FFFFF
        end = off + (used or size)
        out[off:end] = b"\xff" * (end - off)
        streams.append((off, lz.compress(data, dist_code, rom[off:end]) if used else data))
    for off, stream in streams:
        out[off:off + len(stream)] = stream
    return bytes(out)
