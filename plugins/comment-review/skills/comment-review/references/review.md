# Stage 8 -- REVIEW: the finished page

**This stage sees the finished page. Every earlier one saw a plan.**

It is deliberately ALL-ENCOMPASSING. It reads the result as a whole and decides whether these
files are done or whether another comment-review round is wanted. Almost no editorial review
finishes in one round -- each pass refines what the next one works on, and this is where that
judgement is made.

! **Your whole input is the file list, the style sheet, and this file.** Everything you need is
on the page and in the code beside it.

Read each file end to end, as a reader would, and ask of every comment and docstring:

- Does it follow the **style sheet's template** for its kind?
- Is it still appropriate to the **code it is attached to**?
- Are its **sentences checkable claims** about that code?
- Does it state the **reasons, constraints and worked examples** that code needs?

And of the file as a whole: does it still read as one page? Look for --

- **a block that is no longer a proposition** -- a sentence ending mid-clause, a hanging clause
  under a deleted line, a contrast marker whose contrast went. Measured repeatedly, and it
  passes every mechanical check there is: it is not stale, not misplaced, not false -- it is
  ungrammatical, and nothing else asks whether the prose still parses.
- **runs that merged** -- an `add` landing next to an existing block across a blank line makes
  one longer run. A compliant edit producing a violation, visible only here.
- **the same sentence now in two places**, because a `move` landed beside one that already said
  it.
- **drift against the style sheet** -- dialect, capitalisation, citation form.

## What this pass may NOT do

! **Do not edit.** You read and you report; the human decides what happens next. That holds for
a defect this run created and for one that was already there.

! **Do not rewrite for quality.** A better wording you notice is a finding for the next round,
not a licence to write it: the text on the page is what a human approved, and writing over it
puts prose on disk nobody read.

## Report

Two outcomes, and say which.

**Everything answers yes** -- the files are done, and say so plainly.

**Anything answers no** -- bring that section to the human as potentially something to fix,
naming what and where.

Separately, every defect that predates this run. That list is the next round's input and must
not be folded into the first.

## Looking a place up, after the write

!! **EVERY LINE NUMBER IN THE RECORDS IS STALE BY THE TIME YOU READ.** 7b has
written, so each edit moved every line below it. What did NOT move is the
ADDRESS a record carries -- `pkg.mod.py@b3` is the same place before and after,
because it names a spot against the CODE and 7b proved the code byte-identical.

Census the file as it is NOW, then ask:

```bash
python <skill>/scripts/census.py --json --repo . --out <run-dir>/after.json <paths...>
python <skill>/scripts/addresser.py --census <run-dir>/after.json --repo . --resolve <ADDRESS>
```

Out come the lines that cover it today, so a claim you want to re-check against
the source can be found without counting the run's own edits.

! **Do not resolve against the census the run STARTED from.** It answers with
the numbers 7b invalidated, confidently and wrongly -- and the addresser refuses
a census older than the file rather than answering from it, so a stale one
reports `STALE CENSUS` instead of a line range.

! A place can hold more than one block -- a docstring and the comment run under
it sit in the same gap -- so more than one range can come back. Both are real.
