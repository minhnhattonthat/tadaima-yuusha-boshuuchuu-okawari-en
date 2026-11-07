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

## Width
Lines: cells x 16 px. Measured budgets in `docs/re/windows.md`.
