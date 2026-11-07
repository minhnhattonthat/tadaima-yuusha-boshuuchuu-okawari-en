-- Log each distinct caller of an address (JSL return address off the stack). --script tools/debug/calllog.lua --var AT=0xC298EA [--var FROM=4000] [--var EVERY=1 logs repeats]
FROM = FROM or 0
local seen = {}
L.on_exec(AT, AT, function()
  if L.frame < FROM then return end
  local s = emu.getState()
  local sp, m = s["cpu.sp"], emu.memType.snesMemory
  local ret = emu.read(sp + 1, m) | emu.read(sp + 2, m) << 8 | emu.read(sp + 3, m) << 16
  if seen[ret] and not EVERY then return end
  seen[ret] = true
  L.log(string.format("f%d call %06X from %06X A=%04X X=%04X Y=%04X DB=%02X", L.frame, AT, ret, s["cpu.a"], s["cpu.x"], s["cpu.y"], s["cpu.dbr"]))
end)
