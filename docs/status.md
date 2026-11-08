# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 6. Translate (phase 5 closed 2026-11-08: marker tour read, every reached box shows its id or English filler).
- **Done:** Phases 1-5. Extract `script/*.tsv`, identity build, debug tool `tools/debug/` (scenes in `tools/debug/scenes.lua`), recon `docs/re/`. Phase 5: far text + VWF (`asm/vwf.asm`, `tools/insert.py`, `docs/re/vwf.md`), label rects (`tools/rects.py`, `script/label.tsv`), font `fonts/vwf.txt`. Width gate (`docs/re/windows.md`): dialogue 240 px a line, **224 px on a line ending in `{page}`/`{wait}`**, choices listed (`tools/choices.py`). Marker tour: `python -X utf8 build.py --marker` then `python -X utf8 tools/debug/regen.py --rom build/tadaima_marker.sfc --dir marker --jobs 3 --extra 6000 --timeout 3000` (6 jobs time out; ending needs `--extra 2000`, credits `--extra 3000`: more overshoots into the next state).
- **Fixed this session** (found by the marker tour, all in `docs/re/text.md` / `vwf.md`, tests in `tests/test_extract.py`, `test_insert.py`):
  - `059F1A` tournament king line was outside the `clear` range (raw JP shown).
  - `05AB96` -> `05AB97`: the row ate the high byte of pointer `$ABFF` after its `FF` low byte; the far code broke that pointer (junk in versus).
  - Shop place lists (12 rows, `extract.fixed_list`) swallowed the record data after them (blanked by insertion); now end at the last `name FE`.
  - Place records get a call code `F1 lo hi` each (far string, then text goes on): `$C2:D4AB` appends `FE 危険度 ★` after the 10-byte record in the map-town box.
  - Far numbers skip bytes `F0+` (the tilemap path read a number byte `F0` as a new far code).
  - VWF open-cell flag moved from `+0E` bit 0 to bit 1: the ending text window starts at tile `$0001`, every cell looked open and drew scrambled.
- **Facts that change the plan:**
  - Code-built Japanese still to do (phase 7/8): `危険度` (`LDA #$8CF7..` at `$C2:D503`; in the marker build the `F5` cell after it shows a stale small-font tile, blank in the original: fix with it), shop/inn header `勇者` before the name (no text read or rect log names it: find its writer), `1年 0ヶ月` / `0年目 4月` / `NO・1` (G4 small-font tiles, `docs/re/graphics.md`), job words `04B485`/`04B492` slot 17-32 px (Hero, Thief, Mage, Priest, Knight fit; 戦士 = Knight unless reworked).
  - `05AAD4` 勇者のたびだち / しれん道 / 終りなき伝説: three names, no pointer or reader found, not in any tour log. `textcover.py` in phase 8 will say if it shows.
  - Scenario mode has no game over screen: `defeat` is the phase 8 "game over" row. The staff roll and THE END are English in the original; check against D3 in phase 8.
  - Only ch 0's map tiles are scened; other chapters' events (all 23 choice rows) aren't reached. States 02, 04-06, 12, 14 aren't reached.
  - Warp artifacts that match the original: `encounter` shows a lone シ, `standings` a row of 0s.
  - A plain `build.py` overwrites `build/far.tsv` that `tools/windows.py` reads: rebuild the marker before `windows.py` on a marker tour.
- **Next:** phase 6. Prep: `shop.tsv` repeats the same lines across 17 blocks, dedupe for translators; place-list rows (`s212.0899` etc.) keep 12 `{nl}`-separated names, each fits the map-town box line (width gate). Phase 8 checks noted: small text in `C14AF2`-style tabs; speech blip per letter may buzz (`$C215BC`); choices drawn in the dialogue window (code-read only); a screen with more than 6 long names at once.
- **Open bugs:** none known.
- **Waiting on the user:** nothing.
