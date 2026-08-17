# The CODE CHECK refuses `add` and `drop` when the prose is a docstring

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    session · Roy (⭐ 1 ruling)
Raised:   2026-08-17, on the FIRST run ever to reach stage 7b. A docstring `add` failed the
          CODE CHECK, the rail said restore, and an approved edit was reverted.
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

⚠⚠ **`add` cannot land on a docstring, and `add` is defined as "a constraint exists in code and
NOWHERE in prose".** A function with no docstring is the case the verdict exists for, and the
repair is a docstring. `drop` has the same hole from the other side.

⚠ It went unnoticed because **7b had never run.** Two runs today stopped at 7a, as designed; the
first one to cross applied a docstring `add`, failed the proof, and restored — correctly, the
rail says restore — losing an approved edit.

## ⚠ The rule is deliberate and half-right

`_blank_docstrings`: *"A docstring is prose this skill is allowed to rewrite, so its CONTENT
must not enter the fingerprint. **Its presence still does**: deleting a docstring entirely
changes the body's shape and stays visible."*

Written for deletion, and the consequence for ADDITION was never drawn.

⚠⚠ **And presence is genuinely observable**, so it cannot simply be ignored: a docstring binds
`__doc__`, and THIS repo depends on that — `ArgumentParser(description=__doc__)` appears in
every shipped CLI. Blanking presence would let a real change through.

## ⚠ The proof is right; the REPORT is what is wrong

The check answers *"did anything differ"* when the question at 7b is *"did anything differ
BEYOND WHAT THE AUTHOR APPROVED"*. An approved `add` at a named anchor is an expected delta, and
the check has no way to be told so.

⚠ Recommendation: do NOT weaken the fingerprint. **Split the report** — executable code proven
identical, and docstring-presence deltas listed separately with the declaration they sit on. The
operator matches them against the approved set. A delta with no matching approval is still a
stop; a delta that matches one is the edit landing.

## Tasks

- [ ] ⭐ Rule on whether 7b compares against the approved SET or against nothing-changed. ⚠ It
      decides whether the CODE CHECK stays a blanket proof — simple, and unable to admit two
      verdicts — or becomes a diff against an expectation, which is stronger and needs the
      approved list to reach it. Roy's, because it changes what the proof asserts.

- [ ] Report docstring-presence deltas SEPARATELY from executable ones whichever way that goes.
      Today one line says `executable code DIFFERS (ast proof)` for a change that is entirely
      prose, and the operator had to diagnose it by hand with a second AST comparison.

- [ ] Say in `write.md` what a docstring `add` does today, until this is settled. ⚠ An operator
      following the rails loses the edit and has no way to know that was the rule working.

- [ ] Check the LEXICAL side. Non-Python files compare `stripped` text, which removes comments —
      so a docstring has no meaning there, but `///` and `/**` doc comments do. ⚠ Unmeasured;
      this file must not claim which way it goes.

- [ ] Add both cases to `tests/test_prove_unchanged.py`. ⚠ Nothing there covers a docstring
      being ADDED or REMOVED — only rewritten, which is the case that passes.
