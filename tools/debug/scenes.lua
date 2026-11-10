-- Scene list for warp.lua (states: docs/re/memory.md). Fields:
--   title     stay on the title, press nothing
--   newgame   press A through new game but never warp (opening, player select, name entry)
--   state     value for $0DDD when new-game party creation ends
--   ram       { [wram addr] = byte } written at that moment
--   mode      title mode, poked into $1F4B when the title hands over (1 = party mode)
--   mash      press A every N frames after the warp, until state `after` shows up (default: to the end)
--   after     state that starts `route` and stops mash (cold boots drift a few frames, so never count from the warp)
--   route     presses as { {frame, "button", frames}, .. } counted from `after`
--   tile      { x, y }: at the first turn menu, run that map tile's event (shop, inn, battle); stops mash unless keep_mash
--   boot_pad  byte poked into $015F at the boot check $C1:0000 (controller notices)
--   expect    state the run must end in, or regen.py fails it
--   frames    run length for regen.py (one line per scene so it can read it)
local S = {}

S.title = { title = true, frames = 900 }
S.opening = { newgame = true, frames = 1300 }
-- EN: name entry grid ~f2100-2300, then player 2's select with the Human / Computer choice ~f2600
S.player_select = { newgame = true, frames = 2600 }
S.name_entry = { newgame = true, frames = 2250 }
S.battle = { state = 0x0F, frames = 5000 }
-- EN text makes new game longer: the warp lands ~f4400 (4400-frame scenes ended black on the card fade)
S.vs = { state = 0x1A, frames = 6000 }
S.tournament = { state = 0x20, frames = 6000 }
S.config = { state = 0x22, frames = 6000 }
S.save_menu = { state = 0x23, frames = 6000 }
-- Save into slot 1 and confirm: the slot then shows the save's date (年目 / 月, rect $85:BC2D, digits from $C4:2364 and $C4:23CB)
S.save_slot = { state = 0x23, after = 0x23, route = { { 200, "a" }, { 320, "a" }, { 500, "left", 8 }, { 620, "a" }, { 800, "a" }, { 1000, "a" } }, frames = 6800, expect = 0x23 }
-- The ending as the game plays it, from the last clear: states 18, 1D (text over sunset), 1E (epilogue maps + staff roll), 21 (THE END).
S.ending = { state = 0x18, ram = { [0x0A2C] = 12 }, mash = 150, frames = 21000, expect = 0x1D }  -- EN: 1D at ~f20000, 1E at ~f23000
S.credits = { state = 0x18, ram = { [0x0A2C] = 12 }, mash = 150, frames = 24000, expect = 0x1E }
S.the_end = { state = 0x18, ram = { [0x0A2C] = 12 }, mash = 150, frames = 32000, expect = 0x21 }
S.party_mode = { mode = 1, frames = 6500, mash = 60 }
S.party_map = { mode = 1, frames = 5600, mash = 60, mash_end = 5230, poke_at = { 0xC168B3, 0x1234, 1 } }
S.party_map_legend = { mode = 1, frames = 5700, mash = 60, mash_end = 5150, poke_at = { 0xC168B3, 0x1234, 1 },
  press_at = { { 5400, "down" }, { 5560, "down" } } }  -- the 2nd and 3rd map's descriptions  -- $1234 != 0 shows ($C1:68B3) the map choice 勇者のたびだち / しれんの道 / 終りなき伝説 (rects.MAPS)
S.field = { state = 0x17, ram = { [0x0A2C] = 0 }, mash = 150, frames = 22000 }
S.field_menu = { state = 0x17, ram = { [0x0A2C] = 0 }, mash = 150, after = 0x01, frames = 22000 }

-- Turn menus on ch 0's first turn. after = 1: routes count from the command menu (cursor on Move).
-- Inventory: player record +0E ($0BF9), 30 item ids. Spells: character record +19 ($0A48), 12 ids (docs/re/memory.md).
local function turn(route, ram, expect)
  ram = ram or {}
  ram[0x0A2C] = 0
  return { state = 0x17, ram = ram, mash = 150, after = 0x01, expect = expect or 0x01, frames = 22000, route = route }  -- the EN king's intro runs past f18000
end
local items, spells = {}, {}
for i = 0, 29 do items[0x0BF9 + i] = i + 1 end
for i = 0, 11 do spells[0x0A48 + i] = i + 1 end
S.field_menu2 = turn({ { 90, "x" } })
S.field_map = turn({ { 90, "x" }, { 140, "up" }, { 190, "a" } }, nil, 0x07)
S.field_rest = turn({ { 90, "x" }, { 140, "left" }, { 190, "a" } }, nil, 0x08)
S.field_status = turn({ { 90, "x" }, { 140, "right" }, { 190, "a" } }, nil, 0x09)
S.field_items = turn({ { 90, "down" }, { 140, "a" } }, items)
-- all 30 items scrolled down and back up: names on the tilemap path share an 86-tile pool ring (docs/re/vwf.md)
local scroll = { { 90, "down" }, { 140, "a" } }
for k = 1, 60 do scroll[#scroll + 1] = { 200 + 20 * k, k <= 30 and "down" or "up" } end
S.field_items_scroll = turn(scroll, items)
S.field_magic = turn({ { 90, "up" }, { 140, "a" }, { 200, "a" } }, spells)
S.field_orb = turn({ { 90, "right" }, { 140, "a" } }, items)
S.field_status_equip = turn({ { 90, "x" }, { 140, "right" }, { 190, "a" }, { 300, "right" }, { 360, "a" } }, nil, 0x09)
S.field_status_magic = turn({ { 90, "x" }, { 140, "right" }, { 190, "a" }, { 300, "right" }, { 360, "right" }, { 420, "a" } }, spells, 0x09)
S.field_status_profile = turn({ { 90, "x" }, { 140, "right" }, { 190, "a" }, { 300, "right" }, { 360, "right" }, { 420, "right" }, { 480, "a" } }, nil, 0x09)
S.field_map_town =turn({ { 90, "x" }, { 140, "up" }, { 190, "a" }, { 300, "right" }, { 360, "a" } }, nil, 0x07)
-- HP 1 ($0A42, character +13) in the first fight: the defeat scene. Scenario mode has no game over screen: the robot takes items and play goes on.
S.defeat = { state = 0x17, ram = { [0x0A2C] = 0, [0x0A42] = 1 }, mash = 150, keep_mash = true, after = 0x10, expect = 0x10, tile = { 0x31, 0x10 }, frames = 24000 }
-- Same fight, the 3 heroes at 999 HP (+13 HP, +15 max), mashed A until it's won: the result window (NVP / Shillings, 04CB3F / 04CB56).
-- The warp leaves junk RAM: the foe is named "41" and the castle report after it is garbage, the same on the JP ROM.
local hp = { [0x0A2C] = 0 }
for slot = 0, 2 do for _, f in ipairs({ 0x13, 0x15 }) do hp[0x0A2F + 0x25 * slot + f] = 0xE7; hp[0x0A30 + 0x25 * slot + f] = 0x03 end end
S.duel_win = { state = 0x17, ram = hp, mash = 150, keep_mash = true, tile = { 0x0D, 0x0A }, frames = 30000 }
S.victory = { state = 0x17, ram = hp, mash = 150, keep_mash = true, after = 0x10, expect = 0x10, tile = { 0x31, 0x10 }, frames = 26000 }
S.battle_magic = { state = 0x17, ram = spells, mash = 150, keep_mash = true, after = 0x0F, tile = { 0x31, 0x10 }, frames = 23000, expect = 0x0F,
  route = { { 300, "a" }, { 450, "a" }, { 600, "a" }, { 750, "up" }, { 810, "a" } } }
S.battle_menu2 = { state = 0x17, ram = { [0x0A2C] = 0 }, mash = 150, keep_mash = true, after = 0x0F, tile = { 0x31, 0x10 }, frames = 23000, expect = 0x0F,
  route = { { 300, "a" }, { 450, "a" }, { 600, "a" }, { 750, "x" } } }
S.shop_inside = { state = 0x17, ram = { [0x0A2C] = 0 }, mash = 150, keep_mash = true, tile = { 0x20, 0x27 }, frames = 22300, expect = 0x11 }
S.continue = { mode = 2, frames = 4500, expect = 0x16 }
S.versus = { mode = 3, frames = 6400, mash = 60 }  -- EN: Sylphy's map talk ~f5600-7000 (the boss lines before it sit between fades)
S.standings = { state = 0x19, frames = 6000, expect = 0x19 }
S.field_pass = turn({ { 90, "x" }, { 140, "down" }, { 190, "a" } }, nil, 0x0A)
-- Controller notices shown instead of the title (state 26 at boot, $C1:0000): $015F bit 6 and bit 0 pick the string.
S.notice_a = { title = true, boot_pad = 0x40, frames = 900, expect = 0x26 }
S.notice_b = { title = true, boot_pad = 0x01, frames = 900, expect = 0x26 }

-- Ch 0 map tiles by event type (list at $7E:D006, docs/re/memory.md): shops and inns have 3 sites each.
local tiles = { teleport = { 0x1A, 0x19 }, cave = { 0x27, 0x09 }, duel = { 0x0D, 0x0A }, encounter = { 0x31, 0x10 },
  orb_slot = { 0x34, 0x37 }, shop0 = { 0x20, 0x27 }, shop1 = { 0x42, 0x2C }, shop2 = { 0x20, 0x37 },
  inn0 = { 0x21, 0x12 }, inn1 = { 0x35, 0x1E }, inn2 = { 0x2F, 0x2E } }
for name, xy in pairs(tiles) do
  S[name] = { state = 0x17, ram = { [0x0A2C] = 0 }, mash = 150, tile = xy, frames = 22300 }
end
-- Inn menu -> recruit: candidate list (names, race/job/birthday status box, intro talk), then cursor moves between candidates
-- shortcut: timed for build 2026-11-09 (Bendas Inn chatter, 3 pages); the inn's talk varies with the build's timing, so re-time from the sheet
S.inn_recruit = { state = 0x17, ram = { [0x0A2C] = 0 }, mash = 150, tile = tiles.inn0, frames = 25200,
  route = { { 900, "a" }, { 1100, "a" }, { 1300, "a" }, { 1500, "a" }, { 1900, "a" }, { 2200, "a" }, { 2700, "down" }, { 3100, "down" },
    { 3500, "up" }, { 3900, "a" } } }
-- the same with the hero keeping a default name (a far name image on the tilemap path): name bytes copied from the ROM's hero 0 record
local far_ram = { [0x0A2C] = 0 }
for i = 0, 4 do far_ram[0x0A30 + i] = emu.read(0x009744 + i, emu.memType.snesPrgRom) end
S.inn_recruit_far = { state = 0x17, ram = far_ram, mash = 150, tile = tiles.inn0, frames = 25200, route = S.inn_recruit.route }
-- Chapters 0-4 and the branches 5-7 open with state 17. Values 8-12 are chapter 0-4 + 8: state 1F adds the 8 itself for
-- the mid-chapter event, state 18 (clear) expects it set and subtracts 7 for the next intro (docs/re/memory.md).
for ch = 0, 7 do
  S[string.format("ch%02d", ch)] = { state = 0x17, ram = { [0x0A2C] = ch }, mash = 150 }
end
for ch = 0, 4 do
  S[string.format("mid%02d", ch)] = { state = 0x1F, ram = { [0x0A2C] = ch }, mash = 150 }
  S[string.format("clear%02d", ch)] = { state = 0x18, ram = { [0x0A2C] = ch + 8 }, mash = 150 }
end

return S
