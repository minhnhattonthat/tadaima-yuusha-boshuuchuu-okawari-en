# ROM map and free space

HiROM + FastROM (`$FFD5 = 31`), 2 MB (`$FFD7 = 0B`), SRAM (`$FFD8 = 03`), region Japan, maker `33`. Title (half-width kana)
`ﾀﾀﾞｲﾏﾕｳｼｬﾎﾞｼｭｳﾁｭｳｵｶﾜﾘ`.

| File range | Contents |
|---|---|
| `000000-05FFFF` | code and raw data (banks `$C0-$C5`) with raw strings; see `text.md` |
| `060000-06000F` | table pointer + 13 bytes |
| `060010-1DDF3C` | LZ and raw blocks, end to end (`tools/rommap.py`) |
| `1DDF40-1DF837` | resource table |
| `1DF838-1FFFFF` | not mapped by the table: rest of bank `1D` and banks `1E`, `1F` |

Compressed blocks leave only short gaps (`17E418-17FFFF`, `1AEB80-1AFFFF`, `1CF0AD-1CFFFF`): these are **candidates**, not free
(fill-and-tour first).

## Free space plan (**guess**, promote in phase 5)

Expand 2 -> 4 MB: `$FFD7 = 0C`, new banks `$E0-$FF` (file `0x200000+`) are free by construction, and the resource table holds
24-bit sources, so any block can move there. The checksum is fixed at release.

WRAM buffers are fixed-size: dialogue blocks unpack to `$7E:8000/9000/A000` and sit beside other data, so a longer English
block can overrun. Check each dest's real limit before phase 6, or read the text directly from ROM.
