"""What an extractor change did: rows gone or new against the script/ in git. rowdiff.py [REV]"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
rev = sys.argv[1] if len(sys.argv) > 1 else "HEAD"


def rows(text):
    return {c[1]: c[2] for c in (l.split("\t") for l in text.splitlines()[1:])}


for f in sorted((ROOT / "script").glob("*.tsv")):
    if f.name == "nontext.tsv":
        continue
    git = subprocess.run(["git", "show", f"{rev}:script/{f.name}"], cwd=ROOT, capture_output=True, encoding="utf-8")
    old, new = rows(git.stdout), rows(f.read_text(encoding="utf-8"))
    for k in old.keys() - new.keys():
        print("-", f.stem, k, old[k][:80])
    for k in new.keys() - old.keys():
        print("+", f.stem, k, new[k][:80])
