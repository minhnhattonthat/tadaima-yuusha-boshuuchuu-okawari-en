-- Load block TO wherever the game asks the resource lookup ($82:8192, A = index) for block FROM: e.g. another monster in a warped
-- battle (FROM=584 Hobgoblin, the battle_menu2 foe). Proves a block repack.py moved still loads, and shows any foe's name.
-- --script tools/debug/swapblock.lua --var FROM=584 --var TO=629
-- Two entries take A = index: the lookup $82:8192 and the loader $82:8024 (monster blocks come through the loader).
local function swap(pc)
  return function()
    local s = emu.getState()
    if LOGALL then L.log(string.format("f%d %06X a %04X", L.frame, pc, s["cpu.a"] & 0xFFFF)) end
    if s["cpu.a"] & 0x0FFF == FROM then  -- $82:8024 keeps flags in the top 4 bits (AND #$0FFF)
      emu.setState({ ["cpu.a"] = (s["cpu.a"] & 0xFFFFF000) | TO })
      L.log(string.format("f%d %06X block %d -> %d", L.frame, pc, FROM, TO))
    end
  end
end
L.on_exec(0x828192, 0x828192, swap(0x828192))
L.on_exec(0x828024, 0x828024, swap(0x828024))
