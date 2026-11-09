"""docs/polish.md bullets by number (1-based over every `- [` line).

    python -X utf8 tools/polish.py todo [FROM [TO]]   # list unticked bullets with their numbers
    python -X utf8 tools/polish.py tick TICKS.tsv     # TICKS rows: number<TAB>verdict ("fixed..." / "waived: ...")

`tick` turns `- [ ] text` into `- [x] text (verdict)` and skips bullets already ticked; exits 1 and writes nothing if a
number is unknown.
"""
import sys
from pathlib import Path

DOC = Path(__file__).resolve().parents[1] / "docs" / "polish.md"


def bullets(lines):
    return [i for i, l in enumerate(lines) if l.startswith("- [")]


def main(argv):
    lines = DOC.read_text(encoding="utf-8").split("\n")
    idx = bullets(lines)
    if argv[0] == "todo":
        lo = int(argv[1]) if len(argv) > 1 else 1
        hi = int(argv[2]) if len(argv) > 2 else len(idx)
        for n, i in enumerate(idx, 1):
            if lo <= n <= hi and lines[i].startswith("- [ ]"):
                print(f"{n}\t{lines[i][6:]}")
        return 0
    bad = []
    for row in Path(argv[1]).read_text(encoding="utf-8").splitlines():
        if not row.strip():
            continue
        n, verdict = row.split("\t", 1)
        n = int(n)
        if not 1 <= n <= len(idx):
            bad.append(f"{n}: unknown")
            continue
        if not lines[idx[n - 1]].startswith("- [ ]"):
            continue  # already ticked (earlier review pass)
        if not verdict.startswith(("fixed", "waived:")):
            bad.append(f"{n}: verdict must start with fixed / waived:")
            continue
        i = idx[n - 1]
        lines[i] = "- [x]" + lines[i][5:] + f" ({verdict})"
    if bad:
        print("\n".join(bad))
        return 1
    DOC.write_text("\n".join(lines), encoding="utf-8")
    left = sum(lines[i].startswith("- [ ]") for i in idx)
    print(f"ticked; {left} left")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
