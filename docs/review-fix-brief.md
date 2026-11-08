# Review-and-fix brief (one batch)

**Retired 2026-11-08** (phase 6 review): making the reviewer also write every Important fix, with a Minor cap, led
reviewers to file about 70 voice findings as Minor. For later reviews use the read-only `reviewer` agent type (or
`tools/review.py` with codex), no cap on Minors, and fix in a separate step. Kept for the record.

Used when no read-only reviewer can be run separately (codex out of credits, nested workers refused): a fresh agent that
did not translate the batch reviews it and drafts the fixes. The controller merges the fix file.

1. Read `docs/reviewer-brief.md` (the review rules and report format), `glossary.md`, `docs/style-reference.md`.
2. Review every entry in `work/qa/pairs/<batch>.txt` (`>> id | speaker | form limit | JP` then the current English).
   Read all of it, in passes if large.
3. Write the report, in the reviewer brief's format, to `work/qa/reviews/<batch>.md`. Minors: at most 15, one line
   each as `- [ ] id - note`.
4. For every Critical and Important finding, write the corrected English to `work/tl/fix_<batch>.tsv`: one line
   `id<TAB>full English row`. Start from the current English in the pairs file and change only what the finding needs;
   keep every control code; rows are often whole scenes, so copy the rest exactly. Check a row's line widths with
   `python -X utf8 tools/batches.py fit ID "English"`.
5. Run `python -X utf8 tools/batches.py fix work/tl/fix_<batch>.tsv --dry` until it prints `N rows OK`. Always
   `--dry`: the controller merges. Write no other file; never edit `script/`, the glossary or tools.
6. Reply with one line only: `<batch>: C critical, I important (fixed in fix file), M minor; Approved|Needs fixes`.
   If you had no Critical/Important, write no fix file.
