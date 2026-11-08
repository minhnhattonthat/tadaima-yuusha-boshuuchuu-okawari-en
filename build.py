"""Build from the pinned dump. build.py -> build/tadaima_en.sfc (dump + engine + English rows). --marker -> build/tadaima_marker.sfc:
every row shows its id; --marker ID=text.. -> build/tadaima_stress.sfc with those rows overridden. --identity -> rebuild the dump with no edits (what tests/test_identity.py proves)."""
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
import bps  # noqa: E402
import check_rom  # noqa: E402
import extract  # noqa: E402
import insert  # noqa: E402
import rects  # noqa: E402
import repack  # noqa: E402
import romcheck  # noqa: E402


def english_rows():
    """{row id: English} from script/*.tsv."""
    english = {}
    for f in (ROOT / "script").glob("*.tsv"):
        for line in f.read_text(encoding="utf-8").split("\n")[1:]:
            cols = line.split("\t")
            if len(cols) == 4 and cols[3]:
                english[cols[0]] = cols[3]
    return english


def build(out, english=None):
    """Write the ROM to out: the dump with no edits when english is None, else engine + those rows, assembled,
    checksummed and gated by romcheck. Returns an error string (out deleted) or None."""
    rom = next((ROOT / "rom").glob("*.sfc")).read_bytes()
    if english is None:
        built = repack.repack(rom)
    else:
        image, edits = insert.apply(rom, english)
        built = repack.repack(rom, edits, image)
    out.parent.mkdir(exist_ok=True)
    out.unlink(missing_ok=True)  # a failed assemble must not leave an old ROM to test
    out.write_bytes(built)
    if english is not None:
        if subprocess.call([str(ROOT / "tools/asar/asar.exe"), "--fix-checksum=off", "--no-title-check", str(ROOT / "asm/vwf.asm"), str(out)]):
            out.unlink()
            return "asar failed"
        built = bps.snes_checksum(out.read_bytes())[0]  # asar runs with --fix-checksum=off
        out.write_bytes(built)
    print(f"{out.relative_to(ROOT) if out.is_relative_to(ROOT) else out} sha1 {hashlib.sha1(built).hexdigest()} {'identical to the dump' if built == rom else 'differs'}")
    if english is not None and romcheck.main([str(out)]):
        out.unlink()
        return "romcheck: bytes changed outside the allowed ranges (build/ranges.txt)"
    return None


if __name__ == "__main__":
    check_rom.check()
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "--identity":
        english, out = None, ROOT / "build/tadaima_en.sfc"
    elif mode == "--marker":
        rom = next((ROOT / "rom").glob("*.sfc")).read_bytes()
        rows = [r for sec in extract.load(rom).rows.values() for r in sec]
        english = insert.marker(rows) | rects.marker(rom) | dict(a.split("=", 1) for a in sys.argv[2:])  # ID=text: stress one row
        out = ROOT / ("build/tadaima_stress.sfc" if sys.argv[2:] else "build/tadaima_marker.sfc")  # a stress build never clobbers a toured marker
    else:
        english, out = english_rows(), ROOT / "build/tadaima_en.sfc"
    err = build(out, english)
    if err:
        sys.exit(err)
