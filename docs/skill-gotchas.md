# Skill gotchas

One line per gotcha: the reference file it belongs in, then the fact.

- scripts/lua/mesen_lib.lua: `L.on_read` on a ROM range ($80/$C0 mirrors) logged nothing here while the code plainly read it; `L.on_read` on WRAM works. Follow the copy in RAM, or log callers with an exec hook (`tools/debug/calllog.lua`). Cause not found.
- references/platform-snes.md: a game can have a run-the-rest-in-VBlank call (`$80D78F` here: queues its return address, or returns at once in forced blank). Look for it before writing an upload path: name tiles took one record and one DMA call.

- references/setup.md: `fetch_emu.py` fails with CERTIFICATE_VERIFY_FAILED when Python's CA store is stale; `gh release download` works instead, and `python -c "import certifi"` alone doesn't fix urllib.
- scripts/emu.py: `ppudump.lua` needs `--frames` or `DUMP_AT`; a `--route`-only run stops with a Lua error before any frame.
- references/emulator-qa.md: Mesen `watch.lua` reports WRAM writes as `00FCA000` for `$7E:A000` (the probe's address field isn't the CPU address on this path); trust the PC, not `addr`.
- references/platform-snes.md: `dis65816.py` loses M/X across branches; restart at each target with the right `--m8/--x8` when a routine mixes widths.
- scripts/emu.py: `--mash 90` left the opening stuck on one dialogue box while 4-frame presses every 150 frames advanced it; a route or `L.press` works, cause not found.
- references/emulator-qa.md: cold boots here drift by a few frames between runs (state 16 at f483 or f485, warp at f3502 or f3532), so a route counted in frames from boot lands wrong; count from a RAM state instead.
- references/emulator-qa.md: a `--script` file can't `dofile` a repo-relative path, Mesen's cwd isn't the repo; `warp.lua` derives the root from `OUT`.
- scripts/lua/probes/watch.lua: it logs each PC once, so a decompressor rewriting a watched buffer later looks like no write at all; compare a RAM dump with the expected bytes before ruling an overwrite out.
- references/emulator-qa.md: a menu on a dice or board game can sit in a handler that never returns to the dispatcher, so poking the state byte does nothing; write it from an exec hook on the dispatcher. Text that looks like a corrupt font can be a warp into a state the data tables don't define for that value: dump the per-chapter tables before debugging the text path.
- references/pipeline.md (Identity): byte-identical LZ recompression can need never-read look-ahead words copied from the dump (the original tool left stale buffer there), and gaps between blocks can hold data: check before blanking them.
- references/pipeline.md (Identity): before settling for a decompress-equal test, compare the original's tokens with plain greedy longest-nearest: all 749 blocks here matched, one script's work, and `bytes.rfind` compresses 2.7 MB in 4 s in pure Python.
- hooks/guard_bash.py: it blocks a whole chained command if any part pipes tests, even when commit comes after `&&` on a later line; run `check.py` in its own call.
- scripts/lua/mesen_lib.lua: `L.safe` drops return values, so an `L.on_write` callback can't override the written value; patch at the reader instead (`warp.lua` hooks the dispatcher).
- references/pipeline.md (Extract): a clean-kana string filter misses strings glued to data with no terminator (name lists, records ending in a name), and a scan that skips "already covered" ranges hid a whole text range here; audit the data pieces for kana runs too, and scan without the mask.
- references/pipeline.md (Extract): before tracing every pointer to raw strings, consider a control code at each string's start that jumps to new text: list walks and computed tables then need no tracing (proposed here, not yet proven).
- hooks/guard_bash.py: a heredoc writing a .py file is blocked, while `python - <<'X'` on stdin passes; throwaway analysis still works that way.
references/platform-snes.md: on a cooperative scheduler a wait routine that takes a number may be sleep-until-signal, not a frame count ($80E11C here: id 6 = input poll, 2 = never): read the signal side before changing it. A prompt loop that samples input must stay in step with the poll: a slower draw in its loop plus a frame-locked mash (period 30, loop 10) missed every press.
