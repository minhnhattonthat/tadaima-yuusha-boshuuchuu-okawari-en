-- Rect-blit list depth: $11E9 = 2 x entries queued since the last drain; the list at $11D1 holds 11 (docs/re/vwf.md).
-- Logs each frame's peak and each drain ($C21DF7). --script tools/debug/rectcount.lua [--var FROM=0]
FROM = FROM or 0
local wram, peak = emu.memType.snesWorkRam, 0
L.on_exec(0xC21CFE, 0xC21CFE, function()
  if L.frame < FROM then return end
  local n = emu.read(0x11E9, wram) // 2 + 1
  if n > peak then peak = n end
end)
L.on_exec(0xC21DF7, 0xC21DF7, function()
  if L.frame < FROM then return end
  L.log(string.format("f%d drain %d entries", L.frame, emu.read(0x11E9, wram) // 2))
end)
-- --var CALLS=N: also log the first N blits after FROM: caller, VRAM word ($11EF), source ($11ED)
local calls = 0
L.on_exec(0xC21CF0, 0xC21CF0, function()
  if not CALLS or L.frame < FROM or calls >= CALLS then return end
  calls = calls + 1
  local s, m = emu.getState(), emu.memType.snesMemory
  local sp = s["cpu.sp"]
  L.log(string.format("f%d blit from %02X%02X%02X vram %02X%02X src %02X:%02X%02X", L.frame, emu.read(sp + 3, m), emu.read(sp + 2, m),
    emu.read(sp + 1, m), emu.read(0x11F0, wram), emu.read(0x11EF, wram), s["cpu.dbr"], emu.read(0x11EE, wram), emu.read(0x11ED, wram)))
end)
L.on_frame(function(f)
  if f >= FROM and peak > 0 then L.log(string.format("f%d peak %d", f, peak)) end
  peak = 0
end)
