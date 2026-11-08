-- Shoot a chapter card: when the game reads a far-table entry in CARD_LO..CARD_HI (file offsets, build/strings.tsv: the d761
-- card strings), save card.png DELAY frames later and end the run. --script tools/debug/cardshot.lua with warp.lua SCENE='chNN'.
local lo, hi, delay = tonumber(CARD_LO), tonumber(CARD_HI), tonumber(DELAY or "150")
local stop
L.on_read(0xC00000 | lo, 0xC00000 | hi, function(a)
  if stop or (a - 0x210000) % 3 ~= 0 then return end
  stop = L.frame + delay
  L.log(string.format("card %X f%d", a & 0x3FFFFF, L.frame))
end)
L.on_frame(function(f)
  if stop and f == stop then
    L.shot("card.png")
    L.finish(0)
  end
end)
