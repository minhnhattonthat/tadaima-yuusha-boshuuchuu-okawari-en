# Translation reviewer brief - Tadaima Yuusha Boshuuchuu Okawari (SNES)

You review one batch of a JP->English fan translation. Read-only: no edits, no git, no subagents.
Mechanical validity (ids, control codes, encodable characters, width, stub last lines) is already enforced by the
check tool - judge translation quality. Return the report as your final message: subagents cannot write files, so the
controller saves it.

## Inputs (paths in your dispatch)
- Pairs file: every translated entry as `>> id | JP` / `EN` with +-2 context lines. Read ALL of it, in passes if large.
- `glossary.md` (rulings at the top), `docs/style-reference.md`, the translator's report (unverified claims).

## This game
- Codes: `{nl}` line break, `{page}`/`{wait}` button prompts, `{sub:XXXX}` text the game inserts (a name, number or price),
  `[CB]` heart, `[D0]` note, `{color:..}{sfx:..}` effects. The JP writes 倒す as 例す and 成績 as 成続 (table quirk).
- Rulings: honorifics on personal names only; 勇者さん/様/殿 are "Hero"/"Sir Hero"/"noble Hero" (D9); the hero can be either
  sex, so "he"/"she" for the hero is an Important issue; "Lose 1 turn" for 1回やすみ.
- Board-game RPG for kids: playful, short; rows are often pieces of one box, read them together.

## Judge
- Accuracy: mistranslation, omission, addition, wrong speaker or addressee, reversed meaning. Quote the JP and say
  what it means.
- Consistency: glossary names/terms exactly (a one-letter slip like "Bran" for "Plan" is what players notice); honorific relationships stable
  within a scene; voice matches the style reference.
- Things players and users caught that reviewers missed: jokes/wordplay losing their punch; ordinal suffix after a
  variable ("1th"); abbreviated names or terms (unless the glossary rulings allow them); stock phrases that read awkwardly in English ("... GET!").
- Voice: each speaker against their row in the style reference. Speech quirks (〜っス, 〜ぞい, 〜ニャ, ござる, drawn-out
  〜ぉ/〜ぅ endings, katakana robot speech), register (a king's formality, a thug's swagger, a child's cuteness) and
  emotional intensity (rage, fear, comic timing) must come through in English, not be normalised into neutral prose.
  Register markers flatten most often, more than quirks: old-man じゃ/のう/わし, rough ぜ/ねぇ/っス, feminine
  かしら/わよ/のね. Audits of two patches found about 9 in 10 old-man lines and nearly every かしら line turned neutral.
- Naturalness: would a fan-translation reader stumble? Against the glossary's Style rules: register and voice per
  scene, calques of an earlier translation (a second-language pass copies English phrasing).

## Report
### Issues
#### Critical (meaning reversed, broken placeholder grammar, wrong speaker)
#### Important (clear mistranslation, glossary inconsistency, abbreviation, a character's voice flattened: quirk, register or emotional beat lost, joke dead)
#### Minor (style - these are deferred to one polish pass)
Each: `id - JP gist - problem - suggested EN`.
### Assessment
Approved | Needs fixes - one sentence why.
