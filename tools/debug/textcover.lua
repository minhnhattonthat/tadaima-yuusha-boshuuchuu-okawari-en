-- Text coverage for textcover.py: log "TEXT <file offset>" once per string the game reaches. --script tools/debug/textcover.lua
-- Far strings: the far table read ($E1:0000 + 3n, by far_entry) or the name image read ($E2:0000 + 4n, by small_load), both logged
-- as the table entry's offset $210000 + 3n. Raw rows (rects, descriptions, bios): RANGES='lo-hi,..' file offsets, hooked in $C0+
-- and, for $8000+ halves, in $80+; a read logs its offset (build/strings.tsv lists each row's first byte).
local seen = {}
local function log(off)
  if seen[off] then return end
  seen[off] = true
  L.log(string.format("TEXT %X f%d", off, L.frame))
end
local n = tonumber(FARS or "8192")
L.on_read(0xE10000, 0xE10000 + 3 * n, function(a) if (a - 0xE10000) % 3 == 0 then log(a & 0x3FFFFF) end end)
L.on_read(0xE20000, 0xE20000 + 4 * n, function(a) if (a - 0xE20000) % 4 == 0 then log(0x210000 + (a - 0xE20000) // 4 * 3) end end)
for lo, hi in string.gmatch(RANGES or "", "(%x+)-(%x+)") do
  lo, hi = tonumber(lo, 16), tonumber(hi, 16)
  L.on_read(0xC00000 | lo, 0xC00000 | hi, function(a) log(a & 0x3FFFFF) end)
  if lo & 0xFFFF >= 0x8000 and hi >> 16 == lo >> 16 then
    L.on_read(0x800000 | lo, 0x800000 | hi, function(a) log(a & 0x3FFFFF) end)
  end
end
