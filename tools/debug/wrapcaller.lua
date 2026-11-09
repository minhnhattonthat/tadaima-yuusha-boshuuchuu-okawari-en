-- Log each far code (F0) the tilemap path maps through the 16-bit wrapper $C21E8A (HUD panel names and others), with the wrapper's
-- caller, Y and the bytes at DB:Y: who redraws a name and how often (asm/vwf.asm name cache). --script tools/debug/wrapcaller.lua [--var FROM=0]
FROM = FROM or 0
local m = emu.memType.snesMemory
L.on_exec(0xC21E93, 0xC21E93, function()
  if L.frame < FROM then return end
  local s = emu.getState()
  if s["cpu.a"] & 0xFF ~= 0xF0 then return end
  local sp = s["cpu.sp"]
  local ret = emu.read(sp + 1, m) | emu.read(sp + 2, m) << 8
  if ret ~= 0x1E8F then return end
  local caller = emu.read(sp + 4, m) | emu.read(sp + 5, m) << 8 | emu.read(sp + 6, m) << 16
  local p = (s["cpu.dbr"] << 16) | s["cpu.y"]
  local hex = {}
  for i = 0, 4 do hex[#hex + 1] = string.format("%02X", emu.read(p + i, m)) end
  L.log(string.format("f%d wrap caller %06X db:y %06X %s B=%02X", L.frame, caller, p, table.concat(hex, " "), s["cpu.a"] >> 8))
end)
