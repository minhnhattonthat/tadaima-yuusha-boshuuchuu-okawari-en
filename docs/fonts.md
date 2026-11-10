# Fonts

Every font or glyph sheet the build reads ends up inside the released patch, so its licence must allow that. One row
per file; a font with no known licence doesn't go into a release.

| File | Source (URL, version) | Licence | Redistributable in a patch | Used for | Changes made |
|---|---|---|---|---|---|
| fonts/spleen-5x8.bdf | Spleen by Frederic Cambus, copied from battle-tycoon-flash-hiders-sfx-en; licence in fonts/spleen-LICENSE | BSD 2-Clause | yes, keep the copyright line in the release README | names on the tilemap path, a-z in block 001 | trimmed to proportional at build time, 1-px shadow added |
| fonts/TitanOne-Regular.ttf | Titan One by Rodrigo Fuenzalida, github.com/google/fonts `ofl/titanone` (fetched 2026-11-10); licence in fonts/TitanOne-OFL.txt | SIL OFL 1.1 | yes (only rendered pixels ship, never the font file) | title logo NOW / HEROES WANTED (`tools/logo_text.py` -> fonts/logo_text.txt) | rasterised without antialiasing, each glyph scaled to its box |
| fonts/vwf.txt | drawn for battle-zeque-den-en (same owner) | MIT, same as repo | yes | all text, VWF, 95 ASCII glyphs, 11 rows | none (`tools/font.py` adds the blank rows) |
