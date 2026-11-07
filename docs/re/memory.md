# ROM map and free space

HiROM + FastROM (`$FFD5 = 31`), 2 MB (`$FFD7 = 0B`), SRAM (`$FFD8 = 03`), region Japan, maker `33`. Title (half-width kana)
`ﾀﾀﾞｲﾏﾕｳｼｬﾎﾞｼｭｳﾁｭｳｵｶﾜﾘ`.

| File range | Contents |
|---|---|
| `000000-05FFFF` | code and raw data (banks `$C0-$C5`) with raw strings; see `text.md` |
| `060000-06000F` | table pointer + 13 bytes |
| `060010-1DDF3C` | LZ and raw blocks, end to end (`tools/rommap.py`) |
| `1DDF40-1DF837` | resource table |
| `1DF838-1FFFFF` | not mapped by the table: rest of bank `1D` and banks `1E`, `1F` |

Compressed blocks leave only short gaps (`17E418-17FFFF`, `1AEB80-1AFFFF`, `1CF0AD-1CFFFF`): these are **candidates**, not free
(fill-and-tour first).

## Free space plan (**guess**, promote in phase 5)

Expand 2 -> 4 MB: `$FFD7 = 0C`, new banks `$E0-$FF` (file `0x200000+`) are free by construction, and the resource table holds
24-bit sources, so any block can move there. The checksum is fixed at release.

WRAM buffers are fixed-size: dialogue blocks unpack to `$7E:8000/9000/A000` and sit beside other data, so a longer English
block can overrun. Check each dest's real limit before phase 6, or read the text directly from ROM.

## Game state `$0DDD` (verified: dispatcher `$82:90B5`, table `$80:99E9`, 3-byte pointers; data bank per state at `$80:9A5E`)

Handlers return by RTL to the loop at `$82:90AF`, which reads `$0DDD` again. `tools/debug/statelog.lua` logs changes.
`$0A2C-$0D97` and `$0DC5-$1F80` are cleared at boot (**guess**: the save data).

**Chapters (verified from code and tables, shots in `work/qa/scenes/`).** `$0A2C` is 0-4 for the five chapters, 5-7 for branches (`$1DF2 + 5`, `$C1:6888`). State 1F adds 8 for the mid-chapter event (`$C1:5885`), state 18 needs the +8 already set and leaves by subtracting 7 (`$C1:6F4B`), so clear 8 leads to the intro of chapter 1. Value 12 ends in state 1D. Tables by `$0A2C` at `$85:A2F2` and `$85:A3E4` (events), `$85:B844` and `$85:B884` (clear, `FFFF` for 0-7: state 18 on those reads garbage, not a real scene).

Text blocks by `$0A2C`, `$C1:618C`, tables `$85:A24E` and `$85:A268`: 0-7 load 745-752 to `7E:8000` and 753-760 to `7E:9000`; 8-12 load 762-766 to `7E:8000` only. States 18 and 20 load none (clear text is in bank `$85`).
Event text bank is `$1E1D`, pointers `$1DDB/$1DDD`: the intro path sets bank `$7E` (`$C1:5BA6`), the clear path bank `$85` (`$C1:6E25`).
`$1F4B` = title mode: 0 scenario, 1 party, 2 continue, 3 versus battle (state 25). `$1F4B == 1` runs the extra party setup in state 15 (`$C1:67AA`).

**Records (verified by poking and reading the menus).** Current player `$0C9C`. Player record `$0BEB + $2C * p` (`$82:9824`): +0C money (u16), +0E 30 item ids. Character record `$0A2F + $25 * (3p + slot)` (`$82:9846`): +1 name, +13 HP, +15 max HP (**guess** from the value), +19 12 spell ids. Map position `$0CAF,p` / `$0CCF,p`, move target `$1584/$1586`, dice `$12BF`.

**Map tiles.** `$7E:D006` -> list of `x, y, type, site`, ending `FFFF`. State 0C (`$82:C7F6`) reads the tile at `$1584/$1586` and jumps by type (table `$82:C819`):

| Type | Handler | What (ch 0 proof) |
|---|---|---|
| 1 | `C8CC` | teleporter |
| 2 | `C965` -> state 11 | shop |
| 3 | `C96F` -> state 13 | inn |
| 4 | `C979` | cave: random fight or nothing |
| 5 | `CE4A` | named fight |
| 6 | `CA2A` | fixed encounter |
| 7 | `C82D` | orb slot machine |
| 8, 9 | `CABE` | not seen on ch 0 |

| State | Handler | Seen as (warp proof in `work/qa/scenes/`) |
|---|---|---|
| 00 | `$C2:29DC` | start of a player's turn; needs a chapter set up first (black if warped into) |
| 01 | `$C2:663C` | turn command menu |
| 03 | `$C5:080D` | move after the dice |
| 07 | `$C2:573B` | map screen (X menu) |
| 08 | `$C2:3A34` | rest (X menu) |
| 09 | `$82:B654` | status screen (X menu) |
| 0C, 0D | `$82:C7F6`, `$C2:3B47` | tile event, turn change |
| 0E, 0F | `$C2:60F7`, `$C3:0000` | battle entry, side-view battle (data bank `$81`) |
| 10 | `$C2:61E6` | battle result; defeat is here (robot takes items, play goes on: no game over screen in scenario mode) |
| 11, 13 | `$C5:3695`, `$C5:416D` | shop, inn |
| 15 | `$C1:763E` | new game: intro, player select, name entry; ends at `$C1:76A5` |
| 16 | `$C4:3155` | boot: attract loop and title menu; ends at `$C4:322A` |
| 17 | `$C1:76B1` | chapter intro event (`$C1:5BA1`) |
| 18 | `$C1:76D6` | chapter clear event (`$C1:6E23`) |
| 1A | `$C1:771B` | calendar card (year, month) over the world map |
| 1D, 1E | `$C4:619F`, `$C4:63BE` | ending text over sunset, epilogue map |
| 19 | `$C4:27B7` | standings card (rank, NVP points) |
| 1B | `$C5:76A9` | dead: jumps to itself |
| 1C | `$C5:0C45` | leads into the boss fight after state 1F |
| 1F | `$C1:772B` | mid-chapter event, then a boss fight (`$C1:5878`) |
| 20 | `$C1:7770` | tournament "who will win" host screen |
| 21 | `$C4:66D2` | THE END. Needs `$1F2F-$1F35` from state 1D, black on a bare warp |
| 22 | `$C4:04A3` | config menu |
| 23 | `$C4:125C` | save menu (24 leads here from the Y button on the field) |
| 25 | `$C1:3E8B` | runs into a battle (title mode 3) |
| 26 | `$C1:0000` | boot notice instead of the title, from `$015F` (`$C0:D4xx` multitap and pad check): bit 6 multitap string `$84:B1C1`, else `$84:B1FA`. Not a ROM integrity check: the ASCII at `$C0:D4F3` names the multitap code it was taken from |

Bare warps to 02, 04-06, 0A, 12 and 14 stay black or fall through: those need a menu or item that leads there. 0A is PASS (`field_pass`). The rest may be item or spell effects: `textcover.py` in phase 8 will show if their strings are missed. Poking `$0DDD` while in state 03 does nothing: the handler doesn't return to the dispatcher until its move ends, so `warp.lua` writes it in a hook on the dispatcher.
