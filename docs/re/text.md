# Text engine

## Encoding (verified)

`tbl/jp.tbl`. One byte per glyph code `00-F5`, `F7 xx` = glyph `$100 + xx`. **Verified:** read off the font, and decoded
block 740 matches the screen (`シルフィ` / `ようこそロスティアへ！`, `王国のメッセンジャー`). No dictionary.

Font: block 000, unpacked to `$7E:2000`, `0x4000` bytes, 512 glyphs, 16x16 1bpp, code x 32. Byte layout per glyph:
`+0..7` left column rows 0-7, `+8..15` right column rows 0-7, `+16..23` left rows 8-15, `+24..31` right rows 8-15.
Code `$C2:1B0B` fetches it, adds a one-pixel right/down shadow, and writes 4 tiles of 4bpp (colour from window `$14/$15`).
`tools/fontsheet.py` renders it.

Cells: a glyph takes 2 x 2 BG tiles (16x16). Each drawn glyph claims 4 fresh tile numbers from the window's range, written to
VRAM and tilemap at once (`$C2:1852`, during HBlank wait). See the window record below.

## Control codes, `$C2:1421` (verified from code; string pointer in Y, window record in X)

| Code | Args | Meaning |
|---|---|---|
| `FF` | - | end of string |
| `FE` | - | newline (`$C2:1A4B`) |
| `FD` | - | wait for button, then clear (`$C2:160F`, `$C2:0E49`) |
| `FC` | - | wait for button; then new line unless the window is on its last row (`$06,x` ==2) |
| `FB` | 1 | set colour pair `$14,x` |
| `FA` | 1 | text speed `$17,x` |
| `F9` | 1 | pause n frames |
| `F8` | 2 LE | inline substring: `< 0x100`: `$84:1236 + n * 16` (names, 16-byte slots), else a pointer in the current bank |
| `F7` | 1 | glyph `$100 + xx` |
| `F6` | 1 | speech blip voice id (`$18,x`, via `$84:841D` unless bit 7) |
| `F5` | - | a space (advances a cell, draws nothing) |

Glyph slots `F6-FF` (icons) are reachable only outside this path (e.g. menus: **guess**).

Window record at X (fields used here): `+0` active, `+1`, `+2` screen pos (y,x), `+6` col (in half cells: +2 per glyph), `+7` row,
`+8` width limit, `+9` row limit, `+0A/0C` first tile / first VRAM, `+0E/10` next tile / next VRAM, `+12` tile limit, `+14/15` colours,
`+17` speed, `+18` voice, `+19` flags (bit7 = paged, bit0 = BG select), `+1A/1C`, `+1E`. A full row wraps (`$C2:1746`).

Width: the game wraps by count at `+8`, so an 8x16 mode (1 cell per letter) or a VWF is the phase 5 decision. A 16-wide cell
leaves about 14 letters a line: English needs a change here. The tile budget per window is the `+0A..+12` range.

## Where text lives

Script (bytecode + strings) and strings are in LZ blocks and in raw banks. Strings end in `FF`.

| Blocks | Dest | What | Format |
|---|---|---|---|
| 739-744 | `7E:7000`, `7E:A000` | intro, title-side dialogue | u16 offset table at +0 (relative to block), then strings. 740 **verified** |
| 745-766 | `7E:8000`, `7E:9000` | story dialogue | same offset table |
| 212-228 | `7E:8000` | shops, towns, boss talk | absolute pointers `$80xx`, mixed tables and strings |
| 229-302 | `7E:A000` | NPC event scripts | bytecode with absolute `$A0xx` pointers; strings inline. VM not yet read (**next**) |
| 725, 726 | `7E:AA00`, `7E:C700` | bestiary/enemy talk | u16 table, 0 = none, then `{color:09}name{color:0F}{nl}...` |
| 005 | `7E:0000` | **not text**: u16 table of a triangular series | |

Raw text in code banks (ranges merged by `tools/rommap.py`, `work/rommap.txt`): `$C0:A493-$C0:C760` (item descriptions,
~170 short), `$C1:978C-$C1:A887` (party talk), `$C4:A2F4-$C4:CBAE` (system, events, ~140), `$C5:8017-$C5:B841` (events, ~150).
Pointers to these are not traced yet: code loads them by `LDY #imm`-style or via tables, phase 4 work. `$84:1236` names are
filled at run time. `$C4/$C5` carry `{sub:0000}` player-name substitutions.

**Copies:** `$x:4526...`, `$x:4A02...`, `$x:F796` ranges repeat in banks 00, 05, 1E, 1F: bytes look like bank-mirrored data, not
real strings (**guess**, noise from a repeated table). Check before extracting.

## Pointers

- LZ blocks: u16 offsets from block start, or absolute 16-bit addresses (`$80xx`, `$A0xx`).
- Raw banks: to trace in phase 4.
