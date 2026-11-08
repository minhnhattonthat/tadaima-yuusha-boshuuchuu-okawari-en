# Decisions

The user's rulings on scope, style and trade-offs, newest last. Read before asking the user anything; if a later
decision replaces one, mark the old one "replaced by D<n>" instead of deleting it. Binding term spellings live in
`glossary.md`; this file holds the why.

| # | Date | Question | Options offered | Decision and reason |
|---|---|---|---|---|
| D1 | 2026-11-07 | Honorifics and name order | keep (-san), drop; JP or Western order | Keep honorifics; Western name order (given name first). Owner's standing answer for one-shot runs. |
| D2 | 2026-11-07 | Romanization source for names | official art, earlier patch, Hepburn | Official English names where they exist, else an earlier fan patch, else Hepburn without macrons. No earlier patch found in phase 1 searches. |
| D3 | 2026-11-07 | Credits | stay Japanese, translate | English. |
| D4 | 2026-11-07 | Abbreviations | engine work first (default), abbreviate | Engine work first (skill default); abbreviate only as a flagged last resort. |
| D5 | 2026-11-07 | Graphics text left in Japanese | none (default), list | Translate all of it (titles, menus, banners, cards); leave the original Japanese logo only if it has no official English version. |
| D6 | 2026-11-07 | Specs and plans | need approval, pre-approved | Pre-approved: keep going through every checkpoint, no questions. |
| D7 | 2026-11-07 | Saves, memory cards, savestates | user supplies, none | None provided; build the debug tool as usual. |
| D8 | 2026-11-07 | Publishing | - | Never run `gh release create`, never change repo visibility. The run ends at a built and verified release zip. Pushing to main is pre-approved for this run. |
| D9 | 2026-11-08 | How D1 (keep honorifics) applies to titles | keep on every noun (Hero-san, King-sama); keep on names only | Controller's reading of D1 for a pre-approved run: honorifics stay on personal names (Ratar-sama, Sylphy-chan); on titles and common nouns they become English (勇者さん "Hero", 勇者様 "Sir Hero" (replaced by D11), 王様 "Your Majesty"), since "Hero-sama" reads as a mistake. |
| D10 | 2026-11-08 | The hero チンク: Hepburn gives "Chink", an English slur | Chink, Chinku, a new name | Chinku: Hepburn with the final vowel kept, close to the JP and not a slur. |
| D11 | 2026-11-08 | 勇者様 "Sir Hero" (D9) is gendered; the player's hero may be female (Tira, Charmy, Chinku, Tanya) | Sir Hero; great/honored Hero; plain Hero | Plain "Hero" (vocative, capitalised), 様's deference carried by the phrasing. Controller's call for the pre-approved run: gender-neutral, and shorter than "Sir Hero" so no line grows (341 rows changed). Replaces D9's "Sir Hero". |
