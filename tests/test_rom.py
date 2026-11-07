"""The dump is the pinned one; skipped on a clone with no ROM so CI-style checks still run."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import check_rom  # noqa: E402


def test_pinned_dump():
    if not any((ROOT / "rom").glob("*.sfc")):
        pytest.skip("no dump in rom/")
    check_rom.check()
