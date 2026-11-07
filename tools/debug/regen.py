"""Warp to scenes from a cold boot, keep a proof shot and a savestate per scene.

regen.py [--rom ROM] [--frames N] [--jobs N] [NAME_PREFIX ..]  -> work/qa/scenes/<scene>/final.png, work/states/<scene>.mss,
then work/qa/scenes/sheet*.png. Exits 1 if any run failed or ended on a flat colour (black-screen scene).
"""
import argparse
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402


def names():
    """{scene: frames or None}. Same list as scenes.lua: its fixed lines, then its chapter loops."""
    src = (ROOT / "tools/debug/scenes.lua").read_text(encoding="utf-8")
    fixed = {m[0]: int(m[1]) for m in re.findall(r"^S\.(\w+) = .*frames = (\d+)", src, re.M) if m[0] != "name"}
    turns = {m: 18000 for m in re.findall(r"^S\.(\w+) = turn\(", src, re.M)}
    tiles = {m: 18300 for m in re.findall(r"(\w+) = \{ 0x\w\w, 0x\w\w \}", src[src.index("local tiles"):])}
    return (fixed | turns | tiles | {f"ch{c:02d}": None for c in range(8)} | {f"mid{c:02d}": 12000 for c in range(5)}
            | {f"clear{c:02d}": 12000 for c in range(5)})


def run(args, scene, frames):
    out = ROOT / "work/qa" / args.dir / scene
    states = ROOT / "work/states" if args.dir == "scenes" else out
    cmd = [sys.executable, "-X", "utf8", f"{SKILL}/scripts/emu.py", str(args.rom), "--out", str(out), "--script",
           str(ROOT / "tools/debug/statelog.lua"), "--script", str(ROOT / "tools/debug/textlog.lua"), "--script",
           str(ROOT / "tools/debug/warp.lua"), "--var", f"SCENE='{scene}'",
           "--frames", str(frames or args.frames), "--state-out", str(states / f"{scene}.mss")]
    code = subprocess.run(cmd, cwd=ROOT, capture_output=True).returncode
    shot = out / "final.png"
    flat = not shot.exists() or len(Image.open(shot).convert("RGB").getcolors(1 << 16) or [0, 0]) < 2
    log = (out / "log.txt").read_text(encoding="utf-8")
    expect = re.search(r"^expect (\w\w)$", log, re.M)
    wrong = expect and re.findall(r"^f\d+ state (\w\w)$", log, re.M)[-1:] != [expect[1]]
    return scene, 4 if wrong else code, flat


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rom", default=next((ROOT / "rom").glob("*.sfc")))
    ap.add_argument("--frames", type=int, default=6000)
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--dir", default="scenes", help="under work/qa/; anything but `scenes` keeps states there too")
    ap.add_argument("prefix", nargs="*")
    args = ap.parse_args()
    (ROOT / "work/states").mkdir(parents=True, exist_ok=True)
    todo = {n: f for n, f in names().items() if not args.prefix or n.startswith(tuple(args.prefix))}
    with ThreadPoolExecutor(args.jobs) as ex:
        res = list(ex.map(lambda s: run(args, s, todo[s]), todo))
    bad = [r for r in res if r[1] or r[2]]
    for scene, code, flat in res:
        print(scene, "exit", code, "FLAT" if flat else "ok")
    shots = [str(ROOT / "work/qa" / args.dir / r[0] / "final.png") for r in res if not r[2]]
    subprocess.run([sys.executable, "-X", "utf8", f"{SKILL}/scripts/sheet.py", *shots, "--out",
                    str(ROOT / "work/qa" / args.dir / "sheet.png")], cwd=ROOT)
    print(len(res) - len(bad), "of", len(res), "scenes ok")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
