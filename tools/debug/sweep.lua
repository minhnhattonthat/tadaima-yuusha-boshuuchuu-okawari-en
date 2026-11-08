-- Forced text sweep (text coverage, "force, don't play"): every time the game starts a far string (far_entry, A = far number),
-- A is swapped for the next number of LIST[FROM..TO], so each print of the opening shows a list string instead and reads its
-- far-table entry (textcover.lua logs the read). Run with warp.lua SCENE='opening' (its A presses turn the pages); tools/debug/sweep.py.
-- A WRAM chain of call codes stalled after one glyph (the typing task resumes from state kept elsewhere): one swap per print works.
local list = {}
for n in L.read_file(LIST):gmatch("%x+") do list[#list + 1] = tonumber(n, 16) end
local k = FROM

L.on_exec(ENTRY, ENTRY, function()
  if k > TO then return end
  local s = emu.getState()
  s["cpu.a"] = list[k]
  emu.setState(s)
  if k == TO then
    L.log(string.format("sweep done f%d", L.frame))
    local stop = L.frame + 30  -- the table read comes a few instructions after the swap
    L.on_frame(function() if L.frame == stop then L.shot("final.png"); L.finish(0) end end)
  end
  k = k + 1
end)
