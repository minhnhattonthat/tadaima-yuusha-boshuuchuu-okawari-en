# English engine: far text and VWF (`asm/vwf.asm`, `tools/insert.py`, `tools/font.py`)

## Far text (verified: marker build, `tests/test_insert.py`)
The ROM grows to 4 MB (`$FFD7 = 0C`). Every translated row keeps its place: its first 3 bytes become `F0 lo hi`, the rest is blanked with `F4` and
a closing `FF` stays, so no pointer, table, list walk or block size changes. Number `hilo` indexes u24 entries at `$E1:0000` (file `210000`) that point
at the English. Far strings live in the **upper half** of file banks `21+`, read through CPU banks `$A1+:8000`: the text engine runs with DB = the string's
bank and reads low RAM by absolute address, so a `$C0+` bank would break it. Numbers skip any byte `F4+`, so a far code never reads as a padding or end byte.
Far code ends the string: the old text is never read again. A row with no `FF` (a pointer enters the next row) gets `F0` to the next row at the end of its English.
**Place lists** (`s212.0899`, `s213`-`s219`, `s225`-`s228`: 12 records of 10 bytes + `FE`, no `FF`) get a far code per record: `$C2:D4AB` copies
10 bytes of record `n` (`[$7E:800A] + n * 11`) into slot `$1236`, then code-builds `FE` 危険度 ★ after it (map town box, `field_map_town`). 危険度 is
code-built (`LDA #$8CF7` at `$C2:D503`): no row, phase 7 patches those immediates or keeps the glyphs.
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
`POS` say where the open cell is: if the window moved its cursor without setting `+0E`, the next glyph takes a new tile. Newline and page close it in `far_read`, through `align`: the cursor steps past the open cell, so the page arrow lands after the text, not over its last cell.

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

Upload: `$80D78F` makes the rest of the caller run in the next VBlank with X = a record (5 bytes queue, ours after), or inline during forced blank (`$00FF` bit 7). `$80D6F5` = DMA to VRAM, D = size, A = bank, X = source, Y = word address; it leaves D = 0. A record is a linked-list node: `+0` next, `+2` return address (`$80:D79D`), so it must sit in bank 0, and a stray write there sends the scheduler to garbage. Game callers each own a static record (`LDX #$07E0`, `#$12B8`, text cells `#$10CA`). Ours: 3 records of 6 bytes at `$1538-$1549` (never written on the original's tour, no absolute operand names `$1538-$154A`); the payload (source, bank, tile count, VRAM word, busy flag) is at `$7F:FF40`, 12 bytes a record. `small_load` sleeps while 8 continuations are queued, and up to 3 frames while its next record is still busy. **Was** 8 x 14 bytes at `$0483`, the tail of the sprite buffer (`$82:A070 STA $0220,x`, `$C2:5F83`, written in 62 of 64 scenes), and worse, its ring bound was written `!RECORDS+!RECSIZE*8`: asar math runs left to right, so it never wrapped and each name upload took the next 14 bytes of low RAM. That was the versus crash (state `3A`, STP at `$80:D94B` through a node returning to `$00:2000`) and the black screens. `tools/debug/contlog.lua` logs each node the drain (`$80:D602`, in VBlank) runs. Brackets in every asar expression that mixes operators.

Pool: tiles `$4A-$9F`, blanked in block 001, in two rings: names `$4A-$79` (48 tiles: 6 names of 8) and lines `$7A-$9F` (38: a 3-line description), `HEAD` / `HEADB`. `small_map` picks the lines ring when its caller is the FE/FF loop (return `$C220C4`); `small_load` places the image from `NEXT - 2` and moves the ring's head (`RING`). Each ring keeps room for 10 tiles (`!ROOM`, asserted in `insert.images`). **Was one ring:** each cursor move in the item list drew a new description (~40 tiles), so after two moves the list names still on screen showed other names' tiles (`work/qa/scroll`, fixed). Tiles `$30-$49` of the sheet (the game's own hiragana) are a-z in fixed cells for text from RAM (player names); the game's mapping sends codes `$24-$3D` there, so a leftover kana on this path shows as a wrong letter. `$27 $28 $29 $2B` (marks, long bar, slash) stay the game's. **Limit:** no dedupe: a screen showing more than 6 long names at once (or a description over 3 lines) still wraps its ring. Real English names are shorter than the marker's (tiles = text width).

## Sleeping inside a hooked routine (`nap`)
The game never sleeps inside the routines we hook, and its tasks share direct-page scratch `$0000-$001F`. Ours do (`small_load` waits on the upload queue, `rect_room` on the blit list), so every sleep goes through `nap`: it saves registers, DB, D and `$0000-$001F` on the stack and puts them back. Without it the item list's row counter `$09` was clobbered mid-loop, rows ran on, and the blit list overflowed (below).

## Blit list
`$C21CF0` appends to a list at `$7E:11D1` (offsets into `$7F:BC00`, `FFFF` after the last), count x 2 at `$11E9`, and never checks room: the list holds 11, then the count itself. A drain task (`$C21DC1`, JSL `$C21DCE` each frame, DMA at `$C21DFC`) empties it. A 12th entry put its `FFFF` on the count, the drain took a 0-row entry and ran 65535 rows of 64 KB DMAs: the item list's black screen (`field_items`, both builds). `rect_room` (start of `rect_read`) naps while 11 are queued. `tools/debug/rectcount.lua` logs the depth per frame and each drain; the original peaks at 9.

## Lines on the tilemap path (`tools/insert.py lines_in`)
Item, equipment and spell descriptions and bios (`insert.LINES`) reach the tilemap through `$C220C1` one line at a time, FE between, 10 cells wide (rect 10x4 or 10x6 in `$1111`). A far code per line, `F0 a b FE F0 c d F4.. FF`, inside the row's own bytes: 3 bytes a line plus its FE. The box is blitted as tall as its lines, so `lines_in` keeps every line the Japanese had: an empty line is a bare FE (a dropped one left the last description's tiles on screen, `00B5F0`). `tests/test_insert.py::test_lines_keep_count`. Spell records keep the bytes from `／` on, so the MP cost lines up.

## Label rects (`tools/rects.py`, `script/label.tsv`)
`$C21CF0` blits `W H tiles` from DB:`$11ED` to BG2 at `$11EF`, attr `$11F1`, through the queue at `$7FBC00`: 183 call sites. Labels are records in `$C0`, `$C4`, `$C5` in tile numbers (no string table holds them, so `findtext` never saw them). `tools/debug/rectlog.lua` logs sources; a brute scan of banks 00-05 gave `rects.RECTS`. Tiles: `rects.TILE`. English uses the sheet's own A-Z, 0-9 and the a-z above, one 8 px tile per letter: in place if it fits in W, else `F0 lo hi` over the record (a W no record has) and `rect_read` runs the blit with DB on the far copy. `rects.COPIED` are templates code copies to RAM and writes numbers into: they can't take a far code, English stays inside W, and `rebuild` fails if it runs into a number. Other sources at `$1111` are built from strings through `$C21E93`.

## Direct readers
`$C2A63F`: label `$C4:B220` (5 glyphs, `name_misc` row) then a 5-byte name, a glyph at a time: `top_name` sends both through `strip`. `$C4:B485`, `$C4:B492`: job names as a sheet of cells read whole by `strip`, two 16 px cells a word, then male, female one cell each: put `{cell}` between words, it ends the open cell. A job word must be 17-32 px wide. `$C2C34E`, `$C4:B8E7`: digits, no text.

## Width
Lines: cells x 16 px. Measured budgets in `docs/re/windows.md`.
