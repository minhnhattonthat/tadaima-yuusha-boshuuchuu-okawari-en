"""Phase 4: every extracted string re-encodes to the ROM's bytes, every text-container byte is accounted for."""
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import extract  # noqa: E402
import unpack  # noqa: E402

ROM = next((ROOT / "rom").glob("*.sfc"), None)
pytestmark = pytest.mark.skipif(ROM is None, reason="no dump in rom/")


@pytest.fixture(scope="module")
def world():
    rom = ROM.read_bytes()
    blocks = {i: unpack.load(rom, src, size)[0] for i, src, size, _, _ in unpack.entries(rom)}
    return rom, blocks, extract.load(rom)


def span(loc, rom, blocks):
    """loc `b745+1A:30` or `r04A2F4:30` -> (container key, start, end, container bytes)."""
    m = re.fullmatch(r"(?:b(\d+)\+|r)([0-9A-F]+):(\d+)", loc)
    start, n = int(m[2], 16), int(m[3])
    return (int(m[1]) if m[1] else "rom"), start, start + n, (blocks[int(m[1])] if m[1] else rom)


def test_roundtrip(world):
    rom, blocks, sink = world
    rows = [r for rows in sink.rows.values() for r in rows]
    assert len(rows) > 4500
    for _, loc, s in rows:
        _, a, b, data = span(loc, rom, blocks)
        assert extract.T.encode(s) == bytes(data[a:b]), loc


def test_rows_never_overlap(world):
    rom, blocks, sink = world
    seen = {}
    for rows in sink.rows.values():
        for _, loc, _ in rows:
            key, a, b, _ = span(loc, rom, blocks)
            for i in range(a, b):
                assert (key, i) not in seen, (loc, seen[key, i])
                seen[key, i] = loc


def test_string_tables_start_rows(world):
    """The song list ($A13A, op 01) points past `[F4]..{nl}` heads: each target starts a row, or the English shows blank pads."""
    ids = {r[0] for r in world[2].rows["event"]}
    assert {"e230.0FA3", "e230.0FCA", "e230.104F", "e237.0240", "e237.0267", "e237.02EC"} <= ids


def test_ids_unique(world):
    ids = [r[0] for rows in world[2].rows.values() for r in rows]
    assert len(ids) == len(set(ids))


def test_name_fields(world):
    """Foe names (battle box) and the second hero tables (versus, preset parties): fixed fields, pads only after the name."""
    rom, blocks, sink = world
    foes, heroes = sink.rows["name_foe"], sink.rows["name_hero"]
    assert len(foes) == 139 and len(heroes) == 24
    for _, loc, s in foes + heroes:
        key, a, b, data = span(loc, rom, blocks)
        name = data[a:b].rstrip(b"\xf4")
        assert name and 0xF4 not in name and 0xFF not in name, loc
    assert next(s for i, _, s in foes if i == "foe584").startswith("ホブゴブリン")


def test_blocks_fully_accounted(world):
    """Script code is listed as a byte total, so sum per block: text + data == block size, with no gap left over."""
    rom, blocks, sink = world
    done = {b: 0 for b in (*extract.DIALOGUE, *extract.TALK, *extract.SHOP, *extract.SCRIPT)}
    for rows in sink.rows.values():
        for _, loc, _ in rows:
            key, a, b, _ = span(loc, rom, blocks)
            if key in done:  # name fields in data blocks (foes, preset parties) aren't text blocks
                done[key] += b - a
    for loc, n, _ in sink.other:
        if loc[0] == "b":
            done[int(loc[1:].split("+")[0])] += n
    assert {b: n for b, n in done.items() if n != len(blocks[b])} == {}


def test_raw_ranges_fully_accounted(world):
    rom, blocks, sink = world
    covered = set()
    for rows in sink.rows.values():
        for _, loc, _ in rows:
            key, a, b, _ = span(loc, rom, blocks)
            if key == "rom":
                covered.update(range(a, b))
    for loc, n, _ in sink.other:
        if loc[0] == "r":
            start = int(loc[1:], 16)
            covered.update(range(start, start + n))
    gaps = [p for first, end, _ in extract.RAW for p in range(first, end) if p not in covered and rom[p] != 0xFF]
    assert gaps == []


def test_no_japanese_left_in_data(world):
    """A long clean kana run filed as data would be text the patch never touches."""
    rom, blocks, sink = world
    run = re.compile(r"[ぁ-ん]{13,}")  # shop id lists decode to runs of up to 12 random hiragana
    bad = []
    for loc, n, why in sink.other:
        if why == "code" or why == "offset table":
            continue
        _, a, b, data = span(f"{loc}:{n}", rom, blocks)
        s = extract.plain(extract.T.decode(data, a, length=b - a)[0])
        if run.search(s) and loc not in ("b237+13A", "r00A038"):  # read by eye: a value table and a glyph grid
            bad.append((loc, s[:40]))
    assert bad == []


def test_tables_are_not_rows(world):
    """Bytes that only decode as kana: a far code over them breaks the game (F4F4 as a script set, versus, orb table in b213)."""
    rows = {r[1].split(":")[0] for rows in world[2].rows.values() for r in rows}
    assert not {f"b{b}+0" for b in extract.SHOP} & rows
    assert not {"b233+92", "b238+212", "r05AB8D", "r05AB96"} & rows  # 05AB96: high byte of pointer $ABFF after its FF low byte
    assert {"b213+30E", "b230+508", "r05A09F", "b212+C04"} <= rows  # the string behind each table starts at its own text
    assert {"r05AB97", "r059F1A"} <= rows  # versus result line; tournament king, first entry of table $C5:9F06
    # record bytes before a shop line (00005{sfx, ぞ{sfx, {color:85}4テA): the row starts at the text, the bytes stay data
    assert {"b217+935", "b226+92E", "b226+781", "b225+5FB", "b227+5FB"} <= rows
    assert not {"b217+930", "b226+929", "b226+780", "b225+5F6", "b227+5F6"} & rows


def test_script_files_match(world):
    for sec, rows in world[2].rows.items():
        lines = (ROOT / f"script/{sec}.tsv").read_text(encoding="utf-8").split("\n")[1:-1]
        assert [tuple(l.split("\t")[:3]) for l in lines] == rows, sec
