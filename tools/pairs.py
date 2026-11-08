"""Reviewer pairs files (docs/reviewer-brief.md): pairs.py bNNN.. -> work/qa/pairs/bNNN.txt, `>> id | speaker | JP` / `EN` per entry,
with the batch's neighbouring entries as context (they are in script order)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import batches  # noqa: E402


def write(batch):
    ents = batches.entries()
    rows = batches.read_tsv(batches.TL / f"{batch}.tsv")
    out = []
    for i, r in enumerate(rows):
        e = ents[r[0]]
        out.append(f">> {r[0]} | {r[1]} | {r[2]} {r[3]} | {e['jp']}\n   {e['en'] or '(untranslated)'}\n")
    path = ROOT / f"work/qa/pairs/{batch}.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(out), encoding="utf-8", newline="\n")
    return path


if __name__ == "__main__":
    for b in sys.argv[1:]:
        print(write(b))
