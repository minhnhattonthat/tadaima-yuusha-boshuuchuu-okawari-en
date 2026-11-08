-- Rect-blit queue drain ($C21DFC, docs/re/vwf.md): log each entry it takes, first N: DB:Y, offset into $7F:BC00, VRAM, rows, bytes.
-- --script tools/debug/rectq.lua [--var FROM=0] [--var N=200]
FROM = FROM or 0
N = N or 200
local m, seen = emu.memType.snesMemory, 0
L.on_exec(0xC21E06, 0xC21E06, function()
  if L.frame < FROM or seen >= N then return end
  seen = seen + 1
  local s = emu.getState()
  local x = s["cpu.a"] & 0xFFFF
  local e = 0x7FBC00 + x
  L.log(string.format("f%d q DB%02X Y%04X off %04X vram %02X%02X rows %d bytes %d", L.frame, s["cpu.dbr"], s["cpu.y"], x,
    emu.read(e + 1, m), emu.read(e, m), emu.read(e + 3, m), emu.read(e + 4, m)))
end)
-- inside an entry: rows left ($06), bytes a row ($08), source ($00), VRAM ($02); once a frame
local last = -1
L.on_exec(0xC21E2E, 0xC21E2E, function()
  if L.frame < FROM or L.frame == last then return end
  last = L.frame
  local w = function(a) return emu.read(a, m) | emu.read(a + 1, m) << 8 end
  local s = emu.getState()
  L.log(string.format("f%d row left %d bytes %d src %04X vram %04X D%04X", L.frame, w(s["cpu.d"] + 6), w(s["cpu.d"] + 8), w(s["cpu.d"]), w(s["cpu.d"] + 2), s["cpu.d"]))
end)
