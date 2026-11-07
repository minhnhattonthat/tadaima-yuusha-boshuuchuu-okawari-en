-- Who writes the name entry's tile buffer, and with what, around a press of A: --script tools/debug/namewatch.lua after warp.lua, SCENE='name_entry'.
local seen = {}
L.on_write(0x7E1E13, 0x7E1E17, function(addr, value)
  local pc = L.pc()
  local key = string.format("%X %02X", pc, value)
  if not seen[key] then seen[key] = true; L.log(string.format("f%d write %06X = %02X pc %s", L.frame, addr, value, pc)) end
end)
L.on_frame(function(f)
  if f == 3400 or f == 3460 then L.press("a", 4) end
  if f == 3430 then L.press("right", 4) end
end)
