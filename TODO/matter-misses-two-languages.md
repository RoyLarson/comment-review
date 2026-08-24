# A licence header is unprotected in Rust and TypeScript

```
Status:   open (T5's ruling deferred to a prose classifier; T2, the Rust half, does not
          wait on it)
Progress: 2 of 5 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-23 (2026-08-23, re-measuring `front-matter-protection-is-python-only`
          during a backlog audit -- its title was false and the surviving defect is a
          different one)
RE-MEASURED: 2026-08-23 — 2026-08-23, all three findings still reproduce, re-measured on
             purpose-built probes rather than the repo fixtures --
             tests/fixtures/sample.ts opens with a LINE comment and sample.rs with
             '//!', so neither exercises the case this file is about, and both look like
             passes. Probes: a .ts opening '/**' types f0 dark-matter; a .rs opening '//
             Copyright' above fn main() types f0 dark-matter; a .c opening '/* */' types
             f0 matter. So task 4 holds -- C proves the mechanism reaches beyond Python
             -- and the ruling in task 5 is the only thing standing.
TRIAGED:  2026-08-23 — the probes were re-run a second time today, through `page_for`
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
so nothing here is a Python-only mechanism to be generalised.

## Tasks

- [x] T1 -- MEASURED 2026-08-23 on four identical licence headers, and re-run the
      same day: `lic.py` and `lic.c` both type `f0 kind=matter`; `lic.rs` and
      `lic.ts` type `f0 dark-matter`, so the `query` guard that protects a licence
      from being edited never fires for them. Recorded in the Objective's table;
      the two causes are T2 and T3.
- [ ] T2 -- Stop an ordinary `//` run at the head of a Rust file being claimed as the
      next declaration's documentation. MEASURED 2026-08-23: `// Copyright` above `fn
      main()` types `a1 kind=comment` and `f0 kind=dark-matter`. ! Rust's `doc_line` is
      `('///', '//!')`, so `//` is not a doc opener and the `a` claim has no basis in
      the row. Verify: a `.rs` opening `// Copyright` above `fn main()` types
      `f0 kind=matter`, and `a1` is empty. ! Independent of T5's ruling.
- [ ] T3 -- Make a TypeScript licence header written in `/** */` protectable.
      MEASURED 2026-08-23: `/**` is TS's `doc_block`, so a file opening with one types
      `a1 kind=docstring` and `f0 kind=dark-matter`. Verify: a `.ts` opening
      `/** ... */` above `export const x = 1;` types `f0 kind=matter`. ! BLOCKED on
      T5 -- the fix is whatever the ruling says a doc-shaped opener at the head of a
      file IS.
- [x] T4 -- ! WHAT IS ALREADY RIGHT, so it is not re-litigated: the rule is
      POSITIONAL and per-language only in what counts as a comment -- a run starting
      on line 1 or ending on the last line is matter. C proves the mechanism reaches
      beyond Python.
- [ ] T5 -- * THE RULING WANTED: is a doc-shaped opener -- `/**` in TS, `///` in
      Rust -- matter when it is the FIRST thing in the file? ! The lexer says a
      docstring is never matter, which is right for a module docstring and wrong for
      a licence written in `/** */`. The two cannot both hold on one clause. Verify:
      the ruling is recorded in `docs/decision-log.md`.
      !! **DEFERRED 2026-08-23, AND THE POSITION MOVED FROM NO TO NOT NOW.** Roy,
      asked with three candidate rules -- blank line decides, position wins, kind
      wins: *"Ruled several times - We would need a prose classifier to catch the
      edge cases and while I stated that as a no previously, I think it is more of a
      Not Now."*
      ! **WHAT BLOCKS IT IS A CAPABILITY, NOT A PREFERENCE.** Every candidate rule
      decides from SHAPE -- the opener's characters, the blank line, the position --
      and the cases that separate a licence from a module docstring are decided by
      what the prose SAYS. No rule available to the lexer today reads that, so any
      of the three would be right in the common case and silently wrong in the ones
      the ruling exists to settle. ! Waits on a prose classifier. ! Deferred is not
      done: the box stays unchecked because the ruling is still owed.
