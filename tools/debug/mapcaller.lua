-- Log calls into the tilemap mapper $C21E93 from frame FROM: byte, return address, its caller (stack +4), DB, and the pointer at DP $00.
-- Finds which loop draws a small-font box (asm/vwf.asm small_map). --script tools/debug/mapcaller.lua --var FROM=18000 [--var MAX=400]
local m = emu.memType.snesMemory
local n, max = 0, MAX or 400
L.on_exec(0xC21E93, 0xC21E93, function()
  if L.frame < (FROM or 0) or n >= max then return end
  n = n + 1
  local s = emu.getState()
  local sp = s["cpu.sp"]
  local function rd(a, k) local v = 0 for i = k - 1, 0, -1 do v = v << 8 | emu.read(a + i, m) end return v end
  L.log(string.format("f%d byte %02X ret %06X up %06X db %02X p00 %04X d %04X x %04X y %04X", L.frame, s["cpu.a"] & 0xFF,
    rd(sp + 1, 3), rd(sp + 4, 3), s["cpu.dbr"], rd(s["cpu.d"], 2), s["cpu.d"], s["cpu.x"], s["cpu.y"]))
end)
