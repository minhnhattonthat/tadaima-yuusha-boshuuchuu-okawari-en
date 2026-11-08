-- Each continuation the VBlank drain runs ($80:D616 JSR $00CF jumps to [$D0]): node address, its next, return address.
-- --script tools/debug/contlog.lua [--var FROM=60]. A wild return address names the corrupt node (docs/re/vwf.md, Upload).
FROM = FROM or 0
local m = emu.memType.snesMemory
L.on_exec(0x80D616, 0x80D616, function()
  if L.frame < FROM then return end
  local s = emu.getState()
  local x = s["cpu.x"]
  L.log(string.format("f%d node %04X next %02X%02X ret %02X%02X%02X", L.frame, x, emu.read(x + 1, m), emu.read(x, m),
    emu.read(0xD2, m), emu.read(0xD1, m), emu.read(0xD0, m)))
end)
