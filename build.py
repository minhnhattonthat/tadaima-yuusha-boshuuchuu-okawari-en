"""Build from the pinned dump. build.py -> build/tadaima_en.sfc (dump + engine + English rows). --marker -> build/tadaima_marker.sfc:
every row shows its id; --marker ID=text.. -> build/tadaima_stress.sfc with those rows overridden. --identity -> rebuild the dump with no edits (what tests/test_identity.py proves)."""
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
import check_rom  # noqa: E402
import extract  # noqa: E402
import insert  # noqa: E402
import rects  # noqa: E402
import repack  # noqa: E402

check_rom.check()
rom = next((ROOT / "rom").glob("*.sfc")).read_bytes()
mode = sys.argv[1] if len(sys.argv) > 1 else ""
if mode == "--identity":
    built = repack.repack(rom)
    out = ROOT / "build/tadaima_en.sfc"
else:
    rows = [r for sec in extract.load(rom).rows.values() for r in sec]
    if mode == "--marker":
        english = insert.marker(rows) | rects.marker(rom) | dict(a.split("=", 1) for a in sys.argv[2:])  # ID=text: stress one row
        out = ROOT / ("build/tadaima_stress.sfc" if sys.argv[2:] else "build/tadaima_marker.sfc")  # a stress build never clobbers a toured marker
    else:
        english = {}
        for f in (ROOT / "script").glob("*.tsv"):
            for line in f.read_text(encoding="utf-8").split("\n")[1:]:
                cols = line.split("\t")
                if len(cols) == 4 and cols[3]:
                    english[cols[0]] = cols[3]
        out = ROOT / "build/tadaima_en.sfc"
    image, edits = insert.apply(rom, english)
    built = repack.repack(rom, edits, image)
out.parent.mkdir(exist_ok=True)
out.unlink(missing_ok=True)  # a failed assemble must not leave an old ROM to test
out.write_bytes(built)
if mode != "--identity":
    code = subprocess.call([str(ROOT / "tools/asar/asar.exe"), "--fix-checksum=off", "--no-title-check", str(ROOT / "asm/vwf.asm"), str(out)])
    if code:
        out.unlink()
        sys.exit(code)
    built = out.read_bytes()
print(f"{out.relative_to(ROOT)} sha1 {hashlib.sha1(built).hexdigest()} {'identical to the dump' if built == rom else 'differs'}")
if mode != "--identity":
    import romcheck  # noqa: E402
    if romcheck.main([str(out)]):
        out.unlink()
        sys.exit("romcheck: bytes changed outside the allowed ranges (build/ranges.txt)")
