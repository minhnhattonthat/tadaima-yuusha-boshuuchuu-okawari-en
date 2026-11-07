-- Log the block loader's raw DMA path $828139: frame, DP A1-AB, return addresses. --script tools/debug/dmalog.lua [--var FROM=1600]
FROM = FROM or 0
L.on_exec(0x828139, 0x828139, function()
  if L.frame < FROM then return end
  local s = emu.getState()
  local m, sp = emu.memType.snesMemory, s["cpu.sp"]
  local dp, st = {}, {}
  for a = 0xA1, 0xAB do dp[#dp + 1] = string.format("%02X", emu.read(a, m)) end
  for i = 1, 16 do st[#st + 1] = string.format("%02X", emu.read(sp + i, m)) end
  L.log(string.format("f%d dma dp %s db %02X sp %04X stack %s", L.frame, table.concat(dp, " "), s["cpu.dbr"], sp, table.concat(st, " ")))
end)
