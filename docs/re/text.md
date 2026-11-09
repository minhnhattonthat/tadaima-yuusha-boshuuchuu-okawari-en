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

**Scrolling narrations (verified, player bug report 2026-11-09):** story `04BD14`, `04C50C`, `04C669` (attract mode) and `04C6E2`
(ending) draw in a paged window (`+19` bit 7) on a BG2 that scrolls at a fixed speed. Each newline clears the next 2 tilemap rows
(`$C2:19EE`); nothing else clears them. Every JP line (glyphs at 1 frame each + `{pause}` + newline) takes exactly 65 frames, so the
text keeps pace with the scroll. EN letters draw at ~1.33 frames each: with the JP pauses the text fell ~300 frames behind and rows not
yet cleared (earlier lines) scrolled into view. The EN pauses are retimed to 65 frames a line (`tools/retime.py`, from
`tools/debug/rowclear.lua` logs); `batches.py check` lets pause values differ (count must match). **Re-run `tools/retime.py` after
any change to these 4 rows.**

Width: the game wraps by count at `+8`, so an 8x16 mode (1 cell per letter) or a VWF is the phase 5 decision. A 16-wide cell
leaves about 14 letters a line: English needs a change here. The tile budget per window is the `+0A..+12` range.

## Extraction (verified: `tests/test_extract.py`, `tools/extract.py` writes `script/*.tsv`)

Every string re-encodes to the ROM's bytes, and every byte of the 120 text blocks and the raw ranges in `extract.RAW` is
either a row or listed in `script/nontext.tsv`. What counts as text in a script or shop block is a filter (`extract.texty`), not proof: pointers
decide only for VM print operands, so the marker build still has to confirm it. Rows hold the JP with the `FF`; a row that doesn't end in `{end}` runs on
into the next row, because a pointer enters the string there (e.g. `b232+2D8`). Fixed-width place lists in the shop blocks
(`b213+8A6`) have no `FF` at all: `name{nl}name{nl}`, records follow directly.

No text found outside these: a sweep of banks 00-05 and `1D-1F` for clean kana found only noise, and so did the sweep of the other 743 blocks
(short kana-shaped hits in graphics data, `work/sweep.txt`). Blocks 722-724 and 303-306 look like text to the sweep and aren't.
Not checked: strings built by code from `LDA #glyph` chains; the marker build will show them as Japanese that stays.

Found by the marker tour: `$C5:9F06` (tournament king) starts its table at `9F1A`, so the `clear` range starts there; in the `$C5:AB8D` table the
last pointer `$ABFF` puts an `FF` before its high byte, so a raw piece that starts right after a pointer-low `FF` skips that byte (`05AB97`, versus);
shop place lists end at their last `name FE` record (`extract.fixed_list`), the records after them are data.

Multi-string lists: `$82:9D0F` walks `X` entries past a terminator word in `A` (`FFFF`), so a list is `str FF FF str FF FF`.
Used with `$C0:A490` (item descriptions, by item id), and by VM op 1F when its second operand isn't 0.

## Event VM, `$C2:D69F` (verified from code; the walker in `extract.walk` decodes every entry point of blocks 229-302 with no bad opcode)

Script block = u16 table of entry points (`$A0xx`, loaded at `$7E:A000`), then code, data tables and strings mixed.
Block for a script set: `$84:BAC9[$1816]`: entries read `$8000 + block`, bit 15 not looked at. Indices 0-73 are blocks 229-302 (the first four
out of order: 230, 231, 232, 229). The table runs on to 306, but 303-306 aren't scripts.

Instruction: opcode, then `$84:BB6F[op]` operands. `FF` ends the script; 02, 08 and 29 don't fall through, and neither does 45 (**guess**: text follows it directly). Dispatch `$C2:D70C`.
Operand, `$C2:D84F`: byte `t`, byte `a`, then by `t >> 4`: 0 none, 1/2/5 one nested operand, 3 two, 4/6/7 none. Low nibble 4 = one more
byte at the end. `04 lo hi` is an immediate. Nested calls keep their state (**guess**: `$80:DD84` saves `$F8-$FF`, not read; the parse only works if so).

| Op | Operands | What |
|---|---|---|
| 00 | dst, value | assign |
| 01 | dst, index, table | value table lookup |
| 02 / 07 / 08 | target / target / - | jump / call / return |
| 09-14 | a, b, target | compare and branch |
| 15 / 16 | index, table | jump table: u16 size in bytes, then targets (0 = skip) |
| 1F | string, list index | print (`$C2:0E0F`) |
| 20 / 21 / 22 | strings, then dst | choice windows (`$C2:2116`): each string goes in a slot as `F8 ptr FF`, so pointers must stay in the bank |
| 29 | script set, entry | far jump to another block |
| 2A-2C, 2D, 4C | data table | shops, encounters, fixed 10-byte data; tables can end in a name string with no pointer of its own |

Handlers for the other ops were not read: no operand of theirs points into the block.

## Item, equipment and spell records (verified from `$C2:98D2-98FE`, `$C2:9880`)

| Base | Stride | Count | Name | Fetched by |
|---|---|---|---|---|
| `$C0:800E` | `$24` | 108 | +1, 5 cells | `$C2:987F` (characters; 45-107 are the inn recruits, 3 levels each, then a pointer table at `$8F3E`. Was 45 until a player bug report: recruit names stayed katakana) |
| `$C0:A230` | 16 | 38 | +1, 8 cells | `$C2:98EA` (items) |
| `$C0:A6DA` | 16 | 231 | +1, 8 cells | `$C2:98A4` (equipment) |
| `$C0:C298` | 16 | 41 | +1, 9 cells: name, `／`, cost | `$C2:98D2` (spells) |

Names are padded with `F4` (blank glyph). `$C2:2246` trims the padding and appends `FFFF`. Records are copied to `$0F7A`, and names reach
text through the 16-byte slots at `$84:1236` (`{sub:0000}`). Item descriptions are copied until `FFFF` into `$1246`: there's a RAM limit to measure.

## Where text lives

Script (bytecode + strings) and strings are in LZ blocks and in raw banks. Strings end in `FF`.

| Blocks | Dest | What | Format |
|---|---|---|---|
| 739-744 | `7E:7000`, `7E:A000` | intro, title-side dialogue | u16 offset table at +0 (relative to block), then strings. 740 **verified** |
| 745-766 | `7E:8000`, `7E:9000` | story dialogue | same offset table |
| 212-228 | `7E:8000` | shops, towns, boss talk | absolute pointers `$80xx`, mixed tables and strings |
| 229-302 | `7E:A000` | NPC event scripts | bytecode with absolute `$A0xx` pointers; strings inline. See Event VM |
| 725, 726 | `7E:AA00`, `7E:C700` | bestiary/enemy talk | u16 table, 0 = none, then `{color:09}name{color:0F}{nl}...` |
| 005 | `7E:0000` | **not text**: u16 table of a triangular series | |

Raw text in code banks: exact ranges in `extract.RAW`. `$84:1236` names are filled at run time. `$C4/$C5` carry `{sub:0000}` player-name
substitutions. **Copies:** `$x:4526...`, `$x:4A02...`, `$x:F796` ranges repeat in banks 00, 05, 1E, 1F: these are noise, none of it is a string.

## Pointers

- LZ blocks: u16 offsets from block start, or absolute 16-bit addresses (`$80xx`, `$A0xx`).
- Raw banks: `LDY #imm` before a print call (`$C2:0E0F`, `$C2:140A`), and tables (`$C4:D189` n=47, `$C4:D2DF` n=12, `$C5:B1B7` n=40 ...). **Not all
  traced**: 843 of 1234 FF-split pieces (noise included) have no pointer the scan could find (lists, computed tables). Phase 5 plan below doesn't need them.

## Plan for insertion (**guess**, prove in phase 5)

Strings stay where they are and get replaced from the front: a new control code + 24-bit pointer to the English in new banks `$E0+`, read
from ROM. Then no pointer, table, list walk or block size changes, and WRAM limits on script blocks stop mattering. Costs and traps:
- `$C2:1421` reads through DBR + Y, so the code must switch both. A `{sub}` to a slot and text in a 16-byte slot need it too.
- Pieces under 4 bytes need a shorter form (a table index), or stay in place when the English fits.
- A list walk scans for `FFFF`, so the pointer bytes must not make that word, and the rest of the old string stays in place after the code.
- A row with no end code runs into the next row: the English of the first must end by jumping there, or hold both.
- Text copied to RAM until `FFFF` (item descriptions, `$1246`) copies the code, fine, if the reader handles it from RAM.
