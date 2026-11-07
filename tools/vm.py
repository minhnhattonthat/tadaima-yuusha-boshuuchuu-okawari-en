"""Event script VM ($C2:D69F): operand parser and flow walker. See docs/re/text.md §Event VM.

    vm.py BLOCK [--org A000]   disassemble one script block
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARGC = 0x04BB6F  # $84:BB6F, operand count per opcode


class Op:
    def __init__(self, addr, code, args, end):
        self.addr, self.code, self.args, self.end = addr, code, args, end  # args: list of (offset of operand, kind, value)

    def __repr__(self):
        return f"{self.addr:04X}: {self.code:02X} " + " ".join(f"#{v:04X}" if k == "imm" else k for _, k, v in self.args)


def operand(data, pos, top=True):
    """One operand at data[pos]. Mirrors $C2:D84F. Returns (kind, value, next pos). An immediate is `04 lo hi`."""
    t = data[pos]
    a = data[pos + 1]
    pos += 2
    kind, sub = t >> 4, t & 15
    if kind in (1, 2, 5):
        _, _, pos = operand(data, pos, False)
    elif kind == 3:
        _, _, pos = operand(data, pos, False)
        _, _, pos = operand(data, pos, False)
    elif kind > 7:
        raise ValueError(f"operand type {t:02X} at {pos - 2:#x}")
    if sub == 4:
        b = data[pos]
        pos += 1
        return ("imm" if kind == 0 else f"m{t:02X}", a | b << 8, pos)
    return (f"m{t:02X}", a, pos)


def instr(data, pos, org, argc):
    """One instruction at block offset pos."""
    code = data[pos]
    start, p, args = pos, pos + 1, []
    if code != 0xFF:
        n = argc[code]
        if n >= 0x80:
            raise ValueError(f"bad opcode {code:02X} at {org + pos:04X}")
        for _ in range(n):
            q = p
            k, v, p = operand(data, p)
            args.append((q, k, v))
    return Op(org + start, code, args, p)


def load_argc(rom):
    return rom[ARGC:ARGC + 0x60]


if __name__ == "__main__":
    rom = next((ROOT / "rom").glob("*.sfc")).read_bytes()
    data = (ROOT / f"work/blocks/{int(sys.argv[1]):03d}.bin").read_bytes()
    argc = load_argc(rom)
    org = 0xA000
    first = (data[0] | data[1] << 8) - org
    pos = first
    for i in range(0, first, 2):
        print(f"entry {i // 2}: {data[i] | data[i + 1] << 8:04X}")
    while pos < len(data):
        try:
            op = instr(data, pos, org, argc)
        except (ValueError, IndexError) as e:
            print(f"{org + pos:04X}: ?? {e}")
            break
        print(op)
        pos = op.end - 0 if op.end > pos else pos + 1
