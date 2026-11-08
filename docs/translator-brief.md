# Translator brief - Tadaima Yuusha Boshuuchuu Okawari (SNES, 1994)

You translate part of the Japanese script of a light, jokey board-game RPG for kids into English for a fan patch. Players
roll dice across maps as one of 12 heroes; the King of Lostia and his fairy aide Sylphy send them against the demon lord Zagan.
Work only on the batches named in your dispatch, one at a time in the order given, each to a passing check before the next.
Do all translation yourself; do not dispatch subagents. Never edit `glossary.md`, `tools/` or `script/`.

## Read first
1. `docs/style-reference.md` - voices and approved example pairs. Match this voice.
2. `build/terms_<batch>.txt` - binding glossary rows for this batch (full table and style rules in `glossary.md`; read its
   Rulings and Style rules once).
3. `docs/synopsis.md` - setting and cast.

## Input: `work/tl/<batch>.tsv`
`id<TAB>speaker<TAB>form<TAB>limit<TAB>Japanese`. Lines are in script order: use neighbours for context.
- form `dlg`/`menu`: text in a 240 px window. limit `240px x4` = 4 rows. The speaker, when there is one, is the first row
  (`{color:07}Name{color:0F}{nl}`): translate the name per the glossary and keep the codes.
- form `choice`: one option of a choice; options share one line, so keep them short (limit px per option).
- form `name`: an item/equipment/spell/character name drawn in a small font; limit = pixels (about 5 px a letter).
- form `lines`: an item description or character bio in a small font, `{nl}` between lines, 80 px a line (about 15-16
  letters), at most the rows in the limit (`80px x3`).

## Output: `work/tl/<batch>.out.tsv`, written with your file-write tool (not a shell heredoc)
`id<TAB>English`, every input id exactly once, same order. Plain ASCII only: straight quotes, `...`. No tabs, no Japanese
or fullwidth characters, no `\n` or `\uXXXX`.

## Codes (the check enforces them)
- Copy every `{...}` and `[XX]` code exactly and in a sensible place, except these, which you place freely:
  - `{nl}` line break: you lay out the lines yourself. Each line must fit its pixel width.
  - `{page}` = wait for a button, then go on (the window scrolls). Keep every JP `{page}`; you may ADD `{page}` where an
    English page would run past the window's rows. A line ending in `{page}` or `{wait}` has 224 px, not 240.
  - `{wait}` = wait for a button, then clear the window. Keep these exactly.
  - Between two prompts there may be at most as many lines as the window has rows (the speaker line counts).
  - `[F4]` blank cell (indent), `{cell}`, `[CB]` heart glyph, `[D0]` note glyph.
- `{sub:XXXX}` = text the game inserts (a name, a number, a price). Nothing glued to it: no `'s`, no ordinals, no a/an
  before it. Rephrase ("It's {sub:0000}'s turn" -> "Turn: {sub:0000}" or "{sub:0000}, it's your turn").
- `{end}` closes the English exactly when it closes the JP. A row without `{end}` runs straight on into the next row:
  make the two read as one.
- `{sfx:..}` (talk blips), `{color:..}`, `{speed:..}`, `{pause:..}` stay; timed scrolls with `{pause:..}` on every line keep one
  English line per JP line.

## Validate
`python -X utf8 tools/batches.py check <batch>` from the repo root; fix every reported id until it prints `<batch>: OK`.
Dry-run one row: `python -X utf8 tools/batches.py fit <id> "<English>"` prints each line's width and any problem.
Quote the English in single quotes in bash if it contains `!` or `$`.

## Style
- Faithful: keep the information and order of ideas; adapt idiom, not meaning. Don't add details the Japanese doesn't
  state; don't summarise or skip. Adapt wordplay so the joke still lands (no translator notes).
- Keep the speaker audible. JP register markers carry voice and must turn into English devices, not vanish:
  old men's じゃ/のう/わし ("eh?", "my boy"), rough ぜ/ねぇ/っス ("ain't", "ya", clipped grammar), feminine かしら/わよ/のね
  ("I wonder...", "you know", "dear"), animal tics ニャ ("meow"), ワン ("arf"), なのだ, っしゅ (lisp). A line any speaker could
  have said is a mistake.
- Names and terms exactly as in the glossary. Never abbreviate to fit (D4): rephrase, add a `{page}`, and if it still can't
  fit, keep the meaning and report `LONG: id`.
- Honorifics: kept on personal names (Ratar-sama, Sylphy-chan); titles become English (勇者さん "Hero", 勇者様 "Sir Hero",
  王様 "Your Majesty" / "the King"). Western name order.
- The hero can be male or female: never "he"/"she" for 勇者 or the player; "the Hero", "you", or rephrase.
- Punctuation: 「」 -> "...", ・・・ -> `...`, ！？ -> `?!`, ‼ -> `!!`, 〜 -> stretched vowels or `~`, ♪ -> `[D0]`, ♥ -> `[CB]`.
- The JP writes 倒す (defeat) as 例す and 成績 as 成続 (a table quirk): read them as 倒 / 成績.
- Board-game terms: 1回やすみ -> "Lose 1 turn"; シリング -> "Shillings"; 仲間 -> party/ally/companion.

## Consistency
For a recurring name or term not in the glossary, pick a form, use it consistently, and report it.

## Report (reply with only this)
Files written and entry count; then any lines: `NEW TERM: jp -> en`, `UNSURE: id - note`, `LONG: id - note`.
