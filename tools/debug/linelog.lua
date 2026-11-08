-- Log each tile pair the FE/FF line loop ($C2209E) stores: source byte, Y, A (lower row), B (upper row), $0A, after JSL $C21E93 at
-- $C220C5 and after small_end's own JSL. Description and bio lines (asm/vwf.asm small_map). --script tools/debug/linelog.lua
local m = emu.memType.snesMemory
local function dp(a) return emu.read(a, m) | emu.read(a + 1, m) << 8 end
local function log(tag)
  local s = emu.getState()
  local p = (s["cpu.dbr"] << 16) | dp(0x0000)
  L.log(string.format("f%d %s byte %02X y %d a %02X b %02X 0A %02X r02 %04X r04 %04X", L.frame, tag, emu.read(p, m), s["cpu.y"] & 0xFF,
    s["cpu.a"] & 0xFF, (s["cpu.a"] >> 8) & 0xFF, emu.read(0x000A, m), dp(0x0002), dp(0x0004)))
end
L.on_exec(0xC220C5, 0xC220C5, function() log("map") end)
L.on_exec(0xC220D6, 0xC220D6, function() log("fe") end)
