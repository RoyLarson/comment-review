# The CODE CHECK refuses `add` and `drop` when the prose is a docstring

```
Status:   open
Progress: 1 of 5 tasks done
Owner:    backend
Requires-Roy: true
Raised:   2026-08-17, on the FIRST run ever to reach stage 7b. A docstring `add` failed the
          CODE CHECK, the rail said restore, and an approved edit was reverted.
Split:    2026-08-23 -- boxes cut to two lines each, a Verify written for every open one,
          and the reasoning each carried moved into the Objective
Measured: 2026-08-25 — on the CHAIN, not the 7b gate: flows/proof_setter.run refuses
          {m.py@a0: None}, {m.py@a1: None} and an add at a2 with Refusal('prove', ...,
          'the executable code is not what it was'), on tests/conftest.SAMPLE. T5's two
          cases now RUN, as
          TestEveryVerdictThePlacesCanEXPRESSGetsThroughTheChain::test_a_docstring_{DROP,ADD}_is_STILL_REFUSED_at_prove;
          T1 is untouched and the fingerprint was not weakened -- six modules in
          src/comment_review/commands read ArgumentParser(description=__doc__)
```

## Objective

**Stage 7b proves executable code unchanged by comparing `ast.dump`. A docstring is an AST node,
so adding or deleting one fails the proof.** Measured:

| edit | CODE CHECK |
| --- | --- |
| add a `#` comment | PROVEN |
| rewrite a docstring's text | PROVEN |
| **ADD a docstring** | **FAIL** |
| **DELETE a docstring** | **FAIL** |

!! **`add` cannot land on a docstring, and `add` is defined as "a constraint exists in code and
NOWHERE in prose".** A function with no docstring is the case the verdict exists for, and the
repair is a docstring. `drop` has the same hole from the other side.

! It went unnoticed because **7b had never run.** Two runs today stopped at 7a, as designed; the
first one to cross applied a docstring `add`, failed the proof, and restored -- correctly, the
rail says restore -- losing an approved edit.

## ! The rule is deliberate and half-right

`_blank_docstrings`: *"A docstring is prose this skill is allowed to rewrite, so its CONTENT
must not enter the fingerprint. **Its presence still does**: deleting a docstring entirely
changes the body's shape and stays visible."*

Written for deletion, and the consequence for ADDITION was never drawn.

!! **And presence is genuinely observable**, so it cannot simply be ignored: a docstring binds
`__doc__`, and THIS repo depends on that -- `ArgumentParser(description=__doc__)` appears in
every shipped CLI. Blanking presence would let a real change through.

## ! The proof is right; the REPORT is what is wrong

The check answers *"did anything differ"* when the question at 7b is *"did anything differ
BEYOND WHAT THE AUTHOR APPROVED"*. An approved `add` at a named anchor is an expected delta, and
the check has no way to be told so.

! Recommendation: do NOT weaken the fingerprint. **Split the report** -- executable code proven
identical, and docstring-presence deltas listed separately with the declaration they sit on. The
operator matches them against the approved set. A delta with no matching approval is still a
stop; a delta that matches one is the edit landing.

## What the boxes used to carry, and why each is wanted

! **T1 is Roy's** because it changes what the proof ASSERTS. It decides whether the CODE CHECK
stays a blanket proof -- simple, and unable to admit two verdicts -- or becomes a diff against an
expectation, which is stronger and needs the approved list to reach it.

! **T2 stands whichever way T1 goes.** Today ONE line says `executable code DIFFERS (ast proof)`
for a change that is entirely prose, and the operator had to diagnose it by hand with a second
AST comparison.

! **T3 is the interim rail.** Until this is settled, an operator following `write.md` loses the
edit and has no way to know that was the rule working.

! **T4 is UNMEASURED and this file must not claim which way it goes.** Non-Python files compare
`stripped` text, which removes comments -- so a docstring has no meaning there, but `///` and
`/**` doc comments do.

! **T5 is the gap in the suite.** Nothing in `tests/test_prove_unchanged.py` covers a docstring
being ADDED or REMOVED -- only rewritten, which is the case that passes.

## Tasks

- [?] T1 -- * Rule whether 7b compares against the approved SET or nothing-changed.
      Verify: `docs/decision-log.md` records the answer and `write.md` states it.
- [ ] T2 -- Report docstring-presence deltas SEPARATELY from executable ones. Verify:
      `prove_unchanged.py` prints them under their own heading with each declaration.
- [ ] T3 -- Say in `write.md` what a docstring `add` does today, until T1 is settled.
      Verify: `write.md` states that it fails the CODE CHECK and that the rail restores.
- [ ] T4 -- Measure the LEXICAL side: a `///` or `/**` doc comment ADDED and REMOVED,
      against the `stripped` comparison. Verify: this file records which way each goes.
- [x] T5 -- Add a docstring-ADDED case and a docstring-REMOVED case to
      `tests/test_prove_unchanged.py`. Verify: both cases run and the suite is green.
