-- Which WRAM bytes get written at all, DMA included, from frame FROM on (after the boot clear): lowmap.txt in the run's
-- folder, one 0/1 per byte of $7E:0000-$7F:FFFF, for tools/debug/freeram.py. Run it on the original ROM: our code's writes count too. --script tools/debug/lowmap.lua [--var FROM=60]
FROM = FROM or 60
local w = {}
local ranges = { { 0x7E0200, 0x7FFFFF } }
local hooked = {}
for _, r in ipairs(ranges) do
  for a = r[1] & 0x1FFFF, r[2] & 0x1FFFF do hooked[a] = true end
  L.on_write(r[1], r[2], function(addr)
    if L.frame >= FROM then w[addr & 0x1FFFF] = true end  -- no L.pc() here: getState per write times the tour out
  end)
end
L.on_frame(function(f)
  if f % 500 ~= 0 then return end
  local t = {}
  -- 1 written, 0 never written, - not watched
  for a = 0, 0x1FFFF do t[#t + 1] = w[a] and "1" or (hooked[a] and "0" or "-") end
  L.write_file("lowmap.txt", table.concat(t))
end)
