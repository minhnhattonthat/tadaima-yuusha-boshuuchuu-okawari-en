-- Log each tilemap row clear ($C2:19EE: DMA of a blank word to 2 tilemap rows): frame, VRAM word address, bytes, return address.
-- --script tools/debug/rowclear.lua [--var FROM=0]
FROM = FROM or 0
local m = emu.memType.snesMemory
L.on_exec(0xC219EE, 0xC219EE, function()
  if L.frame < FROM then return end
  local sp = emu.getState()["cpu.sp"]
  local w = function(a) return emu.read(a, m) | emu.read(a + 1, m) << 8 end
  L.log(string.format("f%d clear %04X n %d ret %02X%04X", L.frame, w(0x10C1), w(0x10C5), emu.read(sp + 3, m), w(sp + 1)))
end)
