# Front matter is absorbed by an interval, and the galley then deletes it

```
Status:   open
Progress: 0 of 6 tasks done
Owner:    session
Requires-Roy: true
Raised:   2026-08-20 (both reviews of 2026-08-20, independently; verified in-session)
```

## Objective

Front matter is absorbed by an interval, and the galley then deletes it.

## Tasks

- [ ] !! VERIFIED. On `#!/usr/bin/env python` / `# Copyright 2024` / `"""Module
      doc."""` / `X = 1`: `@b0` is the front-matter comment with
      `orig=(None,None)` and `raw=[]` -- it owns NOTHING -- while `@b1`, an
      INTERVAL, owns lines 1-2 with `raw_lines` holding the shebang and the
      copyright. An `interval` is the kind the census tells four reviewers holds
      no prose, and the only thing an `add` may cite.
- [ ] !! SO AN `add` ON `b1` REPLACES THE LICENCE HEADER, SILENTLY, rc=0.
      `paragraph_matches` passes because `raw_lines` matches the file exactly.
      Demonstrated end to end by one review: the shebang, copyright and module
      docstring were gone from the galley output with 0 edits refused.
- [ ] CAUSE, `page.py` `fill_the_gaps`: `here` collects every paragraph whose
      folio starts with `b` AND whose `start` falls in the gap. Front matter
      carries `b0`, a place that is NOT that gap -- `attach` gives it `b0`
      wherever it sits -- so `b0` and the gap's own `bN` are re-cut against each
      other.
- [ ] AND THE SAME LINE DOUBLE-OWNS A DOCSTRING. `here[-1].end = free[-1]` spans
      contiguously and ignores the `exact` lines an `a`/`c` holds INSIDE the span.
      On `def f():` / blank / `"""Doc."""` / blank / `return 1`, `@b2` gets 2-4
      and `@a1` is line 3. Two paragraphs own line 3, against `docs/addressing.md`
      and against the ruling in the commit that introduced it.
- [ ] !! INTRODUCED BY 5fd5baf, 2026-08-20 -- this session's own work, hours after
      Roy ruled *"a's and c's own their lines exactly, b's own all the other
      lines."* The code three lines below that comment does not do it.
- [ ] * RULING WANTED: front matter is a `b` that is NOT its gap's `b`. Either
      `fill_the_gaps` must exclude a paragraph whose folio is not the gap's own,
      or `b0` needs to stop being in the `b` series for this purpose. The first is
      a one-line fix and the second is a design change; which one is Roy's.
