-- Who writes a low RAM byte late in a run, with PC, stack and registers: --script tools/debug/ddd.lua --var ADDR=0x7E00A3 --var FROM=1600
local n = 0
L.on_write(ADDR, ADDR, function(addr, value)
  if L.frame < FROM or n > 30 then return end
  n = n + 1
  local s = emu.getState()
  local m, sp = emu.memType.snesMemory, s["cpu.sp"]
  local st = {}
  for i = 1, 12 do st[#st + 1] = string.format("%02X", emu.read(sp + i, m)) end
  L.log(string.format("f%d w=%02X pc %06X sp %04X db %02X d %04X a %04X x %04X y %04X stack %s", L.frame, value, L.pc(), sp, s["cpu.dbr"], s["cpu.d"], s["cpu.a"], s["cpu.x"], s["cpu.y"], table.concat(st, " ")))
end)
