# Graphics text survey

Static sweep: `tools/unpack.py`, then `tools/gfxsweep.py 4` (every block over 0x200 bytes as 4bpp thumbnails, skipped list printed;
page index in `work/gfx4/index.txt`), `tools/gfxzoom.py OUT BPP ZOOM BLOCK[+OFF[:LEN]]` to zoom. Read so far: all 4bpp pages.

| # | Block | Source | Dest | Format | Text | Plan |
|---|---|---|---|---|---|---|
| G1 | 002 | `$C6:32DB` LZ | `7F:A000`, then VRAM | 4bpp, 32x16 buttons | 移動 魔法 オーブ 道具 / 休憩 地図 状態 PASS / 攻撃 魔法 オーブ 道具 / 防御 逃げる オート SOS / はい いいえ / 能力値 装備 魔法 / クエスト 街 勇者 施設 | redraw in English |
| G2 | 794 | `$D9:CA6B` LZ | `01:7000` | 4bpp, title BG | しなりおモード / ぱーてぃーモード / つづきをする, plus the HUMAN 1994 line | redraw in English |
| G3 | 793 | `$D9:B5FB` LZ | `01:4000` | 4bpp, title BG | logo ただいま 勇者募集中 おかわり | **keep** (D5: no official English version) |
| G4 | 001 | `$C6:2134` LZ | `01:4000` | 2bpp + art | second font (0-9, A-Z, kana, 年月日): HUD and small labels. Has Latin, so only strings need work; find its table and users in phase 2 | check users |
| G5 | 738 | `$D8:A3D5` LZ | `01:2000` | small icon sheet | icons, digits: no kana seen at 3x | check on a marker tour |

**No Japanese seen at thumbnail scale:** portraits 799-811 (and 812 group), sprites 34-82, 425-477, 478-525, effects 526-555, map
tiles 20-33, backgrounds 313-350, 403-407.

**Not swept yet:** blocks that read as noise at 4bpp (e.g. 005, 069, 097, 120-145, 556-729, 817-862) may be 2bpp tiles,
tilemaps or data. Run `tools/gfxsweep.py 2` limited to these before closing phase 1, since block 001 only became legible at 2bpp.
Also: screens that only show mid-game (chapter cards, game over, ending, credits) need warps from phase 2.
