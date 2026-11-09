"""Japanese-looking strings in the raw banks that no script row covers: the sweep for extractor blind spots (a range that starts
late, a table it never listed). Finds FF-ended pieces that pass extract.texty, and fixed-size records (F4-padded names) by
the same filter. textsweep_raw.py [LO-HI hex, default 000000-060000] [--min N Japanese chars, default 3]"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import extract  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def covered():
    spans = []
    for f in (ROOT / "script").glob("*.tsv"):
        for line in f.read_text(encoding="utf-8").splitlines()[1:]:
            p = line.split("\t")
            m = re.fullmatch(r"r([0-9A-F]{6}):(\d+)", p[1]) if len(p) > 1 else None
            if m:
                spans.append((int(m[1], 16), int(m[1], 16) + int(m[2])))
    return spans


def sweep(rom, lo, hi, least):
    spans = covered()
    hit = lambda a, b: any(s < b and a < e for s, e in spans)
    out = []
    pos = lo
    while pos < hi:
        e = rom.find(b"\xff", pos, hi)
        e = hi if e < 0 else e + 1
        s = extract.T.decode(rom, pos, length=e - pos)[0]
        # the text part of a piece: from the first Japanese glyph on, so table bytes in front don't hide it
        m = extract.JP.search(extract.plain(s))
        if m and len(extract.JP.findall(extract.plain(s))) >= least and not hit(pos, e):
            q = next((q for q in range(pos, e) if extract.texty(t := extract.T.decode(rom, q, length=e - q)[0]) and not extract.dirty(t)), None)
            if q is not None and not hit(q, e):
                out.append((q, e, extract.T.decode(rom, q, length=e - q)[0]))
        pos = e
    return out


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    least = int(sys.argv[sys.argv.index("--min") + 1]) if "--min" in sys.argv else 3
    lo, hi = (int(x, 16) for x in (args[0] if args and "-" in args[0] else "000000-060000").split("-"))
    rom = next((ROOT / "rom").glob("*.sfc")).read_bytes()
    for a, b, s in sweep(rom, lo, hi, least):
        print(f"{a:06X}\t{b - a}\t{s}")
