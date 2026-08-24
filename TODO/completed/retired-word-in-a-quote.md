# A retired word inside a quoted ruling forces a whole-file exemption

```
Status:   open
Progress: 5 of 5 tasks done
Owner:    systems
Requires-Roy: false
Raised:   2026-08-23 (2026-08-23, restoring six quotations a mechanical rename had
          rewritten)
Ruled:    2026-08-23 -- Roy ruled it twice the same day and the second ruling stands:
          a quotation is NOT an exemption, history leaves the shipped code, and the
          gate goes strict. `folio` joined RETIRED and no file is exempt.
Closed:   2026-08-23 -- every task here is settled. `check_vocabulary.py` reports
          '8 retired words, 0 uses in the shipped tree', exit 0. Ready for `complete`.
```

## Objective

**A retired word inside a quoted ruling forced a whole-file exemption -- and the collision was
resolved by removing the history rather than by exempting anything.**

!! **THE TWO RULES THAT COLLIDED, AND BOTH WERE ROY'S.** `CLAUDE.md`: *"When a ruling is quoted
here, quote all of it"* -- changing a word inside a quotation is worse than shortening one,
because nothing marks the edit. And Roy, 2026-08-19, on the vocabulary gate: a file carrying the
marker is *"EXEMPT WHOLE"*, because exempting a LINE would let a retired word creep back into a
file about the current representation *"one suppression at a time."*

! **MEASURED 2026-08-23: the mechanical rename rewrote SIX quotations across five shipped
modules** -- `addresser.py`, `lexer.py`, `page.py`, `galley.py`, `compositor.py` -- and every
gate stayed green. Only reading them caught it. The sharpest was a SUPERSEDED ruling quoted as
saying `path@cue`, a word ruled three days after the ruling was made. They were restored at
`2f9ee2c`, and 32 more at `b048c72`.

!! **RULING ONE, `0d53a8a`: a quoted span is exempt only where no agent reads it.** Roy: *"Yes, a
quoted span is exempt -- add folio to RETIRED"*, narrowed to *"the specific doc files that could
have old references"*, with *"strict no mistakes even quoted in the agents files."* Measured
there: of the 31 `foli*` uses left in the shipped tree, ZERO were in `agents/`, `SKILL.md` or
`references/`; all 31 were inside quotations in `scripts/*.py`.

!! **RULING TWO, `8141b7a`, LATER THE SAME DAY, AND IT SUPERSEDES THE FIRST.** Roy: *"It simply
isn't necessary to know the history to understand the code. It is a bad habit to think it needs
it."* The quotations came out of the shipped code, the exemption came out of the gate, and what
survives is the rule and the reason -- both checkable against the code in front of the reader.
! A pointer to a decision-log entry is not a way round it: Roy, on the first attempt, *"Making a
link referencing the change is just prose history laundering."*

**WHAT SHIPS NOW, verified 2026-08-23:**

- `scripts/check_vocabulary.py:63-67` holds `folio`, `folios`, `foliation`, `foliator`,
  `foliate` in `RETIRED`, with the reason beside them.
- `uv run python scripts/check_vocabulary.py` exits 0 and prints
  *"8 retired words, 0 uses in the shipped tree"* -- so no file needed the whole-file exemption
  this TODO was raised about.
- `tests/test_vocabulary.py:241-294` holds the gate to it: a quoted ruling fails like any other
  use, `portfolio` does not, and `cv` carries no `QUOTED` or `AGENT_FACING` attribute.
- `docs/vocabulary.md:49` records `folio -> cue` with the error it shipped as a DEFINITION.

! **THE CREEP ARGUMENT WAS ANSWERED BY NOT NEEDING AN EXEMPTION AT ALL.** The question this file
asked -- whether a quoted span is exempt, given the repo already marks quotes one way as
`*"..."*` -- has no live remainder: there is nothing left to exempt.

## Tasks

- [x] T1 -- The two rules that collide, both Roy's. A RULING already made, kept as
      the record of why the question was hard; it is not work anyone can finish.
      Moved into the Objective.
- [x] T2 -- SUPERSEDED. `folio` DID join `RETIRED` -- `check_vocabulary.py:63-67`
      -- and the five modules named here were NOT exempted whole. The premise that
      it could not join as things stood was overtaken the same day by `0d53a8a`
      and then `8141b7a`.
- [x] T3 -- FINISHED. The ruling owed arrived: `8141b7a`, Roy, 2026-08-23 -- a
      quotation is NOT an exemption, because history is not needed to understand
      the code and quotation marks do not stop a dead term reaching an LLM's
      attention. The gate carries no quote rule and
      `tests/test_vocabulary.py:278-281` asserts it never grows one.
- [x] T4 -- SUPERSEDED. This recorded that `RETIRED` was left UNCHANGED so nothing
      was weakened, at the cost of `folio` being unpoliced. Both halves are gone:
      the family is retired and the gate reports 0 uses across the shipped tree.
- [x] T5 -- A MEASUREMENT, not a task -- six quotations rewritten across five files
      with every gate green. Kept in the Objective, because it is the evidence that
      a mechanical rename can pass every check and still change what someone said.
