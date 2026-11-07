-- Log the bytes the tilemap text path maps, one line per caller run: return address, frame, bytes. --script tools/debug/smalllog.lua [--var FROM=4000]
FROM = FROM or 0
local ret0, bytes, count = nil, {}, 0
local function flush()
  if ret0 and count < 400 then L.log(string.format("f%d small %06X %s", L.frame, ret0, table.concat(bytes, " "))) end
  count, bytes = count + 1, {}
end
L.on_exec(0xC21E93, 0xC21E93, function()
  if L.frame < FROM then return end
  local s = emu.getState()
  local sp, m = s["cpu.sp"], emu.memType.snesMemory
  local ret = emu.read(sp + 1, m) | emu.read(sp + 2, m) << 8 | emu.read(sp + 3, m) << 16
  if ret ~= ret0 or #bytes >= 24 then flush(); ret0 = ret end
  bytes[#bytes + 1] = string.format("%02X", s["cpu.a"] & 0xFF)
end)
