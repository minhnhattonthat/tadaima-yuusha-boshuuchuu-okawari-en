# Resources and compression

Addresses are for the dump in `rom.sha1`. HiROM: file offset = `addr & 0x3FFFFF`; banks `$C0-$DF` hold the 2 MB.

## Resource table (verified)

`$C6:0000` holds a 24-bit pointer to the table: `$DD:DF40` (file `0x1DDF40`). 863 entries of 8 bytes:

| Bytes | Field |
|---|---|
| 0-2 | source (24-bit CPU address) |
| 3-4 | unpacked size |
| 5-6 | default dest address |
| 7 | dest bank: `7E`/`7F` WRAM, `01` VRAM (dest is a word/byte address there), `81`/`FE` stored raw |

Lookup: `$82:8192` (index x 8 + table base; returns Y = source low word, A = bank, X = size).
**Verified:** `tools/unpack.py` unpacks all 863; 749 reproduce the table's size exactly, and block 740 equals the WRAM
script buffer at `$7E:A000` on the first dialogue. The other 114 (dest bank `81`/`FE`) are stored raw, not compressed.
Callers can override the dest: blocks with absolute pointers `$A0xx` list dest `7E:0000` in the table.

Blocks are packed end to end from `0x060010` to `0x1DDF3C`. Moving a block only needs its table entry changed.

## LZ format, `$82:81DA` (verified: 749 blocks, sizes exact; port in `tools/lz.py`)

One stream of flag bytes, literal bytes and 16-bit LE words of code bits, interleaved. Reader state: a 16-bit window
`buf` (top bit first), a pending word. Start: fill `buf` with 16 bits (first word), then loop:

- Every 8 items read a flag byte; bits MSB first. **1** = literal byte from the stream. **0** = copy.
- Copy: decode `count` from `buf`, then `dist`, then copy `count + 1` bytes from `dest - dist - 1`.
- `count`: top bit 1 means `count = 1` with no bits consumed. Otherwise `y = buf >> 9`:
  `y == 0`: `count = (buf >> 2) | 0x80`, 13 bits, and `0xFF` is the **end code**. `y < 8`: `count = (buf >> 1) >> tbl_8444[y]/2`.
  else `count = tbl_83C5[y]`. Bits consumed: `tbl_8405[y] / 2`.
- `dist`: `a = buf << 1`. `a < 0x6000`: `y = (a << 1) >> 8`, `dist = tbl_844C[y]`, bits `tbl_850C[y >> 4] / 2`. Else `y = a >> 13`,
  `dist = ((buf & 0xFFF) | 0x1000) >> tbl_8515[y]/2`, bits `tbl_851A[y] / 2`. The top bit of `buf` here is the last bit the
  count code consumed (or the "1" bit), which is why it is skipped.
- Tables live in bank `$82` (`$83C5-$8522`); `lz.py` reads them from the ROM.

Max distance 4096 (the codes reach `dist` 0-`0xFFF`); copies use MVN with bank `$7E` or `$7F` from `dest`, so 16-bit wrap inside one WRAM bank.

## Compressor (verified: `tests/test_identity.py`, rebuild equals the dump's SHA-1; `lz.compress`, `tools/repack.py`)

- Codes: `count` is Elias gamma (`1` = 1, `010` = 2, `00100` = 4...); from 128 it is 7 zeros + the low 7 bits. A count code's last bit is the bit the distance decoder skips, so it isn't sent twice. Copy length 2-255, distance 1-4096.
- The original parse is plain greedy: at each position the longest match, the nearest one on a tie, a literal if under 2 bytes. No lazy matching. Reproduces all 749 blocks.
- A code word sits in the stream where the decoder pulls it, between flags and literals. The pull is look-ahead: a word can hold no real bits, only the bits past the end code.
  - 46 blocks: that word would be the last 2 bytes, so the original tool left it out and the decoder reads the next block's first word as padding. `tools/unpack.py` reports `used` 2 too high for these, and in the dump the next block starts there.
  - 19 blocks: flags or literals follow it, so it has to exist. Its bytes are never used. The original left a stale output buffer in it: 13 match the same offset of an earlier block (e.g. 84 from 83, 124 from 121), 6 match no earlier block. `compress(old=...)` copies them from the dump, for identity only; a new block gets zeros.

Compressing all 2.7 MB of unpacked blocks takes about 4 seconds (`bytes.rfind`).
