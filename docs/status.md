# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 3. Identity build next. Last build: none yet.
- **Done:** Phase 1 closed. Phase 2 closed: `tools/debug/` reaches every scene from a cold boot, no save. `warp.lua` + `scenes.lua` patch the new-game exit in emulator memory, then run a state, a menu route or a map tile event. `python -X utf8 tools/debug/regen.py --jobs 7 [prefix..]` runs them (about 10 minutes for all), keeps shots in `work/qa/scenes/` and states in `work/states/`, and fails a scene that ends flat or not in its `expect` state. Game map in `docs/re/memory.md`: states, chapters, records, tile events. `tools/debug/textlog.lua` logs drawn characters, `poke.lua` writes RAM on frame 1.
- **Scenes (all proven by a shot, sheets read):** title, opening, player_select, name_entry, battle, vs, tournament, config, save_menu, party_mode, versus, continue, standings, field, field_menu, field_menu2, field_map, field_map_town, field_rest, field_status, field_status_equip, field_status_magic, field_items, field_magic, field_orb, field_pass, ch00-ch07, mid00-mid04 (boss fights), clear00-clear04, ending, credits, the_end, defeat, battle_magic, battle_menu2, teleport, cave, duel, encounter, orb_slot, shop0-2, shop_inside, inn0-2, notice_a, notice_b.
- **Facts that change the plan:**
  - Scenario mode has no game over screen: `defeat` is the battle-lost line, then the robot takes items and play goes on. So the phase 8 "game over" row is `defeat`.
  - The staff roll runs over the epilogue maps and shows English in the original ROM; THE END too. Only one frame of it was read: check all of it against D3 in phase 8.
  - Only ch 0's map tiles are scened; other chapters' shops, inns and sites share handlers but have their own text. `textcover.py` in phase 8 will name what to add. Tile types 8, 9 aren't on ch 0's map. States 02, 04-06, 12, 14 aren't reached: pressing A on the first item or spell stayed in state 01, cause not looked at.
- **Next:** phase 3, identity build. Needs a compressor (none yet; `tools/lz.py` only decompresses): rebuild blocks from `work/blocks/` to an image equal to the ROM, as a test. An LZ repack may not match byte for byte: the test can compare decompressed contents plus untouched bytes if so.
  Later needs: the event bytecode VM in blocks 229-302, pointers to the raw strings in banks `$C0/$C1/$C4/$C5`, WRAM buffer limits for dialogue blocks.
- **Open bugs:** none (nothing built yet).
- **Waiting on the user:** nothing.
