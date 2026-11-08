"""Width-gate stress rows for the opening (4-line, 240 px window): python -X utf8 tools/stress.py runs
build.py --marker ID=text.. -> build/tadaima_stress.sfc; then warp SCENE='opening'.
d740.000A: a 240 px line, then 241 px. d740.0024 + d740.004D: the glyph torture line (all printable ASCII but { }, which are
code brackets in script/, with double spaces). d740.0074: four 240 px lines, so the page arrow sits after a full last line."""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from width import width  # noqa: E402

FULL = "W" * 30
OVER = "W" * 29 + "fl!"
assert width(FULL) == 240 and width(OVER) == 241


def torture():
    chars = [chr(c) for c in range(33, 127) if chr(c) not in "{}"]
    lines, cur = [], ""
    for k in range(0, len(chars), 8):
        word = "".join(chars[k:k + 8])
        nxt = f"{cur}  {word}" if cur else word
        if width(nxt) > 240:
            lines.append(cur)
            nxt = word
        cur = nxt
    return lines + [cur]


def rows():
    t = torture()
    assert len(t) <= 6 and all(width(s) <= 240 for s in t), t
    page = "{sfx:FE}{page}{end}"
    return {
        "d740.000A": f"{{color:07}}{FULL}{{color:0F}}{{nl}}{{sfx:01}}{OVER}{page}",
        "d740.0024": "{sfx:01}" + "{nl}".join(t[:3]) + page,
        "d740.004D": "{sfx:01}" + "{nl}".join(t[3:] or ["(end)"]) + page,
        "d740.0074": "{sfx:01}" + "{nl}".join([FULL] * 4) + page,
    }


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    sys.exit(subprocess.call([sys.executable, "-X", "utf8", str(root / "build.py"), "--marker",
                              *(f"{k}={v}" for k, v in rows().items())], cwd=root))
