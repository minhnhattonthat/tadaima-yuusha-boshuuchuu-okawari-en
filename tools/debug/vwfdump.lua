-- Log the VWF cell buffers and window state: --script tools/debug/vwfdump.lua --var AT=1350
local wram = emu.memType.snesWorkRam
L.on_frame(function(f)
  if f ~= AT then return end
  local function hex(a, n)
    local t = {}
    for i = 0, n - 1 do t[#t + 1] = string.format("%02X", emu.read(a + i, wram)) end
    return table.concat(t, " ")
  end
  L.log("bufA " .. hex(0x1FE00, 128))
  L.log("bufB " .. hex(0x1FE80, 64))
  L.log("vars " .. hex(0x1FF00, 40))
  L.log("0FC1 " .. hex(0x0FC1, 128))
  L.log("10EF " .. hex(0x10EF, 32))
end)
