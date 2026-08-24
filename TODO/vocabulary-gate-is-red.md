# The vocabulary gate is green, and the test that would hold it there does not exist

```
Status:   open
Progress: 2 of 5 tasks done
Owner:    systems
Requires-Roy: false
Raised:   2026-08-20 (both reviews of 2026-08-20; verified in-session)
Fixed:    2026-08-20 -- the gate exits 0. Roy ruled the direction: the four roles KEEP
          'original' because it is a purposeful definition, and the brief now states it
          (nothing is written to disk before 7b, so what a reviewer opens at stage 4 is
          the original). The four also gained 'page', which the envelope introduced
Re-verified: 2026-08-23 -- `uv run python scripts/check_vocabulary.py` exits 0: 0 holes,
          0 defined twice, 6 roles 0 drifted, 8 retired words 0 uses. The title is
          corrected -- the gate is GREEN and unheld. Two defects survive and a third is
          added
```

## Objective

**The gate passes and nothing keeps it passing.** `tests/test_vocabulary.py` asserts two of the
four checks `check_vocabulary.main()` runs, so the suite can be green while the gate is red -- as
it was on 2026-08-20, and as nothing in the tree would notice again.

!! **VERIFIED 2026-08-20, FIXED THE SAME DAY.** `uv run python scripts/check_vocabulary.py` EXITED
1: four roles -- `block-context`, `function-context`, `module-context`, `ownership-context` --
were handed the term `original`, which their own text never used
(`references/vocabulary.toml:128,164,201,240`). Branch-introduced: 1 occurrence at `3e1fedf`, 5 at
HEAD. Roy ruled the four KEEP `original` and the brief now states why.

!! **AND IT WAS REPORTED AS PASSING THREE TIMES WHILE IT WAS RED** -- in the commit messages for
`4d576d3` and others, 2026-08-20 -- because the run was piped through `tail -2`, the last line was
read, and `$?` was never checked. **The commit messages are wrong where they say `vocabulary gate
0`**, and they are not being rewritten: this is the record of the error, which is why the tests
below are the answer rather than more care.

!! **THE GATE ALSO BOUGHT ITS GREEN ONCE BY BENDING THE SUBJECT.** `check_vocabulary.py:124-143`
records it: `block` is polysemous and only the NOUN meaning *paragraph* was retired, but the verb,
a Python code block and a Java text block are current English and current terms of art. Undeclared,
the gate flagged all four, and the rename that followed replaced the LIVE senses instead of the
dead one -- `SKILL.md`'s verdict table read *"it PARAGRAPHS every other verdict"*, the
`block-context` agent was told its own role was `PARAGRAPH-CONTEXT`, and `prove_unchanged`
described *"a Java text PARAGRAPH"*, a language feature that does not exist. Five sites, filed as
`the-rename-corrupted-live-prose`. The four senses were declared in `NOT_THE_TERM` on 2026-08-23
and the gate has been green since.

! **This is `docs/gates.md`'s rule from the other side**: the run was green because the SUBJECT was
bent to the check. A word with several senses needs each one declared, or the gate reads correct
prose as a defect and the cheapest way to satisfy it is to make the prose wrong.

## Tasks

- [x] T1 -- FINISHED 2026-08-20. This box held the VERIFIED measurement that the gate exited 1 on
      `original` drift across four roles. A measurement is not a task; it is in the Objective, and
      the fix it names landed the same day.

- [ ] T2 -- Assert `check_drift() == 0` in `tests/test_vocabulary.py`. VERIFIED 2026-08-23: the
      file asserts `check_duplicate(...) == 0` at `:161` and `check_retired() == 0` at `:197` and
      asserts nothing about `check_drift`, which `check_vocabulary.py:382` runs and which is the
      check that was red. `CLAUDE.md` requires this gate after any edit to an agent file or a
      reference. Verify: the new assertion fails on a `vocabulary.toml` that hands a role a term
      its text never uses, and passes on HEAD.

- [x] T3 -- SUPERSEDED. This box held the record of the gate being reported as passing three times
      on 2026-08-20 while it was red. It is reasoning kept so the error stays legible, not work --
      the commit messages are not being rewritten. Stated in the Objective.

- [ ] T4 -- The retired-word regex is blind to a retired word inside an identifier. VERIFIED
      2026-08-23 at `check_vocabulary.py:355`: `re.findall(rf"(?<![\w-]){word}(?![\w-])", hay,
      re.I)`. `_` is a `\w`, so `block_problem` (`desk.py:646`), `block_text` (`lexer.py:609`) and
      `as_block` (`desk.py:358`) -- all live -- are invisible, and the gate prints a false
      *"8 retired words, 0 uses in the shipped tree"*. ! The line number this file carried, `:88`,
      is stale. Verify: a test that the checker COUNTS a retired word in an identifier, written
      before the regex changes, plus whatever `NOT_THE_TERM` declarations the three live names then
      need.

- [ ] T5 -- `NOT_THE_TERM` carries a dead exemption. VERIFIED 2026-08-23: `block_matches` is
      listed at `check_vocabulary.py:147` and `grep -rc "block_matches" plugins/` matches nothing
      -- the function was renamed `paragraph_matches` and then retired (`lexer.py:202`, `:813`,
      `:846` all call it *"the retired `paragraph_matches`"*). ! An exemption nothing uses widens
      the hole T4 is about and no gate can see it, because `ruff` reads an unused import and an
      unused local, not a string in a tuple. Verify: `block_matches` is gone from `NOT_THE_TERM`
      and `uv run python scripts/check_vocabulary.py` still exits 0.
