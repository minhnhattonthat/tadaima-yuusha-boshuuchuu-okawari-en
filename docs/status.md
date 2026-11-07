# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1. Research and recon in progress. Last build: none yet.
- **Done:** Step 0 (emulator, asar, pre-commit, guard proven). Resource table + LZ decompressor (`tools/lz.py`, `tools/unpack.py`) verified on all 863 blocks. Font and `tbl/jp.tbl` read. Control codes from the engine. ROM map (`tools/rommap.py`). Notes in `docs/re/`.
- **Next:** finish the graphics-text survey in `docs/re/graphics.md`: read `work/gfx4/m_*.png` from `python -X utf8 tools/gfxsweep.py 4` (run `tools/unpack.py` first), plus a boot tour. Then phase 2 debug tool.
- **Open bugs:** none.
- **Waiting on the user:** nothing.
