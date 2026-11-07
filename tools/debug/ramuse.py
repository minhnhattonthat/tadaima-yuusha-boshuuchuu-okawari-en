"""Find WRAM that no scene touches: run scenes with the ramdump probe, then list long runs that stay one value in every dump.

ramuse.py SCENE..   -> work/qa/ram/<scene>/ram_*.bin, prints runs of >= 0x100 bytes. A candidate, not proof: free.lua proves it.
"""
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402

FRAMES = {"ending": 18000, "field_status": 18000, "battle_magic": 19000, "shop_inside": 18300, "name_entry": 3200, "save_menu": 4400, "versus": 5000}


def run(scene):
    out = ROOT / "work/qa/ram" / scene
    subprocess.run([sys.executable, "-X", "utf8", f"{SKILL}/scripts/emu.py", str(next((ROOT / "rom").glob("*.sfc"))), "--out", str(out),
                    "--script", f"{SKILL}/scripts/lua/probes/ramdump.lua", "--var", "RAM_EVERY=1500", "--script", str(ROOT / "tools/debug/warp.lua"),
                    "--var", f"SCENE='{scene}'", "--frames", str(FRAMES.get(scene, 18000))], cwd=ROOT, capture_output=True)


scenes = sys.argv[1:] or list(FRAMES)
with ThreadPoolExecutor(7) as pool:
    list(pool.map(run, scenes))
dumps = [p.read_bytes() for s in scenes for p in sorted((ROOT / "work/qa/ram" / s).glob("ram_*.bin"))]
print(len(dumps), "dumps", {len(d) for d in dumps})
stable = bytearray(0x20000)
for i in range(0x20000):  # one value in all dumps taken after the game cleared RAM
    stable[i] = len({d[i] for d in dumps[1:]}) == 1
i = 0
while i < 0x20000:
    if stable[i]:
        j = i
        while j < 0x20000 and stable[j] and dumps[1][j] == dumps[1][i]:
            j += 1
        if j - i >= 0x100:
            print(f"7E+{i:05X}..{j:05X} {j - i:5X} value {dumps[1][i]:02X}")
        i = j
    else:
        i += 1
