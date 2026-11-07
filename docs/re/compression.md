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

Max distance `0x1FFF + 1`; copies use MVN with bank `$7E` or `$7F` from `dest`, so 16-bit wrap inside one WRAM bank.

**Not written yet:** a compressor. Phase 3 needs one, tested byte-for-byte or at least decompress-equal on all 749 blocks.
