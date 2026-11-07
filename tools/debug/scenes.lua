-- Scene list for warp.lua (states: docs/re/memory.md). Fields:
--   title     stay on the title, press nothing
--   newgame   press A through new game but never warp (opening, player select, name entry)
--   state     value for $0DDD when new-game party creation ends
--   ram       { [wram addr] = byte } written at that moment
--   mode      title mode, poked into $1F4B when the title hands over (1 = party mode)
--   mash      press A every N frames after the warp, until state `after` shows up (default: to the end)
--   after     state that starts `route` and stops mash (cold boots drift a few frames, so never count from the warp)
--   route     presses as { {frame, "button", frames}, .. } counted from `after`
--   intro_exit  state to enter when the chapter intro (state 17) ends
--   frames    run length for regen.py (one line per scene so it can read it)
local S = {}

S.title = { title = true, frames = 900 }
S.opening = { newgame = true, frames = 1300 }
S.player_select = { newgame = true, frames = 1700 }
S.name_entry = { newgame = true, frames = 3200 }
S.battle = { state = 0x0F, frames = 5000 }
S.vs = { state = 0x1A, frames = 4400 }
S.tournament = { state = 0x20, frames = 4400 }
S.config = { state = 0x22, frames = 4400 }
S.save_menu = { state = 0x23, frames = 4400 }
S.ending = { state = 0x1D, mash = 150, frames = 5000 }
S.epilogue = { state = 0x1E, mash = 150, frames = 5000 }
S.party_mode = { mode = 1, frames = 5000, mash = 60 }
S.field = { state = 0x17, ram = { [0x0A2C] = 0 }, mash = 150, frames = 19500 }
S.field_menu = { state = 0x17, ram = { [0x0A2C] = 0 }, mash = 150, after = 0x03, frames = 21500,
  route = { { 300, "a" }, { 424, "a" }, { 548, "right" }, { 612, "a" } } }

for ch = 0, 12 do
  S[string.format("ch%02d", ch)] = { state = 0x17, ram = { [0x0A2C] = ch }, mash = 150 }
  -- the clear event reads text the intro loaded, so play the intro first
  S[string.format("ch%02d_clear", ch)] = { state = 0x17, ram = { [0x0A2C] = ch }, mash = 150, intro_exit = 0x18 }
end

return S
