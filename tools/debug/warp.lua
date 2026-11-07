-- Cold boot to a scene from tools/debug/scenes.lua: --script tools/debug/warp.lua --var "SCENE='ch03'"
-- Plays new game with A presses, then (emulator RAM only, the ROM file is untouched) makes the new-game handler's exit
-- at $C1:76A5 store the scene's state and return to the dispatcher, instead of chaining into chapter 1.
-- shortcut: repo root comes from --out, so --out must sit under work/ (Mesen's cwd isn't the repo).
local scene = assert(dofile(OUT:gsub("work[/\\].*$", "") .. "tools/debug/scenes.lua")[SCENE], "unknown SCENE")
local wram, prg = emu.memType.snesWorkRam, emu.memType.snesPrgRom
local NEWGAME_EXIT, TITLE_EXIT, DISPATCH = 0xC176A5, 0xC4322A, 0x8290BD

local function state() return emu.read(0x0DDD, wram) end

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
if scene.intro_exit then  -- first dispatch of state 00 after the warp: the intro has ended, swap in ours before the read
  local done = false
  L.on_exec(DISPATCH, DISPATCH, function()
    if warped and not done and state() == 0 then
      done = true
      emu.write(0x0DDD, scene.intro_exit, wram)
    end
  end)
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
  if not warped then
    if f % 300 == 0 and state() == 0x16 then L.press("start", 4) end
    if f > 900 and f % PERIOD == 0 and L.route_done() then L.press("a", 4) end
    return
  end
  if scene.after and not after_frame and state() == scene.after then after_frame = f end
  for _, r in ipairs(scene.route or {}) do
    if after_frame and f - after_frame == r[1] then L.press(r[2], r[3] or 4) end
  end
  if scene.mash and not after_frame and f % scene.mash == 0 and L.route_done() then L.press("a", 4) end
end)
