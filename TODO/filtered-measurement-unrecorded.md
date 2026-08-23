# The filtered-census measurement exists only in run history

```
Status:   open
Progress: 1 of 5 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-20 (Roy, 2026-08-20, correcting a claim that only size had been
          measured)
Unblocked: 2026-08-20 — not lost -- reproducible. Roy: 'we can always rerun it by
           checking out the 0.1.x tag and the 0.2.1 tag.' Requires-Roy cleared: nobody's
           history is needed, only a checkout. The seam is 771547e, so v0.1.6 -> v0.1.7
           isolates it in 11 commits where v0.1.6 -> v0.2.1 confounds it in 87.
```

## Objective

!! **THE COMPARISON THAT JUSTIFIES `--filtered` IS NOT WRITTEN DOWN, AND IT IS THE ONE THAT
MATTERS.** `--filtered` REMOVES information from the census a role reads. The only numbers in the
tree measure how much smaller that made the prompt -- 39% of the listing was repeated paths,
`--filtered` saved 61%. Those are the COST. The BENEFIT was measured and recorded nowhere.

Roy, 2026-08-20, on going from filtered to unfiltered: *"the agents got a lot more tokens and used
a lot more tokens on effectively the same level of output. They did miss a lot in the
difference."* And: *"unfortunate that I did not tell the agents to put their results in evidence
before the stuff in there."*

## It is not lost -- it is REPRODUCIBLE

Roy: *"we can always rerun it by checking out the 0.1.x tag and the 0.2.1 tag."* That is the
fixture model already ruled in
[`the-harness-cannot-run-the-system-it-grades`](the-harness-cannot-run-the-system-it-grades.md):
**a fixture is a CHECKOUT AT A HASH, this repo's own history included.**

!! **THE SEAM IS NARROWER THAN THE BRACKET.** The behaviour change is `771547e`,
*"feat(census)!: every interval between two lines of code is a block"*, 2026-08-17. It is first
released in **v0.1.7**, and the last release without it is **v0.1.6**:

| bracket | commits between | what it isolates |
| --- | ---: | --- |
| `v0.1.6` -> `v0.1.7` | **11** | the enumeration, nearly alone |
| `v0.1.7` -> `v0.2.1` | 76 | everything after it |
| `v0.1.6` -> `v0.2.1` | 87 | confounded |

! `census.py` goes 754 -> 854 lines across the narrow one.

! **The tags are ANNOTATED, so `git rev-parse v0.1.6` returns the TAG OBJECT.** Use `v0.1.6^{}`
wherever a commit is wanted -- the trap anyone re-deriving which code produced a measurement hits
first, and `CLAUDE.md` records it.

## What the re-run has to state

!! **"MISSED A LOT" NEEDS A DENOMINATOR.** A recall claim without one is the shape this repo
already retired: `acquittal rate` went because it was *"a measured quantity whose denominator no
site stated."* Say what was compared, over which files, and what a miss is counted against --
findings, planted hazards, or something else.

! **It is the baseline the PAGE must beat**, and the page claims to beat BOTH ends at once: more
information than filtered, fewer tokens than unfiltered, recall at least filtered. Roy: the page
is *"partially to get the best of both worlds."* Without the prior recorded there is nothing to
hold that to.

## Tasks

- [ ] !! RE-RUN IT ACROSS `v0.1.6^{}` -> `v0.1.7^{}`, the 11 commits that
      isolate `771547e` -- *"every interval between two lines of code is a
      block"*. ! Roy remembered it as a v0.1.0 -> v0.2.0 split and offered
      v0.1.x -> v0.2.1; that bracket holds 87 commits and confounds the
      variable. The narrow one is the experiment. Roy on the result: 'the agents
      got a lot more tokens and used a lot more tokens on effectively the same
      level of output. They did miss a lot in the difference.' ! And WRITE IT TO
      `evidence/` this time -- Roy: 'unfortunate that I did not tell the agents
      to put their results in evidence.'
- [ ] ! It is the justification for `--filtered`, which is the single most
      consequential thing about what a reviewer sees -- it REMOVES information
      from the census a role reads. The only numbers written down measure how much
      SMALLER it made the prompt: 39% of the listing was repeated paths,
      `--filtered` saved 61%. Those are the cost, not the benefit.
- [ ] State what was compared, over what, and what 'missed a lot' counts --
      findings, hazards, or something else. A recall claim with no denominator is
      the shape this repo already retired once, as `acquittal rate`.
- [ ] ! It is the baseline the PAGE has to beat, and the page claims to beat BOTH
      formats at once -- more information than filtered, fewer tokens than
      unfiltered. Without the prior recorded there is nothing to hold it to.
- [x] * RULING WANTED from Roy: where the runs are, or whether the comparison must
      be re-run. Only he has the history.
