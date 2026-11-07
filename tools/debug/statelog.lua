-- Log each change of the game state byte $0DDD (see docs/re/memory.md). Use with emu.py --script.
local wram = emu.memType.snesWorkRam
local last = -1
L.on_frame(function(f)
  local s = emu.read(0x0DDD, wram)
  if s ~= last then
    L.log(string.format("f%d state %02X", f, s))
    last = s
  end
end)
