"""Carry text-coverage logs to a newer build: far numbers shift when rows change, so a log's TEXT addresses only mean
something with the strings.tsv of the build it ran on. Maps each address to its row id, then to that row's address in
the new strings.tsv, and writes the TEXT lines under DST (same sub-paths). Rows the new build no longer has are dropped.

relog.py OLD_STRINGS.tsv NEW_STRINGS.tsv SRC_DIR DST_DIR
then: textcover.py <dir holding DST and the new build's own logs> NEW_STRINGS.tsv --mask 0x3FFFFF
"""
import sys
from pathlib import Path

MASK = 0x3FFFFF


def table(path):
    return {line.split("\t")[0]: int(line.split("\t")[1], 16) & MASK
            for line in Path(path).read_text(encoding="utf-8").splitlines() if line}


def main(old, new, src, dst):
    by_addr = {a: i for i, a in table(old).items()}
    to = table(new)
    src, dst = Path(src), Path(dst)
    kept = dropped = 0
    for log in src.rglob("log.txt"):
        out = []
        for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.startswith("TEXT "):
                continue
            i = by_addr.get(int(line.split()[1], 16) & MASK)
            if i in to:
                out.append(f"TEXT {to[i]:06X}")
                kept += 1
            else:
                dropped += 1
        d = dst / log.parent.relative_to(src)
        d.mkdir(parents=True, exist_ok=True)
        (d / "log.txt").write_text("".join(s + "\n" for s in sorted(set(out))), encoding="utf-8")
    print(f"{kept} reads kept, {dropped} dropped (not a string of the old build, or gone from the new)")


if __name__ == "__main__":
    main(*sys.argv[1:5])
