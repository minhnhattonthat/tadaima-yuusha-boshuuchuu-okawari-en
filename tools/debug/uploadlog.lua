-- Name-tile upload records (asm/vwf.asm small_load): each wait on a busy record and each give-up that reuses one still queued.
-- Addresses from `asar --symbols=wla` (work/vwf.sym): small_load_busy + 9 = jsr nap, + 17 = the give-up pha. --script tools/debug/uploadlog.lua [--var FROM=0]
FROM = FROM or 0
BUSY = BUSY or 0xE005E9
L.on_exec(BUSY + 9, BUSY + 9, function() if L.frame >= FROM then L.log(string.format("f%d busy wait", L.frame)) end end)
L.on_exec(BUSY + 17, BUSY + 17, function() if L.frame >= FROM then L.log(string.format("f%d GIVE UP: record reused while queued", L.frame)) end end)
