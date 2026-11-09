"""Extract all game text to script/*.tsv and account for every byte of the text containers. See docs/re/text.md.

    extract.py          write script/ and script/nontext.tsv, print totals

Rows: id, loc, jp, en. loc = `b<block>+<hex offset>` or `r<hex file offset>`, then `:<byte length>`, end code included.
`load(rom)` returns the same rows, so tests compare them against the ROM without reading the files.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import rects  # noqa: E402
import unpack  # noqa: E402
import vm  # noqa: E402
from tbl import Table  # noqa: E402

T = Table.load(ROOT / "tbl/jp.tbl")
DIALOGUE = range(739, 767)  # u16 offset table at +0, then strings (761: chapter cards, MAP n + title)
TALK = [725, 726]  # u16 offset table, 0 = none
SHOP = range(212, 229)  # dest $8000, absolute pointers
SCRIPT = range(229, 303)  # event VM, dest $A000
VM_ORG, SHOP_ORG = 0xA000, 0x8000

# (first, end, section): file ranges of the raw strings. Bytes inside that aren't text go to nontext.tsv.
RAW = [
    (0x008F3E, 0x00A230, "bio"), (0x00A490, 0x00A6DA, "desc_item"), (0x00B54A, 0x00C298, "desc_equip"), (0x00C52B, 0x00C72F, "desc_spell"),
    (0x01978C, 0x01A841, "party"),
    # inn menu 仲間をいれる (recruit) starts at $4987C; attract-mode intro 遠い昔・・・ at $4BCF6 (both from a player bug report)
    (0x04987C, 0x049899, "system"), (0x049943, 0x049953, "system"), (0x04A1E7, 0x04A1F3, "system"),
    (0x04A2F4, 0x04B220, "system"), (0x04B485, 0x04B4A0, "system"), (0x04B8D7, 0x04B8E7, "system"),
    # recruit offer はい / いいえ choice (after 仲間にしますか？; player bug report), a second はい / いいえ ($C5:0B53) and どこに？
    # ($C2:4630): all three in tools/textsweep_raw.py; マップ がめん だよ〜ん‼ at $494E1 has no reference (debug)
    (0x04BAB9, 0x04BAC8, "system"), (0x0485E4, 0x0485F3, "system"), (0x049318, 0x04931D, "system"),
    (0x04BCF6, 0x04C84E, "story"), (0x04C84E, 0x04CBA7, "system"),
    # boss lines from the bank start: the hero's イザ、勝負っ！ at $C5:8000 (blind-spot sweep, tools/textsweep_raw.py)
    (0x058000, 0x0589D0, "boss"), (0x059F1A, 0x05A258, "clear"), (0x05AB4B, 0x05B854, "clear"),
    (0x05BBFB, 0x05BC09, "system"),  # save-slot confirm Yes/No (found on the phase 8 tour)
    (0x059452, 0x059471, "system"),  # player select: ひと / コンピュータ choice, name entry はい / いいえ (phase 8 tour)
]
# (first, count, stride, name offset, name bytes, section): fixed-size name fields, padded with F4
RECORDS = [
    # name_char: 0-44 heroes/NPCs, 45-107 inn recruits (3 levels each), then a pointer table at $8F3E
    (0x00800E, 108, 0x24, 1, 5, "name_char"), (0x00A230, 38, 0x10, 1, 8, "name_item"),
    (0x00A6DA, 231, 0x10, 1, 8, "name_equip"), (0x00C298, 41, 0x10, 1, 9, "name_spell"),
    (0x04B220, 1, 0x10, 0, 5, "name_misc"),  # label read 5 glyphs at a time, no end code ($C2A645)
    (0x009743, 12, 0x25, 1, 5, "name_hero"),  # the 12 heroes again, index byte + 5-byte name: versus mode (the shop header showed チンク)
    # battle result box label [F4]シリング + the next label's F4 ($C3:391A copies 6, asm/vwf.asm): small path, so a far name image
    (0x018479, 1, 0, 0, 6, "name_result"),
]
JP = re.compile(r"[ぁ-んァ-ヴー一-龥]")
NOISE = re.compile(r"[Ⓐ-ⓩ🅐-🅨♂♀／％＆★「」]")
LATIN_OK = re.compile(r"HP|MP|NVP|NPC|BOSS|BOO|SOS|MAP|HUMAN|THE|END|CONFIG|MODE|GO|LV[0-9]*|[🅐🅨🅧🅑]ボタン|[0-9]+(?=シリング|回|番|位|人|つ|コ|カ|が|ほん|さい|かい|キ|セ|時間|年|ポイント|$)")


def plain(s):
    return re.sub(r"\{[^}]*\}", "", s)


def texty(s):
    """Text, not table bytes that happen to decode: no unknown byte, mostly Japanese or a capitals word, no pointer sub."""
    p = plain(s).replace("[F4]", "").replace(" ", "")
    if "[" in p or re.search(r"\{sub:[0-9A-F]{2}(?!00)[0-9A-F]{2}\}", s):
        return False
    jp = len(JP.findall(p)) + p.count("・")  # 王様・・・・ is a line (King's silence in the opening; was cut to its dots)
    if re.fullmatch(r"[A-Z ]{4,}", p):
        return True
    return jp >= 2 and jp * 2 >= len(p) or set(p) <= set("・・？！…") and bool(p) or p == "あ"


def dirty(s):
    """Table bytes in front of a string pass texty: u16 tables and records decode as kana. Junk shows in the head, the glyphs
    before the row's first code: a stray letter, digit or icon, or a pointer table's rhythm (the high byte every 2nd glyph)."""
    head = re.split(r"\{", re.sub(r"^(\{nl\})+", "", s))[0]
    if re.search(r"[0-9]\[F4\]", head) or re.search(r"[0-9]", head) and len(head) <= 4 or re.match(r"[。、ァィゥェォャュョッぁぃぅぇぉゃゅょっ]", head):
        return True
    if re.fullmatch(r"\D?[0-9]{3,}", head) or len(head) == 1 and s.startswith(head + "{sfx:"):  # record bytes before a voice code: 00005{sfx, ぞ{sfx
        return True
    if re.match(r"\{color:[0-9A-F]{2}\}[0-9][^0-9{]?[A-Za-z]", s):  # a colour code then digit, kana, letter: record bytes (s225.05F6)
        return True
    if re.search(r"[0-9A-Za-z]|[Ⓐ-ⓩ🅐-🅩]", LATIN_OK.sub("", head.replace("[F4]", ""))[:12]):
        return True
    p = plain(s).replace("[F4]", "")[:24]
    return any(p[i] == p[i + 2] == p[i + 4] == p[i + 6] and p[i] not in "〜ー・ッ" and len(set(p[i + 1:i + 6:2])) == 3 for i in range(len(p) - 6))


def ptr_run(data, q, e, cuts, org):
    """3 words in a row that point inside the block: a pointer table, whatever it decodes to."""
    return e - q >= 6 and all((data[w] | data[w + 1] << 8) - org in cuts for w in range(q, q + 6, 2))


def tail(data, p, e, cuts, org=0):
    """A piece with no FF before its text: table bytes, then a string. Returns where the string starts, or None.
    The start is a pointer target or a colour or voice code, and everything after it must read as clean text."""
    if data[e - 1] not in (0xFF, 0xFE):
        return None
    marks = {q for q in range(p + 1, e - 1) if data[q] in (0xFB, 0xF6)}
    marks |= {q + 5 for q in range(p, e - 6) if data[q:q + 2] == b"\xf4\x01"}  # encounter record: name 5 bytes after F4 01
    for c in sorted({c for c in cuts if p < c < e - 1} | marks):
        s = T.decode(data, c, length=e - c)[0]
        if texty(s) and not dirty(s) and not ptr_run(data, c, e, cuts, org):
            return c
    return None


class Sink:
    """Collects rows and, per container, which bytes are accounted for."""

    def __init__(self):
        self.rows, self.other = {}, []

    def text(self, sec, tag, loc, data, pos, end):
        s = T.decode(data, pos, length=end - pos)[0]
        self.rows.setdefault(sec, []).append((f"{tag}{pos:04X}" if tag else loc[1:], f"{loc}:{end - pos}", s))

    def data(self, loc, n, why):
        self.other.append((loc, n, why))


def split(data, lo, hi, cuts=()):
    """FF-ended pieces of data[lo:hi], also cut at known pointer targets. A trailing piece with no FF comes back too."""
    marks = sorted({c for c in cuts if lo < c < hi})
    pos, m = lo, 0
    while pos < hi:
        e = data.find(b"\xff", pos, hi)
        end = e + 1 if e >= 0 else hi
        while m < len(marks) and marks[m] <= pos:
            m += 1
        if m < len(marks) and marks[m] < end:
            end = marks[m]
        yield pos, end
        pos = end


def table_block(sink, b, data, skip_zero):
    first, i = len(data), 0
    while i < first:  # the table ends where its lowest offset points
        first = min(first, (data[i] | data[i + 1] << 8) or first)
        i += 2
    offs = sorted({data[i] | data[i + 1] << 8 for i in range(0, first, 2)} - {0})
    sink.data(f"b{b}+0", first, "offset table")
    for pos, end in split(data, first, len(data), offs):
        if texty(T.decode(data, pos, length=end - pos)[0]) or pos in offs:
            sink.text("talk" if skip_zero else "dialogue", f"d{b}.", f"b{b}+{pos:X}", data, pos, end)
        else:
            sink.data(f"b{b}+{pos:X}", end - pos, "not text")


def walk(data, argc):
    """Follow the VM from the entry table. Returns (code byte set, data roots, string pointers)."""
    first = (data[0] | data[1] << 8) - VM_ORG
    todo = [(data[i] | data[i + 1] << 8) - VM_ORG for i in range(0, first, 2)]
    seen, code, tables, ptrs = set(), bytearray(len(data)), set(), set()
    code[:first] = b"\x01" * first
    inside = lambda v: VM_ORG <= v < VM_ORG + len(data)
    while todo:
        p = todo.pop()
        while 0 <= p < len(data) and p not in seen:
            seen.add(p)
            try:
                op = vm.instr(data, p, VM_ORG, argc)
            except (IndexError, ValueError) as e:
                raise ValueError(f"{p + VM_ORG:04X} {data[p:p + 8].hex(' ')} prev {[hex(q + VM_ORG) for q in sorted(seen)[-5:]]}") from e
            code[p:op.end] = b"\x01" * (op.end - p)
            imm = [v for _, k, v in op.args if k == "imm" and inside(v)]
            if op.code in (0x02, 0x07) or 0x09 <= op.code <= 0x14:
                todo += [op.args[-1][2] - VM_ORG] if op.args[-1][1] == "imm" else []
            elif op.code in (0x15, 0x16):  # jump table: word 0 is its size in bytes, then pointers
                t = op.args[1][2] - VM_ORG
                size = data[t] | data[t + 1] << 8
                code[t:t + size + 2] = b"\x01" * (size + 2)
                todo += [w - VM_ORG for w in (data[t + i] | data[t + i + 1] << 8 for i in range(2, size + 2, 2)) if w]
            elif op.code in (0x1F, 0x20, 0x21, 0x22):
                ptrs.update(v - VM_ORG for v in imm)
            else:
                tables.update(v - VM_ORG for v in imm)
            if op.code in (0x02, 0x08, 0x29, 0x45, 0xFF):  # 45 leaves the script: text follows it directly
                break
            p = op.end
    return code, tables, ptrs


def script_block(sink, b, data, argc):
    code, tables, ptrs = walk(data, argc)
    sink.data(f"b{b}+0", sum(code), "code")
    cuts = words(data, VM_ORG)
    pos, n = 0, len(data)
    while pos < n:
        if code[pos]:
            pos += 1
            continue
        end = pos
        while end < n and not code[end]:
            end += 1
        for p, e in split(data, pos, end, ptrs | tables):
            piece(sink, "event", f"e{b}.", b, data, p, e, cuts, p in ptrs)
        pos = end


def words(data, org):
    """Every u16 in the block read as a pointer, odd offsets too: possible string starts."""
    return {w - org for w in (data[i] | data[i + 1] << 8 for i in range(len(data) - 1)) if org <= w < org + len(data)}


def fixed_list(data, p, e, w=10):
    """Place names copied 10 bytes at a time ($C2:D4DE): `name FE` records, no FF. The list's end if 3+ records, else 0."""
    q = p
    while q + w < e and data[q + w] == 0xFE and 0xFE not in data[q:q + w] and texty(T.decode(data, q, length=w)[0]):
        q += w + 1
    return q if q - p >= 3 * (w + 1) else 0


def piece(sink, sec, tag, b, data, p, e, cuts, known=False):
    """Files data[p:e] as text, as table bytes then text, or as data."""
    s = T.decode(data, p, length=e - p)[0]
    org = VM_ORG if sec == "event" else SHOP_ORG
    lst = sec == "shop" and fixed_list(data, p, e)
    if lst:  # records may follow the list directly: they are data, not part of the row
        sink.text(sec, tag, f"b{b}+{p:X}", data, p, lst)
        if lst < e:
            piece(sink, sec, tag, b, data, lst, e, cuts)
        return
    if known or texty(s) and not dirty(s) and not ptr_run(data, p, e, cuts, org):  # no FF at the end: a pointer enters the string there, it runs on into the next row
        sink.text(sec, tag, f"b{b}+{p:X}", data, p, e)
        return
    head = max((q + 1 for q in range(p, e) if data[q] == 0xFE and data[q - 1] != 0xF6 and texty(t := T.decode(data, p, length=q + 1 - p)[0])
                and not dirty(t)), default=0)
    if head:  # fixed-width name list, FE after each name, no FF: records follow it directly
        sink.text(sec, tag, f"b{b}+{p:X}", data, p, head)
        sink.data(f"b{b}+{head:X}", e - head, "not text")
        return
    c = tail(data, p, e, cuts, org)
    sink.data(f"b{b}+{p:X}", (c or e) - p, "not text")
    if c:
        sink.text(sec, tag, f"b{b}+{c:X}", data, c, e)


def shop_block(sink, b, data):
    cuts = words(data, SHOP_ORG)
    for p, e in split(data, 0, len(data), {c for c in cuts if c and data[c - 1] == 0xFF}):
        piece(sink, "shop", f"s{b}.", b, data, p, e, cuts)


def records(sink, rom):
    for first, count, stride, off, size, sec in RECORDS:
        for i in range(count):
            pos = first + i * stride + off
            s = T.decode(rom, pos, length=size)[0]
            if JP.search(plain(s)):
                sink.rows.setdefault(sec, []).append((f"{sec[5:]}{i:03d}", f"r{pos:06X}:{size}", s))


FOES = range(558, 697)  # monster blocks: 4 u16 section offsets, the last section starts with the 8-byte name (no end code, F4 pads),
# copied to $7E:8161 and drawn by the tilemap path in the battle target box ($C21E66). docs/re/text.md


PARTIES = range(310, 313)  # preset parties: 4 hero records of 0x6F bytes, index byte at +3, the 5-byte name at +4


def foes(sink, blocks):
    for b in PARTIES:
        for k in range(4):
            pos = 4 + k * 0x6F
            s = T.decode(blocks[b], pos, length=5)[0]
            assert JP.search(plain(s)), (b, k, s)
            sink.rows.setdefault("name_hero", []).append((f"hero{b}{k}", f"b{b}+{pos:X}:5", s))
    for b in FOES:
        d = blocks[b]
        pos = d[6] | d[7] << 8
        s = T.decode(d, pos, length=8)[0]
        assert JP.search(plain(s)), (b, s)
        sink.rows.setdefault("name_foe", []).append((f"foe{b:03d}", f"b{b}+{pos:X}:8", s))


def load(rom):
    sink = Sink()
    blocks = {i: unpack.load(rom, src, size)[0] for i, src, size, _, _ in unpack.entries(rom)}
    argc = vm.load_argc(rom)
    for b in DIALOGUE:
        table_block(sink, b, blocks[b], False)
    for b in TALK:
        table_block(sink, b, blocks[b], True)
    for b in SHOP:
        shop_block(sink, b, blocks[b])
    for b in SCRIPT:
        script_block(sink, b, blocks[b], argc)
    for first, end, sec in RAW:
        bank = first & 0xFF0000
        cuts = {bank | rom[i] | rom[i + 1] << 8 for i in range(first, end - 1)}
        for p, e in split(rom, first, end):
            ptr = bank | rom[p - 1] | rom[p] << 8  # an FF that is a pointer's low byte: its high byte isn't text ($C5:AB8D table)
            if rom[p - 1] == 0xFF and first <= ptr < end and p + 1 in cuts:
                sink.data(f"r{p:06X}", 1, "not text")
                p += 1
            s = T.decode(rom, p, length=e - p)[0]
            clean = texty(s) and not dirty(s)
            c = None if clean else tail(rom, p, e, ())
            if c or clean and rom[e - 1] == 0xFF:
                sink.text(sec, "", f"r{c or p:06X}", rom, c or p, e)
                if c:
                    sink.data(f"r{p:06X}", c - p, "not text")
            elif s != "{end}":  # an extra FF: list separator
                sink.data(f"r{p:06X}", e - p, "not text")
    records(sink, rom)
    foes(sink, blocks)
    return sink


if __name__ == "__main__":
    rom = next((ROOT / "rom").glob("*.sfc")).read_bytes()
    sink = load(rom)
    out = ROOT / "script"
    out.mkdir(exist_ok=True)
    for sec, rows in sink.rows.items():
        path = out / f"{sec}.tsv"
        old = [r.split("\t") for r in path.read_text(encoding="utf-8").splitlines()[1:]] if path.exists() else []
        en = {r[0]: r[3] for r in old}
        # a row that now starts later (record bytes cut off its head) keeps the English of the old row it ends
        moved = {i: next((r[3] for r in old if r[0] != i and r[2].endswith(s) and r[0][:5] == i[:5]), "") for i, _, s in rows if i not in en}
        lines = ["id\tloc\tjp\ten"] + [f"{i}\t{loc}\t{s}\t{en.get(i, moved.get(i, ''))}" for i, loc, s in rows]
        (out / f"{sec}.tsv").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        print(f"{sec:12} {len(rows):5d} rows {sum(len(plain(r[2])) for r in rows):7d} chars")
    labels = rects.rows(rom)
    (out / "label.tsv").write_text("id\tloc\tjp\ten\n" + "".join(f"{i}\t{loc}\t{s}\t\n" for i, loc, s in labels), encoding="utf-8", newline="\n")
    print(f"{'label':12} {len(labels):5d} rows")
    (out / "nontext.tsv").write_text("loc\tbytes\twhy\n" + "".join(f"{a}\t{b}\t{c}\n" for a, b, c in sink.other),
                                     encoding="utf-8", newline="\n")
    print("nontext", len(sink.other), sum(n for _, n, _ in sink.other))
