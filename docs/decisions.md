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
