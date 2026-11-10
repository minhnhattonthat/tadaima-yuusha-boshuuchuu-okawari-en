"""release.py: build -> check -> smoke -> untranslated-row scan + jp_left -> QA gates -> textcover -> polish -> README
-> BPS (re-applied, compared) -> zip.

    python -X utf8 tools/release.py [--version 1.0] [--force]

Stops at the first failure. Writes release/TadaimaYuushaBoshuuchuuOkawari_EN_v<version>.{bps,zip} + README.txt (local,
gitignored) and keeps the playable patched image in build/tadaima_en_v<version>.sfc. Refuses to overwrite an existing
version's files without --force. The debug tool is Lua only (tools/debug/*.lua, run by the emulator), so no debug code
is in the ROM; the build fixes the header checksum itself (build.py), so the patched image is build/tadaima_en.sfc.
Never publishes.

Text coverage: work/qa/cover14 = cover13 (v1.1 tour + sweeps) re-logged from work/qa/v11_strings.tsv (tools/debug/relog.py)
plus sweeps of what was left (sweep.py --ids --out cover14/sweep14, sweep14b);
after a text change, re-tour and re-log (docs/status.md item 3) or textcover fails on the new far addresses.
jp_left scans the raw row slots (build/ranges.txt "# row" lines); LZ-block rows are checked in script/ instead.
"""
import argparse
import hashlib
import re
import subprocess
import sys
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402

SCRIPTS = Path(SKILL) / "scripts"
ROM = ROOT / "rom" / "Tadaima Yuusha Boshuuchuu Okawari (Japan).sfc"
BUILT = ROOT / "build" / "tadaima_en.sfc"
QA = ROOT / "work" / "qa"
COVER = QA / "cover14"
NAME = "TadaimaYuushaBoshuuchuuOkawari_EN"
PY = [sys.executable, "-X", "utf8"]
JP = re.compile(r"[぀-ヿ一-鿿]")
CODE = re.compile(r"\{[^}]*\}|\[[^\]]*\]")


def run(*cmd):
    print("+", " ".join(map(str, cmd)), flush=True)
    if subprocess.run([*PY, *map(str, cmd)], cwd=ROOT).returncode:
        sys.exit(f"release: failed: {Path(str(cmd[0])).name}")


def hashes(data):
    return f"CRC32 {zlib.crc32(data):08X}, MD5 {hashlib.md5(data).hexdigest()}, SHA-1 {hashlib.sha1(data).hexdigest()}"


def untranslated():
    """Rows of script/ (raw and LZ-block alike) whose Japanese has no English, or whose English holds kana/kanji."""
    bad = []
    for f in sorted((ROOT / "script").glob("*.tsv")):
        for line in f.read_text(encoding="utf-8").split("\n")[1:]:
            cols = line.split("\t")
            if len(cols) != 4 or f.name == "nontext.tsv":
                continue
            if JP.search(CODE.sub("", cols[3])) or (not cols[3] and JP.search(CODE.sub("", cols[2]))):
                bad.append(f"{f.name} {cols[0]}")
    return bad


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="1.0")
    ap.add_argument("--force", action="store_true", help="overwrite this version's existing release files")
    a = ap.parse_args()
    out = ROOT / "release"
    patch, zpath = out / f"{NAME}_v{a.version}.bps", out / f"{NAME}_v{a.version}.zip"
    if (patch.exists() or zpath.exists()) and not a.force:
        sys.exit(f"release: {patch.name} or {zpath.name} exists; pass --force to overwrite")

    run(ROOT / "build.py")
    run(ROOT / "tools" / "check.py")
    run(SCRIPTS / "emu.py", BUILT, "--out", QA / "smoke", "--route", ROOT / "tools" / "routes" / "boot.txt", "--smoke")
    bad = untranslated()
    if bad:
        sys.exit(f"release: {len(bad)} rows untranslated or with Japanese in the English:\n" + "\n".join(bad[:20]))
    rows = [x for line in (ROOT / "build" / "ranges.txt").read_text(encoding="utf-8").splitlines()
            if "# row" in line for x in ("--range", line.split()[0])]
    run(SCRIPTS / "jp_left.py", BUILT, "--orig", ROM, "--tbl", ROOT / "tbl" / "jp.tbl", "--min", "3", *rows)
    for manifest in sorted(QA.glob("**/manifest.tsv")):
        run(SCRIPTS / "qa_gate.py", "check", manifest, manifest.parent / "verdicts")
    run(SCRIPTS / "textcover.py", COVER, ROOT / "build" / "strings.tsv", "--mask", "0x3FFFFF")
    open_lines = [l for l in (ROOT / "docs" / "polish.md").read_text(encoding="utf-8").splitlines()
                  if l.startswith("- [ ]")]
    if open_lines:
        sys.exit(f"release: docs/polish.md has {len(open_lines)} unticked lines:\n" + "\n".join(open_lines[:10]))
    if re.search(r"<(Game title|platform|publisher|year|repo|file|size|sha1)>", (ROOT / "README.md").read_text(encoding="utf-8")):
        sys.exit("release: README.md still has template placeholders")

    final = ROOT / "build" / f"tadaima_en_v{a.version}.sfc"
    final.write_bytes(BUILT.read_bytes())
    out.mkdir(exist_ok=True)
    run(ROOT / "tools" / "bps.py", "make", ROM, final, patch)
    work = ROOT / "work" / "release"
    work.mkdir(parents=True, exist_ok=True)
    check = work / "reapplied.sfc"
    run(ROOT / "tools" / "bps.py", "apply", ROM, patch, check)
    if check.read_bytes() != final.read_bytes():
        sys.exit("release: the re-applied patch differs from the build")
    check.unlink()
    readme = (ROOT / "docs" / "README.release.txt").read_text(encoding="utf-8")
    readme = (readme.replace("{VERSION}", a.version).replace("{BASE}", hashes(ROM.read_bytes()))
              .replace("{PATCHED}", hashes(final.read_bytes())))
    if "{" in readme:
        sys.exit("release: docs/README.release.txt has an unfilled {FIELD}")
    (out / "README.txt").write_text(readme, encoding="utf-8", newline="\r\n")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(patch, patch.name)
        z.write(out / "README.txt", "README.txt")
    print(f"release: {zpath.relative_to(ROOT)} (patch sha1 {hashlib.sha1(patch.read_bytes()).hexdigest()}); "
          f"playable image {final.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
