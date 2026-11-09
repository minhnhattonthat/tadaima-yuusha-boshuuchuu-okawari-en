-- Names-ring allocation log (asm/vwf.asm name_cache / protect / cache_put): addresses from build/tadaima_en.sym.
-- --script tools/debug/protectlog.lua --var NC=0xE007BB --var PR=0xE00852 --var PRO=0xE00879 --var CP=0xE008C6 [--var FROM=0]
FROM = FROM or 0
local m = emu.memType.snesMemory
local function b(a) return emu.read(a, m) end
local function cache()
  local t = {}
  for i = 0, 5 do
    local x = 0x7FFF64 + 4 * i
    t[#t + 1] = string.format("%04X@%02X+%d", b(x) | b(x + 1) << 8, b(x + 2), b(x + 3))
  end
  local p = {}
  for i = 0, 5 do
    local x = 0x7FFF80 + 4 * i
    p[#p + 1] = string.format("%04X:%02X+%d", b(x) | b(x + 1) << 8, b(x + 2), b(x + 3))
  end
  return table.concat(t, " ") .. " | panels " .. table.concat(p, " ")
end
local function a8() return emu.getState()["cpu.a"] & 0xFF end
local function ret()
  local sp = emu.getState()["cpu.sp"]
  return string.format("%02X%02X/%02X%02X", b(sp + 7), b(sp + 6), b(sp + 10), b(sp + 9))
end
L.on_exec(NC, NC, function() if L.frame >= FROM then L.log(string.format("f%d cache? head %02X ret %s", L.frame, a8(), ret())) end end)
L.on_exec(PR, PR, function() if L.frame >= FROM then L.log(string.format("f%d protect in %02X | %s", L.frame, a8(), cache())) end end)
L.on_exec(PRO, PRO, function() if L.frame >= FROM then L.log(string.format("f%d protect out %02X", L.frame, b(0x7FFF7E))) end end)
L.on_exec(CP, CP, function() if L.frame >= FROM then L.log(string.format("f%d put end %02X hud %d hit %d | %s", L.frame, a8(), b(0x7FFF2E), b(0x7FFF7D), cache())) end end)
