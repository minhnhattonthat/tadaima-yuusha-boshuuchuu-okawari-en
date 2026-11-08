-- Forced text sweep (text coverage, "force, don't play"): when the opening's dialogue starts a far string, the text routine is pointed
-- at a buffer in free WRAM of call codes `F1 lo hi` (far string, then go on: asm/vwf.asm far_read .call) for far strings
-- LIST[FROM..TO], ending FF. When the routine reaches that FF, the buffer is refilled with the next batch and Y set back to its start.
-- Run with warp.lua SCENE='opening' (its A presses turn the pages) and textcover.lua; driven by tools/debug/sweep.py.
-- CALLX = the .call path's lda $0001,y (Y = the code being run: marks progress). Registers only: an exec hook can't move PC.
local wram = emu.memType.snesWorkRam
local BUF, BATCH = 0x7E00, 150  -- $7E:7E00-7FFF is free (docs/re/vwf.md)
local list = {}
for n in L.read_file(LIST):gmatch("%x+") do list[#list + 1] = tonumber(n, 16) end
local done_k, base, count = FROM, FROM, 0  -- next string not yet printed; buffer holds list[base .. base+count-1]
local finished = false

local function fill()
  base, count = done_k, math.min(BATCH, TO - done_k + 1)
  for i = 0, count - 1 do
    local n = list[base + i]
    emu.write(BUF + i * 3, 0xF1, wram); emu.write(BUF + i * 3 + 1, n & 0xFF, wram); emu.write(BUF + i * 3 + 2, n >> 8, wram)
  end
  emu.write(BUF + count * 3, 0xFF, wram)
  for slot = 0, 15 do  -- {sub:n} slots at $1236 + 16n hold junk in the opening: "999" FF, or a string runs on forever
    for i, v in ipairs({ 0x69, 0x69, 0x69, 0xFF }) do emu.write(0x1236 + slot * 16 + i - 1, v, wram) end
  end
end

L.on_exec(READ, READ, function()  -- far_read: A = the code byte at DB:Y
  if finished then return end
  local s = emu.getState()
  local db, y = s["cpu.dbr"], s["cpu.y"]
  local inbuf = db == 0x7E and y >= BUF and y <= BUF + BATCH * 3
  if inbuf and y ~= BUF + count * 3 then return end
  if not inbuf and (s["cpu.a"] & 0xFF ~= 0xF0 or db >= 0xA0) then return end  -- far strings live in $A1-$BF: not a top-level one
  if inbuf and done_k < base + count then done_k = base + count end  -- reached the FF: the whole batch ran
  if done_k > TO then
    finished = true
    L.log(string.format("sweep done f%d", L.frame))
    L.shot("final.png")
    L.finish(0)
    return
  end
  fill()
  L.log(string.format("SWEEP %d-%d f%d from %02X:%04X", base, base + count - 1, L.frame, db, y))
  s["cpu.dbr"], s["cpu.y"], s["cpu.a"] = 0x7E, BUF, 0xF1
  emu.setState(s)
end)
L.on_exec(CALLX, CALLX, function()
  local s = emu.getState()
  if s["cpu.dbr"] == 0x7E and s["cpu.y"] >= BUF and s["cpu.y"] < BUF + count * 3 then
    done_k = math.max(done_k, base + (s["cpu.y"] - BUF) // 3)  -- this one starts now; a stop mid-batch resumes here
    if DEBUG then L.log(string.format("call %04X f%d", s["cpu.y"], L.frame)) end
  end
end)
