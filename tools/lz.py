"""The game's LZ codec ($82:81DA). See docs/re/compression.md for the format.

decompress(rom, off) -> (data, consumed). `rom` is the whole file, `off` a file offset.
The code tables stay in ROM (bank $82): read them from there, so the codec can't disagree with the game.
"""


class _Bits:
    """Flag bytes, literals and 16-bit words of code bits interleaved in one stream."""

    def __init__(self, rom, pos):
        self.rom, self.pos = rom, pos
        self.buf = self.nxt = self.avail = 0

    def word(self):
        w = self.rom[self.pos] | self.rom[self.pos + 1] << 8
        self.pos += 2
        return w

    def byte(self):
        b = self.rom[self.pos]
        self.pos += 1
        return b

    def read(self, n):
        """Port of $82:82BE: shift n bits out of the top of buf, topping it up from the stream."""
        self.buf = self.buf << n & 0xFFFF
        if self.avail < n:
            n -= self.avail
            self.buf |= (self.nxt & (1 << self.avail) - 1) << n & 0xFFFF
            self.nxt = self.word()
            self.avail = 16
        self.avail -= n
        self.buf |= self.nxt >> self.avail & (1 << n) - 1


def tables(rom):
    b = 0x20000
    return {"lit_len": rom[b + 0x83C5:b + 0x8405], "len_bits": rom[b + 0x8405:b + 0x8445],
            "len_shift": rom[b + 0x8444:b + 0x844C], "dist": rom[b + 0x844C:b + 0x850C],
            "dist_bits": rom[b + 0x850C:b + 0x8518], "far_shift": rom[b + 0x8515:b + 0x851D],
            "far_bits": rom[b + 0x851A:b + 0x8522]}


def decompress(rom, off):
    """Returns (data, bytes consumed). Ends on the stream's own end code."""
    t = tables(rom)
    b = _Bits(rom, off)
    b.read(16)
    out = bytearray()
    flags = left = 0
    while True:
        if left == 0:
            flags, left = b.byte(), 8
        left -= 1
        lit = flags & 0x80
        flags = flags << 1 & 0xFF
        if lit:
            out.append(b.byte())
            continue
        a = b.buf
        if a & 0x8000:
            count = 1
        else:
            y = a >> 9
            if y == 0:
                count = a >> 2 | 0x80
                if count == 0xFF:
                    return bytes(out), b.pos - off
            elif y < 8:
                count = a >> 1 >> (t["len_shift"][y] >> 1)
            else:
                count = t["lit_len"][y]
            b.read(t["len_bits"][y] >> 1)
        a = b.buf << 1 & 0xFFFF  # the top bit is never part of the distance code
        if a < 0x6000:
            y = a << 1 >> 8
            dist = t["dist"][y]
            n = t["dist_bits"][y >> 4]
        else:
            y = a >> 13
            dist = (b.buf & 0x0FFF | 0x1000) >> (t["far_shift"][y] >> 1)
            n = t["far_bits"][y]
        b.read(n >> 1)
        src = len(out) - dist - 1
        for i in range(count + 1):
            out.append(out[src + i])
