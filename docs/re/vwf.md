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

WRAM `$7F:FE00-FFFF`: in the original, only block 4's load (`7F:E000`, 8 KB, its last 512 bytes zero) writes it, and only the LZ decoder reads it (read watch, `tools/debug/readlog.lua --var PAGE=1`; a DMA at `$80D761` reads `7F:F980-FCxx` in versus, below it). So a screen load can zero our state mid-text: every state byte is clamped or harmless at 0 (`HEAD` falls back to `POOL`).

Free WRAM by write map (`tools/debug/lowmap.lua` on the original over the 64-scene tour, `tools/debug/freeram.py work/qa/origmap`): `$7E:CC00-CFFF` (but blocks 405, 424, 726 load there), `$7E:7E00-7FFF` (no block, but caller-dest loads up to `$2140` bytes could reach it from `7E:7000`), low RAM only scraps. Low RAM `$1Fxx` is task stacks (`$80:E145` saves each task's S), so unwritten bytes there are slack, not free.

## Tilemap path: names as tiles (verified: `work/qa/m_items`, marker ids in the item list)
Second text path, no window: `$C21E93` maps a code to a tile pair, A = upper row (blank `$26`, or a dakuten tile), B = lower row. BG2 chr at VRAM word `$4000`, tiles `$00-$FF` = block 001, 4bpp, ink 15, shadow 14, one row tall. Callers: `$C21E74` (count, `$C21E66`, 9 sites), `$C220C1` (until FE/FF, `$C2209E`, 6 sites), `$C26EC7` (list rows, 8 cells), and `$C21E8A`, a 16-bit wrapper (`$C1049E`, `$C2ABE4`, `$C2B0F4`, `$C2B5FA`). The first two add a font offset to the lower tile, `$02` / `$0A`: `small_map` subtracts it by return address.

English: `tools/insert.py images()` renders each row of `NAMES` at build time (`fonts/spleen-5x8.bdf`, trimmed to proportional, `font.small_tiles`) into the lower halves of banks `$23+`. `$E2:0000` holds u24 source + tile count per far number; rows with no image point at 3 blank tiles. Every small-path byte goes through `small_map`, so no caller changed: `F0` takes tile `HEAD`, the next two bytes are the number (still each emits a tile, so a name has at least 3), and when the number is complete it queues the DMA. After that `F4` pads emit the next tile until the name runs out, then blanks; any other byte ends it. `small_end` (`$C220BD`) keeps the FE/FF loop running while tiles remain.

Upload: `$80D78F` makes the rest of the caller run in the next VBlank with X = a record (5 bytes queue, ours after), or inline during forced blank (`$00FF` bit 7). `$80D6F5` = DMA to VRAM, D = size, A = bank, X = source, Y = word address; it leaves D = 0. A record is a linked-list node: `+0` next, `+2` return address (`$80:D79D`), so it must sit in bank 0, and a stray write there sends the scheduler to garbage. Game callers each own a static record (`LDX #$07E0`, `#$12B8`, text cells `#$10CA`). Ours: 3 records of 6 bytes at `$1538-$1549` (never written on the original's tour, no absolute operand names `$1538-$154A`); the payload (source, bank, tile count, VRAM word, busy flag) is at `$7F:FF40`, 12 bytes a record. `small_load` sleeps while 8 continuations are queued, and up to 3 frames while its next record is still busy. **Was** 8 x 14 bytes at `$0483`: that is the tail of the sprite buffer (`$82:A070 STA $0220,x`, `$C2:5F83`), written in 62 of 64 scenes: the versus crash (state `3A`, low RAM overwritten) and black screens came from there.

Pool: tiles `$4A-$9F` in a ring, blanked in block 001. Tiles `$30-$49` of the sheet (the game's own hiragana) are a-z in fixed cells for text from RAM (player names); the game's mapping sends codes `$24-$3D` there, so a leftover kana on this path shows as a wrong letter. `$27 $28 $29 $2B` (marks, long bar, slash) stay the game's. **Limit:** no dedupe: a name stays until 86 tiles are drawn after it, so a screen that keeps a label while a list scrolls long enough loses the label. Not seen yet; test on shop and status scrolls.

## Lines on the tilemap path (`tools/insert.py lines_in`)
Item, equipment and spell descriptions and bios (`insert.LINES`) reach the tilemap through `$C220C1` one line at a time, FE between, 10 cells wide (rect 10x4 or 10x6 in `$1111`). A far code per line, `F0 a b FE F0 c d F4.. FF`, inside the row's own bytes: 4 bytes a line. Spell records keep the bytes from `／` on, so the MP cost lines up.

## Label rects (`tools/rects.py`, `script/label.tsv`)
`$C21CF0` blits `W H tiles` from DB:`$11ED` to BG2 at `$11EF`, attr `$11F1`, through the queue at `$7FBC00`: 183 call sites. Labels are records in `$C0`, `$C4`, `$C5` in tile numbers (no string table holds them, so `findtext` never saw them). `tools/debug/rectlog.lua` logs sources; a brute scan of banks 00-05 gave `rects.RECTS`. Tiles: `rects.TILE`. English uses the sheet's own A-Z, 0-9 and the a-z above, one 8 px tile per letter: in place if it fits in W, else `F0 lo hi` over the record (a W no record has) and `rect_read` runs the blit with DB on the far copy. `rects.COPIED` are templates code copies to RAM and writes numbers into: they can't take a far code, English stays inside W, and `rebuild` fails if it runs into a number. Other sources at `$1111` are built from strings through `$C21E93`.

## Direct readers
`$C2A63F`: label `$C4:B220` (5 glyphs, `name_misc` row) then a 5-byte name, a glyph at a time: `top_name` sends both through `strip`. `$C4:B485`, `$C4:B492`: job names as a sheet of cells read whole by `strip`, two 16 px cells a word, then male, female one cell each: put `{cell}` between words, it ends the open cell. A job word must be 17-32 px wide. `$C2C34E`, `$C4:B8E7`: digits, no text.

## Width
Lines: cells x 16 px. Measured budgets in `docs/re/windows.md`.
