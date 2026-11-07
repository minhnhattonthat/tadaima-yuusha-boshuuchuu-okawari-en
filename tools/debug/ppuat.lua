-- Dump PPU state at a frame, to tell black screens apart: --script tools/debug/ppuat.lua --var AT=3300
L.on_frame(function(f)
  if f ~= AT then return end
  L.dump_ppu("ppu")
  L.shot("at.png")
end)
