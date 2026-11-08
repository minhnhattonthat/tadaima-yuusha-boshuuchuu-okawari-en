"""Graphics text and the code-built status box: English drawn where the code and the tilemap expect it (tools/gfx.py, rects.status)."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import gfx  # noqa: E402
import rects  # noqa: E402
import unpack  # noqa: E402

ROM = next((ROOT / "rom").glob("*.sfc"), None)
pytestmark = pytest.mark.skipif(ROM is None, reason="no dump in rom/")


def block(rom, n):
    return next(unpack.load(rom, s, z)[0] for b, s, z, _, _ in unpack.entries(rom) if b == n)


def test_buttons_keep_the_frame():
    sheet = block(ROM.read_bytes(), 2)
    out = gfx.buttons(sheet)
    assert len(out) == len(sheet) and out != sheet
    for r, row in enumerate(gfx.BUTTONS):
        for c, word in enumerate(row):
            first = r * 32 + c * 4
            old, new = gfx.get(sheet, first), gfx.get(out, first)
            assert [line[:2] for line in old] == [line[:2] for line in new]  # border columns untouched
            if word:
                assert any(gfx.INK in line for t in range(4) for line in gfx.get(out, first + 16 + t) + gfx.get(out, first + t))


def test_title_only_touches_its_box():
    sheet = block(ROM.read_bytes(), 794)
    out = gfx.title(sheet)
    box = {t + k for _, t, n in gfx.TITLE_ROWS for k in range(n)}
    for t in range(len(sheet) // 32):
        if t not in box:
            assert out[t * 32:t * 32 + 32] == sheet[t * 32:t * 32 + 32], hex(t)


def test_panel_keeps_the_face():
    sheet = block(ROM.read_bytes(), 1)
    out = gfx.panel(sheet)
    assert out[:gfx.PANEL_TILE * 32] == sheet[:gfx.PANEL_TILE * 32] and out[(gfx.PANEL_TILE + 36) * 32:] == sheet[(gfx.PANEL_TILE + 36) * 32:]
    for k in range(36):
        if k % 9 < 4:  # x 0-31: the face
            assert gfx.get(out, gfx.PANEL_TILE + k) == gfx.get(sheet, gfx.PANEL_TILE + k)
    assert out != sheet


def test_status_box_cells():
    rom = ROM.read_bytes()
    body = rects.status(rom, "Time left{nl}Shillings")
    w = rom[rects.STATUS]
    for y, x, n in rects.STATUS_CELLS.values():
        assert body[y * w + x:y * w + x + n] == bytes(n)  # the code writes the digits here (asm/vwf.asm)
    assert body[8:8 + 9] == bytes(rects.tiles("Shillings", 0x26))
    with pytest.raises(AssertionError):
        rects.status(rom, "Time remaining{nl}Shillings")
