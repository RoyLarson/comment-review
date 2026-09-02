# A licence header is unprotected in Rust and TypeScript

```
Status:   open (T5's ruling deferred to a prose classifier; T2, the Rust half, does not
          wait on it)
Progress: 2 of 5 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-23 (2026-08-23, re-measuring `front-matter-protection-is-python-only`
          during a backlog audit -- its title was false and the surviving defect is a
          different one)
RE-MEASURED: 2026-08-23 -- 2026-08-23, all three findings still reproduce, re-measured on
             purpose-built probes rather than the repo fixtures --
             tests/fixtures/sample.ts opens with a LINE comment and sample.rs with
             '//!', so neither exercises the case this file is about, and both look like
             passes. Probes: a .ts opening '/**' types f0 dark-matter; a .rs opening '//
             Copyright' above fn main() types f0 dark-matter; a .c opening '/* */' types
             f0 matter. So task 4 holds -- C proves the mechanism reaches beyond Python
             -- and the ruling in task 5 is the only thing standing.
TRIAGED:  2026-08-23 -- the probes were re-run a second time today, through `page_for`
          directly, and every result reproduced. ! The three measurement boxes are
          rewritten as the FIXES they name, so each can be ticked by someone who runs
          the probe. ! THE TWO HALVES ARE NOT EQUALLY BLOCKED: Rust's `//` is not a
          doc-shaped opener -- Rust declares `doc_line = ('///', '//!')` -- so task 2 is
          a straightforward defect and does not wait on the ruling. Only TypeScript's
          `/**` does.
```

## Objective

**A licence header is unprotected in Rust and TypeScript.** The `query` guard that protects a
file's own matter from being edited never fires for them, because the run is never typed
`matter`.

MEASURED 2026-08-23 on four identical licence headers, re-run the same day through `page_for`:

| probe | `f0` | where the header went |
| --- | --- | --- |
| `lic.py` | `matter` | `f0`, anchored `<module>` |
| `lic.c` | `matter` | `f0`, anchored `<module>` |
| `lic.rs` | **`dark-matter`** | `a1 kind=comment`, anchored `fn main() {}` |
| `lic.ts` | **`dark-matter`** | `a1 kind=docstring`, anchored `export const x = 1;` |

!! **THE TWO FAIL FOR DIFFERENT REASONS AND ONLY ONE NEEDS A RULING.**

- **Rust loses the run to the `a` series.** `// Copyright` above `fn main()` is typed
  `comment`, then claimed as that declaration's documentation, so the matter clause at
  `lexer.py:1137` -- `if kind == "comment" and (run[0][0] == 1 or run[-1][0] == len(lines))` --
  never sees it. ! Rust declares `doc_line = ('///', '//!')`, and an ordinary `//` run above a
  declaration is still being claimed as that declaration's doc.
- **TypeScript is typed `docstring` before the clause runs.** `/**` is TS's `doc_block`, so a
  file opening `/** to get started */` is a docstring -- and the lexer's own rule is that a
  docstring is not matter and is what ENDS matter. ! This is the
  `corpora/sentry/eslint.config.ts` case the superseded file measured, still live.

! **The rule is POSITIONAL and per-language only in what counts as a comment** -- a run starting
on line 1 or ending on the last line is matter. C proves the mechanism reaches beyond Python,
so nothing here is a Python-only mechanism to be generalised, and that half is not re-litigated.

## The ruling wanted, and why it is DEFERRED

**The question:** is a doc-shaped opener -- `/**` in TS, `///` in Rust -- matter when it is the
FIRST thing in the file? ! The lexer says a docstring is never matter, which is right for a
module docstring and wrong for a licence written in `/** */`. The two cannot both hold on one
clause.

!! **DEFERRED 2026-08-23, AND THE POSITION MOVED FROM NO TO NOT NOW.** Roy, asked with three
candidate rules -- blank line decides, position wins, kind wins: *"Ruled several times - We would
need a prose classifier to catch the edge cases and while I stated that as a no previously, I
think it is more of a Not Now."*

! **WHAT BLOCKS IT IS A CAPABILITY, NOT A PREFERENCE.** Every candidate rule decides from SHAPE
-- the opener's characters, the blank line, the position -- and the cases that separate a licence
from a module docstring are decided by what the prose SAYS. No rule available to the lexer today
reads that, so any of the three would be right in the common case and silently wrong in the ones
the ruling exists to settle. ! Waits on a prose classifier.

! **Deferred is not done: the box stays unchecked because the ruling is still owed.** The
TypeScript fix waits on it, because the fix IS whatever the ruling says a doc-shaped opener at
the head of a file is. The Rust fix does not.

## Tasks

- [x] T1 | FINISHED | unknown | T1 -- MEASURED 2026-08-23 on four identical
      licence headers, and re-run the same day. The table and what each probe
      typed are in the Objective.
- [ ] T2 | T2 -- Stop a Rust file's opening `//` run being claimed as a
      declaration's doc. Verify: a `.rs` opening `// Copyright` types `f0
      matter` and an empty `a1`.
- [ ] T3 | T3 -- Make a TypeScript licence header written in `/** */`
      protectable, per T5's ruling. Verify: a `.ts` opening `/** ... */` above a
      declaration types `f0 matter`.
- [x] T4 | FINISHED | unknown | T4 -- NOT A TASK. What is already right -- the
      rule is POSITIONAL, and C proves the mechanism reaches beyond Python -- is
      recorded in the Objective.
- [ ] T5 | T5 -- * RULE whether a doc-shaped opener is matter when it is FIRST
      in the file; DEFERRED to a prose classifier. Verify: the ruling is in
      `docs/decision-log.md`.
