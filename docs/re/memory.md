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
`$0A2C-$0D97` and `$0DC5-$1F80` are cleared at boot (**guess**: the save data). `$0A2C` = chapter 0-12 (**verified** for intros 0-8, 10 and 11: each warp shows its own map
or scene. Intros 9 and 12 show garbage text, cause open). Chapter 12 clear -> state 1D is read from code at `$C1:76F6`, not seen in a run.
Event text bank is `$1E1D`, pointers `$1DDB/$1DDD`: the intro path sets bank `$7E` (`$C1:5BA6`), the clear path bank `$85` (`$C1:6E25`).
`$1F4B` = title mode: 0 scenario, 1 party, 2 continue. `$1F4B == 1` runs the extra party setup in state 15 (`$C1:67AA`).

| State | Handler | Seen as (warp proof in `work/qa/scenes/`) |
|---|---|---|
| 00 | `$C2:29DC` | start of a player's turn; needs a chapter set up first (black if warped into) |
| 01 | `$C2:663C` | turn command menu |
| 03 | `$C5:080D` | field map |
| 0C, 0D | `$82:C7F6`, `$C2:3B47` | turn change steps |
| 0E, 0F | `$C2:60F7`, `$C3:0000` | battle entry, side-view battle (data bank `$81`) |
| 15 | `$C1:763E` | new game: intro, player select, name entry; ends at `$C1:76A5` |
| 16 | `$C4:3155` | boot: attract loop and title menu; ends at `$C4:322A` |
| 17 | `$C1:76B1` | chapter intro event (`$C1:5BA1`) |
| 18 | `$C1:76D6` | chapter clear event (`$C1:6E23`); text garbled on warps so far, `$C1:6F84` not read yet |
| 1A | `$C1:771B` | calendar card (year, month) over the world map |
| 1D, 1E | `$C4:619F`, `$C4:63BE` | ending text over sunset, epilogue map |
| 20 | `$C1:7770` | tournament "who will win" host screen |
| 22 | `$C4:04A3` | config menu |
| 23 | `$C4:125C` | save menu (24 leads here from the Y button on the field) |
| 25 | `$C1:3E8B` | runs into a battle; purpose unknown (**guess**: battle mode) |

Other states need context a warp doesn't set up: 02, 04-0B, 10-14, 19, 1B, 1C, 1F, 21, 26. A bare warp to 08, 0A, 0C, 11-13 hangs.
