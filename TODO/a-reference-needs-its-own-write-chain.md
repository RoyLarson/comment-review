# A reference needs its own write chain, and it is NOT YET

```
Status:   deferred -- waits on the middle piece working end to end (Roy, 2026-08-27:
          "is a todo for the future Not Yet - i want the middle piece to work first")
Progress: 0 of 3 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-27 (Roy, answering whether a `references` page is settable: "Yes - needs a
          separate flow with separate galley-compositor chain")
```

## Objective

**A `references` page is settable, and the chain that sets a code page cannot set it.** Roy ruled
both halves in one sentence -- the capability is wanted, and it is a SEPARATE flow with its own
galley and its own compositor.

! **Two of the three checks have no subject on a reference**, which is what makes it a second
chain rather than a flag on the first:

| the check | on a code page | on a reference |
| --- | --- | --- |
| the sha | this is the file the roles read | **still applies** |
| the compositor | set these lines back where the CUES say | **no cues.** A reference is `path:line` |
| `prove_unchanged` | the executable code is byte-identical | **no code.** See [`prove-refuses-a-doc`](prove-refuses-a-doc.md) |

! **AND THE TEXT MAY REFLOW.** Roy, 2026-08-27: *"because it doesn't have the constraints that
require exact addresses that program files do can probably be `file_address:line_number` / And a
modification in those docs can flow the text to the required line-width."* A code compositor sets
a paragraph back into the room the cues name; a reference compositor may rewrap it. **Those are
different contracts, not one contract with an option.**

### The signal is undecided, and is to be decided WHILE building

Roy: *"Docket probably needs a code/reference schedule split to be the appropriate signal for the
flow that needs to happen but maybe there is a different way of signaling and should be discussed
while implementing."*

So what is settled is that **something must tell the flow which chain a schedule belongs to**. The
candidate is a `code`/`reference` split on the docket, mirroring the binder's `pages`/`pulled` /
`references`. It is not ruled, and the alternatives have not been laid out.

### What is NOT in scope here

- **`pulled`.** Ruled settable by the EXISTING chain -- *"has to be"* -- because a pulled page has
  cues, a sha and code. It needs nothing built. See `decision-log.md Process: #32`.
- **WHICH documents reach a reviewer.** That is
  [`reference-only-misses-the-documentation`](reference-only-misses-the-documentation.md), an
  `agents` question about SELECTION. This file is about the WRITE side of one already selected.

!! **WHY IT WAITS, AND IT IS THE STANDING PRACTICE.** `CLAUDE.md`: *a thing whose dependencies are
broken is not worked on, it is refused.* A second galley-compositor pair written now would be
shaped by a middle that has not settled -- the same cost the six recorded refusals name, most
directly *"there was no reason to try to fix the galley as it was."*

## Tasks

- [ ] T1 | T1 -- Lay out the candidate signals for which chain a schedule takes
      -- the docket split Roy named, and at least one alternative -- with what
      each costs. Verify: written in this file, and Roy has ruled on it.
- [ ] T2 | T2 -- Build the reference galley and compositor, whatever T1's signal
      decides. Verify: a reference schedule produces a draft, and a code
      schedule is untouched by it.
- [ ] T3 | T3 -- Prove the reference chain skips `prove_unchanged` for the right
      reason -- because the page is DECLARED not-code, not because a suffix was
      matched. Verify: a test that fails when the discriminator is a suffix
      test. ! Blocked on `prove-refuses-a-doc.md` T2.
