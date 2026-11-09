"""Lint: a row whose text has no {end} runs on into the next row on the same line (e240.02BB "....." then e240.02FD).
The batch lint measures each row alone; this adds the row's last line to the next row's first. Exit 1 on a line past the window.
python -X utf8 tools/runon.py
"""
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import font  # noqa: E402

BRK = re.compile(r"\{(?:nl|page|wait|end)\}")


def width(s, adv):
    s = re.sub(r"\{sub:[^}]*\}", "AAAAA", s)  # a 5-letter name
    s = re.sub(r"\[D1\]", "*", s)
    s = re.sub(r"\{[^}]*\}", "", s)
    return sum(adv.get(c, 8) for c in s) + 4  # the dialogue inset


def problems():
    adv = font.advances()
    rows = []
    for f in sorted((ROOT / "script").glob("*.tsv")):
        for r in csv.reader(open(f, encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE):
            m = len(r) >= 4 and r[3] and re.fullmatch(r"b(\d+)\+([0-9A-F]+):(\d+)", r[1])
            if m:
                rows.append((int(m[1]), int(m[2], 16), int(m[3]), r[0], r[2], r[3]))
    rows.sort()
    out = []
    for a, b in zip(rows, rows[1:]):
        if a[0] != b[0] or a[4].endswith(("{end}", "{page}", "{wait}")) or b[1] - (a[1] + a[2]) > 2:
            continue
        last, nxt = BRK.split(a[5])[-1], BRK.split(b[5])[0]
        m = re.search(r"\{(nl|page|wait|end)\}", b[5])
        lim = 224 if m and m[1] in ("page", "wait") else 240  # docs/re/windows.md
        w = width(last + nxt, adv)
        if w > lim:
            out.append(f"{a[3]} -> {b[3]}: {w} px > {lim}: {last!r} + {nxt!r}")
    return out


if __name__ == "__main__":
    p = problems()
    print("\n".join(p) or "run-on rows: 0 problems")
    sys.exit(1 if p else 0)
