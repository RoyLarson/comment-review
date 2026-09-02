# Every address lookup parses the whole census, so query cost scales with the project

```
Status:   open
Progress: 4 of 14 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-23 (Roy, 2026-08-23: if we pulled on a BIG project and had to do this
          a lot that would add up fast, and each invocation is a separate run)
TRIAGED:  2026-08-23 -- three boxes were measurements: the 0.28 s lookup and its
          split, the linear-in-project-size extrapolation, and the finding that re-
          lexing is faster above ~14k lines but is NOT the fix because a fresh lex
          answers about the file AS IT IS NOW while the census answers about it AS THE
          REVIEWERS WERE GIVEN IT. Two things left -- the RULING (shard the census per
          file, which changes the on-disk shape four consumers read) and batching the
          lookups, which is independent of it and is where 0.17 s of every 0.28 s goes.
RE-CHECKED: 2026-08-23 -- the one-address-per-invocation half of the batching box
            verified against the code: `addresser.py:1110-1126` declares `--anchor` and
            `--resolve` with no `nargs`, so each takes a single value and a second
            address is a second process.
SPLIT:    2026-08-23 -- one action per box. The five boxes written from the evening
          ruling became nine: the new CLI split from retiring `census.py`'s lookup, the
          lexer substep from the addresser substep, and writing the staleness rule from
          testing it. Every Roy quotation moved to the Objective verbatim.
RE-SPLIT: 2026-08-23 -- the ten boxes still over two lines were cut again. Roy's two
          steps to the reviewers -- the page's whole address list, then the records
          filtered from it -- are now two boxes; the rest duplicated the Objective.
```

## Objective

Every address lookup parses the whole census, so query cost scales with the project.

MEASURED 2026-08-23 on the 19 shipped scripts (11,009 lines, 8,734 paragraphs, 5.5 MB census).
Producing the census costs 2.48 s, once per run, and that is fine. QUERYING one address costs
0.28 s -- 0.17 s interpreter startup, 25 ms parsing the census, ~0.09 s the addresser's own work.
! The addresser does NO page work: it imports `constants` and `exceptions` and nothing else, and
its CLI reads the census JSON.

!! **THE COST IS LINEAR IN THE WHOLE PROJECT**, because every invocation parses the entire census
to answer about one file. Extrapolated at 630 bytes/paragraph: 100k lines -> ~50 MB and ~0.2 s per
lookup; 500k lines -> ~250 MB and ~1.1 s per lookup, plus reading 250 MB from disk every time.

! **RE-LEXING IS FASTER ABOVE ~14k LINES AND IS NOT THE FIX.** Building one page (987 lines) costs
31 ms, constant per file; the census parse is 25 ms today and crosses 31 ms at roughly a 7 MB
census. ! But the census answers about the file AS THE REVIEWERS WERE GIVEN IT and a fresh lex
answers about it AS IT IS NOW -- which differ exactly when something changed mid-run, the case the
census exists to catch. `addresser.py` states the dependency: the scheme *"rests entirely on the
census being a HASHED STATIC TABLE -- exact, constant, FULLY ENUMERATED."* Speed would be bought
with staleness detection.

! **The cheap half and the ruled half are independent.** Batching needs no decision and recovers
the 0.17 s.

!! **THE RULING CAME BACK NEITHER WAY IT WAS ASKED, 2026-08-23.** It was offered as *shard the
census per file, or do not* -- both answers about an on-disk SHAPE. Roy ruled the shape was never
the problem: *"they shouldn't have to go through the whole census to get an address ... No parse
everything"*, and then named the cause -- *"It is silly to make the census be the cli it breaks
things like this option."* **`census.py` BEING the CLI is what forecloses stopping early**: if the
only way to ask a question is to run the thing that builds everything, every question costs the
whole project. **The census is a BINDER you ask; the CLI is what asks it.** A caller names its
grain -- the whole census, one page, a subpart of a page -- and the chain stops as soon as the
addresser can answer. `decision-log.md Addressing: #9`.

### The rest of the ruling, verbatim

- **Stop at the answer.** Roy: *"an intermediate cli that is able to run the chain of command to
  that point and once the addresser is able to answer the line number stops."*
- **Then refine inside the file.** Roy: *"some refinements to this could also substep the lexer
  and the addresser until it gets to the requested spot and stops."* ! That is the refinement, not
  the ruling, and it depends on the chain stopping first.
- **Two steps to the reviewers.** Roy: *"get the whole address list for the page then filter the
  records back down to hand to the reviewers."* ! The address list is cheap and total; the records
  are what cost, so the filter belongs AFTER the list rather than inside the walk.

### What early stopping costs

The measurement above is the reason it is not free: anything that re-runs the chain answers about
the file AS IT IS NOW, and those two answers differ exactly when a file changed mid-run. An
early-stopping lookup therefore needs a STATED answer for the disagreement rather than an assumed
one, written where `addresser.py` states the hashed-static-table dependency.

## Tasks

- [ ] T1 | T1 -- Batch the lookups: `--anchor` and `--resolve` take one value
      each. Verify: one invocation answers N addresses, and N=10 costs less than
      10 calls.
- [ ] T2 | T2 -- Give the binder a CLI that is not the census builder. Verify: a
      command returns ONE page without building the other 18 files' pages.
- [ ] T3 | T3 -- Retire address lookup from the census builder once T2 lands.
      Verify: `census.py --help` no longer advertises address lookup.
- [ ] T4 | T4 -- Stop the chain as soon as the addresser can answer. Verify:
      resolving one address in a 19-file scope reads fewer than 19 files, reads
      counted.
- [ ] T5 | T5 -- Substep the LEXER so it stops at the requested spot inside a
      file. Verify: an address near the top of a 987-line file lexes fewer lines
      than a late one.
- [ ] T6 | T6 -- Substep the ADDRESSER so it stops walking at the requested
      place. Verify: resolving an early address builds fewer places than a late
      one.
- [ ] T7 | T7 -- Return the page's whole address list in ONE call. Verify: one
      invocation returns every address on a page, and builds no records.
- [ ] T8 | T8 -- Filter the reviewers' records from T7's list, not inside the
      walk. Verify: a reviewer gets a subset of the one-call list.
- [ ] T9 | T9 -- Write what happens when the early chain disagrees with the
      census, beside `addresser.py`'s hashed-static-table dependency. Verify:
      the rule is in that file.
- [ ] T10 | T10 -- Test the rule T9 states. Verify: a test changes a file
      between census and lookup and asserts the stated behaviour, and fails if
      the behaviour changes.
- [x] T11 | FINISHED | unknown | T11 -- MEASUREMENT, not a checkpoint. The 0.28
      s lookup and its split are in the Objective, with the tree they were taken
      on.
- [x] T12 | FINISHED | unknown | T12 -- MEASUREMENT, not a checkpoint. The
      linear-in-project-size extrapolation at 630 bytes/paragraph, out to 500k
      lines, is in the Objective.
- [x] T13 | FINISHED | unknown | T13 -- MEASUREMENT AND FINDING, not a
      checkpoint. Re-lexing is faster above ~14k lines and is NOT the fix. Both
      are in the Objective.
- [x] T14 | FINISHED | unknown | T14 -- RULED 2026-08-23, and neither way it was
      asked. In the Objective in full, with both Roy quotations.
