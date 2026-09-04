# A non-code document has no read, review, resolve or write chain of its own

```
Status:   open
Progress: 0 of 2 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-09-03 (Addressing 21, 2026-09-03 -- the remaining pieces external_address
          waits on)
```

## Objective

A non-code document has no read, review, resolve or write chain of its own.

Roy, 2026-09-03, naming what "the remaining pieces" in Addressing 21 means:
*"the parallel flows and parts required for reading, reviewing, editing, writing
these files that the current code specific system does. It is a whole editorial
resolving system that has to be added to the current code to make it possible."*

The code chain's 8 stages -- GATHER, FIND REFERENCES, MARK, APPLY, COMPACT,
PRESENT/WRITE, REVIEW -- all assume a page: cues, a sha, a galley and a
compositor that sets prose back into the room the cues name. A referenced
document a role cites and recommends a change to has none of that, and two of
the four pieces this needs are already filed elsewhere:

| piece | status |
| --- | --- |
| WRITE | a-reference-needs-its-own-write-chain -- filed, deferred pending the code chain working end to end |
| SELECTION | reference-only-misses-the-documentation -- filed, three rulings owed |
| READ | not filed until now. Measured: `Binder` carries only `pages`; no `pulled`, no `references` |
| MARK/APPLY | not filed until now. Nothing today lets a role's finding against an external address become an alteration the docket can carry |

T1 is the whole chain, T2 is running it alongside the code chain in one pass.
Both are broad by design -- this is the objective the two filed pieces plug
into, not a replacement for either of them.

## Tasks

- [ ] T1 | Implement a read, editorial review, resolution and write chain for
      non-code documents. Verify: a document reaches a role, a finding
      round-trips to approval, and the file sets back changed
- [ ] T2 | Wire the document chain into the code one, so one run changes both.
      Verify: a run touching a code file and a cited document proposes and
      applies changes to each
