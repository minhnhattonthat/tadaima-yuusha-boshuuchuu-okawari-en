-- Cold boot to a scene from tools/debug/scenes.lua: --script tools/debug/warp.lua --var "SCENE='ch03'"
-- Plays new game with A presses, then (emulator RAM only, the ROM file is untouched) makes the new-game handler's exit
-- at $C1:76A5 store the scene's state and return to the dispatcher, instead of chaining into chapter 1.
-- shortcut: repo root comes from --out, so --out must sit under work/ (Mesen's cwd isn't the repo).
local scene = assert(dofile(OUT:gsub("work[/\\].*$", "") .. "tools/debug/scenes.lua")[SCENE], "unknown SCENE")
local wram, prg = emu.memType.snesWorkRam, emu.memType.snesPrgRom
local NEWGAME_EXIT, TITLE_EXIT, DISPATCH = 0xC176A5, 0xC4322A, 0x8290BD

local function state() return emu.read(0x0DDD, wram) end
if scene.expect then L.log(string.format("expect %02X", scene.expect)) end  -- regen.py compares the run's last state

if scene.state then
  emu.write(0x0176A6, scene.state, prg)
  for a = 0x0176AC, 0x0176AF do emu.write(a, 0xEA, prg) end  -- NOP the JSL $C176B1
end

local warped, after_frame = false, nil
L.on_exec(NEWGAME_EXIT, NEWGAME_EXIT, function()
  if warped or scene.newgame then return end
  warped = true
  for a, v in pairs(scene.ram or {}) do emu.write(a, v, wram) end
  L.log(string.format("warp: %s at f%d", SCENE, L.frame))
end)
if scene.tile then  -- first turn menu of the map: act as if the player just stopped on this tile (state 0C runs its event)
  local done = false
  L.on_exec(DISPATCH, DISPATCH, function()
    if warped and not done and state() == 1 then
      done = true
      for i, base in ipairs({ 0x1584, 0x1586 }) do emu.write(base, scene.tile[i], wram); emu.write(base + 1, 0, wram) end
      emu.write(0x0CAF, scene.tile[1], wram)
      emu.write(0x0CCF, scene.tile[2], wram)
      emu.write(0x0DDD, 0x0C, wram)
      if not scene.keep_mash then after_frame = L.frame end
      L.log(string.format("tile event %02X,%02X at f%d", scene.tile[1], scene.tile[2], L.frame))
    end
  end)
end
if scene.poke_at then  -- { pc, addr, value }: write RAM each time pc runs (for screens that don't pass the new-game exit)
  local pc, a, v = table.unpack(scene.poke_at)
  L.on_exec(pc, pc, function() emu.write(a, v, wram) end)
end
if scene.boot_pad then
  L.on_exec(0xC10000, 0xC10000, function() emu.write(0x015F, scene.boot_pad, wram) end)
end
if scene.mode then
  L.on_exec(TITLE_EXIT, TITLE_EXIT, function() emu.write(0x1F4B, scene.mode, wram) end)
end

local PERIOD = 30
L.on_frame(function(f)
  if scene.title then
    if f == 700 then L.press("start", 4) end
    return
  end
  for _, r in ipairs(scene.press_at or {}) do  -- { frame from boot, button }
    if f == r[1] then L.press(r[2], 4) end
  end
  if not warped then
    if f >= (scene.mash_end or math.huge) then return end
    if f % 300 == 0 and state() == 0x16 then L.press("start", 4) end
    if f > 900 and f % PERIOD == 0 and L.route_done() then L.press("a", 4) end
    return
  end
  if scene.after and not after_frame and state() == scene.after then after_frame = f end
  for _, r in ipairs(scene.route or {}) do
    if after_frame and f - after_frame == r[1] then L.press(r[2], r[3] or 4) end
  end
  if scene.mash and not after_frame and f < (scene.mash_end or math.huge) and f % scene.mash == 0 and L.route_done() then L.press("a", 4) end
end)
