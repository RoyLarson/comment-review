# The census emits rows, not pages, and page.py defines no Page

```
Status:   open
Progress: 0 of 7 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-19 (Roy, 2026-08-19: 'I don't think there is any pagish like things
          happening right now even though it should')
```

## Objective

The census emits rows, not pages, and page.py defines no Page.

## Tasks

- [ ] !! `page.py` DEFINES NO `Page` -- only `Paragraph`. The module is named for
      a concept it does not implement, and the vocabulary defines a page as ONE
      FILE: its paragraphs in order, among the code they sit with.
- [ ] What a reviewer is handed is ROWS: `print(f'{i:4d}  @{at}  {span}  {kind}
      {lines}L  {notes}')` under a `== path` heading. A row list is not a page,
      and `--filtered` collapses runs so it is not even a complete list.
- [ ] !! THE CENSUS STACKS PAGES. Roy: 'make the census stack the pages together
      for the agents to review -- the pages should actually be the pages, not just
      a small piece of the pages.' The census is the enumeration across every page
      in scope; one page is one file.
- [ ] A reviewer rules on prose IN THE CODE IT SITS WITH, which is what a page is
      for. Decide what a page renders as -- the file with its addresses in the
      margin is the obvious candidate, and it is what makes an anchor readable
      without a second lookup.
- [ ] Verify against `tests/fixtures/python_edge_cases.md`: a role handed the PAGE
      can see that a0 and b1 sit either side of the module docstring, which no row
      list shows.
- [ ] !! THE PAGE BUILDS ITSELF; THE CENSUS FORMATS EVERY PAGE. Roy, 2026-08-20:
      'seems like the census's job should be to take the output of all of the
      pages and reformat it into the (most) usable format for the agents.' The
      vocabulary already said it -- the census is the enumeration across EVERY
      page in scope, not one page as a list -- so `census_for` is misnamed: it
      builds a PAGE, and moves with `intervals`, `margins`, `_undocumented`,
      `fill_the_gaps` and `mark_front_matter`, about half of census.py's 1,759
      lines.
- [ ] !! 'MOST USABLE' IS MEASURED OR THE WORD DOES NOT SHIP. Roy: 'most is
      subjective but measurable in that sentence ... we can test formats and find
      if one is better than the others.' ! Every format decision so far was graded
      on SIZE -- 80,912 of the listing's 205,753 bytes were repeated paths (39%),
      `--filtered` saved 61%. Bytes are the COST; nothing has measured the
      BENEFIT. `evals/grade_hazards.py` scores a run from its DIFF against twelve
      planted hazards, so: vary the format, hold the rest, compare recall. !
      Blocked on the-harness-cannot-run-the-system-it-grades, because a hand-run
      comparison is what that TODO exists to end.
