Tadaima Yuusha Boshuuchuu Okawari (SNES) - English Translation v{VERSION}
========================================================================

An unofficial fan translation of Human's 1994 Super Famicom board-game RPG
"Tadaima Yuusha Boshuuchuu Okawari" ("Now Recruiting Heroes: Second Helping")
into English.

Translated:
- All story events, quests, recruits, boss scenes, the King's and Sylphy's
  guide text, and the endings.
- Menus, items, equipment, spells, monster and place names, shops and inns,
  battle and system messages, save/load and name entry.
- Graphics text: the command buttons, title menu, chapter cards and status
  labels.
- Left in Japanese: the title logo (it has no official English version).
  The staff credits, THE END and CONFIG MODE are English in the original.

The Japanese font is replaced by a variable-width English font.

Applying the patch
------------------
Apply TadaimaYuushaBoshuuchuuOkawari_EN_v{VERSION}.bps to an unmodified,
unheadered dump with Flips, Beat or RomPatcher.js
(https://www.marcrobledo.com/RomPatcher.js/).

Base ROM: Tadaima Yuusha Boshuuchuu Okawari (Japan).sfc (No-Intro),
  2,097,152 bytes
  {BASE}
Patched ROM: 2,097,152 bytes
  {PATCHED}

If your file is 2,097,664 bytes it has a 512-byte copier header: remove it first.

Notes
-----
- Tested in Mesen 2.2.1. Start from a fresh boot: save states made with the
  Japanese game hold the old text engine. Battery saves made with the
  Japanese game are untested.

Known issues
------------
- A few labels are abbreviated to fit their boxes: "/mo" on
  the salary line, "DOB" and "Yr/Mo" on the status and save
  screens, "K. Salamander" in the battle target box.

Report bugs at https://github.com/minhnhattonthat/tadaima-yuusha-boshuuchuu-okawari-en/issues
(a savestate helps most).

Credits
-------
Translation, tools and hacking: minhnhattonthat, with extensive AI assistance
(Claude by Anthropic). Corrections are very welcome.

This is an unofficial fan work, not affiliated with the rights holders.
Do not distribute pre-patched ROMs.
