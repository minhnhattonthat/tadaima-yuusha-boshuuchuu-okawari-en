"""Unpack every resource-table entry to work/blocks/ and print a summary. See docs/re/compression.md."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import lz  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TABLE = 0x1DDF40  # $DD:DF40, pointed to by $C6:0000
COUNT = 863


def entries(rom):
    for i in range(COUNT):
        e = rom[TABLE + i * 8:TABLE + i * 8 + 8]
        yield i, e[0] | e[1] << 8 | e[2] << 16, e[3] | e[4] << 8, e[5] | e[6] << 8, e[7]


def load(rom, src, size):
    """Returns (data, compressed?). A stream that doesn't reproduce `size` is taken as stored raw."""
    off = src & 0x3FFFFF
    try:
        data, used = lz.decompress(rom, off)
        if len(data) == size:
            return data, used
    except IndexError:
        pass
    return rom[off:off + size], 0


if __name__ == "__main__":
    rom = next((ROOT / "rom").glob("*.sfc")).read_bytes()
    out = ROOT / "work/blocks"
    out.mkdir(parents=True, exist_ok=True)
    for i, src, size, dst, bank in entries(rom):
        data, used = load(rom, src, size)
        (out / f"{i:03d}.bin").write_bytes(data)
        kana = sum(1 for b in data if 0x24 <= b <= 0x57) / max(len(data), 1)
        print(f"{i:3d} src={src:06X} size={size:04X} dst={bank:02X}:{dst:04X} used={used:04X} "
              f"{'LZ ' if used else 'RAW'} hira={kana:.2f}")
