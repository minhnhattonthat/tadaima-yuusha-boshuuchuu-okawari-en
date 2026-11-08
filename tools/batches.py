"""Translation batches (docs/translator-brief.md): split untranslated text, check translator output, merge it back.

    python -X utf8 tools/batches.py split [--size 3500]   work/tl/bNNN.tsv and build/terms_bNNN.txt for untranslated JP
    python -X utf8 tools/batches.py check [bNNN ...]      a batch's .out.tsv; with no batch, all shipped English (for check.py)
    python -X utf8 tools/batches.py merge bNNN ... [--overwrite]   check, then write the English into script/
    python -X utf8 tools/batches.py fit ID "English"      widths and lines of one row's English, as check sees them
    python -X utf8 tools/batches.py fix FILE.tsv [--dry]  id<TAB>English rows (review/terms fixes): check, then overwrite

Copied from the skill's assets/batches.py, ADAPTER fitted to script/*.tsv (id, loc, jp, en) and the width gate in
docs/re/windows.md. Rows with the same JP in one section are one entry (shop.tsv repeats its lines across 17 blocks):
the batch carries the first id, merge writes the English to every copy.
Batch TSV: id, speaker, form, limit, JP. Output: work/tl/bNNN.out.tsv, id<TAB>English, every id once, same order.
"""
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
TL = ROOT / "work/tl"
SCRIPT = ROOT / "script"
GLOSSARY = ROOT / "glossary.md"
MAX_ENTRIES = 150

# ---- ADAPTER: this game's text format ----
TOKEN = re.compile(r"\{[^}]*\}|\[[0-9A-F]{2}\]")  # control codes and raw bytes; must survive translation
GLYPHS = {"★": "[D1]", "🅐": "[E0]", "🅑": "[E1]", "🅧": "[E2]", "🅨": "[E3]", "🅛": "[E4]", "🅡": "[E5]", "♥": "[CB]", "♪": "[D0]"}  # the game's own glyphs, raw bytes in English
FREE = {"{nl}", "[F4]", "{cell}", "{page}", *GLYPHS.values()}  # layout and glyphs; {page} checked separately: never fewer
VARIABLE = r"\{sub:[0-9A-F]{4}\}"  # a name the game draws
HONORIFICS = {}  # extra JP -> EN honorific forms; empty: honorifics() builds name+suffix from the glossary's katakana names (D1)
ORDER = ["name_char", "name_item", "name_equip", "name_spell", "name_misc", "bio", "desc_item", "desc_equip", "desc_spell",
         "story", "event", "talk", "party", "boss", "clear", "dialogue", "shop", "system"]  # names first: they go into the glossary before dialogue; label.tsv is done by hand
DLG = {"story", "event", "talk", "party", "boss", "clear", "dialogue", "shop", "system"}
LINES = {"bio", "desc_item", "desc_equip", "desc_spell"}  # tilemap lines, insert.lines_in
LINE_PX, DLG_PX, PROMPT_PX, ROWS = 80, 240, 224, 3  # 10 small cells; dialogue line; line before {page}/{wait}; unmeasured window
SUB_PX, CELL_PX = 40, 16  # a {sub} name (5 letters); a [F4] / {cell} / {kanji} glyph
SPEAKER = re.compile(r"^(?:\{[^}]*\})*\{color:[0-9A-F]{2}\}([^{]+)\{color:0F\}\{nl\}")
_cache = {}


def _font():
    if not _cache:
        import font
        from tbl import Table
        _cache["adv"], _cache["small"] = font.advances(), font.small()
        _cache["tbl"] = Table.load(ROOT / "tbl/en.tbl")
        win = ROOT / "work/windows.tsv"
        _cache["win"] = {r[0]: (int(r[1]), int(r[2])) for r in (ln.split("\t") for ln in win.read_text().splitlines()) if len(r) == 3} if win.exists() else {}
        try:
            import choices
            rom = next((ROOT / "rom").glob("*.sfc")).read_bytes()
            hits = choices.choices(rom)
            _cache["choice"] = {f"e{b}.{o:04X}": op for (b, o), op in hits.items()}
        except (StopIteration, OSError):
            _cache["choice"] = {}
    return _cache


def px(s):
    """Dialogue-font width of one line of English with codes."""
    f, w = _font(), 0
    for piece in re.split(r"(\{[^}]*\}|\[[0-9A-F]{2}\])", s):
        if not piece:
            continue
        if piece.startswith("{sub:"):
            w += SUB_PX
        elif piece == "{cell}" or piece.startswith(("{kanji:", "[")):  # a raw byte draws the game's glyph in a 16 px cell
            w += CELL_PX
        elif not TOKEN.fullmatch(piece):
            w += sum(f["adv"].get(c, 8) for c in piece)
    return w


def small_px(s):
    g = _font()["small"]
    return sum(g[c][1] if c in g else 8 for c in TOKEN.sub("", s))


def cells(loc):
    return int(loc.split(":")[1])


def docs():
    """(path, header, rows) per script file; rows are [id, loc, jp, en] lists."""
    for path in sorted(SCRIPT.glob("*.tsv")):
        if path.stem in ("nontext", "label"):
            continue
        lines = path.read_text(encoding="utf-8").split("\n")
        rows = [ln.split("\t") for ln in lines[1:] if ln]
        for r in rows:
            r += [""] * (4 - len(r))
        yield path, lines[0], rows


def entries():
    """{first id: entry}; an entry is one (section, JP) with every id that holds it."""
    out, first = {}, {}
    for path, _, rows in docs():
        sec = path.stem
        for i, loc, jp, en in rows:
            key = (sec, jp)
            if key in first:
                e = out[first[key]]
                e["ids"].append(i)
                e["locs"].append(loc)
                e["en_all"].append(en)
                continue
            first[key] = i
            m = SPEAKER.match(jp)
            out[i] = {"id": i, "sec": sec, "jp": jp, "en": en, "ids": [i], "locs": [loc], "en_all": [en],
                      "speaker": m[1] if m else ""}
    for e in out.values():
        e["en"] = next((x for x in e["en_all"] if x), "")
    return out


def needs_english(entry):
    return bool(TOKEN.sub("", entry["jp"]).replace(" ", "")) and not entry["en"]


def form(entry):
    sec = entry["sec"]
    if sec in DLG:
        return "choice" if any(i in _font()["choice"] for i in entry["ids"]) else ("menu" if sec == "system" else "dlg")
    return "lines" if sec in LINES else "name"


def name_cap(entry):
    """Pixels a name may take on the tilemap path (insert.images clips at cells x 8)."""
    loc, jp = entry["locs"][0], entry["jp"]
    n = cells(loc)
    if entry["sec"] == "name_spell":
        import extract
        import insert
        m = insert.COST.search(jp)
        n -= len(extract.T.encode(m[0])) if m else 0
    return n * 8


def rows_of(entry):
    """Measured window rows; unmeasured: as many as the JP itself puts between prompts (the JP fits its window), at least 3."""
    win = _font()["win"]
    jp = max([ROWS] + [len(lines) - (not p and len(lines) > 1 and lines[-1] == "") for lines, p in segments(entry["jp"])])
    return max(min((win[i][1] for i in entry["ids"] if i in win), default=jp), jp)


def limit_label(entry):
    f = form(entry)
    if f == "name":
        return f"{name_cap(entry)}px"
    if f == "lines":
        return f"{LINE_PX}px x{min(3, (cells(entry['locs'][0]) + 1) // 4)}"
    if f == "choice":
        return "112px" if _choice_op(entry) == 0x21 else f"{DLG_PX}px"
    return f"{DLG_PX}px x{rows_of(entry)}"


def _choice_op(entry):
    return next((_font()["choice"][i] for i in entry["ids"] if i in _font()["choice"]), None)


def segments(en):
    """[(lines, prompt)]: text between prompts, split at {nl}; prompt is True when {page} or {wait} ends it."""
    body = en.removesuffix("{end}")
    parts = re.split(r"(\{page\}|\{wait\})", body)
    out = []
    for k in range(0, len(parts), 2):
        lines = parts[k].split("{nl}")
        prompt = k + 1 < len(parts)
        out.append((lines, prompt))
    return out


def width_problems(entry, en):
    n = min(cells(loc) for loc in entry["locs"])
    if n < 3 and len(_font()["tbl"].encode(en)) > n:  # too short for a far code: the English stays in the row's own bytes
        return [f"row has {n} bytes, too few for a far string: the English must fit in {n} bytes with its {{end}}"]
    f = form(entry)
    if f == "name":
        cap = name_cap(entry)
        w = small_px(en)
        return [f"{w} px over the {cap} px name slot"] if w > cap else []
    if f == "lines":
        text = en.removesuffix("{end}").split("{nl}")
        size = cells(entry["locs"][0])
        out = [f"line {k + 1} is {small_px(s)} px, over {LINE_PX}" for k, s in enumerate(text) if small_px(s) > LINE_PX]
        cost = sum(3 if s else 0 for s in text) + len(text) - 1
        if len(text) > 3 or cost > size - 1:
            out.append(f"{len(text)} lines: room for {min(3, (size + 1) // 4)} (each line costs 3 bytes + 1 between, row has {size})")
        return out
    if f == "choice":
        cap = 112 if _choice_op(entry) == 0x21 else DLG_PX
        w = max(px(s) for s in en.removesuffix("{end}").split("{nl}"))
        return [f"option {w} px, over {cap}"] if w > cap else []
    out, rows = [], rows_of(entry)
    segs = segments(en)
    for k, (lines, prompt) in enumerate(segs):
        shown = [s for s in lines]
        if not prompt and k == len(segs) - 1 and len(shown) > 1 and shown[-1] == "":
            shown = shown[:-1]  # a closing {nl}
        if len([s for s in shown]) > rows:
            out.append(f"{len(shown)} lines between prompts, window has {rows}: add a {{page}}")
        for j, s in enumerate(lines):
            cap = PROMPT_PX if prompt and j == len(lines) - 1 else DLG_PX
            if px(s) > cap:
                out.append(f"line {TOKEN.sub('', s)[:24]!r}.. is {px(s)} px, over {cap}")
    return out


def stub_problems(entry, en):
    """A lowercase word or two orphaned on the last line of a dialogue paragraph ("..., so" / "but"); a name variable,
    a speaker label above it, or a capitalised exclamation ("Why?!") is not a stub."""
    if form(entry) != "dlg":
        return []
    out = []
    for lines, prompt in segments(en):
        if lines and lines[-1] == "" and not prompt:
            lines = lines[:-1]
        last = TOKEN.sub("", lines[-1]).strip() if len(lines) > 1 else ""
        if last and len(last) < 6 and last[0].islower() and "{sub:" not in lines[-1] and not SPEAKER.match(lines[-2] + "{nl}"):
            out.append(f"stub last line {last!r}: rewrap the paragraph")
    return out


def encodable_problems(en):
    try:
        _font()["tbl"].encode(en)
    except ValueError as err:
        return [str(err).split(" in ")[0]]
    return []
# ---- end of ADAPTER ----


def kind(char):
    if "぀" <= char <= "ゟ":
        return "hiragana"
    if "゠" <= char <= "ヿ":
        return "katakana"
    if "一" <= char <= "鿿" or char == "々":
        return "kanji"
    return "other"


def has_term(jp, term):
    """term occurs as a whole kana or kanji run: ミン isn't in タイミング, くも isn't in ぼくも."""
    for m in re.finditer(re.escape(term), jp):
        a, b = m.start(), m.end()
        if (a == 0 or kind(jp[a - 1]) != kind(term[0])) and (b == len(jp) or kind(jp[b]) != kind(term[-1])):
            return True
    return False


def glossary():
    """[(JP forms, EN forms, avoid forms)] from glossary.md's | JP | EN | max | notes | Avoid | tables."""
    rows = []
    if not GLOSSARY.exists():
        return rows
    for line in GLOSSARY.read_text(encoding="utf-8").splitlines():
        cells_ = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and len(cells_) >= 2 and cells_[0] not in ("JP", "") and not set(cells_[0]) <= set("-: "):
            avoid = [x.strip() for x in cells_[4].split("/") if x.strip()] if len(cells_) > 4 else []
            rows.append(([x.strip() for x in cells_[0].split("/")], [x.strip() for x in cells_[1].split("/")], avoid))
    return rows


def honorifics(terms):
    """D1: honorifics stay on personal names. Name+suffix from the glossary's katakana names, e.g. ラター様 -> Ratar-sama."""
    if "hon" not in _cache:
        suf = {"さん": "-san", "様": "-sama", "ちゃん": "-chan", "くん": "-kun"}
        _cache["hon"] = {j + s: e + x for jps, ens, _ in terms for j in jps if j and all(kind(c) == "katakana" for c in j)
                         for e in ens[:1] for s, x in suf.items()}
    return _cache["hon"]


def problems(entry, en, terms):
    """Every rule, on one row of English."""
    jp = entry["jp"]
    if not en.strip():
        return ["empty English"]
    out = []
    if re.search(r"\\u[0-9a-fA-F]{4}|\\n", en) or "\t" in en:
        out.append("escape sequence or tab in the English (breaks are {nl})")
    out += encodable_problems(en)
    want = Counter(t for t in TOKEN.findall(jp) if t not in FREE)
    have = Counter(t for t in TOKEN.findall(en) if t not in FREE)
    if want != have:
        out.append(f"control codes differ: JP {dict(want)} EN {dict(have)}")
    if en.count("{page}") < jp.count("{page}"):
        out.append(f"{{page}} count {en.count('{page}')}, JP has {jp.count('{page}')}: never fewer")
    if jp.endswith("{end}") != en.endswith("{end}"):
        out.append("{end} must close the English exactly when it closes the JP")
    if re.search(VARIABLE + r"(st|nd|rd|th|'s)\b", en):
        out.append("suffix glued to a name variable")
    jp_plain = TOKEN.sub("", jp)
    for jps, ens, avoid in terms:
        if any(has_term(jp_plain, j) for j in jps) and not any(x.lower() in en.lower() for x in ens):
            out.append(f"glossary: {jps[0]} -> {ens[0]}")
        out += [f"glossary Avoid: {a}" for a in avoid if re.search(rf"\b{re.escape(a)}\b", en)]
    for jp_form, en_form in (HONORIFICS or honorifics(terms)).items():
        if has_term(jp_plain, jp_form) and en_form.lower() not in en.lower():
            out.append(f"honorific {jp_form} needs {en_form}")
    return out + width_problems(entry, en) + stub_problems(entry, en)


def read_tsv(path):
    return [line.split("\t") for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def existing():
    return sorted(TL.glob("b[0-9][0-9][0-9].tsv"))


def split(size):
    """Numbers on from the last batch and leaves out ids already batched, so a repeat run can't duplicate work."""
    TL.mkdir(parents=True, exist_ok=True)
    (ROOT / "build").mkdir(exist_ok=True)
    taken = {r[0] for p in existing() for r in read_tsv(p)}
    n = max((int(p.stem[1:]) for p in existing()), default=0)
    todo = [e for e in entries().values() if needs_english(e) and e["id"] not in taken]
    todo.sort(key=lambda e: ORDER.index(e["sec"]))  # stable: file order inside a section
    batches, cur, chars = [], [], 0
    for e in todo:
        c = len(TOKEN.sub("", e["jp"]))
        if cur and (chars + c > size or len(cur) >= MAX_ENTRIES or (cur[-1]["sec"] in DLG) != (e["sec"] in DLG)):
            batches.append(cur)
            cur, chars = [], 0
        cur.append(e)
        chars += c
    if cur:
        batches.append(cur)
    for batch in batches:
        n += 1
        name = f"b{n:03d}"
        path = TL / f"{name}.tsv"
        if path.exists():
            sys.exit(f"{path} already exists")
        rows = [f"{e['id']}\t{e['speaker']}\t{form(e)}\t{limit_label(e)}\t{e['jp']}" for e in batch]
        path.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
    terms_files()
    print(f"{len(batches)} new batches in {TL}, {len(taken)} ids already batched")


def terms_files():
    """build/terms_bNNN.txt for every batch, from the glossary as it is now (re-run after merging new terms)."""
    terms = glossary()
    for path in existing():
        jps = " ".join(TOKEN.sub("", r[4]) for r in read_tsv(path) if len(r) > 4)
        used = [(j, ens[0]) for jpl, ens, _ in terms for j in jpl if has_term(jps, j)]
        (ROOT / f"build/terms_{path.stem}.txt").write_text("".join(f"{j}\t{x}\n" for j, x in dict.fromkeys(used))
                                                           or "(no glossary terms in this batch)\n", encoding="utf-8", newline="\n")


def check_batch(batch, ents, terms):
    want = [r[0] for r in read_tsv(TL / f"{batch}.tsv")]
    rows = [(r[0], "\t".join(r[1:])) for r in read_tsv(TL / f"{batch}.out.tsv")]
    bad = []
    if [r[0] for r in rows] != want:
        got = [r[0] for r in rows]
        dup = sorted(i for i, c in Counter(got).items() if c > 1)
        bad.append(f"ids differ: missing {sorted(set(want) - set(got))[:8]} extra {sorted(set(got) - set(want))[:8]} "
                   f"duplicate {dup[:8]} (order must match too)")
    for eid, en in rows:
        if eid in ents:
            bad += [f"{eid}: {p}: {en!r}" for p in problems(ents[eid], en, terms)]
    return bad, dict(rows)


def merge(new, overwrite):
    """Every copy of an entry gets its English. Refuses to replace different English unless told to, before anything is written."""
    ents = entries()
    want = {i: en for eid, en in new.items() for i in ents[eid]["ids"]}
    docs_ = list(docs())
    if not overwrite:
        for _, _, rows in docs_:
            for r in rows:
                if r[0] in want and r[3] and r[3] != want[r[0]]:
                    sys.exit(f"{r[0]} would lose {r[3]!r}: pass --overwrite if that is meant")
    changed = 0
    for path, head, rows in docs_:
        touched = False
        for r in rows:
            if r[0] in want and r[3] != want[r[0]]:
                r[3] = want[r[0]]
                touched = True
                changed += 1
        if touched:
            path.write_text("\n".join([head] + ["\t".join(r) for r in rows]) + "\n", encoding="utf-8", newline="\n")
    print(f"merged: {changed} rows changed")


def main(argv):
    if not argv:
        sys.exit(__doc__)
    cmd, args = argv[0], argv[1:]
    if cmd == "split":
        return split(int(args[args.index("--size") + 1]) if "--size" in args else 3500)
    if cmd == "terms":  # also refreshes each batch's limit column after an engine change
        ents = entries()
        for p in existing():
            rows = read_tsv(p)
            for r in rows:
                r[3] = limit_label(ents[r[0]])
            p.write_text("\n".join("\t".join(r) for r in rows) + "\n", encoding="utf-8", newline="\n")
        return terms_files()
    ents, terms = entries(), glossary()
    if cmd == "fit":
        e = ents.get(args[0]) or next(x for x in ents.values() if args[0] in x["ids"])
        print(f"{e['id']} {form(e)} {limit_label(e)}")
        for lines, prompt in segments(args[1]) if form(e) not in ("name", "lines") else [(args[1].split("{nl}"), False)]:
            for s in lines:
                print(f"  {px(s) if form(e) != 'lines' and form(e) != 'name' else small_px(s):4} px  {s}")
            print("  -- prompt" if prompt else "  -- end")
        for p in problems(e, args[1], terms):
            print("PROBLEM:", p)
        return 0
    if cmd == "fix":  # review / terms fixes: FILE of id<TAB>English rows, checked, then merged over the old English
        first = {i: e["id"] for e in ents.values() for i in e["ids"]}
        new = {first.get(r[0], r[0]): "\t".join(r[1:]) for r in read_tsv(Path(args[0]))}
        bad = [f"{i}: {p}: {en!r}" for i, en in new.items() for p in
               (problems(ents[i], en, terms) if i in ents else ["unknown id"])]
        print("\n".join(bad) or f"{len(new)} rows OK")
        if bad:
            return 1
        return 0 if "--dry" in args else merge(new, True)
    overwrite = "--overwrite" in args
    names = [a for a in args if a != "--overwrite"]
    if cmd == "check" and not names:
        bad = [f"{i}: {p}: {e['en']!r}" for i, e in ents.items() if e["en"] for p in problems(e, e["en"], terms)]
        bad += [f"{e['id']}: copies differ: {sorted(set(e['en_all']))}" for e in ents.values() if len(set(e["en_all"])) > 1]
        print(f"{len(ents)} entries, {sum(bool(e['en']) for e in ents.values())} translated, {len(bad)} problems")
        print("\n".join(bad[:200]))
        return 1 if bad else 0
    if cmd not in ("check", "merge") or not names:
        sys.exit(__doc__)
    new, failed = {}, 0
    for batch in names:
        bad, rows = check_batch(batch, ents, terms)
        new.update(rows)
        failed += bool(bad)
        print(f"{batch}: " + ("OK" if not bad else f"{len(bad)} problems"))
        for line in bad:
            print("  " + line)
    if failed:
        return 1
    if cmd == "merge":
        merge(new, overwrite)
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
