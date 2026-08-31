# Front matter is absorbed by an interval, and the galley then deletes it

```
Status:   in-progress
Progress: 6 of 6 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-20 (both reviews of 2026-08-20, independently; verified in-session)
Fixed:    2026-08-20 — 2026-08-20 -- fixed by giving front matter ITS OWN SERIES rather
          than by carving an exception. Roy: *"we should have just made the front matter
          its own foliation -- then the rule that b owns all the lines that are not
          another foliation's lines would explicitly stay true. Treating the front
          matter as regular comments, even though they are not, is the mistake."* ! An
          earlier fix that DID carve the exception -- naming front matter twice inside
          `fill_the_gaps` -- was written, measured working, and reverted for this.
          MEASURED after: over 662 corpus files, 51 paragraphs reporting no lines became
          0, and the licence headers reported as `interval` are gone. The `exact` rule
          now reads *every series but `b`* and names nothing.
Triaged:  2026-08-23 — RE-VERIFIED IN THE CODE, and the last box is closed. `page.py:914-
          922` builds `exact` as `series and series != GAP and b.original_start and
          b.original_end`, so it names no series and carves no exception; the comment at
          `page.py:901-906` states the reason -- *"`f` IS IN THAT LIST BECAUSE IT IS A
          SERIES, not because it is front matter."* ! Requires-Roy cleared: the ruling
          the last box waited on was MADE on 2026-08-20 and is quoted in `Fixed:` above,
          and a ruling already made carries no box.
```

## Objective

**Front matter was absorbed by an interval, and the galley then deleted it.** The fix landed
2026-08-20 by giving front matter its own series, `f`, rather than by naming it in the gap
filler.

!! **THE RULING IS THE OBJECTIVE, and it is Roy's, 2026-08-20**: *"we should have just made the
front matter its own foliation -- then the rule that b owns all the lines that are not another
foliation's lines would explicitly stay true. Treating the front matter as regular comments, even
though they are not, is the mistake."*

! **THE TWO CANDIDATES THE LAST BOX HELD OPEN ARE BOTH ANSWERED BY IT.** The box asked whether
`fill_the_gaps` should exclude a paragraph whose cue is not the gap's own (a one-line fix) or
whether `b0` should stop being in the `b` series (a design change). **The design change is what
happened**, and it went further than the box proposed: front matter is not a `b` at all.
VERIFIED 2026-08-23 at `page.py:914-922` -- `exact` collects every paragraph whose series is not
`GAP`, so the rule reads *every series but `b`* and names nothing. `page.py:901-906` records why
`f` is in that list: *"because it is a SERIES, not because it is front matter."*

! **AND LEADING JOINED THAT LIST BY ITS SYMBOL RATHER THAN ITS ADDRESS**, since `d` gave up its
address -- `page.py:908-913`. Read from `address` alone the walk returned `""` for a `d`, the
gap took the blank lines a run of leading already held, and they were set TWICE. That is a
separate defect, already closed, and it is recorded here only because it is the same line of
code.

## Tasks

- [x] T1 | FINISHED | unknown | T1 -- !! VERIFIED. On `#!/usr/bin/env python` /
      `# Copyright 2024` / `"""Module doc."""` / `X = 1`: `@b0` is the
      front-matter comment with `orig=(None,None)` and `raw=[]` -- it owns
      NOTHING -- while `@b1`, an INTERVAL, owns lines 1-2 with `raw_lines`
      holding the shebang and the copyright. An `interval` is the kind the
      census tells four reviewers holds no prose, and the only thing an `add`
      may cite.
- [x] T2 | FINISHED | unknown | T2 -- !! SO AN `add` ON `b1` REPLACES THE
      LICENCE HEADER, SILENTLY, rc=0. `paragraph_matches` passes because
      `raw_lines` matches the file exactly. Demonstrated end to end by one
      review: the shebang, copyright and module docstring were gone from the
      galley output with 0 edits refused.
- [x] T3 | FINISHED | unknown | T3 -- CAUSE, `page.py` `fill_the_gaps`: `here`
      collects every paragraph whose cue starts with `b` AND whose `start` falls
      in the gap. Front matter carries `b0`, a place that is NOT that gap --
      `attach` gives it `b0` wherever it sits -- so `b0` and the gap's own `bN`
      are re-cut against each other.
- [x] T4 | FINISHED | unknown | T4 -- AND THE SAME LINE DOUBLE-OWNS A DOCSTRING.
      `here[-1].end = free[-1]` spans contiguously and ignores the `exact` lines
      an `a`/`c` holds INSIDE the span. On `def f():` / blank / `"""Doc."""` /
      blank / `return 1`, `@b2` gets 2-4 and `@a1` is line 3. Two paragraphs own
      line 3, against `docs/addressing.md` and against the ruling in the commit
      that introduced it.
- [x] T5 | FINISHED | unknown | T5 -- !! INTRODUCED BY 4d576d3, 2026-08-20 --
      this session's own work, hours after Roy ruled *"a's and c's own their
      lines exactly, b's own all the other lines."* The code three lines below
      that comment does not do it.
- [x] T6 | FINISHED | unknown | T6 -- * RULING MADE, NOT OWED, so this carries
      no work. It asked whether `fill_the_gaps` must exclude a paragraph whose
      cue is not the gap's own, or whether `b0` must stop being in the `b`
      series. **Roy ruled the second on 2026-08-20** -- front matter gets its
      own foliation -- and the code did it: VERIFIED 2026-08-23,
      `page.py:914-922` builds `exact` from `series != GAP`, naming no series
      and carving no exception, with the reason stated at `page.py:901-906`. A
      ruling already made is not a task.
