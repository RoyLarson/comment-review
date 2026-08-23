# A rename left history in the comments, and every gate stayed green

**The defect class this system exists to catch, produced by accident, in this
repo, on 2026-08-23.** A mechanical rename of 1,027 sites rewrote 32 quoted
rulings and left 31 uses of a retired word inside code that had moved on. The
test suite, the type checker, the linter, the floor-syntax gate, the vocabulary
gate and the corpus round trip were all green throughout.

| | |
| --- | --- |
| base (defect present) | `326af1a` |
| answer key (defect gone) | `cfffa70` |
| repo | this one |

! **The base is a commit in this tree, which is a deliberate fixture shape** --
see [`TODO/the-harness-cannot-run-the-system-it-grades.md`](../../TODO/the-harness-cannot-run-the-system-it-grades.md):
*"a fixture is a CHECKOUT AT A HASH -- this repo's own history included, since a
fix commit is an answer key."*

## What happened

A branch renamed `foliator.py` to `addresser.py`, `folio` to `cue`, `Foliation`
to `Cues` and `foliate()` to `cue()` -- 1,027 sites across 70 files. The rename
was mechanical and word-boundary aware.

It rewrote **32 quotations**. This repo quotes rulings verbatim in `*"..."*`, and
a quotation is a record of what someone said, not prose to be maintained. The
rename edited inside them, so a 2026-08-20 ruling came out saying `path@cue` --
a word that was not coined until three days after the ruling was made.

Then, after the quotations were restored, **31 uses of `folio` remained**, all
inside those restored quotations, in seven live modules.

## Why no gate saw it

| gate | why it passed |
| --- | --- |
| 820 tests | prose is not executed |
| `ty`, `ruff` | a comment is not typed or linted for content |
| `check_shipped_syntax.py` | the files still parse |
| `check_vocabulary.py` | `folio` was not in `RETIRED` -- it had just been retired in the docs and nowhere a command reads |
| corpus round trip | 3,148 / 5 / 3,153 before the rename and after; the identity is about bytes of code, not truth of prose |

! **`dead_sweep.py` also reports nothing**, because a word in a comment is not a
name anything imports.

## What found each part

- **the corrupted quotations** -- reading, then a script comparing every `*"..."*`
  span against the pre-rename tree. The first pass matched single-line spans only
  and missed a wrapped one, so a seventh corrupted quote survived a green suite.
- **the 31 survivors** -- Roy, asking whether any CODE statement held the word.
  `codegraph_explore` over the whole family returned 31 symbols and none named
  `folio*`: every identifier was current. That is what proved the 31 were prose.
- **a corrupted word and 8 NUL BYTES** in `TODO/leaf-means-two-things.md` --
  `grep` reporting the file as binary. The rename guarded `portfolio` with
  `GUARD = "\x00PORTFOLIO\x00"`, and the guard itself contains `FOLIO`, so the
  `FOLIO` -> `CUE` pair rewrote the guard to `\x00PORTCUE\x00` and the restore
  had nothing to match. The protection failed one case fold away from working.

## The three defect shapes, for grading

1. **A quotation edited by a mechanical pass.** Reads perfectly; is a false
   attribution. `addresser.py` at base states that a 2026-08-20 ruling said
   `path@cue`.
2. **A retired term surviving in prose** where every identifier has moved on --
   `README.md`'s *Why* records the cost: a dead term is a context anchor, and an
   agent pulls toward the most common concept even when it is the wrong one.
3. **History presented as current documentation.** Roy, 2026-08-23: *"It simply
   isn't necessary to know the history to understand the code. It is a bad habit
   to think it needs it."* At base, `addresser.py`'s module docstring opens with
   30 lines about a superseded naming ruling.

! **A citation is not a repair.** The first fix replaced each quotation with a
pointer to a decision-log entry, and created the entries to point at. Roy:
*"Making a link referencing the change is just prose history laundering."* A
graded run that relocates the history and links to it has not passed.

## Graded as D13

See [`../../evals/discriminators.md`](../../evals/discriminators.md). The pass
criterion is that the run reports the prose as history or as a false
attribution -- not that it reflows or relocates it.
