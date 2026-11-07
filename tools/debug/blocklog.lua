-- Log block requests: frame, block number, dest override, return addresses. --script tools/debug/blocklog.lua [--var FROM=1500]
-- $829F9A queues one for the background task, $828024 loads one now.
FROM = FROM or 0
for _, pc in ipairs({ 0x829F9A, 0x828024 }) do
  L.on_exec(pc, pc, function()
    if L.frame < FROM then return end
    local s = emu.getState()
    local m, sp = emu.memType.snesMemory, s["cpu.sp"]
    local st = {}
    for i = 1, 12 do st[#st + 1] = string.format("%02X", emu.read(sp + i, m)) end
    L.log(string.format("f%d block %06X a %04X x %04X y %04X stack %s", L.frame, pc, s["cpu.a"], s["cpu.x"], s["cpu.y"], table.concat(st, " ")))
  end)
end
