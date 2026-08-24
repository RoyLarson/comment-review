# addresser --check prints SHARED and exits 0

```
Status:   open
Progress: 0 of 3 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-21 (the /code-review xhigh of 2026-08-21, focused on the file-to-
          census route)
TRIAGED:  2026-08-23 — 2026-08-23, all three verified in place and all three STILL LIVE.
          `_check` still returns `1 if missing else 0` (addresser.py:1465) while SHARED
          is printed at :1438. The advice string at :1457-1458 still says *"cite the
          census index alongside the address for those"*, and record.py:679-681 says a
          slot has carried an address and NO index since 2026-08-18. record.entry_for
          still says *"`--check` is what reports it"* (record.py:754-755).
          !! AND THE DOCSTRING NOW DISAGREES WITH ITSELF: addresser.py:1408 reads
          *"SHARED IS NOW A FAULT TOO"* and the Returns block twelve lines later, at
          :1417-1419, reads *"A shared place does not fail the check -- it is a fact
          about the file"*. One of the two is the rule; nothing in the file says which.
          ! MEASURED 2026-08-23: the SHARED branch is UNEXERCISED in this tree --
          0 shared over 12,447 paragraphs in 28 Python files and 0 over 22,627 in 30
          neovim Lua files. So the defect is real in the code and cannot currently be
          reproduced from a run, which is why T1 is stated against the source and not
          against a fixture.
```

## Objective

addresser --check prints SHARED and exits 0.

`_check` gates only UNADDRESSED paragraphs. The measurement that raised this --
`SHARED lic.c@b0 <- 1-3 comment | 4-4 docstring` at exit 0 -- came from the file in
`two-paragraphs-one-address`, which is now in `TODO/completed/`, and addresser.py:1412-1414
records that *"the one shape that produced it is fixed"*.

!! **THAT DOES NOT CLOSE THIS, BECAUSE THE CODE STILL DECIDES.** The SHARED branch, its
advice string and the exit rule are all still in `_check`, and the docstring states BOTH
answers -- :1408 that a shared place is a fault, :1417-1419 that it is not. A rule stated
twice in opposite directions is a rule a reader cannot apply, and the run that would
settle it by observation no longer occurs.

## Tasks

- [ ] T1 -- MAKE `_check` AND ITS DOCSTRING STATE ONE RULE about a shared place.
      addresser.py:1408 says *"SHARED IS NOW A FAULT TOO"*; addresser.py:1417-1419
      says *"A shared place does not fail the check"*; addresser.py:1465 returns
      `1 if missing else 0`, which is the second. Verify: the docstring says one
      thing, the return agrees with it, and a test builds a two-paragraph gap and
      asserts the exit code -- so the branch has a caller again. ! MEASURED
      2026-08-23: 0 shared over 12,447 paragraphs (28 Python files) and 0 over
      22,627 (30 Lua files), so nothing in the tree exercises this today.
- [ ] T2 -- ITS ADVICE NAMES A DELETED FIELD. addresser.py:1457-1458 prints
      *"cite the census index alongside the address for those"*, and `record.slot`
      carries no index -- record.py:679-681: *"a slot has carried an ADDRESS and no
      index since 2026-08-18"*. Verify: no shipped file tells a reader to cite a
      census index.
- [ ] T3 -- record.entry_for:754-755 says *"`--check` is what reports it"*, which
      is true only for a human reading stdout: `_check` prints SHARED and returns 0,
      so nothing downstream can act on it. Verify: the sentence names what actually
      reports a shared place once T1 has settled what that is.
