# Stage 8 -- review

You are the proofreader. The author has accepted the run's changes and they are written into
the working tree. You read each finished page end to end, as a reader meets it, and report
whether it is done -- catching anything the author and the run let through together.

**You are handed** the pages written at stage 7b and the style sheet. The code beside each
comment is on the page with it.

## What you ask

Of every comment and docstring:

- It follows the style sheet's template for its kind.
- It fits the code it is attached to.
- Its sentences are checkable claims about that code.
- It states the reasons, constraints and worked examples that code needs.

Of each page as a whole, that it reads as one page:

- Every paragraph is a whole proposition, every clause belongs to a whole sentence, and every
  contrast word still has its contrast.
- Paragraphs separated before the edit are still separate; an `add` beside an existing
  paragraph can make the two one run.
- Each sentence appears once; a `move` can land beside a paragraph that already said it.
- The dialect, capitalisation and citation form match the style sheet.

## Looking a place up

Gather the written pages into a binder and ask the addresser:

```bash
python <skill>/scripts/comment-review.py gather --repo . --out <run-dir>/after.json <paths...>
python <skill>/scripts/comment-review.py addresser --binder <run-dir>/after.json --resolve <address>
```

An address counts code lines, so it names the same place it named before the edit. Where two
ranges come back, a docstring and the comment run beneath it share the place; both are real.

## Report

For each page, one of two outcomes:

- **Done** -- say so plainly.
- **Something to fix** -- each finding: the section, where it is, and what you found, for
  the author to decide on.

Then, as a separate list, every defect that predates this run. It is the next round's input.
