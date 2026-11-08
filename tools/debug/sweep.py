"""Forced text sweep for text coverage: print every far string of build/strings.tsv in the opening's dialogue window (sweep.lua),
split over jobs, each logging textcover.lua reads under work/qa/sweep/jNN. Then:
python -X utf8 $SKILL/scripts/textcover.py work/qa build/strings.tsv --waive docs/text_unshown.tsv --mask 0x3FFFFF

sweep.py [--rom build/tadaima_en.sfc] [--jobs 4] [--per 120] [--only N]   (--only: the first N strings, a quick try)
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
    ap.add_argument("--per", type=int, default=120, help="frames budget per string")
    ap.add_argument("--only", type=int)
    ap.add_argument("--skip", type=int, default=0, help="start at this list index (with --only: a window, to retry a stall)")
    args = ap.parse_args()
    rom = args.rom.read_bytes()
    callx = label(args.rom.with_suffix(".sym"), "far_read_call") + 1
    assert rom[(callx & 0x3FFFFF) - 1:(callx & 0x3FFFFF) + 3] == b"\x5a\xb9\x01\x00"  # phy, lda $0001,y
    nums = sorted({(int(l.split("\t")[1], 16) - TABLE) // 3 for l in (ROOT / "build/strings.tsv").read_text(encoding="utf-8").splitlines()
                   if int(l.split("\t")[1], 16) >= TABLE})[args.skip:][:args.only]
    out = ROOT / "work/qa/sweep"
    out.mkdir(parents=True, exist_ok=True)
    (out / "list.txt").write_text("".join(f"{n:X}\n" for n in nums), encoding="utf-8")
    size = -(-len(nums) // args.jobs)

    def run(j):
        a, b = j * size + 1, min((j + 1) * size, len(nums))
        d = out / f"j{j:02d}"
        cmd = [sys.executable, "-X", "utf8", f"{SKILL}/scripts/emu.py", str(args.rom), "--out", str(d),
               "--script", str(ROOT / "tools/debug/textcover.lua"), "--var", f"FARS={max(nums) + 1}",
               "--script", str(ROOT / "tools/debug/warp.lua"), "--var", "SCENE='opening'",
               "--script", str(ROOT / "tools/debug/sweep.lua"), "--var", f"LIST='{(out / 'list.txt').as_posix()}'",
               "--var", f"FROM={a}", "--var", f"TO={b}", "--var", f"CALLX={callx}",
               "--frames", str(3000 + (b - a + 1) * args.per), "--shot-every", "3000", "--timeout", "7200"]
        code = subprocess.run(cmd, cwd=ROOT, capture_output=True).returncode
        log = (d / "log.txt").read_text(encoding="utf-8")
        return j, code, "sweep done" in log, log.count("SWEEP ")  # batches started

    with ThreadPoolExecutor(args.jobs) as ex:
        res = list(ex.map(run, range(args.jobs)))
    for j, code, done, n in res:
        print(f"j{j:02d} exit {code} {'done' if done else 'NOT DONE'} {n} strings")
    return 0 if all(r[2] for r in res) else 1


if __name__ == "__main__":
    sys.exit(main())
