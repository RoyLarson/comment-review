# Nine measurements in shipped prose no longer match the tree

```
Status:   open
Progress: 1 of 6 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-20 (the branch review of 2026-08-20)
DOGFOOD:  2026-08-23 -- Same cluster as docstrings-that-contradict-themselves. A stale
          COUNT in shipped prose is block-context's state case by name -- a claim about
          the tree that no longer holds. ! Fifteen-odd numbers across shipped prose is a
          graded run's output, not a hand pass, and the numbers are already known, so
          the run can be scored against them. The tasks below run and score the tool;
          they do not hand-correct the numbers.
Re-taken: 2026-08-23 -- the language count IS FIXED: `vocabulary.toml:34` reads 'Four of
          the eighteen', `desk.py:384` reads 'seventeen of the eighteen', and no test
          docstring says 'eleven languages'. Every other site is live and every line
          number in this file had moved; the inventory below is today's.
SPLIT:    2026-08-23 -- no box held two tasks; six boxes stay six. What moved is the
          reasoning inside them -- the corrected language count and the rule against
          hand-correcting first now sit in the Objective.
```

## Objective

**Measurements in shipped prose no longer match the tree, and the tool this repo ships is the
thing that finds them.** A stale count is a claim about the tree that no longer holds, which is
`block-context`'s state case. So this file is a SCORING KEY: the sites are known, so a run over
them can be graded rather than trusted.

! **ONE IS ALREADY CORRECTED, 2026-08-23, and it is the reason the rest are worth a graded run
rather than a sweep.** `census.py --languages` prints **18** rows; `vocabulary.toml:34` now reads
*"Four of the eighteen have no docstring practice at all -- sql, toml, ini, yaml"* and
`desk.py:384` *"seventeen of the eighteen languages"*. The tests that carried *"eleven
languages"* no longer do. `vocabulary.toml` is read by all four roles, and `grep -ri eleven
tests/` no longer returns a language claim in `test_cues.py`, `test_galley.py` or
`test_verdicts.py`.

!! **DO NOT HAND-CORRECT THE NUMBERS FIRST.** Correcting them destroys the only graded case
this repo has for the state class -- the run has to meet the sites while they are still wrong.

**THE INVENTORY, re-taken 2026-08-23. Each line is a site, the claim, and what re-derives it:**

| site | says | re-derive with |
| --- | --- | --- |
| `page.py:877` | *"105 blank lines -- 16 of 16 shipped scripts"* | `ls plugins/comment-review/skills/comment-review/scripts/*.py` -- 19 |
| `SKILL.md:410` | *"`census.py` over itself is 1,607 paragraphs, 118 of them prose"* | `census.py` over `census.py` |
| `verdicts.py:369` | the same figure, second copy | the same run |
| `addresser.py:1222` | *"12 such places in this repo's own 13 shipped scripts"* | `addresser.py --check`; the `a` series removed the stated cause |
| `census.py:476` | *"the 13 shipped scripts"* | the same `ls` -- 19 |
| `census.py:540` | *"15 shipped scripts"* -- a second count in the same file | the same `ls` -- 19 |
| `SKILL.md:936` | *"three of the seven reasons"* a galley refuses | `grep -n REFUSED galley.py` plus the one `CANNOT USE` -- 8 sites |
| `SKILL.md:346-348` | *"6,828 paragraphs: 397,685 -> 159,316"* | a filtered census over the same paths |
| `test_page.py:244` | the 16-of-16 figure again | the same `ls` |
| `test_cues.py:216` | cites `census.address` | `grep -n "def address" census.py` -- no such name |

! **Two of the ten are in `tests/`,** which a run over the shipped scripts does not reach. That
is the last task below, and it is a decision about the run's scope rather than a defect in the
prose. The second of the two cites `census.address`, which does not exist.

! **`SKILL.md:936` is not a plain stale count** -- the sentence's subject is that this section
*"was wrong about the set for two releases"*, so correcting the number without keeping the point
loses the reason the sentence exists.

! **Five shipped files hold the sites a run can reach**: `page.py`, `verdicts.py`,
`addresser.py`, `census.py` and `SKILL.md`.

## Tasks

- [x] T1 -- FINISHED. The language count is corrected everywhere it shipped --
      `vocabulary.toml:34`, `desk.py:384`, the tests. Kept in the Objective.
- [ ] T2 -- Freeze the inventory above as the SCORING KEY before the run. Verify: each row
      names its file:line, the claim verbatim, and a command runnable from the repo root.
- [ ] T3 -- Once v0.2.4 ships, run the shipped review over the five shipped files holding
      the inventory's sites. Verify: a run dir holds a record per role, naming those five.
- [ ] T4 -- Score that run against T2's key -- sites flagged, sites missed, and flags not
      in the key. Verify: the three numbers are written in this file, with the run named.
- [ ] T5 -- Apply what the run proposes and the human approves, through the normal stages.
      Verify: each key site matches its command's output, and `uv run pytest -q` is green.
- [ ] T6 -- Decide whether the dogfood run covers `tests/`, holding two of the ten sites.
      Verify: `tests/` is under review, or `grep -rn census.address tests/` is empty.
