# Correcting one copy strands the copy in a REFERENCE ONLY file

```
Status:   open
Progress: 0 of 6 tasks done
Owner:    agents
Requires-Roy: true
Raised:   2026-08-17 (Roy: "This shouldn't happen - As much as FOR REFERENCE only might make
          sence - leaving stale documenation behind references just asks to make these harder
          to trace down later")
```

## Objective

**A run corrects a claim in a file under review, and the same claim in a REFERENCE ONLY file
keeps the old text. Nothing may target the reference file, so the run ships a disagreement it
created.**

Measured 2026-08-17: a docstring said *"Four kinds of problem"* where the code has seven, and
`.claude/skills/todo-tool/SKILL.md` carries the same sentence. The reference copy is out of
scope, so the proposal could correct one and only mention the other.

!! **The run makes the tree worse in a specific way.** Before it, two copies AGREE and are both
wrong -- findable as a pair, and a grep for either finds both. After it, they DISAGREE, and the
stale one is harder to trace precisely because its twin no longer matches it. The pass turned a
duplicated error into a silent divergence.

## ! The rule already names the failure; its remedy does not reach this case

`SKILL.md`: *"**Two findings quoting the same sentence in different files are ONE finding.** A
pass edits where it is reading, fixes the copy in front of it, and manufactures a disagreement
with the one it never opened."*

That is exactly this. But the sentence continues *"Contradicting verdicts trigger a re-review"* --
and a re-review needs two findings. **A REFERENCE ONLY file carries none**, because no verdict
may target it. The rule sees the failure and its cure operates on a case that cannot arise here.

`reviewer-brief.md` gives the reviewer its instruction -- *"if a reference is wrong it needs to be
stated with the record"* -- and that worked: the run stated it. Stating it is not enough when the
correction is what creates the divergence.

## ! The precedent for the shape of the answer is 1.4

When the tree a verdict needs is absent, `SKILL.md` 1.4 does not silently proceed and does not
silently refuse. It **says so, and offers the human the one-line alternative** -- create the tree,
or name another destination. ! The difference here is timing: 1.4 settles at stage 1, and this
cannot be known until stage 5, when the correction lands on a claim whose twin is out of scope.

## * RULED 2026-08-17 -- `REFERENCE CONCERNS`, a sibling to `CODE CONCERNS`

Roy: *"Gets a sibling - REFERENCE CONCERNS"*. `CODE CONCERNS` does not widen to carry a defect
in a document. One is a problem in the program and the other a problem in a document, and they
reach different readers -- so they are two sections, each one line per entry and no verdict.

! It is also where a SYSTEMIC finding goes: 15 blocks citing `CLAUDE.md stage N` where the scheme
belongs to another file is one `REFERENCE CONCERNS` line, not thirty near-identical verdicts.

## Tasks

- [ ] * Rule on what the run DOES, Roy having ruled that shipping the divergence is not it.
      Candidates:
      **(a) withhold the correction** -- leave both copies wrong and agreeing, and report the
      pair. Truthful, and it means a run can be blocked from fixing a real falsehood by a file
      it may not touch;
      **(b) apply it and mark the proposal INCOMPLETE**, naming the stranded copy as work the
      author must do, so the divergence is deliberate and recorded rather than silent;
      **(c) offer to widen scope**, 1.4's move -- present the reference file and let the author
      add it to FILES UNDER REVIEW, which makes it reviewable properly rather than edited blind.
      ! Recommendation: **(c), falling back to (b)** when the author does not answer. (a) makes
      an out-of-scope file able to veto a correction, which is worse than the disagreement.

- [ ] Detect it at all. Nothing does today. ! The task agent holds the reference file list and
      the replacement text, so the check is available at stage 5: grep the FALSE clause of every
      `correct` across the REFERENCE ONLY files before applying. ! It cannot be the join's --
      `contradictions()` keys on the census BLOCK index and a reference file has no blocks.

- [ ] Extend the existing `SKILL.md` rule rather than writing a second one. It already names
      the failure; what it lacks is the branch where the second copy cannot carry a verdict.

- [ ] Decide whether this applies to `drop` and `move` as well as `correct`. Dropping a sentence
      whose twin survives in a reference file leaves the reference as the only copy -- which may
      be the right outcome, or may strand it. ! Not obvious in either direction.

- [ ] ! Check the interaction with `a-prose-file-has-no-blocks`. The stranded copy in the
      measured case is a `.md` file, which cannot be censused at all -- so even widening scope
      does not make it reviewable today. The two tasks may have one answer.

- [ ] Say in `docs/limitations.md` that a run can strand a copy it may not touch, until this is
      settled. ! It is true today and a reader of a proposal has no way to know it.
