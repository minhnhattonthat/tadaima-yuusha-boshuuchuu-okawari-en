-- Log CPU writes to a VRAM byte range (who drew a stray tilemap cell): frame, VRAM byte address, value, PC.
-- --script tools/debug/vramwrite.lua --var LO=0x7022 --var HI=0x7029 [--var FROM=0]   (byte address = word address * 2)
FROM = FROM or 0
emu.addMemoryCallback(function(addr, value)
  if L.frame < FROM then return end
  L.log(string.format("f%d vram %04X = %02X pc %06X", L.frame, addr, value, L.pc()))
end, emu.callbackType.write, LO, HI, emu.cpuType.snes, emu.memType.snesVideoRam)
