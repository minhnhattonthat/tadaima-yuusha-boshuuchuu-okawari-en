# Skill gotchas

One line per gotcha: the reference file it belongs in, then the fact.

- references/setup.md: `fetch_emu.py` fails with CERTIFICATE_VERIFY_FAILED when Python's CA store is stale; `gh release download` works instead, and `python -c "import certifi"` alone doesn't fix urllib.
- scripts/emu.py: `ppudump.lua` needs `--frames` or `DUMP_AT`; a `--route`-only run stops with a Lua error before any frame.
- references/emulator-qa.md: Mesen `watch.lua` reports WRAM writes as `00FCA000` for `$7E:A000` (the probe's address field isn't the CPU address on this path); trust the PC, not `addr`.
- references/platform-snes.md: `dis65816.py` loses M/X across branches; restart at each target with the right `--m8/--x8` when a routine mixes widths.
- scripts/emu.py: `--mash 90` left the opening stuck on one dialogue box while 4-frame presses every 150 frames advanced it; a route or `L.press` works, cause not found.
- references/emulator-qa.md: cold boots here drift by a few frames between runs (state 16 at f483 or f485, warp at f3502 or f3532), so a route counted in frames from boot lands wrong; count from a RAM state instead.
- references/emulator-qa.md: a `--script` file can't `dofile` a repo-relative path, Mesen's cwd isn't the repo; `warp.lua` derives the root from `OUT`.
- scripts/lua/mesen_lib.lua: `L.safe` drops return values, so an `L.on_write` callback can't override the written value; patch at the reader instead (`warp.lua` hooks the dispatcher).
