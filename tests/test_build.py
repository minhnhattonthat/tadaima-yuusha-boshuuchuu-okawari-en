"""The shipped English builds: insert asserts, asar and romcheck all pass, so the pre-commit check gates them."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build  # noqa: E402

pytestmark = pytest.mark.skipif(next((ROOT / "rom").glob("*.sfc"), None) is None or not (ROOT / "tools/asar/asar.exe").exists(),
                                reason="no dump or no asar")


def test_english_build(tmp_path):
    out = tmp_path / "en.sfc"
    assert build.build(out, build.english_rows()) is None
    assert out.exists()
