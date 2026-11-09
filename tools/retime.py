# Retime the scrolling narrations (story 04BD14, 04C50C, 04C669, 04C6E2): the BG scrolls at a fixed speed and each JP line
# (glyphs + {pause} + newline) takes 65 frames to match it. EN lines draw slower (~1.33 frames a letter), so with the JP pauses
# the text fell behind and unwritten, uncleared rows scrolled into view (player bug report 2026-11-09). docs/re/text.md.
# 1. Log the newline row clears: emu.py ROM --out work/qa/rc --route-str "300 -;4 a;5800 -" --script tools/debug/rowclear.lua
#    (ending: --script tools/debug/warp.lua --var "SCENE='ending'" --frames 24500 as well)
# 2. python -X utf8 tools/retime.py LOG FIRST_CLEAR_FRAME ROW_ID [LOG FRAME ROW ...] > work/tl/retime.fix.tsv
#    FIRST_CLEAR_FRAME = the row's first clear (a new window's first clear is VRAM 3840), then batches.py fix the file.
# Idempotent: a line already at 65 frames keeps its pause. Line 0 has no clear before it: its draw time is estimated.
import re
import sys

PERIOD = 65


def chars(line):
    return len(re.sub(r"\{[^}]*\}", "", line).replace("[F4]", "_"))


def main(args):
    rows = {l.split("\t")[0]: l.rstrip("\n").split("\t") for l in open("script/story.tsv", encoding="utf-8")}
    fits, out = [], []
    for i in range(0, len(args), 3):
        log, start, rid = args[i], int(args[i + 1]), args[i + 2]
        frames = [int(m.group(1)) for m in re.finditer(r"^f(\d+) clear", open(log).read(), re.M)]
        c = frames[frames.index(start):]
        new = []
        for k, line in enumerate(rows[rid][3].split("{nl}")):
            m = re.search(r"\{pause:([0-9A-F]{2})\}$", line)
            n = chars(line)
            if not m or n == 0 or k >= len(c):
                assert not (n and k >= len(c)), (rid, k, "log ends before this line")
                new.append(line)
                continue
            p = int(m.group(1), 16)
            dur = c[k] - c[k - 1] if k else None
            if dur is not None:
                fits.append((n, dur - p))
            new.append((k, p, n, dur, line[:m.start()]))
        out.append((rid, new))
    rate = sum(d for _, d in fits) / sum(n for n, _ in fits)
    print("frames per char %.3f" % rate, file=sys.stderr)
    for rid, new in out:
        res = []
        for x in new:
            if isinstance(x, str):
                res.append(x)
                continue
            k, p, n, dur, body = x
            q = PERIOD - ((dur - p) if dur is not None else round(rate * n))
            assert q >= 8, (rid, k, body, q)  # a line too long to draw in 65 frames: shorten the English
            res.append("%s{pause:%02X}" % (body, q))
        print(rid + "\t" + "{nl}".join(res))


if __name__ == "__main__":
    main(sys.argv[1:])
