# Style reference

From the pilot (batch b005: the attract prologue, hero bios, the ending scroll, first event squares and the travelling shops),
checked in-game (`work/qa/pilot_title`). Match this voice. The game is a light, jokey board-game RPG for kids: short, punchy,
playful, never stiff. Every speaker keeps their tic.

## Voices
| Speaker | JP markers | English devices | Example |
|---|---|---|---|
| King (王様) | じゃ, のう, わし, そなた, 〜ぞ, ううむ | grand, fussy old man: "eh", "my dear", "we shall", "Hmmm..." | 勇者じゃ！ -> "Heroes, that's it!"; うかうかしておれんぞ -> "we cannot sit idly by any longer, eh..." |
| Sylphy (シルフィ) | 〜の, 〜わ, 〜ね, っ!, たいへん | bubbly, breathless, "you see", "you know!", exclamations | 王様っ！たいへん、たいへんっ！ -> "Your Majesty! It's terrible, just terrible!" |
| Pikoko item shop | 〜♪, しら〜, まし〜 | sing-song, stretched vowels, `~[D0]` | どれを買います〜♪ -> "What will you buuuy~[D0]" |
| Pikoko weapon shop | でしゅ, っしゅ, でし, にゃ | lisped "-sh" endings, "meow" | 何をおもとめでし？ -> "What are you after-sh?"; これでいいかにゃ？ -> "Is that okay, meow?" |
| Berorin Q (べろりんQ) | なのだ | ", yes indeedy!" on every line | べろりんQの負けなのだ -> "Berorin Q loses, yes indeedy!" |
| Kojima (コジマ) | オ〜ッホッホッ, 私, 〜よ | haughty lady laugh, vain | -> "Oh-ho-ho-ho-ho! My name is Kojima, the most beautiful lady thief in the world!!" |
| Gan (ガン) | 〜ワン | ", arf!" | ついてないワン‼ -> "What bad luck, arf!!" |
| Kojiro (コジロー) | わが剣, 〜わ (old samurai) | clipped, proud, sword talk | カタナのサビにしてくれるわ -> "You'll be rust on my katana!!" |
| Narration / event squares | 勇者は〜, 1回やすみ | plain past tense, sound effect first; the penalty line exactly "Lose 1 turn" | ガラガラガラ〜ッ！ -> "CRASH, CRASH, CRAAASH!" |
| Monsters, villains | キサマ, 〜ぞ, ガハハ | menacing, "you", "Gahaha!" | |

## Rules shown by the pilot
- The hero is any of 12 characters, male or female: never "he/she" for 勇者; say "the Hero" or rephrase.
- 勇者さん / 勇者様 / 勇者殿 are titles, not names: "Hero", "Hero", "noble Hero" by register (D11: never "Sir Hero"; carry 様's deference in the phrasing).
- The hero taking the crown (王 said of the hero) is "ruler" / "on the throne", never "King" (glossary Style rules).
- Katakana robots and machines (Gigantia, Gigo, Gattan) speak in ALL CAPS; their sound effects stay mixed case.
- Sound effects lead, in capitals or with stretched letters and the JP punctuation: ザッ！ "Zip!", ブワッ！ "FWOOSH!", アチチ〜ッ！ "Hot, hot, hooot!".
- Timed scrolls (`{pause:..}` after every line, no prompts) keep exactly one English line per JP line, same pause codes.
- Hearts and notes are the game's glyphs: ♥ `[CB]` (inside the JP's `{color:09}..{color:0F}`), ♪ `[D0]`.

## Corrected example
- 04C27C デューク bio, first draft "he stands against the dark fiends!" - the JP is an imperative cheer (闇の魔物たちにたちむかえっ！): fixed to "go take on the dark fiends!". Keep the JP's mood (command, question, exclamation) as well as its content.
