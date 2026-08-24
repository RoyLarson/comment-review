# code_concerns is a bare list of strings, so a code problem reaches no gate

```
Status:   blocked (on the * ruling in a-role-with-no-code-out-damages-the-prose, which
          decides the shape this must carry; and on a working grader -- 'effectiveness
          unchanged' is a comparison and the-harness-cannot-run-the-system-it-grades is
          open)
Progress: 0 of 9 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-23 (2026-08-23, splitting a-role-with-no-code-out-damages-the-prose:
          Roy, 'there is giving the machinery to surface them properly, that is the
          backend lane')
TRIAGED:  2026-08-23 — 2026-08-23, every claim in the Objective re-read against the tree
          and all four hold. `reviewer-brief.md:255` publishes code_concerns as *"a list
          of strings, one line each, no verdict"*; `record.py:883` seeds `"code_concerns":
          []`; `held.py:190` returns `[str(c) for c in (report.get("code_concerns") or
          [])]`; and a grep for `code_concerns` over the shipped scripts hits only
          held.py:92, :116, :190 and record.py:883 -- verdicts.py does not appear, so
          nothing joins or gates it. ! T2, T3 and T5 were statements of fact rather than
          checkpoints and are rewritten with a verification each. Status unchanged: this
          is step 1 of the two-lane sequence in CLAUDE.md and both its gates are open.
SPLIT:    2026-08-23 -- the shape box held three artifacts (a definition, a validator and
          the brief) and the stage-5 box held the reading AND the proof that the gate can
          fail. Six boxes became nine; nothing changed meaning.
```

## Objective

A reviewer that finds a CODE problem has one channel for it, and it carries almost nothing.
`code_concerns` is published in the brief as *"a list of strings, one line each, no verdict"*
(`reviewer-brief.md:255`); `record.py:883` seeds it empty and `held.py:190` reads it back as
`[str(c) for c in ...]`, so anything structured a role emitted is flattened to its repr.

!! **IT IS THE ONE REVIEWER OUTPUT NO GATE CHECKS.** `verdicts.py` is stage 5 -- it joins every
prose finding against the census, resolves every citation, and refuses what does not hold. It
never reads `code_concerns` (verified 2026-08-23: the name does not appear in that file). So the
channel a role is supposed to use for the findings it cannot fix is also the only channel
nothing verifies, which is the shape [`docs/gates.md`](../docs/gates.md) is about: not *does the
check pass*, but *could it fail*.

! **A CODE CONCERN HAS NO ADDRESS**, so it cannot be re-run against a later tree, deduplicated
when two roles raise it, or checked for staleness -- the three things an address buys every
other finding.

## !! THIS LANDS FIRST, AND ITS PASS CRITERION IS THAT NOTHING CHANGES

Roy, 2026-08-23: *"it has to be landed in the code, tested that the effectiveness didn't
change, and then change the agents to tell them they can use it. Verify that it improved the
recommendations."*

**The machinery is the CONTROL.** No role is told about the new shape while this lands, so a
run over the same subject must produce the same findings and the same verdicts as before. If
effectiveness moves on this change, the machinery is doing something it was not asked to do
and that is the finding.

! **THE TWO HALVES MUST NOT LAND TOGETHER**, and this is a measurement rule rather than a
tidiness one: shipped in one step, a change in the recommendations cannot be attributed to the
INSTRUCTION rather than to the SHAPE, and the experiment that
[`a-role-with-no-code-out-damages-the-prose`](a-role-with-no-code-out-damages-the-prose.md)
exists to run has no baseline.

!! **AND BOTH MEASUREMENTS NEED A HARNESS THAT DOES NOT EXIST YET.** "Effectiveness did not
change" and "the recommendations improved" are both comparisons, and nothing in this repo
currently grades a run --
[`the-harness-cannot-run-the-system-it-grades`](the-harness-cannot-run-the-system-it-grades.md).
Building this against no baseline produces a claim nobody can check, which is the practice
`CLAUDE.md` names: a thing whose dependencies are broken is not worked on, it is refused.

## What stage 8 has to be told, and why the ruling on an address is separate

Stage 8 reads the finished page, and **a code concern is by definition not on the page** --
so `references/review.md` has to say what becomes of one, and today it says nothing.

! **The address question is a ruling, not a design.** A finding gets its address from the
census; a concern has none, and whether it should is a decision about what a concern IS. It
is carried below as a `*` box because it finishes the day it is answered.

## Tasks

- [ ] T1 -- Define a code-concern SHAPE that carries a located proposal -- where, what and
      why. Verify: the shape is defined in exactly one file and nothing else redefines it.
- [ ] T2 -- Make `record.py --check` validate that shape. Verify: a malformed
      `code_concerns` entry is refused and a well-formed one passes.
- [ ] T3 -- Publish the same shape in the brief, where `reviewer-brief.md:255` today says
      *"a list of strings, one line each, no verdict"*. Verify: the brief matches T2.
- [ ] T4 -- Remove the `str(c)` coercion at `held.py:190`, which flattens an entry to its
      repr. Verify: a T1-shaped concern leaves `held.parse_report` unflattened.
- [ ] T5 -- Make `verdicts.py` read `code_concerns` and report every one it was handed.
      Verify: two concerns in, two reported, and none dropped silently.
- [ ] T6 -- Prove the stage-5 gate CAN fail on a code concern. Verify: a test refuses a
      bad concern, and fails when the new check is removed.
- [ ] T7 -- * RULE whether a code concern gets an ADDRESS from the census the way a
      finding does. Verify: the answer is here -- addressed, or deliberately not.
- [ ] T8 -- Write into `references/review.md` what stage 8 does with a code concern.
      Verify: `review.md` names the handling, and `check_vocabulary.py` still passes.
- [ ] T9 -- PASS CRITERION: run the graded set before and after this lands, with NO agent
      file touched. Verify: the findings and verdicts are the same in both runs.
