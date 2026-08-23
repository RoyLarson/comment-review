# The space between two paragraphs belongs to nobody, so a page cannot be set back

```
Status:   open
Progress: 0 of 10 tasks done
Owner:    session
Requires-Roy: true
Raised:   2026-08-21 (Roy, 2026-08-21, ruling on a `b` whose lines straddle an `a`: 'I
          like the leading solution even though it added another cues and the
          anchors are empty')
```

## Objective

The space between two paragraphs belongs to nobody, so a page cannot be set back.

## Tasks

- [ ] * RULED 2026-08-21 -- A FIFTH SERIES, `leading`, OWNS THE SPACE BETWEEN
      PARAGRAPHS. Roy took it over the alternative he raised first, collapsing the
      blanks and having the compositor regenerate them: *"It is either this or one
      more foliator that gets the inbetween lines."* ! He accepted its two costs
      by name -- another cues, and anchors that are empty.
- [ ] !! THE TRADE WORD IS `leading` -- the strips of lead a compositor puts
      BETWEEN lines of type to space them. Confirmed by Roy after the register
      check: a LEADER is the row of dots carrying the eye across a table of
      contents, a different thing.
- [ ] THE RULE, in Roy's words: *"it covers all empty space between two different
      types of paragraphs. If the new line is internal to the paragraph then the
      two paragraphs + the newlines are in fact one paragraph."* So a blank run
      BETWEEN types is leading; a blank INSIDE a run stays prose, and two runs
      separated by one are one paragraph -- which is what the lexer already does,
      since only code ends a run.
- [ ] !! IT IS NOT CITABLE. Roy: *"it does not need to be citable at all. There is
      no information to rule on. It is just there for document preservation."* So
      it is excluded from `Page.prose`, from record seeding, and from what a
      reviewer is handed.
- [ ] * RULED -- THE SERIES LETTER IS `d`. Roy, 2026-08-21: *"and d works."* ! `l`
      was the obvious choice for `leading` and the worst possible character:
      `m.py@l0` reads as `@10`, and the whole scheme rests on a cue being
      unmistakable. `d` is free, unambiguous beside `a`, `b`, `c` and `f`, and
      cannot be misread as a digit.
- [ ] ! SO IT DOES CARRY A CUE, which the letter settles. The alternative
      considered was no address at all -- an address is what makes a thing
      citable, and this is not -- but a cue keeps `Cues.reading` a plain
      list of cues and keeps the compositor a lookup. ! WHAT IT IS NOT is SEEDED
      or handed to a reviewer; uncitable is enforced there, not by withholding the
      address.
- [ ] !! WHY IT IS NEEDED, MEASURED 2026-08-21. A `b` owns the blanks on BOTH
      sides of an `a` -- ruled, and the covering is exact -- but a cue is ONE
      entry in the reading order, so its two lines emit together and the file
      comes back as blank-blank-comment where it was blank-comment-blank. Neither
      ordering fixes it; the `b`'s lines genuinely straddle the `a`.
- [ ] ! IT IS THE ORDINARY SHAPE OF A PYTHON FILE, not an exotic one: a licence
      header, a blank, the module docstring, a blank, the first import. MEASURED
      on `corpora/meta-package-manager`: 16 of 185 files straddle, 16 of 185 fail
      to set back, and the two sets are the same files. 1,470 docstrings sit
      behind that shape.
- [ ] MEASURED over 3,082 files: 3,049 byte-identical, 3,075 identical IGNORING
      NEWLINES, 7 differing in more than newlines. ! So 26 files are purely this
      defect. * Roy's third measure, ruled the same day: *"out ~= in if
      out.replace('\\n','') == in.replace('\\n','')"*, with a formatter run
      settling the rest -- which is what separates a spacing question from a
      defect.
- [ ] ! THE COLLAPSE-AND-REGENERATE ALTERNATIVE WAS MEASURED AND IS WHY THIS WON.
      Blank runs in that project are ONLY ever 1 or 2 lines -- 6,286 and 1,158,
      zero longer -- so a house rule could carry them. But the 1,158 twos are PEP
      8's gap between top-level definitions, what Black and ruff produce, so
      collapsing to one would reformat every file on a run meant to review
      comments. ! And 1,521 prose paragraphs carry an internal blank -- up to five
      -- which must stay verbatim.
