# Nine measurements in shipped prose no longer match the tree

```
Status:   open
Progress: 0 of 6 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-20 (the branch review of 2026-08-20)
RE-CHECKED: 2026-08-23 — 2026-08-23, still live. census.py --languages lists 18 rows;
            vocabulary.toml:34 still reads 'five of the eleven' and is shipped to all
            four roles. Not triaged further -- every box here is real work (re-measure
            and edit shipped prose), not a record.
```

## Objective

Nine measurements in shipped prose no longer match the tree.

## Tasks

- [ ] `vocabulary.toml:34`, shipped to ALL FOUR roles: *"five of the ELEVEN offer
      none."* `census.py --languages` says 17. The branch split `c-family`/`js-
      family` per language; the numerator survived, the denominator did not. Same
      stale count in `desk.py:380` and four test docstrings.
- [ ] `page.py:610` says *"105 blank lines -- 16 of 16 shipped scripts"*. There
      are 15, and it was written IN THE COMMIT THAT DELETED `locator.py` -- never
      true. Re-taken: 0 such lines.
- [ ] `SKILL.md:409` and `verdicts.py:344-346`, the same figure in two files:
      *"`census.py` over itself is 1,607 paragraphs, 118 prose"*. Now 581 / 35.
      Its own commit message says it had *"rotted twice, in both places that
      record it"*.
- [ ] `addresser.py:758-760`: *"12 such places in this repo's own 13 shipped
      scripts"*, cause given as a docstring sharing a gap with the run beneath it.
      15 scripts; `--check` reports 0 shared; the `a` series removed that cause.
- [ ] `census.py:422` says *"the 13 shipped scripts"* and `census.py:476` says
      *"this repo's own 15"* -- two counts in one file. `SKILL.md:934-937` says
      *"three of the SEVEN reasons"* a galley refuses; `grep -n REFUSED galley.py`
      gives 5. `SKILL.md:346-348` cites `6,828 paragraphs: 397,685 -> 159,316`;
      now 7,375 / 646,337 / 163,921.
- [ ] In tests: `test_page.py:163-166` cites the 16-of-16 figure; *"eleven
      languages"* at `test_cues.py:269,745`, `test_galley.py:655`,
      `test_verdicts.py:1690`; `test_cues.py:215` cites `census.address`,
      which does not exist.
