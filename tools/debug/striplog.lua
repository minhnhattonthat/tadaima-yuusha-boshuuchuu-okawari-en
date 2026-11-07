-- Log calls into the 16 px strip renderer $C21AC4 and direct $C21B0B callers: return address, DB:Y, bytes. --script tools/debug/striplog.lua [--var FROM=4000]
FROM = FROM or 0
local seen = {}
local function hook(addr, tag, ptr)
  L.on_exec(addr, addr, function()
    if L.frame < FROM then return end
    local s = emu.getState()
    local m, sp = emu.memType.snesMemory, s["cpu.sp"]
    local ret = emu.read(sp + 1, m) | emu.read(sp + 2, m) << 8 | emu.read(sp + 3, m) << 16
    local hex = {}
    if ptr then for i = 0, 11 do hex[#hex + 1] = string.format("%02X", emu.read((s["cpu.dbr"] << 16 | s["cpu.y"]) + i, m)) end end
    local key = string.format("%s %06X %02X:%04X X=%04X %s", tag, ret, s["cpu.dbr"], s["cpu.y"], s["cpu.x"], table.concat(hex, " "))
    if not seen[key] then seen[key] = true; L.log("f" .. L.frame .. " " .. key) end
  end)
end
hook(0xC21AC4, "strip", true)
hook(0xC21B0B, "cell", false)
