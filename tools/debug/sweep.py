"""Forced text sweep for text coverage: print every far string of build/strings.tsv in the opening's dialogue window (sweep.lua),
split over jobs, each logging textcover.lua reads under work/qa/sweep/jNN. Then:
python -X utf8 $SKILL/scripts/textcover.py work/qa build/strings.tsv --waive docs/text_unshown.tsv --mask 0x3FFFFF

sweep.py [--rom build/tadaima_en.sfc] [--jobs 4] [--size 6] [--per 300] [--only N]   (--only: the first N strings, a quick try)
Each run of the opening swaps --size strings in (one per print it makes), so the list is split into many short runs.
"""
import argparse
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402

TABLE = 0x210000  # $E1:0000, the far table (asm/vwf.asm !TABLE)


def label(sym, name):
    for line in sym.read_text(encoding="utf-8").splitlines():
        if line.endswith(" " + name):
            bank, addr = line.split()[0].split(":")
            return int(bank, 16) << 16 | int(addr, 16)
    raise KeyError(name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rom", type=Path, default=ROOT / "build/tadaima_en.sfc")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--per", type=int, default=300, help="frames budget per string")
    ap.add_argument("--size", type=int, default=6,
                    help="strings per run: the opening's first 6 prints are plain dialogue; the 7th opens the years picker and a swapped"
                         " string there can end the opening")
    ap.add_argument("--ids", type=Path, help="far numbers (hex, one a line) instead of all: a pass over what textcover still misses")
    ap.add_argument("--out", default="sweep", help="under work/qa/: one directory per pass keeps the earlier passes' reads")
    ap.add_argument("--only", type=int)
    ap.add_argument("--skip", type=int, default=0, help="start at this list index (with --only: a window, to retry a stall)")
    args = ap.parse_args()
    rom = args.rom.read_bytes()
    entry = label(args.rom.with_suffix(".sym"), "far_entry")
    assert rom[(entry & 0x3FFFFF):(entry & 0x3FFFFF) + 3] == b"\x85\x00\x0a"  # sta $00, asl: A = far number
    nums = sorted({(int(l.split("\t")[1], 16) - TABLE) // 3 for l in (ROOT / "build/strings.tsv").read_text(encoding="utf-8").splitlines()
                   if int(l.split("\t")[1], 16) >= TABLE})
    if args.ids:  # hex far numbers, or a textcover.py report ("NEVER SHOWN id offset": its far rows)
        text = args.ids.read_text(encoding="utf-8")
        if "NEVER SHOWN" in text:
            offs = [int(l.split()[-1], 16) for l in text.splitlines() if l.startswith("NEVER SHOWN")]
            nums = sorted({(o - TABLE) // 3 for o in offs if o >= TABLE})
        else:
            nums = sorted(int(n, 16) for n in text.split())
    nums = nums[args.skip:][:args.only]
    out = ROOT / "work/qa" / args.out
    out.mkdir(parents=True, exist_ok=True)
    (out / "list.txt").write_text("".join(f"{n:X}\n" for n in nums), encoding="utf-8")
    size = args.size

    def run(j):
        a, b = j * size + 1, min((j + 1) * size, len(nums))
        d = out / f"j{j:03d}"
        cmd = [sys.executable, "-X", "utf8", f"{SKILL}/scripts/emu.py", str(args.rom), "--out", str(d),
               "--script", str(ROOT / "tools/debug/textcover.lua"), "--var", f"FARS={max(nums) + 1}",
               "--script", str(ROOT / "tools/debug/warp.lua"), "--var", "SCENE='opening'",
               "--script", str(ROOT / "tools/debug/sweep.lua"), "--var", f"LIST='{(out / 'list.txt').as_posix()}'",
               "--var", f"FROM={a}", "--var", f"TO={b}", "--var", f"ENTRY={entry}",
               "--frames", str(3000 + (b - a + 1) * args.per), "--timeout", "7200"]
        code = subprocess.run(cmd, cwd=ROOT, capture_output=True).returncode
        log = (d / "log.txt").read_text(encoding="utf-8")
        return j, code, "sweep done" in log, log.count("TEXT ")

    with ThreadPoolExecutor(args.jobs) as ex:
        res = list(ex.map(run, range(-(-len(nums) // size))))
    for j, code, done, n in res:
        if not done:
            print(f"j{j:03d} exit {code} NOT DONE, {n} reads")
    print(sum(r[2] for r in res), "of", len(res), "runs done")
    return 0 if all(r[2] for r in res) else 1


if __name__ == "__main__":
    sys.exit(main())
