# The read-only contract is enforced by nothing, and four reviewers wrote files

```
Status:   in-progress
Progress: 2 of 7 tasks done
Owner:    agents
Requires-Roy: true
Raised:   2026-08-17 (the 0.2.0 builder run: the operating session noticed scratch
          files left in the run directory by the reviewers themselves)
Triaged:  2026-08-23 -- the contract has been RULED and narrowed in the brief, the
          opposite way from this file's recommendation. Nothing else landed: the agent
          files still carry no `tools:` key and nothing detects a stale census
SPLIT:    2026-08-23 -- the `tools:` box held ADDING the key and CHOOSING what it holds,
          and its Verify covered only the first; they are two boxes now. Two rulings had
          no Verify clause and have one. ! The Triaged note above names pre-split labels.
```

## Objective

**The brief's first rule is absolute and nothing MECHANICAL checks it.** `reviewer-brief.md:8-9`:
*"Do not edit, write or format the code. Not source, not comments, not docs, not a file you
opened to settle a claim. A reviewer that fixes what it finds has destroyed the finding."*

Measured on the builder run: all four reviewers left artifacts in the run directory --
`gen.py`, `blocks.json`, `part_*.md`, and a duplicate `census_prose.txt`. Nobody was told; the
operating session found them by looking.

! **AND THEY CANNOT BE RECOVERED.** Measured 2026-08-23: no `gen.py`, `blocks.json`, `part_*.md`
or `census_prose*` exists anywhere in the tree, and `git log --all --diff-filter=A` finds none
ever committed. The run directory was discarded with the run, so what survives is the
measurement above and not the ability to re-derive it.

! **The agents are granted every tool.** Verified 2026-08-23: all six files in
`plugins/comment-review/agents/` carry `name`, `description` and `model` and **no `tools:` key**,
so each reviewer holds `Write`, `Edit` and `NotebookEdit`. The mechanism to restrict them exists
and is used elsewhere in the same registry -- the `Explore` agent is declared *all tools except
`Agent`, `Artifact`, `ExitPlanMode`, `Edit`, `Write`, `NotebookEdit`*.

! **A `tools:` key does NOT close it** -- `Bash` can redirect to a file -- but it removes the path
that requires no ingenuity, and it makes the intent machine-readable instead of prose.

!! **AND A LOCKDOWN CAN REMOVE THE REMIT WITH THE RISK.** The reviewers' own vocabulary is built
from verbs they are instructed in -- `ran`, `grep`, `count`, `resolve`, `verify` -- so removing
execution removes what they are asked to do. `desk.py:115` is `QUERY_ATTEMPTED`, which refuses a
query naming no attempted check, so a reviewer that cannot check cannot pass its own gate. That
is the decision owed before a tool list is picked.

## !! The rule conflates two different things, and Roy ruled on which

| what a reviewer writes | does it destroy a finding? | the ruling |
| --- | --- | --- |
| a file **under review** | **yes** -- the census goes stale, and the fix retires the finding | forbidden |
| a scratch file elsewhere | no | **also forbidden**, explicitly |

**The rule now names the one exception and closes the rest.** `reviewer-brief.md:13-15`:
*"You write exactly ONE file: the RECORD FILE you were handed, and you edit it in place. That is
your report, and it is the only exception. Nothing you find licenses a second one -- not a summary
beside it, not a note to the task agent, not a corrected copy of a paragraph."*

! **That is the OPPOSITE of the recommendation this file carried**, which was to permit scratch in
the run directory because `gen.py` is provenance -- a script a reviewer wrote to compute its
findings is the only artifact in a report that can be RE-RUN. The argument is kept because it is
the reason the rule had to be stated explicitly rather than assumed, and because a future run
asking for a re-runnable probe has to reopen it deliberately.

## !! Nothing sits between the census and the collator

The census is taken at stage 3 and the reviewers run at stage 4. **If a reviewer edits a file
under review, the census is silently stale and no stage notices.** `prove_unchanged.py` runs at
7b, against the pre-edit ref, and proves only that *executable code* reads the same -- its own
docstring says so: the AST proof blanks every docstring, and the `stripped` proof deletes every
comment. **A reviewer that edited a COMMENT is invisible to it by construction**, because
comments are exactly what both proofs discard.

! **Detecting a stale census is cheaper than it sounds** -- `repo.py` already reads these files,
and the collator already loads the census.

! **THE BOUNDARY IS STATED DELIBERATELY, WHICH IS WHY THE QUESTION IS ROY'S.**
`prove_unchanged.py`'s docstring: *"The claim this skill makes to the people who run it is that
prose changed and the rest reads the same"*. This run shows the claim nobody makes is *the
reviewers changed no prose*, and that one has no proof at all. The answer decides whether the
stale-census check is a gate or a convenience.

! **0.2.0 added an accidental tripwire, and it is still the only one there is.** `address_problem`
(`desk.py:556`) compares each record's transcribed `original` against the census text. A reviewer
that edited a paragraph would transcribe the edited text and mismatch. That is not why the check
exists, and it bears on how far it can be relaxed -- see
[`a-scope-declaration-costs-as-much-as-a-finding`](a-scope-declaration-costs-as-much-as-a-finding.md).

## Tasks

- [x] T1 -- RULED, and `reviewer-brief.md:6-18` carries it: a reviewer writes the record
      file it was handed and NOTHING ELSE. The scratch argument is in the Objective.
- [ ] T2 -- Add a `tools:` key to all six agent files. Verify: `grep -L "^tools:"
      plugins/comment-review/agents/*.md` returns nothing.
- [ ] T3 -- Drop `Write`, `Edit` and `NotebookEdit` from the four reviewers' `tools:`.
      Verify: none of the four reviewer files lists any of the three.
- [ ] T4 -- * Decide what the reviewers still need to EXECUTE, before T3 picks a list.
      Verify: the decision is recorded and names the tools the four reviewers keep.
- [ ] T5 -- Hash the files under review after stage 3 and re-check them before the collator.
      Verify: editing one between makes `verdicts.py` refuse, naming the file.
- [x] T6 -- SUPERSEDED. "Keep the scratch files in the evidence package" cannot be done --
      none exists in the tree or its history. The measurement is in the Objective.
- [ ] T7 -- * Say whether `prove_unchanged.py`'s scope is a gap or a boundary. Verify: the
      answer is in `docs/decision-log.md`, and says whether T5 is a gate.
## Related

- [`stage-5-is-the-only-stage-with-no-independent-reader`](stage-5-is-the-only-stage-with-no-independent-reader.md)
  -- the other place a stage's output is trusted rather than checked.
