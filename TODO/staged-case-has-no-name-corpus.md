# A staged case has no git, so every graded run gets a degraded name corpus

```
Status:   decision-needed
Progress: 0 of 4 tasks done
Owner:    testing
Requires-Roy: true
Raised:   2026-08-29 (2026-08-29, the first two-arm run -- both arms independently
          hedged on symbols)
```

## Objective

**MEASURED on the first two-arm run, 2026-08-29.** B2 stages a case's paths into a bare
directory. That directory is not a checkout, so `repo.tracked_paths` returns `None`,
`code_names` falls back to WALKING, and the census prints its own caveat:

```
NOT CHECKED -- these are gaps, not passes:
    name corpus built by WALKING the tree (not a git checkout, or git unavailable)
      -- untracked or vendored code may mask an obituary
    !! A file missing from the name corpus turns every symbol defined
      only there into a false obituary. Treat symbol notes as weaker
      until this list is empty.
```

!! **BOTH ARMS READ IT AND BOTH HEDGED, INDEPENDENTLY.** Neither was told to. `v0.1.6` filed
`query` on the module docstring's citations *"because the census self-reports its name corpus as
walked-not-tracked"*; `v0.2.2` filed `query` on the same paragraph, saying `clean` **would
certify it** and that the claim was neither confirmable nor refutable at one-file scope. **The
roles behaved correctly. The input was degraded.**

! **SO THE COST LANDS ON THE GRADE, NOT ON THE RUN.** A case whose answer key expects a tombstone
`correct` -- a symbol that exists nowhere -- scores a MISS, and the reason is the harness's rather
than the role's. Every such case is depressed by a constant nobody recorded.

!! **AND IT IS EXACTLY WHAT C1 EXISTS FOR.** The plan's C1 splits a result into MACHINERY
pass-or-void and EDITORIAL A-F, so *"a machinery defect reports VOID and never reaches the
grader"*. This is a machinery defect reaching the grader, found before C1 was built.

## The ruling this needs, and why it is not obvious

**A one-file case cannot have a complete name corpus.** The three candidate answers each give up
something different, which is why T1 is Roy's:

| answer | what it buys | what it costs |
| --- | --- | --- |
| the case's own files, in a real checkout | `tracked_paths` answers, no caveat | a symbol defined outside the case still reads DEAD -- the caveat was TRUE |
| the START tree entire | a real corpus, real liveness | the role can resolve what the case never handed it, and "leave everything else behind" is gone |
| accept the caveat | honest, costs nothing to build | every symbol-shaped case is ungradeable, and the bias must be recorded on each grade |

! **THE THIRD IS NOT A NULL OPTION.** The caveat is CORRECT information about a one-file corpus,
and both roles used it correctly. What is wrong is not the census -- it is scoring a role against
an answer key that assumed a corpus the run did not have.

## Related

- `the-harness-cannot-run-the-system-it-grades` -- C1's void/grade split is the mechanism T3 wants.
- `corpora-are-all-python` -- a fetched corpus IS a checkout, so a corpus-based case does not hit
  this. It is staged cases specifically.

## Tasks

- [ ] T1 -- * RULE what a case's name corpus IS: the case's own files, the START
      tree entire, or the caveat accepted as correct information. Verify: the
      answer is written into this file.
- [ ] T2 -- Make the staged tree answer `tracked_paths`, if T1 says it should.
      Verify: the census over a staged case prints no WALKED_TREE row.
- [ ] T3 -- Make this a VOID condition rather than a grade, if T1 leaves it
      degraded. Verify: a run whose census carries WALKED_TREE reports VOID and
      never reaches the grader.
- [ ] T4 -- Record the bias on any grade taken before T1 lands. Verify: each such
      result in `evidence/` names the caveat it ran under.
