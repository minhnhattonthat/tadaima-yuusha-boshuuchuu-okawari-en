# Skill gotchas

One line per gotcha: the reference file it belongs in, then the fact.

- references/setup.md: `fetch_emu.py` fails with CERTIFICATE_VERIFY_FAILED when Python's CA store is stale; `gh release download` works instead, and `python -c "import certifi"` alone doesn't fix urllib.
- scripts/emu.py: `ppudump.lua` needs `--frames` or `DUMP_AT`; a `--route`-only run stops with a Lua error before any frame.
- references/emulator-qa.md: Mesen `watch.lua` reports WRAM writes as `00FCA000` for `$7E:A000` (the probe's address field isn't the CPU address on this path); trust the PC, not `addr`.
- references/platform-snes.md: `dis65816.py` loses M/X across branches; restart at each target with the right `--m8/--x8` when a routine mixes widths.
