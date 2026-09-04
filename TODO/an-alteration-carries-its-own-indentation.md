# An alteration carries its own indentation and nothing says so

```
Status:   open
Progress: 1 of 3 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-25 (a Task 12 review observation, 2026-08-25, reproduced on the write-
          chain branch)
```

## Objective

An alteration carries its own indentation and nothing says so.

!! **THIS FILE AND [`strip-and-fill-the-markers`](strip-and-fill-the-markers.md)
SPECIFY OPPOSITE CONTRACTS, AND ONE RULING CLOSES BOTH.** Found 2026-09-02 by a
cross-TODO sweep; neither file cited the other.

| | says |
| --- | --- |
| **here** | the AGENT supplies the indentation and the markers -- `Vocabulary: #27`, T2 `[x]` at `f087cd1` |
| **there** | the SYSTEM strips markers and indentation before a role sees a paragraph, and fills them back |

! **THE RULED POSITION IS THIS ONE**, and it is what the code does. Roy,
2026-08-28: *"I don't want to have to figure out indentation again or comment
style. All of the agents can read the page again on their own."*

! **AND THE COUNTER IS ROY'S TOO, ONE DAY LATER, AND WAS NEVER LOGGED.**
2026-08-29: *"having the whole text comment marks and all is brittle ... We may
need to rethink this and strip/fill in the comment marks ourselves."* No
`decision-log.md` entry records it, so `Vocabulary: #27` stands unretracted while
a whole TODO is written against it.

! **THE BOX THAT HOLDS THE RULING IS `strip-and-fill-the-markers` T9**, added
2026-09-02. That file was created `Requires-Roy: true` and lost the flag to the
five-marks migration, so the decision had no box anywhere until then.

!! **WHEN IT IS RULED, CLOSE THE LOSING SIDE IN THE OTHER FILE.** If `#27`
stands, `strip-and-fill-the-markers` is superseded whole. If the strip/fill
design wins, `#27` is superseded and T1 and T3 here go with it -- T3's test
(*"an unindented replacement lands at column 0"*) is the exact behaviour strip/fill
removes, and T1's docstring sentence becomes a false claim about the code.
**Neither file may be worked until then**: building either reverts the other.

## Tasks

- [ ] T1 | Say it in docket/docket.py's docstring: the replacement carries its
      own leading whitespace, and the galley adds none
- [x] T2 | RULED 2026-08-28 -- the AGENT supplies the indentation. decision-log Vocabulary 27: a row carries raw_text that round-trips to the root's exact bytes, indentation and comment markers included | f087cd1 | Decide
      whether the desk supplies the indentation or the agent does. Requires-Roy,
      and it decides what an alteration looks like
- [ ] T3 | A test that pins the measured behaviour -- an unindented replacement
      lands at column 0, an indented one does not. Verify: it fails if the
      galley starts adding whitespace
        > 2026-09-03 strip/fill T9 also decides compose granularity -- Open 5 there
