# Commits this system can be graded against

**A fixture is a CHECKOUT AT A HASH, and a fix commit is an ANSWER KEY.** Ruled in
[`the-harness-cannot-run-the-system-it-grades`](../TODO/the-harness-cannot-run-the-system-it-grades.md):
this repo's own history is a fixture source, because the commit that fixes a prose defect says
what the defect was and what the correct prose is.

!! **EVERY CASE HERE IS A `module-context` FINDING**, and that is what makes them gradeable. That
role asks *do the comments say this module is ONE set of ideas, and does the documentation
account for what the module exposes?* Each case below is a docstring announcing one subject over
a module that holds several -- readable from the file alone, with no knowledge of this session.

! **They are all from `3af9752..7026646`**, branch `fix/folio-placement-is-not-where-the-anchor-is`,
2026-08-19 to 2026-08-20.

## How to run one

```bash
git worktree add <dir> <commit>^{}~1      # the tree BEFORE the fix
# run /comment-review over the file named in the row
git diff <commit>^{}~1 <commit>^{}         # the answer key
```

! The tags are annotated, so `^{}` is needed wherever a commit is wanted. ! Grade from the DIFF,
never from the run's own report -- self-reported confidence has been measured not to
discriminate real findings from fabricated ones.

## The cases

| # | the file, before | what its docstring said | what the module actually held | fixed by |
| --- | --- | --- | --- | --- |
| 1 | `census.py`, **1,759 lines** | *"Stage 2, COLLATE: the pCST -- every line of these files classified"* | one file's paragraphs, AND their addressing, AND the aggregation across files. **Three subjects** | `b342cd1`, `07d40b8` |
| 2 | `page.py`, 220 lines | *"What a pCST NODE is"* | a node, and no PAGE at all -- the module was named for a thing it did not implement | `4daf7be` |
| 3 | `page.py`, **1,543 lines** | *"A PAGE: one file, its paragraphs in order"* | that, plus 709 lines of language-specific LEXING -- the `Language` record, both tier readers, the text helpers | `bfc3441` |
| 4 | `lexer.py` at its split | -- | the reader BUILDS a `Paragraph` and states its anchor, so the type belongs with it. The kinds split on the same line: a reader emits prose it FOUND, a page adds where prose is MISSING | `bfc3441` |
| 5 | `addresser.py`, 835 lines | *"An address that survives the edits this tool makes"* | the FOLIATION -- it supplies a folio and flattens a path. **The address is composed in `page.py`** | `93cc4b0` |

## Why each is findable by reading, not by knowing

**1 -- `census.py`.** The docstring announces stage 2 and the classification of lines. The module
also contains `address()` calls per paragraph, `anchor_every_address()`, the file walk, the name
corpus and the listing. A reader asking *is this one set of ideas* has the whole answer in the
file. ! Roy, 2026-08-20: *"the census's job should be to take the output of all of the pages and
reformat it into the (most) usable format for the agents."*

**2 -- `page.py` had no `Page`.** The module is named `page`, its docstring says what a NODE is,
and `grep "^class"` returns `Paragraph` and nothing else. **The name and the contents disagree,
and the file says so on its own.**

**3 -- the lexer inside the page.** 709 lines answering *how does this language mark its prose*
sat under a docstring about what a page is. Measurable from the file: the `Language` dataclass,
an eleven-row table, two tier readers, and the text helpers, none of which is about a page.

**4 -- what the lexer emits.** The reader constructs the paragraph and states its anchor -- the
exact characters of the line of code -- so the type is the reader's output, not the page's
input. ! A reader emits `comment`, `docstring`, `trailing-comment`, `unparsed`; a page adds
`interval`, `margin`, `undocumented`. **The kinds split exactly where the modules do.**

**5 -- `addresser.py` addressed nothing.** `grep '@{' ` over the tree answers it: the address is
built in `page.py`. Roy, 2026-08-20: *"we have been using that word instead of address all
session ... it doesn't cause the system to crash but it also doesn't make the system work
correctly either."*

## What is NOT a test case for this system

! **Process defects are not prose defects.** A plan checkbox ticked on work that was not done, a
test decorator that reports an unexpected success, a hand-written fixture -- all were found in
this range and all were valuable, and **none is something `/comment-review` could find.** It
reads comments and docstrings against the code they sit with; it has no remit over a plan, a
test harness or a fixture file. Recording them here would measure the system against work it
does not do.

## What has not been done

! **None of these was found by `/comment-review`.** Every one was found by a person reading.
Running the system over them is the point of recording the range, and
[`the-harness-cannot-run-the-system-it-grades`](../TODO/the-harness-cannot-run-the-system-it-grades.md)
is what blocks it.

! **The suite was green throughout** -- 672 to 713 passing across all five, and every gate green
too. `module-context` is the only thing in this repo that could have caught any of them.
