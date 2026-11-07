-- Write WRAM on frame 1 of a run: --script tools/debug/poke.lua --var "POKE={[0xBF9]=1,[0xBFA]=2}"
local wram = emu.memType.snesWorkRam
L.on_frame(function(f)
  if f == 1 then for a, v in pairs(POKE) do emu.write(a, v, wram) end end
end)
