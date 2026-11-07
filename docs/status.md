# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1. Research and recon in progress (one item left). Last build: none yet.
- **Done:** Step 0: Mesen and asar in `tools/` (via `gh`), pre-commit gate proven, guard proven, original ROM smokes. Not checked: GUI keyboard input. Resource table + LZ decompressor verified on all 863 blocks (`tools/lz.py`, `tools/unpack.py`). Font and `tbl/jp.tbl` read off, control codes from the engine, ROM map (`tools/rommap.py`). 4bpp graphics sweep read; rows in `docs/re/graphics.md`. Notes in `docs/re/`.
- **Next:** close phase 1: run `python -X utf8 tools/unpack.py > work/blocks.txt`, then a 2bpp sweep limited to the blocks listed under "Not swept yet" in `docs/re/graphics.md`, add any rows. Then phase 2 debug tool. Later needs: a compressor (none yet), the event bytecode VM in blocks 229-302, pointers to the raw strings in banks `$C0/$C1/$C4/$C5`, WRAM buffer limits for dialogue blocks.
- **Open bugs:** none.
- **Waiting on the user:** nothing.
