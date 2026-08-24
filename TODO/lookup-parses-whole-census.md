# Every address lookup parses the whole census, so query cost scales with the project

```
Status:   open
Progress: 4 of 10 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-23 (Roy, 2026-08-23: if we pulled on a BIG project and had to do this
          a lot that would add up fast, and each invocation is a separate run)
TRIAGED:  2026-08-23 — 2026-08-23. Tasks 1-3 are measurements: the 0.28 s lookup and its
          split, the linear-in-project-size extrapolation, and the finding that re-
          lexing is faster above ~14k lines but is NOT the fix because a fresh lex
          answers about the file AS IT IS NOW while the census answers about it AS THE
          REVIEWERS WERE GIVEN IT. Two things left -- the RULING in task 4 (shard the
          census per file, which changes the on-disk shape four consumers read) and task
          5, batching the lookups, which is independent of it and is where 0.17 s of
          every 0.28 s goes.
RE-CHECKED: 2026-08-23 — the one-address-per-invocation half of task 5 verified against
            the code: `addresser.py:1110-1126` declares `--anchor` and `--resolve` with
            no `nargs`, so each takes a single value and a second address is a second
            process.
```

## Objective

Every address lookup parses the whole census, so query cost scales with the project.

MEASURED 2026-08-23 on the 19 shipped scripts: producing the census costs 2.48 s once per
run; querying ONE address costs 0.28 s, of which 0.17 s is interpreter startup and 25 ms is
parsing a 5.5 MB census to answer about one file.

! **The cheap half and the ruled half are independent.** Batching (T5) needs no decision and
recovers the 0.17 s.

!! **THE RULING CAME BACK NEITHER WAY IT WAS ASKED, 2026-08-23.** T4 offered *shard the census
per file, or not* -- both answers about an on-disk SHAPE. Roy ruled the shape was never the
problem: **the census is a BINDER you ask, and making it the CLI is what forecloses asking
anything small.** A caller names its grain -- the whole census, one page, a subpart of a page --
and the chain stops as soon as the addresser can answer. `decision-log.md Addressing: #9`.

## Tasks

- [x] T1 -- MEASURED 2026-08-23 on the 19 shipped scripts (11,009 lines, 8,734
      paragraphs, 5.5 MB census). Produce the census: 2.48 s, once per run, fine.
      QUERY one address: 0.28 s -- 0.17 s interpreter startup, 25 ms census parse,
      ~0.09 s the addresser's own work. ! The addresser does NO page work: it
      imports `constants` and `exceptions` and nothing else, and its CLI reads the
      census JSON.
- [x] T2 -- !! THE COST IS LINEAR IN THE WHOLE PROJECT because every invocation
      parses the entire census to answer about one file. Extrapolated at 630
      bytes/paragraph: 100k lines -> ~50 MB, ~0.2 s per lookup; 500k lines -> ~250
      MB, ~1.1 s per lookup, plus reading 250 MB from disk every time.
- [x] T3 -- ! RE-LEXING IS FASTER ABOVE ~14k LINES AND IS NOT THE FIX. Building one
      page (987 lines) costs 31 ms, constant per file; the census parse is 25 ms
      today and crosses 31 ms at roughly a 7 MB census. ! But the census answers
      about the file AS THE REVIEWERS WERE GIVEN IT and a fresh lex answers about the
      file AS IT IS NOW -- which differ exactly when something changed mid-run,
      the case the census exists to catch. `addresser.py` states the dependency:
      the scheme *"rests entirely on the census being a HASHED STATIC TABLE --
      exact, constant, FULLY ENUMERATED."* Speed would be bought with staleness
      detection.
- [x] T4 -- RULED 2026-08-23, AND NEITHER WAY IT WAS ASKED. It offered SHARD or
      DO NOT, both of which change or keep an on-disk SHAPE. Roy ruled that the
      shape is not the problem: *"they shouldn't have to go through the whole
      census to get an address ... No parse everything"*, and then named the cause
      -- *"It is silly to make the census be the cli it breaks things like this
      option."* ! **`census.py` BEING the CLI is what forecloses stopping early**:
      if the only way to ask a question is to run the thing that builds
      everything, every question costs the whole project. The census is a BINDER
      you ask; the CLI is what asks it. Tasks T6-T9 are that ruling.
- [ ] T5 -- BATCH THE LOOKUPS. It is the cheap half and independent of the ruling:
      `addresser.py:1110-1126` declares `--anchor` and `--resolve` with no `nargs`,
      so each invocation answers ONE address and 0.17 s of every 0.28 s call is
      interpreter startup. Verify: one invocation answers N addresses, and N=10
      costs measurably less than 10 separate calls.
- [ ] T6 -- Give the binder a CLI that is not the census builder. It answers three
      grains -- the whole census, ONE page, or a subpart of one page -- so a
      caller states what it wants rather than taking everything. Verify: a command
      exists that returns one page without building the census for the other
      files, and `census.py --help` no longer advertises address lookup.
- [ ] T7 -- STOP THE CHAIN AT THE ANSWER. Roy: *"an intermediate cli that is able
      to run the chain of command to that point and once the addresser is able to
      answer the line number stops."* Verify: resolving one address in a 19-file
      scope reads fewer than 19 files, proven by counting reads rather than by
      timing.
- [ ] T8 -- SUBSTEP THE LEXER AND THE ADDRESSER so a lookup stops at the requested
      spot inside a file, not merely at the file. Roy: *"some refinements to this
      could also substep the lexer and the addresser until it gets to the requested
      spot and stops."* ! Depends on T7 and is the refinement, not the ruling.
      Verify: resolving an address near the top of a 987-line file lexes fewer
      lines than resolving one near the bottom.
- [ ] T9 -- HAND THE REVIEWERS THEIR RECORDS IN TWO STEPS. Roy: *"get the whole
      address list for the page then filter the records back down to hand to the
      reviewers."* ! The address list is cheap and total; the records are what
      cost, so the filter belongs AFTER the list rather than inside the walk.
      Verify: the page's full address list is produced by one call, and what
      reaches a reviewer is a filtered subset of it.
- [ ] T10 -- SAY WHAT HAPPENS WHEN THE EARLY CHAIN DISAGREES WITH THE CENSUS. T3
      measured the reason this is not free: the census answers about the file AS
      THE REVIEWERS WERE GIVEN IT, and anything that re-runs the chain answers
      about it AS IT IS NOW. Those differ exactly when a file changed mid-run --
      the case the census exists to catch -- so an early-stopping lookup needs a
      stated answer rather than an assumed one. Verify: the rule is written where
      `addresser.py` states the hashed-static-table dependency, and a test changes
      a file between census and lookup and asserts the stated behaviour.
