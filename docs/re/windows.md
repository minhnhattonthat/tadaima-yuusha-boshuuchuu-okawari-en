# Text budgets (width gate)

Measured on the marker build: `tools/debug/winlog.lua` logs the window record at each string, `python -X utf8 tools/windows.py` sums a tour and writes `work/windows.tsv` (row id, px, rows: the tightest window the row was seen in). Width px = `+8` x 8; the game wraps by itself past it, so a line over budget breaks mid-word.

| Text | Budget | Status |
|---|---|---|
| Dialogue, shop, inn, story, system messages (`dialogue`, `talk`, `event`, `shop`, `story`, `clear`, `boss`, `party`, `system`) | 240 px a line; 3 or 4 lines by window, `work/windows.tsv` per row; unreached rows: 3 lines | measured, 548 rows, every window on the tour is 240 px wide |
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
