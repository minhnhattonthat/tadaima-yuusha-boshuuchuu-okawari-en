"""Cell-sheet lint: words land in their slots the way asm/vwf.asm `strip` lays them out."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import batches  # noqa: E402


def test_strip_cells():
    fill = __import__("width").width
    assert batches.strip_cells("Thief{cell}Mage{cell}[D6][D7][F4]{end}") == [
        ("Thief", 0, 2), ("Mage", 2, 4), ("[D6]", 4, 5), ("[D7]", 5, 6), ("[F4]", 6, 7)]
    w32 = "W" * (32 // batches._font()["adv"]["W"])
    assert fill(w32) == 32
    assert batches.strip_cells(w32 + "{cell}x")[0][1:] == (0, 3)  # a full cell flushes, so {cell} adds a blank one
    entry = {"id": "04B492", "sec": "system"}
    assert batches.width_problems({**entry, "locs": ["r04B492:14"]}, "Thief{cell}Mage{cell}[D6][D7][F4]{end}") == []
    assert batches.width_problems({**entry, "locs": ["r04B492:14"]}, "Thief{cell}Mage{cell}Male{cell}Female[F4]{end}")
