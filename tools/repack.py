"""Rebuild the block area from unpacked blocks, every LZ block recompressed. See docs/re/compression.md."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import lz  # noqa: E402
import unpack  # noqa: E402

BLOCKS = 0x060010  # first block
MOVED = 0x3F0000  # an edited block whose stream outgrew its slot moves here (last expanded bank, unused), its table src repointed


def repack(rom, edits=None, out=None):
    """Blanks every block first, so a test against the dump proves the rebuild. Bytes the table doesn't reach stay:
    the five gaps between blocks are not padding (docs/re/memory.md). `edits` {block: new bytes} keep their size; a stream
    that outgrew its slot moves to MOVED (within one bank) and the resource table's src points there."""
    edits = edits or {}
    out = bytearray(rom if out is None else out)
    streams = []
    moved = MOVED
    dist_code = lz.dist_codes(rom)
    for i, src, size, _, _ in unpack.entries(rom):
        data, used = unpack.load(rom, src, size)
        off = src & 0x3FFFFF
        end = off + (used or size)
        out[off:end] = b"\xff" * (end - off)
        if i in edits:
            assert len(edits[i]) == size, i
            stream = lz.compress(edits[i], dist_code) if used else edits[i]
            if len(stream) > end - off:
                assert len(out) > MOVED and moved + len(stream) <= MOVED + 0x10000, (i, len(stream), end - off)
                assert out[moved:moved + len(stream)] == b"\xff" * len(stream), f"block {i}: {moved:06X} is not free"
                e = unpack.TABLE + i * 8
                out[e:e + 3] = ((src & ~0x3FFFFF) | moved).to_bytes(3, "little")
                streams.append((moved, stream))
                moved += len(stream)
                continue
        else:
            stream = lz.compress(data, dist_code, rom[off:end]) if used else data
        streams.append((off, stream))
    for off, stream in streams:
        out[off:off + len(stream)] = stream
    return bytes(out)
