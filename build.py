"""Build build/tadaima_en.sfc from the pinned dump. No text inserted yet: this is the identity build."""
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
import check_rom  # noqa: E402
import repack  # noqa: E402

check_rom.check()
rom = next((ROOT / "rom").glob("*.sfc")).read_bytes()
built = repack.repack(rom)
out = ROOT / "build/tadaima_en.sfc"
out.parent.mkdir(exist_ok=True)
out.write_bytes(built)
print(f"{out.relative_to(ROOT)} sha1 {hashlib.sha1(built).hexdigest()} {'identical to the dump' if built == rom else 'differs'}")
