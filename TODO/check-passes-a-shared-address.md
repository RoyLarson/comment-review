# addresser --check prints SHARED and exits 0

```
Status:   open
Progress: 0 of 4 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-21 (the /code-review xhigh of 2026-08-21, focused on the file-to-
          census route)
TRIAGED:  2026-08-23 -- 2026-08-23, all three verified in place and all three STILL LIVE.
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
Split:    2026-08-23 -- the box settling the rule also demanded a test that builds a
          two-paragraph gap; the source and the test are two artifacts and are now two
          boxes, T1 and T2
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

! **The three sites, verbatim.** addresser.py:1408 says *"SHARED IS NOW A FAULT TOO"*;
addresser.py:1417-1419 says *"A shared place does not fail the check"*; addresser.py:1465 returns
`1 if missing else 0`, which is the second. ! MEASURED 2026-08-23: 0 shared over 12,447 paragraphs
(28 Python files) and 0 over 22,627 (30 Lua files), so nothing in the tree exercises this today --
which is why T2 asks for a test that builds the shape, giving the branch a caller again.

! **The advice names a deleted field.** addresser.py:1457-1458 prints *"cite the census index
alongside the address for those"*, and `record.slot` carries no index -- record.py:679-681:
*"a slot has carried an ADDRESS and no index since 2026-08-18"*.

! **And one more sentence depends on the ruling.** record.entry_for:754-755 says *"`--check` is
what reports it"*, which is true only for a human reading stdout: `_check` prints SHARED and
returns 0, so nothing downstream can act on it.

## Tasks

- [ ] T1 | T1 -- Make `_check`'s docstring and its return state ONE rule about a
      shared place. Verify: the docstring says one thing and `addresser.py:1465`
      agrees with it.
- [ ] T2 | T2 -- Add a test that builds a two-paragraph gap and asserts
      `--check`'s exit code. Verify: the test goes red when the exit rule T1
      settled is flipped.
- [ ] T3 | T3 -- Stop the advice at addresser.py:1457-1458 naming a deleted
      field. Verify: no shipped file tells a reader to cite a census index.
- [ ] T4 | T4 -- Make record.entry_for:754-755 name what actually reports a
      shared place. Verify: the sentence names the reporter T1 settled, not
      `--check` alone.
