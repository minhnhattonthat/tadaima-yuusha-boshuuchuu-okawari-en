# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2. Debug tool in progress. Last build: none yet.
- **Done:** Phase 1 closed (2bpp sweep, no new graphics text; only 4 of its 11 pages were read, the rest are map and sound data by destination and size). Game state byte `$0DDD` and its table in `docs/re/memory.md`. `tools/debug/warp.lua` + `scenes.lua` warp from a cold boot by patching the new-game exit in emulator memory; `tools/debug/regen.py [prefix..]` runs scenes and keeps shots in `work/qa/scenes/` and states in `work/states/`.
- **Proven by a shot:** title, opening, player_select, name_entry, battle, vs, tournament, config, save_menu, ending, epilogue, party_mode (goes through the party flow, shows the castle), field, ch00-ch08, ch10, ch11.
- **Next:** finish phase 2.
  1. Chapter clears (`chNN_clear`) and intros ch09, ch12 show garbage text. Clear events read bank `$85` (`$1E1D`, set at `$C1:6E25`); read `$C1:6F84` and `$C1:5FD2`, likely `$1DDB`-style pointers or a text load the warp skips. ch12_clear did not reach state 18 in 9000 frames: give it its 22000 default.
  2. `field_menu` shot shows a dialogue, not the command menu; the menu appears about 720 frames after the field in `work/qa/f1`. Move the route and add menu scenes (magic, orb, items, rest, map, status).
  3. Not in the list yet: shops (text in blocks 212-228, loaded through a table, not by `tools/blockrefs.py` sites), game over (no such string found by `tools/findtext.py`: it may be graphics, add a row to `docs/re/graphics.md` if so), battle with enemies and party-mode menus, continue screen.
  4. Run `python -X utf8 tools/debug/regen.py --jobs 7` over everything after the scene changes, and read the sheets. No full run since the last warp edits. Each state should assert a RAM flag before saving: `regen.py` only checks for a flat screen today.
  Later needs: a compressor (none yet), the event bytecode VM in blocks 229-302, pointers to the raw strings in banks `$C0/$C1/$C4/$C5`, WRAM buffer limits for dialogue blocks.
- **Open bugs:** none (nothing built yet).
- **Waiting on the user:** nothing.
