-- Log each far code (F0) the tilemap path maps from the FE/FF loop ($C2209E), with the loop's caller and the far number:
-- which ring a name or line should take (asm/vwf.asm small_map). --script tools/debug/farcaller.lua
local m = emu.memType.snesMemory
L.on_exec(0xC21E93, 0xC21E93, function()
  local s = emu.getState()
  if s["cpu.a"] & 0xFF ~= 0xF0 then return end
  local sp = s["cpu.sp"]
  local ret = emu.read(sp + 1, m) | emu.read(sp + 2, m) << 8
  if ret ~= 0x20C4 then return end
  local caller = emu.read(sp + 4, m) | emu.read(sp + 5, m) << 8 | emu.read(sp + 6, m) << 16
  local p = (s["cpu.dbr"] << 16) | (emu.read(0x0000, m) | emu.read(0x0001, m) << 8)
  L.log(string.format("f%d far caller %06X num %02X%02X", L.frame, caller, emu.read(p + 2, m), emu.read(p + 1, m)))
end)
