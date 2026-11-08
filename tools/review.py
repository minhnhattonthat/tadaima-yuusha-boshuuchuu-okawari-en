"""Independent read-only review of batches with `codex exec` (docs/reviewer-brief.md), for runs where no reviewer subagent
can be started. review.py [--jobs N] bNNN.. -> work/qa/reviews/bNNN.md (needs work/qa/pairs/bNNN.txt: tools/pairs.py)."""
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROMPT = ("You are the translation reviewer. Follow docs/reviewer-brief.md exactly. Read it, glossary.md and "
          "docs/style-reference.md, then review every entry in work/qa/pairs/{b}.txt (read all of it, in passes). "
          "Read-only: do not edit any file. Return only the report in the brief's format as your final message; "
          "list at most 25 Minors.")


def run(b):
    out = ROOT / f"work/qa/reviews/{b}.md"
    if out.exists() and out.stat().st_size > 200:
        return f"{b}: kept"
    r = subprocess.run(["codex", "exec", "--sandbox", "read-only", "--skip-git-repo-check", "-C", str(ROOT),
                        "-o", str(out), PROMPT.format(b=b)], capture_output=True, text=True, encoding="utf-8",
                       errors="replace", stdin=subprocess.DEVNULL, shell=sys.platform == "win32")
    return f"{b}: exit {r.returncode}" + ("" if r.returncode == 0 else " " + r.stderr[-300:])


if __name__ == "__main__":
    args = sys.argv[1:]
    jobs = 4
    if "--jobs" in args:
        i = args.index("--jobs")
        jobs = int(args[i + 1])
        del args[i:i + 2]
    (ROOT / "work/qa/reviews").mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(jobs) as ex:
        for line in ex.map(run, args):
            print(line, flush=True)
