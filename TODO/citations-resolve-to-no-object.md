# Find the four commit citations that resolve to no object

```
Status:   open
Progress: 0 of 1 tasks closed
Owner:    systems
Requires-Roy: false
Raised:   2026-09-02 (systems)
```

## Objective

Four shas cited in this tree's prose name no object in this repository, and
unlike the rest of the orphans they cannot be resolved by translation.

!! **THE 2026-08-23 HISTORY REWRITE IS NOT WHAT BROKE THESE.** It renamed 745
commits and dropped 7, and `.git/filter-repo/commit-map` still maps every one
of the 745 -- which is how the citations repaired on 2026-09-02 were recovered.
**These four are in neither set**, so they were never commits here: they were
mistyped or invented, most likely by the two repair sweeps themselves. `f11374d`
*"fix: every commit citation in this tree resolves again"* is measurably one
source -- `git log -S 4286833 -- docs/plans/` returns that commit alone, and
`4286833` resolves nowhere.

! **A SWAP CANNOT FIX THEM, which is why they are filed rather than repaired.**
The 2026-09-02 pass swapped every citation that had a known replacement; these
have none, so each needs its work re-identified from the surrounding sentence,
or the sentence reworded to name the work instead of a sha.

!! **AND THE MAP THAT RECOVERED THE OTHERS LIVES ONLY IN ONE CLONE.**
`.git/filter-repo/commit-map` is not pushed and not shared. A fresh clone cannot
resolve a pre-rewrite sha at all, so a citation orphaned by that rewrite and not
yet repaired is unrecoverable everywhere except the machine that ran it.

! **A stale hash reads exactly like a good one until someone runs it** --
`the-harness-cannot-run-the-system-it-grades` records the same finding, and its
`T42` tracks the repair on the harness branch.

## Tasks

- [ ] T1 | Find what the four unresolvable shas named
        > 2026-09-02 0599091 -- the-bridge-landed-and-the-rewrite-did-not.md
        > 2026-09-02 1015469 -- completed/verdicts-py-announces-one-subject.md
        > 2026-09-02 5975890 and 7559969 -- TODO/README.md
        > 2026-09-02 None is in the 2026-08-23 rewrite map, nor among its 7 drops
        > 2026-09-02 So none was ever a commit here; a swap cannot fix them
        > 2026-09-02 Verify: cat-file -t answers commit, or the prose names the work
