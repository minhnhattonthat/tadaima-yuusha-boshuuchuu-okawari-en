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


MAX_LEN, MAX_DIST = 255, 4096
END = "00000001111111"  # count 0xFF


def count_code(count):
    """Elias gamma; 128+ drops the top bit, the 7 zeros imply it. Last bit doubles as the distance code's skipped bit."""
    return format(count & 0x7F, "014b") if count >= 128 else format(count, f"0{2 * count.bit_length() - 1}b")


def dist_codes(rom):
    """dist -> code bits (bit strings, after the skipped bit), inverted from the decoder's tables."""
    t = tables(rom)
    codes = {}
    for a in range(0x8000):  # a is 15 code bits, top aligned as in `buf << 1`
        buf = a << 1
        if buf < 0x6000:
            y = buf << 1 >> 8
            dist, n = t["dist"][y], t["dist_bits"][y >> 4]
        else:
            y = buf >> 13
            dist, n = (a & 0x0FFF | 0x1000) >> (t["far_shift"][y] >> 1), t["far_bits"][y]
        codes.setdefault(dist, format(a, "015b")[:(n >> 1) - 1])
    return codes


def longest(data, p):
    """Nearest of the longest matches at p, (0, 0) under 2 bytes. rfind only finds a start before p, overlaps allowed."""
    low = max(p - MAX_DIST, 0)
    best = best_at = 0
    want = 2
    while want <= MAX_LEN and p + want <= len(data):
        s = data.rfind(data[p:p + want], low, p + want - 1)
        if s < 0:
            break
        n = want
        while n < MAX_LEN and p + n < len(data) and data[s + n] == data[p + n]:
            n += 1
        best, best_at, want = n, s, n + 1
    return best, p - best_at


def compress(data, dist_code, old=None):
    """Greedy parse like the original tool: longest match, nearest first. Same bytes as the ROM for all 749 blocks
    (tests/test_identity.py). `dist_code` comes from dist_codes(rom). `old` is the block's original stream: a word
    that holds only look-ahead is never read, the original tool left stale buffer bytes there, so copy them for identity."""
    data = bytes(data)
    out = bytearray(2)  # word 0
    bits = []  # code bit strings; words are written into out at the end
    words = [0]  # where each 16-bit word sits in out
    read = 16  # bits the decoder has shifted out so far
    flag_at = left = 0
    p = 0

    def flag(bit):
        nonlocal flag_at, left
        if left == 0:
            flag_at, left = len(out), 8
            out.append(0)
        left -= 1
        out[flag_at] |= bit << left

    while p < len(data):
        n, dist = longest(data, p)
        if n < 2:
            flag(1)
            out.append(data[p])
            p += 1
            continue
        flag(0)
        c, d = count_code(n - 1), dist_code[dist - 1]
        bits += [c, d]
        read += len(c) + len(d)
        while len(words) * 16 < read:  # the decoder pulls a word here, so it sits at this point of the stream
            words.append(len(out))
            out += b"\0\0"
        p += n
    flag(0)
    stream = "".join(bits) + END
    need = (len(stream) + 15) // 16
    if len(words) > need and words[-1] == len(out) - 2:
        del out[-2:]  # that word only held look-ahead, the block may end there and the next one start
        del words[-1]
    stream = stream.ljust(len(words) * 16, "0")
    for i, at in enumerate(words):
        w = int(stream[i * 16:i * 16 + 16], 2)
        out[at] = w & 0xFF
        out[at + 1] = w >> 8
        if old and i >= need:
            out[at:at + 2] = old[at:at + 2]
    return bytes(out)
