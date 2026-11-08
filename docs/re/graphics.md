# Graphics text survey

Static sweep: `tools/unpack.py`, then `tools/gfxsweep.py 4` (every block over 0x200 bytes as 4bpp thumbnails, skipped list printed;
page index in `work/gfx4/index.txt`), `tools/gfxzoom.py OUT BPP ZOOM BLOCK[+OFF[:LEN]]` to zoom. Read so far: all 4bpp pages.

| # | Block | Source | Dest | Format | Text | Plan |
|---|---|---|---|---|---|---|
| G1 | 002 | `$C6:32DB` LZ | `7F:A000`, then VRAM | 4bpp, 32x16 buttons | 移動 魔法 オーブ 道具 / 休憩 地図 状態 PASS / 攻撃 魔法 オーブ 道具 / 防御 逃げる オート SOS / はい いいえ / 能力値 装備 魔法 / クエスト 街 勇者 施設 | **done** `tools/gfx.py buttons` (D15): ground 11, ink 15, shadow 1 right, spleen + 3-px t |
| G2 | 794 | `$D9:CA6B` LZ | `01:7000` | 4bpp, title BG | しなりおモード / ぱーてぃーモード / つづきをする, plus the HUMAN 1994 line | **done** `tools/gfx.py title`: BG2 tiles 0x325-0x36F, one per cell of a 14x6 box, line n in index n+1 (the HUMAN line is Latin already) |
| G3 | 793 | `$D9:B5FB` LZ | `01:4000` | 4bpp, title BG | logo ただいま 勇者募集中 おかわり | **keep** (D5: no official English version) |
| G4 | 001 | `$C6:2134` LZ | `01:4000` | 2bpp + art | second font (0-9, A-Z, kana, 年月日): HUD and small labels. Has Latin, so only strings need work; find its table and users in phase 2. User found: status screen `1年 0ヶ月` = tiles `F7`, `F8 F9` placed by code into rect `$82:B850` (code-built in `$1111`, 21x2), not a string | **done** (D15): `rects.STATUS` re-lays the template, asm moves the digit writes; save slot date (`$85:BC2D`) and rank `NO・1` (`$C2:B76C`) in asm |
| G5 | 738 | `$D8:A3D5` LZ | `01:2000` | small icon sheet | icons, digits: no kana seen at 3x | check on a marker tour |
| G6 | 001 | `$C6:2134` LZ (4bpp art part) | BG2 tiles `0xB6-0xD9` | 9x4 panel | 仲間 / 募集中! on an empty party slot (field and battle HUD) | **done** `tools/gfx.py panel`: "Allies / Wanted!", ink 11, shadow 14, the row-shaded ground refilled (tour `field`, `battle_magic`) |
| G7 | 001 | same | BG2 tiles `0xB0-0xB1` | 2 cells | 種族 before the race name in the status header (`$C2:BCD2`) | **done** `tools/gfx.py race`: "Race" in 3 px letters (tour `field_status_equip`) |
| G8 | 000 | 1bpp 16x16 font | glyph `$10A` | 1 cell | 年 after the digits in the years picker (ch 0 intro, rect `$85:A9AF`) and config play time | **done** `tools/gfx.py year`: "yr" (D15 last resort; tour `config` "1 yr") |

**No Japanese seen at thumbnail scale:** portraits 799-811 (and 812 group), sprites 34-82, 425-477, 478-525, effects 526-555, map
tiles 20-33, backgrounds 313-350, 403-407.

**2bpp sweep (done):** `tools/gfxsweep.py 2 5 69 97 120-145 556-729 817-862`, 254 cells on 11 pages (4 pages read at thumbnail scale: 0, 1, 7, 8;
the rest are the same map/sound data by destination and size), index in `work/gfx2/index.txt`. Skipped as under 0x200 bytes: 127, 137, 583-585,
699-708, 710-714, 716, 719, 728, 817, 819. No Japanese found: 120-145 effect tiles and tables, 556-696 map data for `7F:3000`, 697-724 data, 817-862
sound data. 820 is the HUMAN ENTERTAINMENT logo (English already); 727 is icons.

Screens that only show mid-game (chapter cards, game over, ending, credits): check with the phase 2 warps and add rows here.
