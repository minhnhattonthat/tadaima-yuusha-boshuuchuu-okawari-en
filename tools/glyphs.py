"""Put the game's own glyphs back where translators wrote an ASCII stand-in: ★ was `*`, a button icon (🅐 🅑 🅧 🅨 🅛 🅡) was its
letter between colour codes (`}A{`). Only a row whose stand-in count equals the JP's glyph count is changed; others are listed.
glyphs.py [--write]: a code-level fix (raw bytes), not prose."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import batches  # noqa: E402

STAND_IN = {"★": r"\*", "🅐": r"(?<=\})A(?=\{)", "🅑": r"(?<=\})B(?=\{)", "🅧": r"(?<=\})X(?=\{)", "🅨": r"(?<=\})Y(?=\{)",
            "🅛": r"(?<=\})L(?=\{)", "🅡": r"(?<=\})R(?=\{)"}


def fix(jp, en):
    """(new English, problems)"""
    bad = []
    for g, pat in STAND_IN.items():
        code = batches.GLYPHS[g]
        need = jp.count(g) - en.count(code)
        if need <= 0:
            continue
        hits = len(re.findall(pat, en))
        if hits != need:
            bad.append(f"{g}: JP {jp.count(g)}, stand-ins {hits}")
            continue
        en = re.sub(pat, lambda m: code, en)
    return en, bad


def main(write):
    changed = 0
    for path, head, rows in batches.docs():
        touched = False
        for r in rows:
            if not r[3]:
                continue
            new, bad = fix(r[2], r[3])
            for b in bad:
                print(f"{r[0]}: {b}: {r[3]!r}")
            if new != r[3]:
                r[3], touched = new, True
                changed += 1
        if touched and write:
            path.write_text("\n".join([head] + ["\t".join(r) for r in rows]) + "\n", encoding="utf-8", newline="\n")
    print(f"{changed} rows {'changed' if write else 'would change'}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    assert fix("{color:07}★★{color:0F}", "{color:07}**{color:0F}")[0] == "{color:07}[D1][D1]{color:0F}"
    assert fix("{color:08}🅐{color:0F}ボタン", "{color:08}A{color:0F} Button")[0] == "{color:08}[E0]{color:0F} Button"
    main("--write" in sys.argv)
