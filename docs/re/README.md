# Reverse-engineering notes

One file per subsystem (text engine, pointers, compression, font, graphics). Mark every finding with how far it is
proven, so a later session doesn't build on a guess:

- **verified** - and how: a decoded known string, a corrupt-and-boot test, a breakpoint hit on the drawing path, a
  passing roundtrip test. Name the test or savestate.
- **guess** - and why it seems likely (byte pattern, another game, an earlier patch's notes). Promote it to verified
  before code depends on it.

Addresses are for the dump in `rom.sha1` unless a note says otherwise.

| File | Covers | State |
|---|---|---|
| [compression.md](compression.md) | resource table, LZ format | verified on all blocks; no compressor yet |
| [text.md](text.md) | encoding, font, control codes, text locations | encoding verified; event VM and raw pointers open |
| [memory.md](memory.md) | ROM map, free space plan | map verified; free space plan a guess |
| [graphics.md](graphics.md) | tile-drawn Japanese survey | static sweep done; mid-game screens pending warps |

Prior work: no earlier fan patch found (searches 2026-11-07, English and Japanese title).
