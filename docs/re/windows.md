# Text budgets (width gate)

Measured on the marker build: `tools/debug/winlog.lua` logs the window record at each string, `python -X utf8 tools/windows.py` sums a tour and writes `work/windows.tsv` (row id, px, rows: the tightest window the row was seen in). Width px = `+8` x 8; the game wraps by itself past it, so a line over budget breaks mid-word.

| Text | Budget | Status |
|---|---|---|
| Dialogue, shop, inn, story, system messages (`dialogue`, `talk`, `event`, `shop`, `story`, `clear`, `boss`, `party`, `system`) | 240 px a line; 3 or 4 lines by window, `work/windows.tsv` per row; unreached rows: 3 lines | measured, 548 rows, every window on the tour is 240 px wide |
| Dialogue line, from pixels | text area x 8-248 in a 240 px window; a 240 px line (30 W) and a 241 px line both show whole, since every advance ends in a blank column. Budget stays 240 px | measured, `tools/stress.py`, `work/qa/stress2/f001320.png` |
| Speaker name line (`{color:07}Name{color:0F}{nl}`) | an ordinary first line of the window: 240 px | measured with the line above |
| Line ending in `{page}` or `{wait}` | **224 px** (14 cells): the arrow takes the next 16 px cell. A full line pushes the arrow onto a new line and the window scrolls one line, so line 1 leaves view at the prompt | measured, `work/qa/stress2/f001640.png` (4 full lines). Fixed with it: the arrow drew over the last open VWF cell (`(end)` showed `(en▼`); `far_read` now steps past the open cell (`align`) |
| Choices (event ops 20-22, `tools/choices.py`: 23 rows) | options are drawn in the dialogue window, one string each, each in its own palette colour (the highlight swaps colours, `$C2:21E5`), so the dialogue line applies: all options on a line together 240 px, keep each row's leading `{nl}` and spacing | code (`$C2:2116`); none on the tour: check in phase 8 |
| Glyph torture line | all printable ASCII but `{` `}` (code brackets in `script/`) render with the right widths; double spaces kept | measured, `work/qa/stress2/f001470.png` |
| Pages | `{page}` starts a new page, no limit on pages. Tiles: 196 a window = 49 cells, 3 lines of 15 | measured from `+0A`, `+12` |
| Title / config strips (`04C84E`-`04C875`) | 120, 168, 184, 216, 256 px, 1 line, flags `80` (strip, no wrap) | measured |
| Item, equipment names | 8 tiles = 64 px at 5 px a letter: about 13 letters (`font.small_tiles` fits by cell count) | code |
| Spell names | 9 bytes less the cost: the record keeps `／` and the cost in place | code |
| Character names | 5 bytes: names on the `$84:1236` slot path, 5 letters in fixed cells for player names | code |
| Descriptions and bios (`desc_*`, `bio`) | 10 cells a line, about 16 letters; 4 bytes of the row per line, so `size // 4` lines at most | code, `insert.lines_in` prints what it cuts |
| Labels (`label.tsv`) | 8 px a letter; `rects.COPIED` stay inside W, others may grow until something else is drawn there | code; check each in the QA tour |
| Job words (`04B485`, `04B492`) | 17-32 px each, `{cell}` between words; `tools/width.py`: Hero 23, Thief 25, Mage 26, Priest 30, Knight 31 fit; Fighter 36, Warrior 37 don't, so 戦士 = Knight here unless the sheet is reworked | `docs/re/vwf.md` |
| Fixed place lists in `shop.tsv` (`b213+8A6` style, no `FF`) | keep the `{nl}` count; a far code per row, bytes after the list are records | code |

`shop.tsv` repeats the same lines across 17 blocks: dedupe them for translators (same JP, same EN).
