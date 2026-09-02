# The filtered-census measurement exists only in run history

```
Status:   open
Progress: 3 of 5 tasks closed
Owner:    testing
Requires-Roy: false
Raised:   2026-08-20 (Roy, 2026-08-20, correcting a claim that only size had been
          measured)
Unblocked: 2026-08-20 — not lost -- reproducible. Roy: 'we can always rerun it by
           checking out the 0.1.x tag and the 0.2.1 tag.' Requires-Roy cleared: nobody's
           history is needed, only a checkout. The seam is d5ad782, so v0.1.6 -> v0.1.7
           isolates it in 11 commits where v0.1.6 -> v0.2.1 confounds it in 85.
Triaged:  2026-08-23 — commit counts RE-MEASURED with `git rev-list --count`: 11, 74 and
           85, where this file said 11, 76 and 87. The 11 is exact and is the number the
           experiment rests on. ! Also confirmed: `d5ad782` is an ancestor of `v0.1.7^{}`
           and NOT of `v0.1.6^{}`, and `census.py` is 754 lines at `v0.1.6^{}` against
           854 at `v0.1.7^{}`. ! `evidence/` still holds no filtered-vs-unfiltered
           comparison -- four directories, none of them this. ! Boxes 2 and 4 were
           statements of WHY the measurement matters, which nobody ticks; they are
           ticked here and restated in the Objective, per `CLAUDE.md`, *A box is a claim
           about whether work remains*.
Split:    2026-08-23 -- boxes cut to two lines each; the Roy quotations and the
           `evidence/` listing moved into the Objective
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

!! **IT IS THE JUSTIFICATION FOR THE SINGLE MOST CONSEQUENTIAL THING ABOUT WHAT A REVIEWER
SEES.** `census.py:510` names `--filtered` *"the command SKILL.md hands a reviewer"*, and the flag
removes information from the listing that reaches four role prompts. The recorded numbers say
only how much SMALLER it made the prompt.

!! **AND IT IS THE BASELINE THE PAGE MUST BEAT**, which the page claims to do at BOTH ends at
once: more information than filtered, fewer tokens than unfiltered, recall at least filtered.
Roy: the page is *"partially to get the best of both worlds."* Without the prior recorded there
is nothing to hold that to.

! **NEITHER ARM IS ON DISK.** MEASURED 2026-08-23: `evidence/` holds four directories --
`comment-review-skill-023-dev-review`, `cycle-0.2.3`, `ga`,
`rename-left-history-in-the-comments` -- and none of them is this.

## It is not lost -- it is REPRODUCIBLE

Roy: *"we can always rerun it by checking out the 0.1.x tag and the 0.2.1 tag."* That is the
fixture model already ruled in
[`the-harness-cannot-run-the-system-it-grades`](the-harness-cannot-run-the-system-it-grades.md):
**a fixture is a CHECKOUT AT A HASH, this repo's own history included.**

!! **THE SEAM IS NARROWER THAN THE BRACKET.** The behaviour change is `d5ad782`,
*"feat(census)!: every interval between two lines of code is a block"*, 2026-08-17. It is first
released in **v0.1.7**, and the last release without it is **v0.1.6** -- verified 2026-08-23 with
`git merge-base --is-ancestor`, which answers yes against `v0.1.7^{}` and no against `v0.1.6^{}`:

| bracket | commits between | what it isolates |
| --- | ---: | --- |
| `v0.1.6` -> `v0.1.7` | **11** | the enumeration, nearly alone |
| `v0.1.7` -> `v0.2.1` | 74 | everything after it |
| `v0.1.6` -> `v0.2.1` | 85 | confounded |

! `census.py` goes 754 -> 854 lines across the narrow one.

! **Roy remembered it as a v0.1.0 -> v0.2.0 split and offered v0.1.x -> v0.2.1.** That bracket
holds 85 commits and confounds the variable. **The narrow one is the experiment.**

! **The tags are ANNOTATED, so `git rev-parse v0.1.6` returns the TAG OBJECT.** Use `v0.1.6^{}`
wherever a commit is wanted -- the trap anyone re-deriving which code produced a measurement hits
first, and `CLAUDE.md` records it.

## What the re-run has to state

!! **"MISSED A LOT" NEEDS A DENOMINATOR.** A recall claim without one is the shape this repo
already retired: `acquittal rate` went because it was *"a measured quantity whose denominator no
site stated."* Say what was compared, over which files, and what a miss is counted against --
findings, planted hazards, or something else.

! **The standard the write-up has to meet**: a reader who ran NEITHER arm can say which arm won
and by how much.

## Tasks

- [ ] T1 | T1 -- Re-run the filtered/unfiltered comparison across the 11 commits
      `v0.1.6^{}` -> `v0.1.7^{}`. Verify: a new `evidence/` directory holds both
      arms and their commits.
- [x] T2 | FINISHED | unknown | T2 -- RECORD, not a task: the justification for
      `--filtered`, and why the recorded 39% and 61% are the cost rather than
      the benefit. Restated in the Objective.
- [ ] T3 | T3 -- State the denominator the recall claim needs, as set out in the
      Objective. Verify: the evidence README names a numerator, a denominator
      and the file set.
- [x] T4 | FINISHED | unknown | T4 -- RECORD, not a task: this is the baseline
      the PAGE has to beat, at both ends at once. Restated in the Objective.
- [x] T5 | FINISHED | unknown | T5 -- * RULING ALREADY MADE, and it is the
      `Unblocked:` line above: the comparison is re-run from a checkout rather
      than recovered. Restated in the Objective.
