# Glossary - Tadaima Yuusha Boshuuchuu Okawari (SNES, Human, 1994)

Binding for every translator and reviewer. Agents propose additions in reports; only the controller edits this file.
`tools/batches.py check` fails a line whose JP holds a term below while its English lacks the term's EN (any of the `/` forms).

## Rulings (asked of the user once; options and reasons in docs/decisions.md)
- Honorifics (D1, D9): kept on personal names, hyphenated: Ratar-sama, Sylphy-chan, Tira-san. On a title or a common noun they become English: 勇者さん / 勇者様 / 勇者殿 -> "Hero" / "Hero" / "noble Hero" by the speaker's register (D11: never "Sir Hero", the hero may be female; carry 様's deference in the phrasing), 王様 -> "the King" / "Your Majesty". Name order: Western (given name first).
- Romanisation (D2): no official English names exist; katakana loanwords take their English source (ゴーレム Golem, シリング Shilling), invented names Hepburn without macrons unless a row below says otherwise.
- Credits (D3): English. Abbreviations (D4): none; full names and terms, engine work before cuts.
- Register / flavour: light, jokey board-game RPG for kids; keep verbal tics (ニャ, ワン, っしゅ, なのだ) as English tics, never flatten them.
- The hero's crown: 王 / 王様 / ロスティア王 said of the player's hero (who may be female) is "ruler" or "on the throne" ("with {sub:0200} on the throne", "the new ruler of Lostia"), never "King". The old King stays "King".
- Robots and machines that speak in katakana (Gigantia, Gigo, Gattan, the bleeping robots) talk in ALL CAPS; their sound effects (Gshshsh, Beep) and katakana monsters stay in mixed case.
- Sound effects: plain capitalised words with punctuation as in the JP (ガラガラ〜ッ！ -> "CRASH, CRASH!"; ザッ！ -> "Whoosh!").

## Style rules
- Punctuation: 「」 -> "...", 『』 -> '...', ・・・ / ．．． -> `...`, ！？ -> `?!`, ‼ -> `!!`, 〜 (drawn-out) -> repeat the vowel or `~` (`~` is in the font), ♥ -> `[CB]` and ♪ -> `[D0]` (the game's own glyphs as raw bytes, 16 px each; keep the `{color:..}` codes around a heart). Nothing else non-ASCII: the check fails it.
- The JP writes 倒す (defeat) as 例す and 成績 as 成続: a glyph quirk of the table, read them as 倒 / 成績.
- `{sub:XXXX}` is text the game inserts: a hero or monster name, a number, a price. Nothing glued to it ("'s", ordinals): rephrase.
- Voices: `docs/style-reference.md`.

## Characters
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 勇者 | Hero | | the player's hero; 勇者たち "heroes" | Brave |
| シルフィ | Sylphy | | the King's fairy aide and the player's guide; bubbly, says "you know!" | Sylphie / Silphy |
| 王様 / ロスティア王 | King / Majesty / ruler / throne | | King of Lostia; old-man speech じゃ/のう -> "eh?", "my boy", grand and fussy. When the hero (any gender) takes the crown: "ruler" / "on the throne", never "King" | |
| ザガン | Zagan | | the demon lord, revived | |
| ダール | Dahl | | the dark source that revived Zagan | |
| ラター | Ratar | | the celestial power that shields the world; ラター様 Ratar-sama | |
| ルナ | Luna | | legendary heroine, Tira's ancestor | |
| バード | Bard | | legendary hero, Duke's ancestor | |
| ティラ | Tira | | hero: gentle, Luna's descendant | |
| デューク | Duke | | hero: hot-blooded swordsman, Bard's descendant | |
| コジロー | Kojiro | | hero: wandering swordsman, samurai talk | |
| チャーミー | Charmy | | hero: sheltered rich girl, runaway | |
| ギミック | Gimmick | | hero: Tinnian prince with a tin heart | |
| チンク | Chinku | | hero: Usamee girl (D10: not "Chink") | Chink |
| ゼファー | Zephyr | | hero: half-demon prince | |
| ガン | Gan | | hero: young Dogfolk adventurer, ends lines with ワン -> "arf!" | Gun |
| ゴッチ | Gotch | | hero: young Dwarf warrior | |
| ターニャ | Tanya | | hero: wandering mercenary woman | |
| グルートス | Grutos | | hero: proud Beast king | |
| ニャギー | Nyaggy | | hero: drifter, "he is the wind" | |
| コジマ | Kojima | | self-styled most beautiful lady thief | |
| ピココ | Pikoko | | shopkeepers (a cat-like race): ピココショップ Pikoko Shop; speech tics でしゅ/っしゅ/にゃ -> lisp "-sh" and "meow" | |
| べろりんQ | Berorin Q | | dice-rolling yokai of event squares, なのだ -> ", yes indeedy!" | |
| 遠見のつかさ / 遠見のじい | Farseer | | keeper of the far-seeing crystal; 遠見のじい "the old Farseer" | |
| ポップ | Pop | | | |
| モンティ | Monty | | | |
| トーク | Torque | | | |
| ヴィッキー | Vicky | | | |
| ベンケー | Benkei | | | |
| ウィズー | Wizoo | | | |
| タケル | Takeru | | | |
| デッガー | Degger | | | |
| ハンターエルフ | Hunter Elf | | | |
| ネクロマンサー | Necromancer | | | |
| ゴーゴン | Gorgon | | | |
| ミノタウロス | Minotaur | | | |
| ケルベロス | Cerberus | | | |
| バルバル | Barbar | | recruit | Barbal |
| ドラーラ | Drara | | recruit | |
| ラスター | Luster | | recruit | |
| ルドルフ | Rudolf | | recruit | |
| ユージー | Yuji | | recruit | |
| ベイオルフ | Beowulf | | recruit | |
| ペルセス | Perseus | | | |
| イリス | Iris | | | |
| マリー | Marie | | | |
| 長老 | Elder | | | |

## Foes and groups
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 魔王 | Demon Lord | | Zagan's title; case by sentence position | |
| 4天王 | Big Four | | Zagan's four generals | Four Heavenly Kings |
| 闇の騎士団 | Dark Knights | | | Knights of Darkness |
| しんえい騎士団 | Royal Guard | | ザガンしんえい騎士団 Zagan's Royal Guard | Royal Knights |
| いにしえの魔物 | Ancient Fiend | | | |
| ダリオロス | Darioros | | | Dariolos |
| オスロー | Oslo | | オスローのつえ Oslo Staff | Oslow |
| ミノスガーダー | Minos Guard | | | Minos Guarder |
| ウィングガーダー | Wing Guard | | | Wing Guarder |
| グニングル | Guningle | | | Gningle / Gningul |
| ケルベニアン | Kerbenian | | | Cerbenian |
| グロス | Gros | | | |
| ゲルドナ | Geldona | | | |
| グルフレグ | Grufreg | | | Gulfreg |
| ビザーレ | Bizarre | | ビザーレはくしゃく Count Bizarre | |
| ディープブル | Deep Bull | | | |

## Races
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| ウサミー | Usamee | | rabbit folk of the plains | |
| にんげん / 人間 | Human | | | |
| エルフィン | Elfin | | | |
| ドワーフ | Dwarf | | | |
| ニャンキー | Nyankee | | cat folk | |
| ブリキニアン | Tinnian | | tin folk (ブリキ = tin) | Brikinian |
| まぞく / 魔族 | Demon | | the race; "Demonkin" also passes (labels have 6 cells) | |
| イヌぞく / イヌ族 | Dogfolk | | | |
| ビースト | Beast | | | |
| エルフ | Elf | | | |

## Places
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| ロスティア | Lostia | | the kingdom; ロスティア城 Lostia Castle | |
| ハズレー | Duddley | | ハズレ = a dud: keep the joke | Hazley |
| 天界 | Heaven | | the celestial realm Zagan marches on | |
| 魔界 | Demon World | | | |
| タシュール | Tashur | | タシュール遺跡 Tashur Ruins | |
| アルセンガルド | Arsengard | | | |
| タイタニア | Titania | | | |
| ペリル | Peril | | | |
| ウィルダ | Wilda | | | |
| ミノス | Minos | | | |
| リレイア | Releia | | | |
| アルディア | Ardia | | | |
| フォート | Fort | | フォートのとりで the Fort stronghold | |
| アストロン | Astron | | アストロン神殿 Temple of Astron | |
| アステア | Astea | | | |
| ハーディス | Hardis | | | |
| ふういんの洞窟 | Sealed Cave | | | |
| ワープゾーン | Warp Zone | | | |
| ブリキランド | Tinland | | | |

## Items / systems / terms
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| シリング | Shilling | | currency; "500 Shillings" | |
| オーブ | Orb | | item class | |
| クエスト | Quest | | | |
| ポイント | point | | | |
| モンスター | monster | | | |
| 仲間 | ally / allies / party / companion / friend / member | | | |
| 1回やすみ | Lose 1 turn | | board-game penalty; keep exactly | |
| ピココショップ | Pikoko Shop | | | |
| 出前道具屋 | Traveling Item Shop | | | |
| 出前武器屋 | Traveling Weapon Shop | | | |
| 攻撃力 | Attack | | stat | |
| 防御力 | Defense | | stat | |
| クリスタル | crystal | | | |
| ハニワ | Haniwa | | | |
| おうけのたて | Royal Shield | | as in name_equip | |
| けっとうオーブ | Duel Orb | | | |
| サラリーオーブ | Salary Orb | | | |
| バイバイオーブ | Bye-Bye Orb | | | |
| ワープオーブ | Warp Orb | | | |

## Decisions from earlier batches
- D11: 勇者様 is plain "Hero", never "Sir Hero" (341 rows, phase 6 terms pass).
- D12: the hero taking the throne is "ruler" / "on the throne", never "King"; katakana robots speak in ALL CAPS (phase 6 review).
- Voice tics are Important, not Minor: old men じゃ/のう/ぞい -> "eh", "mark me", "mind you"; ladies' かしら/わ -> "would you mind", "dear", "I wonder"; Pikoko's っしゅ/でし -> "-sh", "yesh" (never glued to a `{sub}`).
