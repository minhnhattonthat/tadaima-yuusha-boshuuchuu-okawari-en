-- Log CPU position every EVERY frames from frame FROM: finds where a hang sits. --script tools/debug/pclog.lua --var FROM=1590 --var EVERY=4
L.on_frame(function(f)
  if f < FROM or (f - FROM) % EVERY ~= 0 then return end
  local s = emu.getState()
  L.log(string.format("f%d pc %02X:%04X sp %04X db %02X d %04X flags %02X", f, s["cpu.k"], s["cpu.pc"], s["cpu.sp"], s["cpu.dbr"], s["cpu.d"], s["cpu.ps"]))
end)
