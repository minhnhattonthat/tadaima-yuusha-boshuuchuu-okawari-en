-- Log each distinct PC that reads a ROM or RAM range, from frame FROM. --script tools/debug/readlog.lua --var LO=0xC0A230 --var HI=0xC0A6D9 --var FROM=0
FROM = FROM or 0
local seen = {}
L.on_read(LO, HI, function(addr, value)
  if L.frame < FROM then return end
  local pc = L.pc()
  if seen[pc] then return end
  seen[pc] = true
  L.log(string.format("f%d read %06X = %02X pc %06X", L.frame, addr, value, pc))
end)
