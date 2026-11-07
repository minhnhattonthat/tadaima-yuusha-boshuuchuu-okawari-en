"""Pixel width of English in the dialogue font. width.py TEXT.. ; width.py --fill PX: a line of exactly PX px, for a stress row (build.py --marker ID=text)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import font  # noqa: E402

ADV = font.advances()


def width(s):
    return sum(ADV[c] for c in s)


if __name__ == "__main__":
    if sys.argv[1] == "--fill":
        px = int(sys.argv[2])
        line = "W" * (px // ADV["W"]) + "l" * (px % ADV["W"] // ADV["l"])
        assert width(line) == px
        print(line)
    else:
        for s in sys.argv[1:]:
            print(width(s), s)
