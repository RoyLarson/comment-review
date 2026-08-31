# Correcting one copy strands the copy in a REFERENCE ONLY file

```
Status:   decision-needed
Progress: 0 of 9 tasks done
Owner:    agents
Requires-Roy: true
Raised:   2026-08-17 (Roy: "This shouldn't happen - As much as FOR REFERENCE only might make
          sence - leaving stale documenation behind references just asks to make these harder
          to trace down later")
TRIAGED:  2026-08-23 — 2026-08-23. The measured pair STILL AGREES, so the divergence has not
          been created yet and the case is reproducible: `scripts/todo_tool.py:1129` and
          `.claude/skills/todo-tool/SKILL.md:253` both read "Four kinds", and the docstring
          under :1129 enumerates more than four. ! The RULING is recorded only in
          `docs/superpowers/specs/2026-08-17-review-process-coherence-design.md:337` --
          `REFERENCE CONCERNS` appears in NO shipped file, so landing it is work and is now a
          task. ! One claim in this file was stale and is corrected below: `contradictions()`
          keys on the ADDRESS, not the census block index.
Split:    2026-08-23 -- every box cut to two lines. The `drop`/`move` ruling was two
          rulings and the landing box was two files, so six boxes became eight
Split:    2026-08-24 -- second pass, eight boxes to nine. The stage-5 detection box held a
          `SKILL.md` change AND a demonstration run on the measured case, which are two
          artifacts nobody ticks at the same time
```

## Objective

**A run corrects a claim in a file under review, and the same claim in a REFERENCE ONLY file
keeps the old text. Nothing may target the reference file, so the run ships a disagreement it
created.**

MEASURED 2026-08-17 and RE-MEASURED 2026-08-23: `scripts/todo_tool.py:1129` reads *"Four kinds
of problem are left untouched"* and `.claude/skills/todo-tool/SKILL.md:253` reads *"Four
kinds"*. Both files are tracked. The two copies still AGREE and are both wrong -- the docstring
below :1129 goes on to enumerate more than four -- so the failure this file describes is still
ahead of the tree rather than behind it, and the case can be run.

!! **The run makes the tree worse in a specific way.** Before it, two copies AGREE and are both
wrong -- findable as a pair, and a grep for either finds both. After it, they DISAGREE, and the
stale one is harder to trace precisely because its twin no longer matches it. The pass turned a
duplicated error into a silent divergence.

## ! The rule already names the failure; its remedy does not reach this case

`SKILL.md:800-804`: *"**Two findings quoting the same sentence in different files are ONE
finding.** A pass edits where it is reading, fixes the copy in front of it, and manufactures a
disagreement with the one it never opened."*

That is exactly this. But the sentence continues *"Contradicting verdicts trigger a
re-review"* -- and a re-review needs two findings. **A REFERENCE ONLY file carries none**,
because no verdict may target it. The rule sees the failure and its cure operates on a case
that cannot arise here.

! **AND THE COLLATOR CANNOT SEE IT EITHER, for a reason this file used to state wrongly.**
`SKILL.md:803-804` says *"`contradictions()` keys on the ADDRESS, and the same sentence copied
into two files is two different paragraphs it can never relate"* -- confirmed 2026-08-23 at
`verdicts.py:225-238`, which groups by `f.address`. The earlier text here said it keys on the
census BLOCK index; it does not, and the conclusion is unchanged either way.

`reviewer-brief.md` gives the reviewer its instruction -- *"if a reference is wrong it needs to
be stated with the record"* -- and that worked: the run stated it. Stating it is not enough when
the correction is what creates the divergence.

## ! The precedent for the shape of the answer is 1.4

When the tree a verdict needs is absent, `SKILL.md` 1.4 does not silently proceed and does not
silently refuse. It **says so, and offers the human the one-line alternative** -- create the
tree, or name another destination. ! The difference here is timing: 1.4 settles at stage 1, and
this cannot be known until stage 5, when the correction lands on a claim whose twin is out of
scope.

### The candidates the first ruling chooses between

**(a) withhold the correction** -- leave both copies wrong and agreeing, and report the pair;
**(b) apply it and mark the proposal INCOMPLETE**, naming the stranded copy as work the author
must do; **(c) offer to widen scope**, 1.4's move -- present the reference file and let the
author add it to FILES UNDER REVIEW.

! **Recommendation: (c), falling back to (b)** when the author does not answer. (a) makes an
out-of-scope file able to veto a correction, which is worse than the disagreement.

### And whether it reaches `drop` and `move` is not obvious in either direction

Dropping a sentence whose twin survives in a reference file leaves the reference as the only
copy -- which may be the right outcome, or may strand it. ! It is asked rather than assumed, and
`move` is asked separately for the same reason.

## RULED 2026-08-17 -- `REFERENCE CONCERNS`, a sibling to `CODE CONCERNS`

Roy: *"Gets a sibling - REFERENCE CONCERNS"*. `CODE CONCERNS` does not widen to carry a defect
in a document. One is a problem in the program and the other a problem in a document, and they
reach different readers -- so they are two sections, each one line per entry and no verdict.

! It is also where a SYSTEMIC finding goes: 15 blocks citing `CLAUDE.md stage N` where the
scheme belongs to another file is one `REFERENCE CONCERNS` line, not thirty near-identical
verdicts.

! **THE RULING IS NOT IN THE SYSTEM.** MEASURED 2026-08-23: `REFERENCE CONCERNS` occurs once in
the repo, in `docs/superpowers/specs/2026-08-17-review-process-coherence-design.md:337`. It is
in no shipped file -- not `SKILL.md`, not `reviewer-brief.md`, not `verdicts.py`, all three of
which carry `CODE CONCERNS` (`verdicts.py:694`, `reviewer-brief.md:453,471`).

## Where a widened scope runs out

MEASURED 2026-08-23: `census.py --repo . --json CLAUDE.md` exits nonzero with *"no language
record for its suffix"*, and `language.py` holds no `.md` record. The stranded copy in the
measured case is a `.md` file, so adding it to FILES UNDER REVIEW does not make it reviewable
today. See [`a-prose-file-has-no-blocks`](a-prose-file-has-no-blocks.md) -- the two may have one
answer.

! **AND THE LIMITATION IS UNWRITTEN.** MEASURED 2026-08-24: `grep -n "REFERENCE ONLY"
docs/limitations.md` is EMPTY, so nothing tells a reader that a run can strand a copy it may not
touch. ! Extending `SKILL.md:800-804` is preferred to writing a second numbered rule, because
`docs/limitations.md` says a rule belongs in exactly one file.

! **DETECTION CANNOT BE THE COLLATOR'S.** `contradictions()` keys on the address
(`verdicts.py:225-238`) and a reference file has no census, so it can never relate two copies.
The task agent, which holds the reference file list and the replacement text, is where the check
is available.

## Tasks

- [?] T1 | T1 -- * **RULE what the run DOES with a `correct` whose twin is
      REFERENCE ONLY.** Verify: the ruling names (a), (b) or (c) from the
      Objective and is recorded here.
- [?] T2 | T2 -- * **RULE whether that applies to `drop`**, where the reference
      copy becomes the only copy. Verify: the ruling is recorded in this file.
- [?] T3 | T3 -- * **RULE whether that applies to `move`.** Verify: the ruling
      is recorded in this file.
- [?] T4 | T4 -- **Land the `REFERENCE CONCERNS` section in
      `reviewer-brief.md`.** Verify: `grep -n "REFERENCE CONCERNS"
      reviewer-brief.md` returns the section.
- [?] T5 | T5 -- **Emit `REFERENCE CONCERNS` from `verdicts.py`.** Verify: `grep
      -n "REFERENCE CONCERNS" verdicts.py` returns the emission.
- [?] T6 | T6 -- **Land the stage-5 stranding check in `SKILL.md`**: grep each
      `correct`'s FALSE clause across the REFERENCE ONLY files first. Verify:
      `SKILL.md` says so.
- [?] T7 | T7 -- **Prove that check on the measured case.** Verify: a run
      correcting `todo_tool.py:1129` reports the stranded copy at
      `todo-tool/SKILL.md:253`.
- [?] T8 | T8 -- **Extend the existing `SKILL.md:800-804` rule** rather than
      writing a second one. Verify: that paragraph states what happens when the
      twin is REFERENCE ONLY.
- [?] T9 | T9 -- **Say in `docs/limitations.md` that a run can strand a copy it
      may not touch.** Verify: `grep -n "REFERENCE ONLY" docs/limitations.md` is
      non-empty.
