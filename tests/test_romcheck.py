"""romcheck's allowed ranges: the hooks are in, plain code is not, and a stray byte fails."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import romcheck  # noqa: E402
import romdiff  # noqa: E402

ROM = next((ROOT / "rom").glob("*.sfc"), None)
pytestmark = pytest.mark.skipif(ROM is None or not (ROOT / "build/vwf_font.bin").exists(), reason="no dump or no font build")


def test_ranges():
    rom = ROM.read_bytes()
    allowed = set()
    for lo, hi, _ in romcheck.ranges(rom):
        allowed.update(range(lo, hi + 1))
    assert set(range(0x02143B, 0x02143F)) <= allowed  # jml far_read
    assert 0x02143F not in allowed and 0x008000 not in allowed  # code after the hook, the reset area
    stray = bytearray(rom)
    stray[0x02143F] ^= 0xFF
    assert romdiff.check(rom, bytes(stray), allowed, [])[0]
