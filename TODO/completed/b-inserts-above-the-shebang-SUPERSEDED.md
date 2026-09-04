# An empty b whose gap opens on front matter inserts ABOVE the shebang

```
Status:   open
Progress: 4 of 4 tasks closed
Owner:    session
Requires-Roy: false
Raised:   2026-08-20 (found while rendering a page for the P3 ruling, 2026-08-20)
Superseded: 2026-08-20 — SUPERSEDED by Roy, 2026-08-20: *"that is the defect of reading
            line numbers as the address. They are not. I think the problem is that you
            see edit-lines somewhere and you are assuming that means that is where the
            edit goes."* !! THERE IS NO BUG. `original_start=1, original_end=0` on `b1` says the
            paragraph COVERS NOTHING and originally sat at the top of its gap. It does
            NOT say prose written there lands on line 1 -- where it lands is settled by
            the ADDRESS and the a -> b -> c application order, which is A4 and is not
            built yet. ! The finding was the session reading a line range as a position,
            which is the exact defect this branch exists to remove, reproduced by the
            person removing it. The field NAME invited it and is what actually needs to
            change -- `original_start`/`original_end`.
```

## Objective

An empty b whose gap opens on front matter inserts ABOVE the shebang.

## Tasks

- [x] T1 | FINISHED | unknown | !! MEASURED on a file with a shebang, a licence
      line, and a module docstring: `b1` is an empty interval with
      `original_start=1, original_end=0`, so writing it INSERTS AT LINE 1 --
      above `#!/usr/bin/env python3`, which stops being a shebang the moment
      anything precedes it. `b0` is the front matter itself, occupying lines
      1-2.
- [x] T2 | FINISHED | unknown | The cause is in `page.empty_places`, the GAP
      branch: `low = previous + 1` is 1, and 'A DOCSTRING IN THIS GAP MAKES THE
      EDIT AN INSERTION ABOVE IT' then sets `high = low - 1`. That rule is right
      for a docstring -- a comment above a module docstring is ordinary -- and
      wrong for front matter, which is pinned to line 1.
- [x] T3 | FINISHED | unknown | The wanted insert is line 3: BELOW the front
      matter, ABOVE the docstring. So `low` must first advance past any
      FRONT_MATTER lines at the top of the gap, and the
      insert-above-the-occupant rule applies from there.
- [x] T4 | FINISHED | unknown | It is only reachable when the gap's top is front
      matter, which needs a shebang or licence header AND a module docstring AND
      no code between them. Nothing in `tests/` had that shape -- add the
      fixture with the fix.
