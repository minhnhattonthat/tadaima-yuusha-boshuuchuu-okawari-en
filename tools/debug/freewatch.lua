-- Prove the RAM the engine took is free: log each PC outside our code ($E0) that writes it. --script tools/debug/freewatch.lua
local seen = {}
local function watch(lo, hi)
  L.on_write(lo, hi, function(addr, value)
    local pc = L.pc()
    if pc >> 16 == 0xE0 then return end
    local key = string.format("free %06X by %06X", addr & ~15, pc)
    if seen[key] then return end
    seen[key] = true
    L.log(key)
  end)
end
watch(0x7E1538, 0x7E1549)  -- !RECORDS (the scheduler at $80D78F writes them too: its PCs are expected)
watch(0x7FFE00, 0x7FFFFF)  -- VWF cells and state
