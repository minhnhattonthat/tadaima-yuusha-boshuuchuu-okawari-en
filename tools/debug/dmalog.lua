-- Log every DMA start from a frame on: which channel's source, size and bus dest, PC, stack. --script tools/debug/dmalog.lua [--var FROM=1600]
-- Only A-bus to B-bus $80 ($2180, WRAM) unless ALL=1: that is the path that lands in low RAM.
FROM = FROM or 0
-- Banks $00-$3F and $80-$BF: code with DB = $82 writes $82:420B.
local function hook(bank) L.on_write(bank << 16 | 0x420B, bank << 16 | 0x420B, function(addr, value)
  if L.frame < FROM then return end
  local s = emu.getState()
  local m, sp = emu.memType.snesMemory, s["cpu.sp"]
  local st = {}
  for i = 1, 12 do st[#st + 1] = string.format("%02X", emu.read(sp + i, m)) end
  for c = 0, 7 do
    if value & (1 << c) ~= 0 then
      local b = 0x4300 + c * 16
      local bb = emu.read(b + 1, m)
      if ALL or bb == 0x80 then
        L.log(string.format("f%d dma%d ctl %02X bb %02X src %02X:%02X%02X n %02X%02X wram %02X:%02X%02X pc %06X a3 %02X%02X%02X stack %s", L.frame, c, emu.read(b, m), bb,
          emu.read(b + 4, m), emu.read(b + 3, m), emu.read(b + 2, m), emu.read(b + 6, m), emu.read(b + 5, m),
          emu.read(0x7E0000 + 0xA8, m), emu.read(0x7E0000 + 0xA7, m), emu.read(0x7E0000 + 0xA6, m),
          L.pc(), emu.read(0xA5, m), emu.read(0xA4, m), emu.read(0xA3, m), table.concat(st, " ")))
      end
    end
  end
end) end
for bank = 0, 0x3F do hook(bank); hook(bank | 0x80) end
