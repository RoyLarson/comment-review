# The shipped Python's comments say what the code does NOT do

```
Status:   in-progress
Progress: 7 of 9 tasks done
Owner:    backend
Requires-Roy: true
Raised:   2026-08-16 (Roy, on `census.py`: "this creates the pCST and that is it.
          Comments about 'cannot answer OWNERSHIP' are not helpful.")
Triaged:  2026-08-23 -- the eighth box held Roy's 2026-08-18 ruling striking the hand-pass
          rule; a ruling already made is not a task, so it is ticked and stated in the
          Objective. Two real tasks remain
```

## Objective

!! **The reason is not tidiness -- it is what the system learns from reading itself.** Roy,
2026-08-16: *"I don't want the system picking up bad cues from the documentation in the code."*
`CLAUDE.md` carries the same argument for vocabulary: an agent reads these files and then writes
in them, so the REGISTER is an instruction. A repo whose own scripts spend a fifth of their prose
on what the code does NOT do is demonstrating the shape its four editorial roles exist to remove.

**A comment should state what the code does.** These scripts stated what it does *not* do, what it
is *not*, and how it compares to other passes.

Measured over `plugins/**/*.py`, counting comment and docstring lines carrying `cannot` /
`never` / `does not` / `is not` / `nothing` / `neither` / `without` / `no longer` / `not a`:

| file | before 2026-08-16 | after that day's work |
| --- | ---: | ---: |
| `census.py` | 52 / 284 (18%) | 55 / 286 (19%) |
| `prove_unchanged.py` | 21 / 111 (19%) | 22 / 110 (20%) |
| `referrers.py` | 9 / 54 (17%) | 10 / 42 (24%) |
| `run_context.py` | 14 / 104 (13%) | 17 / 96 (18%) |
| `verdicts.py` | 27 / 161 (17%) | 28 / 144 (19%) |
| `vocabulary.py` | -- | 4 / 19 (21%) |
| **total** | **123 / 714 (17%)** | **136 / 697 (20%)** |

! **It went UP.** All five scripts were rewritten that day and the prose written with them carries
the same defect -- which is the argument for fixing it at the source rather than trusting a pass
to notice. The second column is the baseline the hand pass worked from.

## Result, 2026-08-16 -- the hand pass

| file | baseline | after the hand pass |
| --- | ---: | ---: |
| `annotate.py` | 4 / 35 | 2 / 37 |
| `census.py` | 55 / 286 | 2 / 206 |
| `prove_unchanged.py` | 22 / 110 | 12 / 116 |
| `referrers.py` | 10 / 42 | 6 / 49 |
| `repo.py` | 11 / 83 | 7 / 67 |
| `run_context.py` | 17 / 96 | 6 / 115 |
| `verdicts.py` | 28 / 144 | 16 / 165 |
| `vocabulary.py` | 4 / 19 | 0 / 23 |
| **total** | **136 / 697 (20%)** | **51 / 778 (6%)** |

! **The residue is deliberate.** Every survivor names an OUTPUT (*"REPORTED as unprovable"*), a
refusal aimed at the next editor (*"Exceptions are RAISED to the caller"*), or a state
distinction the code turns on (*"None is a THIRD state"*). The line count ROSE because several
one-line hedges became two-line statements of what the code produces.

! **The pass found more than register.** Six defects a rewording would have preserved:

| defect | where |
| --- | --- |
| three sites argued the DISPUTED `query`/EVIDENCE position as settled fact | `verdicts.py` |
| `"is not one of the eight"` -- there are seven verdicts | `verdicts.py` |
| `"the eleven questions this packet asks"` -- nine; `"the other eight are prose"` x2 -- six | `run_context.py` |
| `"the 3.9 floor this script promises"` -- the floor is 3.11 | `prove_unchanged.py` |
| `"the same rule as census.py's READ_ERRORS"` -- it moved to `repo.py` | `run_context.py` |
| `"the reading C1 exists to prevent"` -- a finding label from a session artifact a plugin user has no copy of | `referrers.py` |

! **The one count that had NOT drifted is the one a test guards** -- `test_run_context` asserts
the module docstring carries `len(REQUIRED)`. The three that drifted were in prose nothing
checked. The closing line now derives its number rather than carrying a copy.

Roy's example: `census.py:351` -- *"cannot answer OWNERSHIP, so no block gets an owner and the
ownership-context..."*. **`census.py` builds the pCST. That is what it does.** What it cannot
answer is a fact about a tier, and where it is load-bearing it can be stated positively -- *what
IS recorded* rather than what is not.

! **A negative is not automatically wrong.** *"A file this cannot prove is REPORTED as
unprovable, never passed"* states a real behavior, and a refusal aimed at a future editor is
one of the four refusals the residue check protects. The task is to find the ones that only
compare, hedge, or pre-empt -- not to strip every `not`.

## !! THE RULING THAT SAYS WHAT CLOSES THIS FILE

!! **STRUCK 2026-08-18 by Roy: the hand-pass rule goes, and this file closes on a RUN.** It read
*"Do not run `/comment-review` on this repo to do it ... This is a hand pass, and the eval harness
stays out of it"*, written 2026-08-16 while the skill was mid-rewrite across several branches.

!! **A hand pass produces a REWRITE, not a pass.** Roy, 2026-08-18: *"By definition the code has
to go through the review to state that it has passed."* This file's title is a claim about what
the review returns, and only the review can settle it -- every number in the two tables above was
produced by a person, which is the same gap
[`the-harness-cannot-run-the-system-it-grades`](the-harness-cannot-run-the-system-it-grades.md)
opens with: *"no measurement exists that a human did not perform."*

! **The reason the old rule was written has expired on one count and not the other.** The skill is
no longer mid-rewrite -- `v0.2.3` is cut, tagged and installed. Self-grading is still real, and is
answered by grading from the DIFF rather than from the run's own report, which is already this
repo's rule for every measured run.

! **The harness is NOT a precondition.** Running `/comment-review` over the shipped tree needs the
skill, not the harness; what the harness adds is the same run repeated with an assertion. Ruled
2026-08-18: harness work is not a release candidate and does not gate this.

## Tasks

- [x] T1 -- FINISHED. Establish the test before rewriting anything. A negative stays when it
      names an OUTPUT (*"reports UNPROVABLE rather than passing"*) or is a refusal aimed at
      whoever edits next. It goes when it only distinguishes this thing from another (*"it is
      NOT stage 8's proof pass"*), hedges, or answers a question nobody asked.

- [x] T2 -- FINISHED. `census.py` first -- 52 lines, the largest share, and the file Roy named.
      The module docstring now says it builds the pCST and what each output contains, and the
      tier-capability statements are in positive form.

- [x] T3 -- FINISHED. `census.py`'s two uses of **suppressed** went with the rest. `:80` (*"a real
      obituary is suppressed because some library happens to define that name"*) and `:615` (*"it
      can only ever suppress an obituary, never manufacture one"*) described a FAILURE -- a true
      finding silently lost -- in a word that named a mechanism this system no longer has. Roy,
      2026-08-16, ruling `NOISE_FLOOR` out of `referrers.py`: *"Nothing gets suppressed... that
      form of suppressed will also go."* ! `:149` referenced the brief's *"suppression list"* and
      was fixed with it, not here.

- [x] T4 -- FINISHED. Then `prove_unchanged.py`, `verdicts.py`, `run_context.py`, `referrers.py`.

- [x] T5 -- FINISHED. The measurement was re-run and both numbers are in the table above. The
      point was not zero -- a target of zero would delete the legitimate refusals.

- [x] T6 -- FINISHED. A script's output may state only what the script DID, ruled 2026-08-16. Roy:
      *"the python files are mechanical runs, they should only have documentation about what they
      are doing."* Two headers argued a rule at the reader instead -- `census.py` printed *"every
      block. A block nobody mentions is a gap in the review"* and `verdicts.py` *"a block nobody
      mentioned is a gap, not a pass"*. Both are now what they print: *"every block, numbered"*
      and *"indices no reviewer accounted for"*.

- [x] T7 -- SUPERSEDED. This box held Roy's 2026-08-18 ruling striking the hand-pass rule. A
      ruling already made carries no box; it is stated under *THE RULING THAT SAYS WHAT CLOSES
      THIS FILE* above and the record stays.

- [ ] T8 -- Check the same shape in the shipped MARKDOWN before deciding it is a Python problem.
      `SKILL.md`, `references/reviewer-brief.md` and the five files under
      `plugins/comment-review/agents/` are instructions, where prohibitions are legitimate -- but
      *"it is NOT X"* used as a DEFINITION is the same defect wherever it sits. Verify: the same
      nine-token count run over `plugins/**/*.md`, the number recorded here, and each survivor
      named against the test in T1.

- [ ] T9 -- **Run `/comment-review` over the shipped tree and record what it returns**, against
      the residue test in T1. Verify: the run's verdicts are graded from the DIFF, not from the
      run's own report, and the negative-prose count is re-measured from the result rather than
      asserted.
