# The census degrades silently on four inputs

```
Status:   in-progress
Progress: 5 of 8 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-19 (the seven-agent address review, 2026-08-19)
Measured: 2026-08-19 — the BOM case is worse than filed: the comment came back with
          address '' -- genuinely unaddressed, not merely misparsed -- with anchor set
          to the BOM character itself.
Closed:   2026-08-20 — task 4 -- 'an empty file yields zero blocks and has no a0, so an
          empty __init__.py is uncitable' -- is closed by the lexer/page split of
          2026-08-20. Measured: an empty file carries a0, b0 and b1, where it had
          nothing.
TRIAGED:  2026-08-23 — the file carried each of three defects TWICE, once in short form
          and once in full; the short forms are ticked SUPERSEDED by the fuller box that
          names the same defect, so the count stops reading as six problems where there
          are three. One more box is DONE -- the `--filtered` file boundary was fixed
          2026-08-22 and is re-verified below. Four remain, all re-measured today.
SPLIT:    2026-08-23 -- every box cut to two lines. The measurements and the reasoning
          each carried are in the Objective, where they were already half-stated.
Measured: 2026-08-29 — 2026-08-29 -- T1 DONE, and the mechanism was one layer lower than
          page.py:708. paragraphs_stdlib CATCHES the parse failure and returns one
          unparsed paragraph rather than raising, so commands/census.py's except never
          fired; page_for then gave that page no addresses and carried() hands over only
          addressed paragraphs, so even the paragraph reporting the refusal was filtered
          away. MEASURED, one file per run over one nine-line control: the control
          censused 11 paragraphs at exit 0, while a UTF-8 BOM, a syntax error, a NUL
          byte and an unterminated string each censused 0 PARAGRAPHS AT EXIT 0 -- while
          the same control's DECODE failures (latin-1, UTF-16) correctly exited 1. An
          unparsed page now joins unreadable, so both failure modes have ONE outcome:
          the file is named and the run exits 1, on the text path and on --json. ! T7 IS
          UNTOUCHED -- a BOM'd file is now LOUD, not READ; the readers still open with
          utf-8 rather than utf-8-sig.
```

## Objective

!! **FOUR INPUTS PRODUCE A CENSUS THAT IS WRONG RATHER THAN REFUSED, EACH EXITING 0.** The run
reads as complete, the addresses are nonsense, and nothing says so. `census.py` already holds the
opposite rule -- *"Every file handed in is censused, or this errors"* -- and these are the cases
that slip past it by parsing far enough to produce blocks.

**A Python file that fails `ast.parse` is censused with NO ADDRESSES AT ALL.** MEASURED
2026-08-23 on `'# one\nx = = 1\n# two\n\n# three\ny = 2\n'`: three paragraphs come back --
`matter`, `unparsed`, `comment` -- and every one has an empty `address`. `page.py:708` is the
branch: `if not any(b.kind == "unparsed" for b in got)` guards the whole of the addressing pass,
so no place is emitted, `document_declarations` never runs, and the prose is handed on unaddressed.
! **That is a CHANGE from what this file recorded**, which was three blocks collapsed onto `@b0`.
An empty address is worse in one way and better in another: nothing is misfiled onto a place that
belongs to something else, and nothing can be cited at all. ! Two failure modes for one
condition: a `TokenError` (`def f(:`) is a hard NOT CENSUSED at rc 1, a `SyntaxError` (`x = = 1`)
is a soft `unparsed` block at rc 0.

! **AND `references/compact.md:100` DESCRIBES A THIRD THING.** It says of `unparsed` *"the file
did not parse, so nothing was censused"* -- false, re-verified 2026-08-23: the comment blocks ARE
censused and handed to reviewers; they simply have no addresses.

**A UTF-8 BOM makes any Python file unparseable** -- the readers open with `encoding="utf-8"`
rather than `utf-8-sig` (`repo.py:52`, `census.py:336`, `census.py:177`), and the BOM survives
into `ast.parse`. VERIFIED 2026-08-20 and again 2026-08-23 on a BOM'd module holding a module
docstring: one `unparsed` paragraph, EMPTY address, no places, exit 0 -- the docstring is in the
file and absent from the census. **That breaks the contract `CLAUDE.md` calls absolute** -- every
file handed in is censused or the run stops. Routine on Windows, which is where this repo is
developed. ! The lexical half of the same encoding bug is filed as
[`bom-is-read-as-source`](bom-is-read-as-source.md); one change fixes both.

**A one-line `def f(): pass` has an `a` place that writes ABOVE the `def`.** MEASURED end to end
2026-08-23: `page_for` gives `a1` an anchor of `def f(): pass` and a range of `0-0`, and putting
`"""What f does."""` at `m.py@a1` through `galley.reset` and `compositor.set_page` returns

```
"""What f does."""
def f(): pass
```

-- the docstring is now the MODULE's. `galley.reset` reported no problem. Also hits `@overload`
and `class C: pass`.

! **NO APPLICATION ORDER FIXES IT, and it is not a collision with `a0`:** an address is not an
edit range, and the f -> a -> b -> c order settles two places that share an insertion point. This
is different -- there is no line INSIDE the body to write on, and making one needs the line
SPLIT, which is a code change stage 7b forbids. ! So the shape of the answer is that the place is
UNWRITABLE and an `add` on it is REFUSED with a reason, rather than landing above the `def`.

**An empty file yields zero blocks and has no `a0`** -- CLOSED 2026-08-20, see the header.

! **AND ONE BOUNDARY DEFECT IS FIXED.** `--filtered` used to drop a whole file from the listing a
reviewer is handed: the no-prose run was never flushed at a file boundary and `flush_run` prints
under `heading(first.path)`, so censusing `a.py` then `b.py` printed one run spanning both under
`== a.py` and `b.py` never appeared. `census.py:566-568` now flushes when `b.path != run_path`.
VERIFIED 2026-08-23: `--filtered` over three fixtures printed three headings, each run under its
own file.

## Tasks

- [x] T1 | FINISHED | unknown | T1 -- Give an unparseable Python file ONE
      outcome at `page.py:708`, both failure modes. Verify: censusing `x = = 1`
      exits non-zero, or its paragraphs are addressed.
- [x] T2 | FINISHED | unknown | T2 -- SUPERSEDED by T7, which is the same defect
      stated in full with its verification date. The BOM is one encoding
      argument in three readers.
- [x] T3 | FINISHED | unknown | T3 -- SUPERSEDED by T6, which is the same defect
      stated in full and says what has to be decided.
- [x] T4 | FINISHED | unknown | T4 -- DONE 2026-08-20. An empty file now carries
      `a0`, `b0` and `b1`, so an empty `__init__.py` is citable. Closed by the
      lexer/page split.
- [ ] T5 | T5 -- Correct `references/compact.md:100` -- it says an `unparsed`
      file was not censused, and it was. Verify: the row says the paragraphs
      carry no address.
- [ ] T6 | T6 -- Refuse an `add` at the `a` place of a one-line declaration
      instead of writing above the `def`. Verify: `galley.reset` returns a
      problem for that edit, not `[]`.
- [ ] T7 | T7 -- Open the three readers with `utf-8-sig` -- `repo.py:52`,
      `census.py:336`, `census.py:177`. Verify: a BOM'd `.py` censuses its
      module docstring.
- [x] T8 | FINISHED | unknown | T8 -- DONE 2026-08-22. `census.py:566-568`
      flushes `--filtered` at a file boundary; three fixtures print three
      headings. Measurement in the Objective.
