"""Condense story-pass chapter files for reading: control codes dropped, {nl} -> " / " (~35% smaller).

    python -X utf8 tools/condense.py [OUTDIR]     (default work/qa/story/compact; reads work/qa/story/chapters/*.txt)

Read-only aid for the story reviewer; ids stay, so fixes still go through tools/subfix.py against script/.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODES = re.compile(r"\{(?:color|pause|end|wait|page|sfx|cell)[^}]*\}")


def clean(s):
    s = CODES.sub("", s).replace("{nl}", " / ")
    return re.sub(r"\s+", " ", s).strip(" /")


def condense(text, seen=None):
    """seen: dict (head, en) -> first id; a repeat of an exact JP+EN pair becomes `id|=first_id` (--dedupe)."""
    out = []
    for line in text.splitlines():
        if line.startswith(">> "):
            parts = line[3:].split(" | ", 2)
            out.append(f"{parts[0]}|{parts[1].strip()}|{clean(parts[2]) if len(parts) == 3 else ''}")
        elif line.strip():
            out.append("  " + clean(line))
        else:
            out.append("")
        if seen is not None and line.startswith("  ") and out[-2:-1] and "|" in out[-2]:
            rid, head = out[-2].split("|", 1)
            first = seen.setdefault((head, out[-1]), rid)
            if first != rid:
                out[-2:] = [f"{rid}|={first}"]
    return "\n".join(out) + "\n"


assert condense(">> a | K | {color:0B}王{color:0F}{nl}じゃ{end}\n   x{nl}y{pause:3C}{end}") == "a|K|王 / じゃ\n  x / y\n"
assert condense(">> a | K | 王\n   x\n>> b | K | 王\n   x\n>> c | K | 王\n   y", {}) == "a|K|王\n  x\nb|=a\nc|K|王\n  y\n"

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--dedupe"]
    seen = {} if "--dedupe" in sys.argv else None
    dst = ROOT / (args[0] if args else "work/qa/story/" + ("dedup" if seen is not None else "compact"))
    dst.mkdir(parents=True, exist_ok=True)
    for f in sorted((ROOT / "work/qa/story/chapters").glob("*.txt")):
        (dst / f.name).write_text(condense(f.read_text(encoding="utf-8"), seen), encoding="utf-8")
        print(dst / f.name)
