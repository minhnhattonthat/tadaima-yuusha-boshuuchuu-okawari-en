# Synopsis

Tadaima Yuusha Boshuuchuu Okawari ("Now Recruiting Heroes: Second Helping", Human, SNES 1994): a board-game RPG. Players
move heroes around a field map with dice; squares trigger events (traps, shops, inns, wandering adventurers who join, the
dice yokai Berorin Q), battles and quests. No guide or wiki covers the story in detail; this is built from the script.

## Setting and cast
- **Kingdom of Lostia**, ruled by the fussy old **King**. His aide **Sylphy**, a fairy girl, guides the players, explains
  maps and hands out gifts.
- **Zagan**, a legendary demon lord, is revived by the dark power of **Dahl** and marches on **Heaven** with an army of
  dark fiends. **Ratar-sama** is the celestial power holding the line; the **Farseer** watches through a crystal.
- A prophecy says the **Heroes** who once defeated Zagan will return when the world is in peril. The King sends word for
  their descendants.
- The 12 playable heroes (attract-mode bios, `story.tsv`): Tira (gentle, descendant of the heroine Luna), Duke (hot-blooded,
  descendant of the hero Bard), Kojiro (wandering samurai), Charmy (runaway rich girl), Gimmick (Tinnian prince with a tin
  heart), Chinku (Usamee rabbit girl), Zephyr (half-demon prince), Gan (Dogfolk, says "arf"), Gotch (young Dwarf warrior),
  Tanya (cool mercenary woman), Grutos (Beast king), Nyaggy (drifter).
- Recurring: Kojima (vain lady thief), the Pikoko shopkeepers (travelling item/weapon shops, lisping cat-folk), the elder
  of each region, rival adventurers who can be recruited (`name_char.tsv`, `party.tsv`).

## Structure
- **Scenario mode**: the King gives a map (region) with a quest; the heroes cross it, fight its boss (`boss.tsv`: each
  boss's challenge line), and the King announces the results and ranking at the castle (`clear.tsv`). Sylphy's guide
  pages introduce each region (Arsengard and others). Maps differ in length: a beginner map (~1 h), a training map, a
  level-up map.
- **Party mode / versus**: several players compete; ranking by Shillings and points; a tournament.
- Monsters and named enemies speak before battle (`talk.tsv`); defeated or freed characters may join (`party.tsv`, e.g. Pop,
  an elf boy avenging the Hunter Elf sisters; Monty, who grieves for Degger; Torque; Vicky).
- The final map ends with Zagan; the ending scroll says the Heroes and their friends, winners and losers alike, have
  become legend.

## Notes for translators
- Lines run in script order inside a block: read the neighbours; several rows are pieces of one box.
- A region, item or monster named in one batch is named the same everywhere: glossary first, then report new ones.
