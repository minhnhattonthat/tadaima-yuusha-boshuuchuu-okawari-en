"""Rows that are choice-window options (event VM ops 20/21/22, docs/re/text.md): choices.py -> id, op, jp.
Each option goes in a slot as `F8 ptr FF`; the width gate needs their window measured (docs/re/windows.md)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import extract  # noqa: E402
import unpack  # noqa: E402
import vm  # noqa: E402


def choices(rom):
    """{(block, offset): op} for every string operand of a choice op."""
    blocks = {i: unpack.load(rom, src, size)[0] for i, src, size, _, _ in unpack.entries(rom)}
    argc = vm.load_argc(rom)
    out = {}
    for b in extract.SCRIPT:
        data = blocks[b]
        code, _, _ = extract.walk(data, argc)
        p = 0
        while p < len(data):
            if not code[p]:
                p += 1
                continue
            try:
                op = vm.instr(data, p, extract.VM_ORG, argc)
            except (IndexError, ValueError):
                p += 1
                continue
            if op.code in (0x20, 0x21, 0x22):
                for _, k, v in op.args:
                    if k == "imm" and extract.VM_ORG <= v < extract.VM_ORG + len(data):
                        out[(b, v - extract.VM_ORG)] = op.code
            p = op.end
    return out


if __name__ == "__main__":
    rom = next((ROOT / "rom").glob("*.sfc")).read_bytes()
    hits = choices(rom)
    for sec in extract.load(rom).rows.values():
        for i, loc, jp in sec:
            if not loc.startswith("b"):
                continue
            b, off = loc[1:].split(":")[0].split("+")
            if (int(b), int(off, 16)) in hits:
                print(i, f"{hits[(int(b), int(off, 16))]:02X}", jp, sep="\t")
