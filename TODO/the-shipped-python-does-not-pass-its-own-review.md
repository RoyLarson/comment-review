# The shipped Python's comments say what the code does NOT do

```
Status:   in-progress
Progress: 7 of 12 tasks done
Owner:    backend
Requires-Roy: true
Raised:   2026-08-16 (Roy, on `census.py`: "this creates the pCST and that is it.
          Comments about 'cannot answer OWNERSHIP' are not helpful.")
Triaged:  2026-08-23 -- the eighth box held Roy's 2026-08-18 ruling striking the hand-pass
          rule; a ruling already made is not a task, so it is ticked and stated in the
          Objective. Two real tasks remain
Split:    2026-08-23 -- every box cut to two lines; the two open boxes became four, one
          artifact per task, and what the ticked boxes said is in the Objective
Split:    2026-08-24 -- second pass, eleven boxes to twelve. RUN and GRADE were two verbs
          in one box and are now two boxes; the file list and the instruction-vs-definition
          rule moved to *What the shipped MARKDOWN still owes*
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

## !! THE RESIDUE TEST -- established before anything was rewritten

**A negative STAYS** when it names an OUTPUT (*"reports UNPROVABLE rather than passing"*) or is a
refusal aimed at whoever edits next. **It GOES** when it only distinguishes this thing from
another (*"it is NOT stage 8's proof pass"*), hedges, or answers a question nobody asked.

! **A negative is not automatically wrong.** *"A file this cannot prove is REPORTED as
unprovable, never passed"* states a real behavior, and a refusal aimed at a future editor is
one of the four refusals the residue check protects. The work is to find the ones that only
compare, hedge, or pre-empt -- not to strip every `not`.

Roy's example: `census.py:351` -- *"cannot answer OWNERSHIP, so no block gets an owner and the
ownership-context..."*. **`census.py` builds the pCST. That is what it does.** What it cannot
answer is a fact about a tier, and where it is load-bearing it can be stated positively -- *what
IS recorded* rather than what is not.

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
one-line hedges became two-line statements of what the code produces. ! The point was never zero:
a target of zero would delete the legitimate refusals.

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

### What went with `census.py`, and the word that went with it

`census.py`'s two uses of **suppressed** went with the rest. `:80` (*"a real obituary is
suppressed because some library happens to define that name"*) and `:615` (*"it can only ever
suppress an obituary, never manufacture one"*) described a FAILURE -- a true finding silently
lost -- in a word that named a mechanism this system no longer has. Roy, 2026-08-16, ruling
`NOISE_FLOOR` out of `referrers.py`: *"Nothing gets suppressed... that form of suppressed will
also go."* ! `:149` referenced the brief's *"suppression list"* and was fixed with it, not here.

### RULED 2026-08-16 -- a script's output may state only what the script DID

Roy: *"the python files are mechanical runs, they should only have documentation about what they
are doing."* Two headers argued a rule at the reader instead -- `census.py` printed *"every
block. A block nobody mentions is a gap in the review"* and `verdicts.py` *"a block nobody
mentioned is a gap, not a pass"*. Both are now what they print: *"every block, numbered"* and
*"indices no reviewer accounted for"*.

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

## What the shipped MARKDOWN still owes, kept out of the boxes

**`plugins/**/*.md` is `SKILL.md`, `references/reviewer-brief.md` and the five agent files** --
the same nine tokens counted over the Python above have never been counted over the prose.

! **The residue test reads differently in an INSTRUCTION.** A prohibition is legitimate there --
telling a role what it must refuse is the point of the file. What is not legitimate is *"it is
NOT X"* used as a DEFINITION, which is the comparing form the test already removes from code.

## Tasks

- [x] T1 | FINISHED | unknown | T1 -- FINISHED. The residue test was established
      before anything was rewritten. It is stated in the Objective under *THE
      RESIDUE TEST*.
- [x] T2 | FINISHED | unknown | T2 -- FINISHED. `census.py` first, the file Roy
      named. Its module docstring and its tier-capability statements are now in
      positive form.
- [x] T3 | FINISHED | unknown | T3 -- FINISHED. `census.py`'s two uses of
      **suppressed** went with the rest; the word and the ruling behind it are
      in the Objective.
- [x] T4 | FINISHED | unknown | T4 -- FINISHED. Then `prove_unchanged.py`,
      `verdicts.py`, `run_context.py`, `referrers.py`.
- [x] T5 | FINISHED | unknown | T5 -- FINISHED. The measurement was re-run and
      both numbers are in the Objective's tables.
- [x] T6 | FINISHED | unknown | T6 -- FINISHED. RULED 2026-08-16: a script's
      OUTPUT may state only what the script did. The two headers that argued a
      rule are in the Objective.
- [x] T7 | FINISHED | unknown | T7 -- SUPERSEDED. Roy's 2026-08-18 ruling
      striking the hand-pass rule is stated under *THE RULING THAT SAYS WHAT
      CLOSES THIS FILE*, and the record stays.
- [?] T8 | T8 -- **Run the nine-token count over `plugins/**/*.md`.** Verify:
      the number and the command that produced it are both recorded in this
      file.
- [?] T9 | T9 -- **Rule each shipped-markdown hit against the residue test.**
      Verify: every survivor is named in this file as an output or as a refusal.
- [?] T10 | T10 -- **Run `/comment-review` over the shipped tree.** Verify: the
      run's reports are recorded under `evidence/`, naming the commit they were
      produced at.
- [?] T11 | T11 -- **Grade that run from the DIFF**, never from the run's own
      report. Verify: the recorded grade cites the diff hunks it was read from.
- [?] T12 | T12 -- **Re-measure the negative-prose count from that run's
      result** rather than asserting it. Verify: the new number is in this file
      and names the run it came from.
