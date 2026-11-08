-- Log each distinct PC that reads a ROM or RAM range, from frame FROM. --script tools/debug/readlog.lua --var LO=0xC0A230 --var HI=0xC0A6D9 --var FROM=0
-- PAGE=1: one line per PC and 256-byte page, to see how far a DMA or loop reads.
FROM = FROM or 0
local seen = {}
L.on_read(LO, HI, function(addr, value)
  if L.frame < FROM then return end
  local pc = L.pc()
  local key = PAGE and (pc << 16 | (addr >> 8 & 0xFFFF)) or pc
  if seen[key] then return end
  seen[key] = true
  L.log(string.format("f%d read %06X = %02X pc %06X", L.frame, addr, value, pc))
end)
