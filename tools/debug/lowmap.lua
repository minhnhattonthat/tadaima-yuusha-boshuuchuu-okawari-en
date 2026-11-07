-- Which low RAM bytes get written at all, DMA included: lowmap.txt in the run's folder, for finding truly free RAM (ramuse.py only compares dumps).
-- Code in $E0 is ours. --script tools/debug/lowmap.lua
local w = {}
L.on_write(0x7E0200, 0x7E1FFF, function(addr)
  w[addr & 0x1FFF] = true
end)
L.on_frame(function(f)
  if f % 500 ~= 0 then return end
  local t = {}
  for a = 0x200, 0x1FFF do t[#t + 1] = w[a] and "1" or "0" end
  L.write_file("lowmap.txt", table.concat(t))
end)
