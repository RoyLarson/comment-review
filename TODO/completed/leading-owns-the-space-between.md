# The space between two paragraphs belongs to nobody, so a page cannot be set back

```
Status:   in-progress
Progress: 11 of 11 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-21 (Roy, 2026-08-21, ruling on a `b` whose lines straddle an `a`: 'I
          like the leading solution even though it added another cues and the
          anchors are empty')
Triaged:  2026-08-23 — BOTH REMAINING BOXES CLOSE, one superseded and one finished, so
          every task on this file is now discharged. ! Task 6 said leading DOES carry a
          cue. It stopped: `addresser.py:206-213` says `LEAD` is NOT one of the four
          series `cue` emits, since 2026-08-22 -- Roy: *"it has no anchor, and so by the
          LSR ... it breaks that rule."* `page.py:197-207` says `d` IS OUT BECAUSE IT
          NAMES NO PLACE, *"and that is now the whole test."* MEASURED: an unfiltered
          census of `tests/fixtures/sample.py` prints leading rows with an EMPTY `@`.
          ! Task 11's verify clause is now met -- see the box. ! Requires-Roy cleared:
          both `*` boxes are ticked RULED and no decision is owed.
```

## Objective

**The space between two paragraphs belonged to nobody, so a page could not be set back.** A
fifth series, `leading`, owns it. Roy, 2026-08-21: *"I like the leading solution even though it
added another cues and the anchors are empty."*

!! **THE TRADE WORD IS `leading`** -- the strips of lead a compositor puts BETWEEN lines of type
to space them. Confirmed by Roy after the register check: a LEADER is the row of dots carrying
the eye across a table of contents, a different thing. **The series letter is `d`**, ruled the
same day: *"and d works."* ! `l` was the obvious choice and the worst possible character --
`m.py@l0` reads as `@10`, and the whole scheme rests on a cue being unmistakable.

**THE RULE, in Roy's words:** *"it covers all empty space between two different types of
paragraphs. If the new line is internal to the paragraph then the two paragraphs + the newlines
are in fact one paragraph."* So a blank run BETWEEN types is leading; a blank INSIDE a run stays
prose, and two runs separated by one are one paragraph -- which is what the lexer already does,
since only code ends a run.

!! **IT IS NOT CITABLE.** Roy: *"it does not need to be citable at all. There is no information
to rule on. It is just there for document preservation."* So it is excluded from `Page.prose`,
from record seeding, and from what a reviewer is handed.

!! **AND IT ENDED UP WITH NO ADDRESS AT ALL, which is further than the original design went.**
`addresser.py:206-213`: `LEAD` is not one of the four series `cue` emits, since 2026-08-22. Roy:
*"it has no anchor, and so by the LSR -- any child class has to be able to answer its parent
class's answers as well, correctly -- it breaks that rule."* `places` is `cue -> the line of code
it is attached to`; every other series answers, and a `d` answered `""`, which is the absence of
an answer rather than a different one. `page.py:197-207` then made *names no place* the whole
test for what a reviewer is owed a record on, replacing a list of series letters that had to be
kept current.

## Tasks

- [x] T1 -- * RULED 2026-08-21 -- A FIFTH SERIES, `leading`, OWNS THE SPACE BETWEEN
      PARAGRAPHS. Roy took it over the alternative he raised first, collapsing the
      blanks and having the compositor regenerate them: *"It is either this or one
      more foliator that gets the inbetween lines."* ! He accepted its two costs
      by name -- another cues, and anchors that are empty.
- [x] T2 -- !! THE TRADE WORD IS `leading` -- the strips of lead a compositor puts
      BETWEEN lines of type to space them. Confirmed by Roy after the register
      check: a LEADER is the row of dots carrying the eye across a table of
      contents, a different thing.
- [x] T3 -- THE RULE, in Roy's words: *"it covers all empty space between two different
      types of paragraphs. If the new line is internal to the paragraph then the
      two paragraphs + the newlines are in fact one paragraph."* So a blank run
      BETWEEN types is leading; a blank INSIDE a run stays prose, and two runs
      separated by one are one paragraph -- which is what the lexer already does,
      since only code ends a run.
- [x] T4 -- !! IT IS NOT CITABLE. Roy: *"it does not need to be citable at all. There is
      no information to rule on. It is just there for document preservation."* So
      it is excluded from `Page.prose`, from record seeding, and from what a
      reviewer is handed.
- [x] T5 -- * RULED -- THE SERIES LETTER IS `d`. Roy, 2026-08-21: *"and d works."* ! `l`
      was the obvious choice for `leading` and the worst possible character:
      `m.py@l0` reads as `@10`, and the whole scheme rests on a cue being
      unmistakable. `d` is free, unambiguous beside `a`, `b`, `c` and `f`, and
      cannot be misread as a digit.
- [x] T6 -- SUPERSEDED. It said leading DOES carry a cue, the letter settling it, and
      that the alternative considered was no address at all. **The alternative is
      what happened, on 2026-08-22.** `addresser.py:206-213` records `LEAD` as NOT
      one of the four series `cue` emits -- Roy: *"it has no anchor, and so by the
      LSR ... it breaks that rule"* -- and `page.py:197-207` makes *names no place*
      the whole test for what is owed a record, in place of the series list this
      box was defending. MEASURED 2026-08-23: an unfiltered census of
      `tests/fixtures/sample.py` prints its three leading rows with an empty `@`.
- [x] T7 -- !! WHY IT IS NEEDED, MEASURED 2026-08-21. A `b` owns the blanks on BOTH
      sides of an `a` -- ruled, and the covering is exact -- but a cue is ONE
      entry in the reading order, so its two lines emit together and the file
      comes back as blank-blank-comment where it was blank-comment-blank. Neither
      ordering fixes it; the `b`'s lines genuinely straddle the `a`.
- [x] T8 -- ! IT IS THE ORDINARY SHAPE OF A PYTHON FILE, not an exotic one: a licence
      header, a blank, the module docstring, a blank, the first import. MEASURED
      on `corpora/meta-package-manager`: 16 of 185 files straddle, 16 of 185 fail
      to set back, and the two sets are the same files. 1,470 docstrings sit
      behind that shape.
- [x] T9 -- MEASURED over 3,082 files: 3,049 byte-identical, 3,075 identical IGNORING
      NEWLINES, 7 differing in more than newlines. ! So 26 files are purely this
      defect. * Roy's third measure, ruled the same day: *"out ~= in if
      out.replace('\\n','') == in.replace('\\n','')"*, with a formatter run
      settling the rest -- which is what separates a spacing question from a
      defect.
- [x] T10 -- ! THE COLLAPSE-AND-REGENERATE ALTERNATIVE WAS MEASURED AND IS WHY THIS WON.
      Blank runs in that project are ONLY ever 1 or 2 lines -- 6,286 and 1,158,
      zero longer -- so a house rule could carry them. But the 1,158 twos are PEP
      8's gap between top-level definitions, what Black and ruff produce, so
      collapsing to one would reformat every file on a run meant to review
      comments. ! And 1,521 prose paragraphs carry an internal blank -- up to five
      -- which must stay verbatim.
- [x] T11 -- FINISHED. It read *"LEADING IS STILL HANDED TO A REVIEWER"*, citing 4
      leading rows on `tests/fixtures/sample.py` in a `--filtered` listing, the
      same count as unfiltered. Its own verify clause is now met. MEASURED
      2026-08-23 with `census.py --repo . [--filtered] tests/fixtures/sample.py`:
      the FILTERED listing shows **0** leading rows -- each is folded into a
      no-prose run and counted in the notes column (`1-leading, 1-margin`) -- while
      the UNFILTERED listing still shows them, as rows 9, 13 and 17. ! The count
      was 3, not 4.
