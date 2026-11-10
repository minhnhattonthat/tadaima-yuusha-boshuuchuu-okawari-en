# Tadaima Yuusha Boshuuchuu Okawari English translation

Unofficial English fan translation of **Tadaima Yuusha Boshuuchuu Okawari** (SNES, Human, 1994), a board-game RPG
("Now Recruiting Heroes: Second Helping"): the source text and tools that build the patch.

**Just want to play?** Download the patch from [Releases](../../releases) and follow its README. This repository holds
no game data you can play; you need your own dump of the Japanese game.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## Translation status

| Part | Status |
|---|---|
| Story events, quests, recruits, bosses, endings | Translated |
| Menus, items, equipment, spells, monsters, shops, system messages | Translated |
| Graphics with text (command buttons, title menu, chapter cards, status labels) | Translated, title logo included ("Now Heroes Wanted More") |
| Name entry | Translated (English letters) |
| Staff credits, THE END, CONFIG MODE | English in the original |

Known issues: a few labels are abbreviated to fit their boxes (/mo, DOB, Yr/Mo, K. Salamander in the
battle target box). See [Issues](../../issues).

## What's here

| Path | What it is |
|---|---|
| `script/` | Every text block: original Japanese and English. Translation fixes go here. |
| `glossary.md` | Binding names, terms and style rules. |
| `tools/` | Python build chain: extract, insert, lint, release. |
| `asm/` | Variable-width font and text engine changes (asar). |
| `tests/` | pytest suite (ROM-dependent tests skip when the ROM is absent). |
| `docs/re/` | Reverse-engineering notes. |
| `docs/decisions.md`, `docs/status.md` | Rulings with their reasons; current progress and open bugs. |
| `docs/fonts.md` | Fonts used and their licences. |
| `AGENTS.md` | Instructions for coding agents (`CLAUDE.md` points to it). |
| `.claude/agents/` | Subagent types (translator, reviewer, visual QA, playtester) with only the tools each needs. |

## Build your own patched ROM

Needs Python 3.12+, [asar 1.91](https://github.com/RPGHacker/asar/releases/tag/v1.91) in `tools/asar/asar.exe`, and
your own dump of the Japanese game.

```sh
git clone https://github.com/minhnhattonthat/tadaima-yuusha-boshuuchuu-okawari-en
cd tadaima-yuusha-boshuuchuu-okawari-en
# copy your dump to: rom/Tadaima Yuusha Boshuuchuu Okawari (Japan).sfc
#   (2,097,152 bytes, SHA-1 0a5363fb99ca8bb8efed0beb8e1ce6577f2d8887; the build refuses any other dump, see rom.sha1)
python -X utf8 build.py                                # -> build/tadaima_en.sfc
python -X utf8 tools/check.py                          # tests + text lint
```

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

## Licence

Tools and English translation: MIT. The original Japanese text in `script/` is Human's and is included only so
the translation can be checked against it. Tadaima Yuusha Boshuuchuu Okawari is (c) Human; this project is not
affiliated with them. Do not share patched ROMs.

The translation was made with extensive AI assistance (Claude by Anthropic). Corrections are very welcome.
