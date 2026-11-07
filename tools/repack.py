"""Rebuild the block area from unpacked blocks, every LZ block recompressed. See docs/re/compression.md."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import lz  # noqa: E402
import unpack  # noqa: E402

BLOCKS = 0x060010  # first block


def repack(rom, edits=None, out=None):
    """Blanks every block first, so a test against the dump proves the rebuild. Bytes the table doesn't reach stay:
    the five gaps between blocks are not padding (docs/re/memory.md). `edits` {block: new bytes} keep their size and slot:
    the far-text swap only blanks text, so a stream that grew past its slot is a build error for now.
    shortcut: no move to the expanded banks, add one when an edit outgrows its slot."""
    edits = edits or {}
    out = bytearray(rom if out is None else out)
    streams = []
    dist_code = lz.dist_codes(rom)
    for i, src, size, _, _ in unpack.entries(rom):
        data, used = unpack.load(rom, src, size)
        off = src & 0x3FFFFF
        end = off + (used or size)
        out[off:end] = b"\xff" * (end - off)
        if i in edits:
            assert len(edits[i]) == size, i
            stream = lz.compress(edits[i], dist_code) if used else edits[i]
            assert len(stream) <= end - off, (i, len(stream), end - off)
        else:
            stream = lz.compress(data, dist_code, rom[off:end]) if used else data
        streams.append((off, stream))
    for off, stream in streams:
        out[off:off + len(stream)] = stream
    return bytes(out)
