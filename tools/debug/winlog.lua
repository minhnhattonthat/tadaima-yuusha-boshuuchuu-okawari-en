-- Log each distinct window + string: record fields at the text routine's entry, for tools/windows.py. --script tools/debug/winlog.lua
-- +1 +2 screen y, x; +8 width limit, half cells; +9 rows; +0A / +12 first / limit tile; +19 flags. docs/re/text.md
local DRAW = 0xC21421
local seen = {}
L.on_exec(DRAW, DRAW, function()
  local s = emu.getState()
  local m = emu.memType.snesMemory
  local bank, x, y = s["cpu.dbr"], s["cpu.x"], s["cpu.y"]
  local p = bank << 16 | y
  local b = function(i) return emu.read(x + i, m) end
  local w = function(i) return b(i) | b(i + 1) << 8 end
  local far = emu.read(p, m) == 0xF0 and (emu.read(p + 1, m) | emu.read(p + 2, m) << 8) or -1
  local key = string.format("%d %d %d %d %d %04X %04X %02X", far, b(1), b(2), b(8), b(9), w(0x0A), w(0x12), b(0x19))
  if seen[key] then return end
  seen[key] = true
  L.log("win " .. key)
end)
