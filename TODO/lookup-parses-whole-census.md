# Every address lookup parses the whole census, so query cost scales with the project

```
Status:   decision-needed
Progress: 3 of 5 tasks done
Owner:    backend
Requires-Roy: true
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

! **The cheap half and the ruled half are independent.** Batching (task 5) needs no decision
and recovers the 0.17 s; sharding (task 4) is the only option that keeps the census's
contract, and it changes an on-disk shape four consumers read.

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
- [ ] T4 -- * RULING WANTED: SHARD THE CENSUS PER FILE, or not. It is the option
      that keeps the contract -- a lookup parses one file's shard, a few hundred KB
      whatever the project size, and it is still the authoritative table. Unruled
      because it changes the census's on-disk shape, which `--filtered`, `galley`,
      `verdicts` and `record` all read. Verify: the ruling is recorded in
      `docs/decision-log.md`.
- [ ] T5 -- BATCH THE LOOKUPS. It is the cheap half and independent of the ruling:
      `addresser.py:1110-1126` declares `--anchor` and `--resolve` with no `nargs`,
      so each invocation answers ONE address and 0.17 s of every 0.28 s call is
      interpreter startup. Verify: one invocation answers N addresses, and N=10
      costs measurably less than 10 separate calls.
