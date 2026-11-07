-- The last 200 instruction addresses before the CPU stops (STP, wild jump) or before frame TO: --script tools/debug/lastpc.lua --var FROM=4590 [--var TO=4600]
-- Addresses only: emu.getState per instruction takes minutes a frame. Whole bus: code runs in every mirror.
local ring, n, last, done = {}, 0, -1, false
local function dump()
  done = true
  local t = {}
  for i = n - 199, n do t[#t + 1] = string.format("%06X", ring[i % 200] or 0) end
  L.log("pc " .. table.concat(t, " "))
end
L.on_exec(0x000000, 0xFFFFFF, function(addr)
  if done or L.frame < FROM then return end
  n = n + 1
  ring[n % 200] = addr
  if TO and L.frame >= TO then dump() end
end)
L.on_frame(function(f)
  if not done and n > 0 and n == last then dump() end
  last = n
end)
