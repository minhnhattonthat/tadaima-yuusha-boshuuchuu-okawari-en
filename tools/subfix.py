"""Turn substitution rows into a full-row fix file for `batches.py fix` (which lints before writing script/).

    python -X utf8 tools/subfix.py SUBS.tsv OUT.tsv

SUBS.tsv rows: id<TAB>old<TAB>new  (old must occur exactly once in that row's current English; several rows per id apply
in order). A row id<TAB>=<TAB>English replaces the whole English. Exits 1 and writes nothing if any old text is missing.
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def current():
    rows = {}
    for f in sorted((ROOT / "script").glob("*.tsv")):
        if f.name == "nontext.tsv":
            continue
        with open(f, encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh, delimiter="\t", quoting=csv.QUOTE_NONE):
                rows.setdefault(r["id"], r["en"])
    return rows


def main(subs, out):
    en, new, bad = current(), {}, []
    for line in Path(subs).read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        i, old, rep = line.split("\t")
        if i not in en:
            bad.append(f"{i}: unknown id")
            continue
        text = new.get(i, en[i])
        if old == "=":
            new[i] = rep
        elif text.count(old) != 1:
            bad.append(f"{i}: {old!r} found {text.count(old)} times in {text!r}")
        else:
            new[i] = text.replace(old, rep)
    if bad:
        print("\n".join(bad))
        return 1
    Path(out).write_text("".join(f"{i}\t{t}\n" for i, t in new.items()), encoding="utf-8")
    print(f"{len(new)} rows -> {out}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(*sys.argv[1:3]) if len(sys.argv) == 3 else __doc__)
