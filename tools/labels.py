"""Label rects by hand: work/tl/labels.tsv (id<TAB>English, {nl} between runs) -> script/label.tsv's en column.
Fails on a copied rect that would grow (rects.COPIED) or a run that would cover a number; prints the rects that grow (check them in QA)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import rects  # noqa: E402

rom = next((ROOT / "rom").glob("*.sfc")).read_bytes()
en = dict(ln.split("\t") for ln in (ROOT / "work/tl/labels.tsv").read_text(encoding="utf-8").splitlines() if ln)
path = ROOT / "script/label.tsv"
lines = path.read_text(encoding="utf-8").split("\n")
out = [lines[0]]
for ln in lines[1:]:
    if not ln:
        continue
    c = ln.split("\t") + [""] * 3
    c = c[:4]
    c[3] = en[c[0]]
    off = int(c[0][4:], 16)
    w, _, _ = rects.rebuild(rom, off, c[3])
    assert w == rom[off] or off not in rects.COPIED, (c[0], c[3], "copied rect can't grow")
    if w != rom[off]:
        print(c[0], c[3], f"grows {rom[off]}->{w}")
    out.append("\t".join(c))
path.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
