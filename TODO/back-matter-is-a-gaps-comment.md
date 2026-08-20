# Back matter has the same problem front matter had, and lands in the closing gap

```
Status:   open
Progress: 1 of 4 tasks done
Owner:    session
Requires-Roy: true
Raised:   2026-08-20 (Roy, 2026-08-20: 'the problem with head is what happens if there
          is a tail. Many text documents have both')
Ruled:    2026-08-20 — 2026-08-20 -- ONE SERIES FOR THIS LABEL TYPE. Roy: front matter
          and back matter are both `f`; the address says the file's own matter, not
          which end of the file it sits at. ! AND THE GENERAL RULE THAT COMES WITH IT:
          *"we may find another specific type that doesn't match these four's purposes,
          so keep the code generic in how it picks it up even if we don't know the
          shape. That is how we got into the bind of trying to pick up the matter -- we
          kept trying to push it in instead of considering it was its own thing."* Acted
          on: `foliator.SERIES` is now the only list of them, `foliate` counts the
          foliators rather than naming them, `--series` offers whatever is in the list,
          and `page.empty_places` RAISES on a series it has no branch for rather than
          dropping the place silently. Five tests guard it. ! What is still open here is
          the RECOGNITION half -- nothing looks for matter at the bottom of a file.
```

## Objective

Back matter has the same problem front matter had, and lands in the closing gap.

## Tasks

- [ ] !! THE ARGUMENT THAT MOVED FRONT MATTER APPLIES UNCHANGED. A licence at the
      BOTTOM of a file, a vim modeline, a colophon -- each belongs to the FILE and
      not to the gap in the code above it. Today it lands in the closing `b`,
      which is a gap between code and the end of the file, exactly as front matter
      used to land in `b0`.
- [ ] The `f` series is already built to take it. Roy, 2026-08-20: *"maybe it will
      show up in more places for copyright or other pieces in the docs files."*
      `FRONT` counts like any other series, so a second emission is `f1` and
      nothing else changes -- and the empty kind was named `dark-matter` rather
      than `head` FOR this: Roy, *"what happens if there is a tail? Many text
      documents have both."*
- [ ] What is missing is the RECOGNITION half: `mark_front_matter` asks a
      positional question about the top of the file. There is no equivalent for
      the bottom, and the signals are the same bespoke-rule problem Roy named for
      front matter without a docstring.
- [x] * RULING WANTED: whether back matter is the SAME series as front matter --
      one `f` series holding the file's own matter wherever it sits -- or its own.
      One series keeps the rule 'each series owns its lines exactly' with no
      addition; two make the address say which end.
