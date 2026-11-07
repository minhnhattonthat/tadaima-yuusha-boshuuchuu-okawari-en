"""Window variants from a tour's tools/debug/winlog.lua lines: windows.py [DIR under work/qa, default marker].
Prints each variant (width px, rows, flags) with its rows; writes work/windows.tsv: id, width px, rows, the tightest window the row was seen in.
Width px = +8 half cells x 8; a row with no line here wasn't reached, its section's budget in docs/re/windows.md applies."""
import collections
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
far = dict(l.split("\t") for l in (ROOT / "build/far.tsv").read_text(encoding="utf-8").splitlines())
qa = ROOT / "work/qa" / (sys.argv[1] if len(sys.argv) > 1 else "marker")
seen = collections.defaultdict(set)  # (width, rows, y, x) -> ids
for log in qa.glob("*/log.txt"):
    for m in re.finditer(r"^win (-?\d+) (\d+) (\d+) (\d+) (\d+) \w+ \w+ (\w+)$", log.read_text(encoding="utf-8", errors="replace"), re.M):
        num, y, x, w, h, flags = m.groups()
        seen[(int(w) * 8, int(h), flags)].add(far.get(num, "?" + num))
tight = {}
for (w, h, flags), ids in sorted(seen.items()):
    print(f"{w:4d} px x {h} rows flags {flags}: {len(ids)} rows, e.g. {sorted(ids)[:6]}")
    for i in ids:
        if i not in tight or (w, h) < tight[i]:
            tight[i] = (w, h)
(ROOT / "work/windows.tsv").write_text("".join(f"{i}\t{w}\t{h}\n" for i, (w, h) in sorted(tight.items())), encoding="utf-8")
print(len(tight), "rows seen in a window")
