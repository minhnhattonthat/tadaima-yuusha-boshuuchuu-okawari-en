-- Log each distinct source given to the tile-rect blit $C21CF0, and other small-tile writers: caller, bank:pointer, W H, bytes. --script tools/debug/rectlog.lua
local seen = {}
L.on_exec(0xC21CF0, 0xC21CF0, function()
  local s = emu.getState()
  local m, sp = emu.memType.snesMemory, s["cpu.sp"]
  local ret = emu.read(sp + 1, m) | emu.read(sp + 2, m) << 8 | emu.read(sp + 3, m) << 16
  local bank, y = s["cpu.dbr"], emu.read(0x11ED, m) | emu.read(0x11EE, m) << 8
  local w, h = emu.read((bank << 16 | y), m), emu.read((bank << 16 | y) + 1, m)
  local hex = {}
  for i = 0, math.min(w * h, 80) - 1 do hex[#hex + 1] = string.format("%02X", emu.read((bank << 16 | y) + 2 + i, m)) end
  local key = string.format("%06X %02X:%04X %d %d %s", ret, bank, y, w, h, table.concat(hex, " "))
  if not seen[key] then seen[key] = true; L.log("rect " .. key) end
end)
