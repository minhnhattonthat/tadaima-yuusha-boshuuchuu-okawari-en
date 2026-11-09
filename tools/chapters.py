"""Story-pass chapter files (references/translation.md §Review): work/qa/story/chapters/NN_name.txt, `>> id | speaker | JP` / `EN`
in script order, then `qa_gate.py init work/qa/story/manifest.tsv work/qa/story/chapters --glob "*.txt"`.

    python -X utf8 tools/chapters.py

The game has no chapter table: units are script files and block ranges in play order (opening and results, Sylphy/King
guide pages per map, town events per map, boss scenes, recruits, VS lines), each small enough for one review pass.
"""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "work/qa/story/chapters"
# name, file, first id prefix, last id prefix (inclusive, compared as strings; None = whole file)
UNITS = [
    ("01_story_clear", ["story", "clear"], None, None),
    ("02_guide_d739-d752", ["dialogue"], "d739", "d752"),
    ("03_guide_d753-d766", ["dialogue"], "d753", "d766"),
    ("04_events_e229-e233", ["event"], "e229", "e233"),
    ("05_events_e234-e239", ["event"], "e234", "e239"),
    ("06_events_e240-e245", ["event"], "e240", "e245"),
    ("07_events_e246-e251", ["event"], "e246", "e251"),
    ("08_events_e252-e254", ["event"], "e252", "e254"),
    ("09_events_e255-e257", ["event"], "e255", "e257"),
    ("10_events_e258-e261", ["event"], "e258", "e261"),
    ("11_events_e262-e302", ["event"], "e262", "e302"),
    ("12_bosses_d725", ["talk"], "d725", "d725"),
    ("13_bosses_d726", ["talk"], "d726", "d726"),
    ("14_recruits_vs", ["party", "boss"], None, None),
]
SPEAKER = re.compile(r"\{color:0[9B27]\}([^{]+)\{color:0F\}")


def rows(name):
    with open(ROOT / f"script/{name}.tsv", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t", quoting=csv.QUOTE_NONE))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.txt"):
        old.unlink()
    for name, files, lo, hi in UNITS:
        out = []
        for f in files:
            for r in rows(f):
                block = r["id"][:4]
                if lo and not lo <= block <= hi:
                    continue
                who = ", ".join(dict.fromkeys(SPEAKER.findall(r["en"])))
                out.append(f">> {r['id']} | {who} | {r['jp']}\n   {r['en'] or '(untranslated)'}\n")
        assert out, name
        (OUT / f"{name}.txt").write_text("".join(out), encoding="utf-8", newline="\n")
        print(f"{name}: {len(out)} entries, {sum(map(len, out)) // 1024} KB")


if __name__ == "__main__":
    main()
