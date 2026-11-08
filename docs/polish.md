# Polish pass

Minor findings deferred to one pass before release (`references/translation.md` §Review). Each line gets ticked `[x]`:
fixed, or `waived: reason`. The release script refuses to run while any line is unticked.

- [ ] rect00A0DA, rect0499DB, rect04B871 - シリング as "Sh": these rects are copied to RAM with numbers patched in (rects.COPIED), 4-5 cells; last-resort abbreviation (D4). Engine fix: widen the copy, or draw the unit from a far rect.
- [ ] rect04B871 - まいつき as "/mo" (4 cells before the number); rect00A0DA まいつき as "Pay". Same engine fix.
- [ ] rect04B845 - けいけんち as "EXP" (6 cells): standard RPG term, check it reads well in the status screen.
