"""Reflow dialogue paragraphs to fill the window: the translations kept the Japanese line breaks, so English lines ran to
about half the 236 px width. Writes id<TAB>English rows for `batches.py fix` (which lints them before writing script/).

    python -X utf8 tools/rewrap.py [OUT.tsv]    default work/tl/rewrap.tsv

Per paragraph (text between {page}/{wait}): a speaker line stays on its own; the rest is re-wrapped in the fewest lines,
balanced (the narrowest width that keeps that line count) so no stub is left on the last line, and kept only when that
saves a line (at the same count the translator's breaks fall at clauses).
Skipped: non-dialogue forms (choices, menus, names), paragraphs with a hyphen at a line end, and timed text ({pause},
lines led by a raw glyph, code-only lines: the ending's scroll).
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import batches as B  # noqa: E402

TERMS = sorted({e for _, ens, _ in B.glossary() for e in ens if " " in e}, key=len, reverse=True)
SPEAKER_LINE = re.compile(r"^(?:\{[^}]*\})*\{color:[0-9A-F]{2}\}.*\{color:0F\}$")


def wrap(words, cap, last_cap):
    """Greedy: lines of words, each <= cap px (the last <= last_cap). None if a word alone is too wide."""
    lines, cur = [], ""
    for w in words:
        t = f"{cur} {w}" if cur else w
        if B.px(t) <= cap:
            cur = t
        else:
            if not cur:
                return None
            lines.append(cur)
            cur = w
            if B.px(cur) > cap:
                return None
    lines.append(cur)
    if B.px(lines[-1]) > last_cap:
        lines.append("")  # caller sees one line more and retries
    return lines


def balanced(words, cap, last_cap):
    best = wrap(words, cap, last_cap)
    if best is None:
        return None
    n = len(best)
    seen = []
    for w in range(cap, 0, -2):  # every distinct wrap with the same line count, widest first
        got = wrap(words, w, min(w, last_cap))
        if got is None or len(got) > n or "" in got:
            break
        if got not in seen:
            seen.append(got)

    def score(ls):  # breaks after punctuation, no stub last line, then even lengths
        ends = sum(bool(re.search(r"[.!?,~…)\]]$", B.TOKEN.sub("", s))) for s in ls[:-1])
        stub = len(B.TOKEN.sub("", ls[-1]).strip()) < 8 and len(ls) > 1
        return 10 * ends - 30 * stub - (max(map(B.px, ls)) - min(map(B.px, ls))) / 50

    return max(seen, key=score) if seen else best


def reflow(en):
    body = en.removesuffix("{end}")
    parts = re.split(r"(\{page\}|\{wait\})", body)
    out = []
    for k in range(0, len(parts), 2):
        lines = parts[k].split("{nl}")
        prompt = k + 1 < len(parts)
        closing = len(lines) > 1 and lines[-1] == ""
        text = lines[:-1] if closing else lines
        head = [text[0]] if text and SPEAKER_LINE.match(text[0]) else []
        rest = text[len(head):]
        timed = any("{pause" in s or s.startswith("[") or not B.TOKEN.sub("", s).strip() for s in rest)  # ending scroll: a line at a time
        if len(rest) > 1 and not timed and not any(s.rstrip().endswith("-") for s in rest):
            joined = " ".join(s.strip() for s in rest)
            for term in TERMS:  # a glossary term never breaks across lines ("Big{nl}Four" fails the lint)
                joined = re.sub(re.escape(term), lambda m: m[0].replace(" ", "\xa0"), joined, flags=re.I)
            words = [w.replace("\xa0", " ") for w in joined.split(" ") if w]
            got = balanced(words, B.DLG_PX, B.PROMPT_PX if prompt else B.DLG_PX)
            if got and "" not in got and len(got) < len(rest):  # same count: the translator's breaks fall at clauses, keep them
                rest = got
        out.append("{nl}".join(head + rest + ([""] if closing else [])))
        if prompt:
            out.append(parts[k + 1])
    return "".join(out) + ("{end}" if en.endswith("{end}") else "")


def main(argv):
    dest = Path(argv[0]) if argv else B.ROOT / "work/tl/rewrap.tsv"
    rows, terms = [], B.glossary()
    for e in B.entries().values():
        if B.form(e) != "dlg" or not e["en"]:
            continue
        new = reflow(e["en"])
        if new != e["en"] and not B.problems(e, new, terms):
            rows.append(f"{e['id']}\t{new}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("".join(r + "\n" for r in rows), encoding="utf-8")
    print(f"{len(rows)} rows reflowed -> {dest}")


if __name__ == "__main__":
    main(sys.argv[1:])
