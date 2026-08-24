# Correcting one copy strands the copy in a REFERENCE ONLY file

```
Status:   decision-needed
Progress: 0 of 6 tasks done
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

! **AND THE JOIN CANNOT SEE IT EITHER, for a reason this file used to state wrongly.**
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
which carry `CODE CONCERNS`.

## Where a widened scope runs out

MEASURED 2026-08-23: `census.py --repo . --json CLAUDE.md` exits nonzero with *"no language
record for its suffix"*, and `language.py` holds no `.md` record. The stranded copy in the
measured case is a `.md` file, so adding it to FILES UNDER REVIEW does not make it reviewable
today. See [`a-prose-file-has-no-blocks`](a-prose-file-has-no-blocks.md) -- the two may have one
answer.

## Tasks

- [ ] * T1 -- RULE on what the run DOES, Roy having ruled that shipping the divergence is not
      it. Candidates: **(a) withhold the correction** -- leave both copies wrong and agreeing,
      and report the pair; **(b) apply it and mark the proposal INCOMPLETE**, naming the
      stranded copy as work the author must do; **(c) offer to widen scope**, 1.4's move --
      present the reference file and let the author add it to FILES UNDER REVIEW. !
      Recommendation: **(c), falling back to (b)** when the author does not answer. (a) makes an
      out-of-scope file able to veto a correction, which is worse than the disagreement.

- [ ] * T2 -- RULE whether this applies to `drop` and `move` as well as `correct`. Dropping a
      sentence whose twin survives in a reference file leaves the reference as the only copy --
      which may be the right outcome, or may strand it. ! Not obvious in either direction, so it
      is asked rather than assumed.

- [ ] T3 -- LAND `REFERENCE CONCERNS` in the shipped files, the 2026-08-17 ruling having reached
      only a spec. Verify: `grep -rn "REFERENCE CONCERNS" plugins/` returns the section in
      `reviewer-brief.md` and its emission in `verdicts.py`, alongside the `CODE CONCERNS` lines
      already there (`verdicts.py:694`, `reviewer-brief.md:453,471`).

- [ ] T4 -- DETECT the stranding at stage 5. Nothing does today. The task agent holds the
      reference file list and the replacement text, so the check is available: grep the FALSE
      clause of every `correct` across the REFERENCE ONLY files before applying. ! It cannot be
      the join's -- `contradictions()` keys on the address (`verdicts.py:225-238`) and a
      reference file has no census, so it can never relate two copies. Verify: a run over
      `scripts/todo_tool.py` that corrects the `:1129` sentence reports
      `.claude/skills/todo-tool/SKILL.md:253` before applying.

- [ ] T5 -- EXTEND the existing `SKILL.md:800-804` rule rather than writing a second one. It
      already names the failure; what it lacks is the branch where the second copy cannot carry
      a verdict. Verify: the paragraph at `SKILL.md:800` states what happens when the twin is
      REFERENCE ONLY, and no new numbered rule is added.

- [ ] T6 -- SAY in `docs/limitations.md` that a run can strand a copy it may not touch, until
      this is settled. Verify: `grep -n "REFERENCE ONLY" docs/limitations.md` is non-empty. It is
      empty today, and a reader of a proposal has no way to know it.
