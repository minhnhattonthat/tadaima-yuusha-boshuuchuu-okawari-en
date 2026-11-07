-- Log every string the text routine draws: frame, bank:pointer, first bytes. --script tools/debug/textlog.lua
local DRAW = 0xC21421
L.on_exec(DRAW, DRAW, function()
  local s = emu.getState()
  local bank, y = s["cpu.dbr"], s["cpu.y"]
  local hex = {}
  for i = 0, 15 do hex[#hex + 1] = string.format("%02X", emu.read((bank << 16 | y) + i, emu.memType.snesMemory)) end
  L.log(string.format("f%d text %02X:%04X %s", L.frame, bank, y, table.concat(hex, " ")))
end)
