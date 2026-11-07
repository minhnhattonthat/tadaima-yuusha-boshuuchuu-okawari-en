# Fonts

Every font or glyph sheet the build reads ends up inside the released patch, so its licence must allow that. One row
per file; a font with no known licence doesn't go into a release.

| File | Source (URL, version) | Licence | Redistributable in a patch | Used for | Changes made |
|---|---|---|---|---|---|
| fonts/vwf.txt | drawn for battle-zeque-den-en (same owner) | MIT, same as repo | yes | all text, VWF, 95 ASCII glyphs, 11 rows | none (`tools/font.py` adds the blank rows) |
