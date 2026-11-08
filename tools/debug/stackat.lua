-- Stack bytes when the CPU reaches AT, first N times after FROM: return-address chains. --script tools/debug/stackat.lua --var AT=0xC26F23 [--var N=5] [--var FROM=0]
N = N or 5
FROM = FROM or 0
local hits, m = 0, emu.memType.snesMemory
L.on_exec(AT, AT, function()
  if L.frame < FROM or hits >= N then return end
  hits = hits + 1
  local s = emu.getState()
  local t = {}
  for i = 1, 32 do t[#t + 1] = string.format("%02X", emu.read(s["cpu.sp"] + i, m)) end
  L.log(string.format("f%d at %06X S=%04X DB=%02X: %s", L.frame, AT, s["cpu.sp"], s["cpu.dbr"], table.concat(t, " ")))
end)
