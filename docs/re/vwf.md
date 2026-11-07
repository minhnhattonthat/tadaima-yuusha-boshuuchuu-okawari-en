# English engine: far text and VWF (`asm/vwf.asm`, `tools/insert.py`, `tools/font.py`)

## Far text (verified: marker build, `tests/test_insert.py`)
The ROM grows to 4 MB (`$FFD7 = 0C`). Every translated row keeps its place: its first 3 bytes become `F0 lo hi`, the rest is blanked with `F4` and
a closing `FF` stays, so no pointer, table, list walk or block size changes. Number `hilo` indexes u24 entries at `$E1:0000` (file `210000`) that point
at the English. Far strings live in the **upper half** of file banks `21+`, read through CPU banks `$A1+:8000`: the text engine runs with DB = the string's
bank and reads low RAM by absolute address, so a `$C0+` bank would break it. Numbers skip any byte `F4+`, so a far code never reads as a padding or end byte.
Far code ends the string: the old text is never read again. A row with no `FF` (a pointer enters the next row) gets `F0` to the next row at the end of its English.
Stream recompressed in its slot; an edit that outgrows the slot fails the build (only blanking so far, so it can't yet).

## Codes (`tbl/en.tbl`, generated)
`00-09` fixed digits, old font, 16 px: code-drawn numbers line up by cell. `0A-23` A-Z (the game's own codes), `24-3D` a-z, `3E-5E` rest of ASCII, space is `3E`,
`60-69` digits for text. All `0A-69` draw from `fonts/vwf.txt` (from battle-zeque-den-en, MIT). `F0` far. `F5` = `{cell}`: a blank 16 px cell, for padding that lines up
with fixed text. Anything else draws the old way, aligned to the next cell: leftover katakana in a build shows as katakana.

## VWF (verified: `work/qa/m_open`)
Keeps the game's cell model: a window still spends 4 tiles per 16 px cell, so tile budgets, wrap and scrolling are unchanged. The pen moves inside a cell, and `+06`
and tiles advance when it crosses into the next. Cells are drawn in `$7F:FE00` (current) and `$7F:FE80` (spill), then copied to `$0FC1` and sent by the game's own
`$C217A2` path (`$0FB8` set so `$C21819` skips its cell advance).

An open cell: bit 0 of `+0E`, a tile number that's always a multiple of 4. So any code that sets `+0E` (window open, clear, ~30 menu sites) closes it with no hook. `PEN`, `WIN`,
`POS` say where the open cell is: if the window moved its cursor without setting `+0E`, the next glyph takes a new tile. Newline and page close it in `far_read`.

`$C21AC4` (string to a strip of cells in RAM, 12 callers) is replaced by `strip`: same pen, cells flushed to `X`.

## Hooks
| Site | Original | Why |
|---|---|---|
| `$C2143B` | `CMP #$FF / BNE / JMP $15B9` | reader: `F0`, close cell on `FC FD FE` |
| `$C21780` | `PLA / STA $00 / CMP..` | glyph draw; old path returns at `$C21783` |
| `$C21A99` | `LDA +01,x / AND / JSL $80E11C` | `$80E11C(id)` sleeps until `$80E14D(id)`: 1 = frame, 6 = input poll. The two per-letter waits sleep by frame; page prompt and `{pause}` keep id 6 |
| `$C21AC4` | whole routine | strip renderer |

Free WRAM: `$7F:FE00-FFFF` unchanged across 55 dumps of 7 scenes (`tools/debug/ramuse.py`).

## Tilemap path: names as tiles (verified: `work/qa/m_items`, marker ids in the item list)
Second text path, no window: `$C21E93` maps a code to a tile pair, A = upper row (blank `$26`, or a dakuten tile), B = lower row. BG2 chr at VRAM word `$4000`, tiles `$00-$FF` = block 001, 4bpp, ink 15, shadow 14, one row tall. Callers: `$C21E74` (count, `$C21E66`, 9 sites), `$C220C1` (until FE/FF, `$C2209E`, 6 sites), `$C26EC7` (list rows, 8 cells), and `$C21E8A`, a 16-bit wrapper (`$C1049E`, `$C2ABE4`, `$C2B0F4`, `$C2B5FA`). The first two add a font offset to the lower tile, `$02` / `$0A`: `small_map` subtracts it by return address.

English: `tools/insert.py images()` renders each row of `NAMES` at build time (`fonts/spleen-5x8.bdf`, trimmed to proportional, `font.small_tiles`) into the lower halves of banks `$23+`. `$E2:0000` holds u24 source + tile count per far number; rows with no image point at 3 blank tiles. Every small-path byte goes through `small_map`, so no caller changed: `F0` takes tile `HEAD`, the next two bytes are the number (still each emits a tile, so a name has at least 3), and when the number is complete it queues the DMA. After that `F4` pads emit the next tile until the name runs out, then blanks; any other byte ends it. `small_end` (`$C220BD`) keeps the FE/FF loop running while tiles remain.

Upload: `$80D78F` makes the rest of the caller run in the next VBlank with X = a record (5 bytes queue, ours after), or inline during forced blank (`$00FF` bit 7). `$80D6F5` = DMA to VRAM, D = size, A = bank, X = source, Y = word address; it leaves D = 0. Records: 8 x 14 bytes at `$0483` (**candidate**: only ramuse dumps say free, no write watch yet). `small_load` spins while 8 continuations are queued.

Pool: tiles `$41-$9F` in a ring, blanked in block 001. Rows `$27-$40` of the sheet are a-z in fixed cells for text from RAM (player names), `$24-$3D` map there; kana after them are gone, so a leftover kana on this path shows as a wrong letter. **Limit:** no dedupe: a name stays until 95 tiles are drawn after it, so a screen that keeps a label while a list scrolls long enough loses the label. Not seen yet; test on shop and status scrolls.

## Width
Lines: cells x 16 px. Measured budgets in `docs/re/windows.md`.
