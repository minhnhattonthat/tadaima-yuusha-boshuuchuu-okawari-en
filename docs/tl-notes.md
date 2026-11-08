# Translator reports, wave 1 (2026-11-08)

What the 8 translator agents flagged; work through it in the terms pass and the review. Batches: `work/tl/bNNN.tsv` (regenerate
with `tools/batches.py split` only for new text; the merged English is in `script/`).

## Term drift between agents (pick one, add to glossary.md, fix the losing lines one by one)
- Monsters: ダリオロス Darioros / Dariolos; オスロー Oslo / Oslow; ミノスガーダー Minos Guard / Minos Guarder; ウィングガーダー Wing Guard / Wing Guarder;
  グニングル Gningle / Guningle / Gningul; ケルベニアン Kerbenian / Cerbenian; グロス Gros; ゲルドナ Geldona; グルフレグ Grufreg / Gulfreg;
  ビザーレ(はくしゃく) Bizarre / Count Bizarre; ディープブル Deep Bull.
- Recruits: バルバル Barbar / Barbal; ドラーラ Drara; ラスター Luster; ルドルフ Rudolf; ユージー Yuji; ベイオルフ Beowulf.
- Groups: 4天王 Big Four / Four Heavenly Kings; 闇の騎士団 Dark Knights / Knights of Darkness; ザガンしんえい騎士団 Zagan's Royal Knights / Royal Guard;
  魔道軍団 / 精霊軍団 Corps / Legion; いにしえの魔物 Ancient Fiend / the ancient fiend; 魔王 Demon Lord / demon lord.
- Other: ガーン "SHOCK!" / "KA-BONG!"; 長老 Elder; おねーさん "Young Lady"; ふういんの洞窟 Sealed Cave; ワープゾーン Warp Zone; NVP kept as NVP
  (spelled out once, d758.01BA "Name Value Points"); ブリキランド Tinland; ペルセス Perseus; イリス Iris; マリー Marie; ミッテイ Spy.
- Item names in dialogue vs `name_*.tsv`: おうけのたて (equip185), けっとうオーブ Duel Orb, サラリーオーブ Salary Orb, バイバイオーブ Bye-Bye Orb,
  ワープオーブ Warp Orb; spell family: Glint/Glintra, Ooze/Oozera, Blaze/Blazera, Brrr/Brrrra, Swish/Swishra, Wham/Whamra, Pep/Pep-Pep.

## Questions raised
- 勇者様 "Sir Hero" is gendered and the hero may be female: agents used "my friend", "themself", "ruler" (国王). Decide a neutral form
  (e.g. "great Hero"/"honored Hero") and record it as a decision before the review, or keep D9.
- Rows whose JP starts with junk bytes (extraction may start early, and insertion may blank real data): s217.0930, s226.0929,
  s226.0780, s225.05F6, s227.05F6. Agents dropped the junk. Check the bytes before the polish pass.
- 04B492 job/sex words: 男/女 get one 16 px cell each; no English word fits. Engine or a ruling (e.g. "M"/"F" as last resort).
- e234.1281 " obtained!" assumes the item name is drawn just before; e236.047E/04BA run into e236.0549: check in-game.
- s212/s213 monster + LV rows: JP spaces line up "LV"; the VWF won't line up with plain spaces (use `{cell}`?).
- Katakana-only speech (Tinnians, robots, golems): ALL CAPS for robots, mixed case for monsters; agree one rule in review.
- Hero battle cries 058017-058980 and idle lines e235.*: speaker per slot guessed from voice.

## Resolved in the terms pass and review (2026-11-08)
- Drift list: ruled in `glossary.md` (not ruled: 魔道/精霊軍団 Corps/Legion, ガーン, おねーさん, ミッテイ, spell families - reviewers saw them, Minors in `docs/polish.md`).
- 勇者様: D11, plain "Hero". Junk-byte rows: extractor fix, the rows now start at their text (`docs/status.md`).
- Still open for phase 7/8: 04B492 男/女 cell, e234.1281 / e236.047E in-game, s212/s213 LV alignment, robot ALL CAPS rule.
