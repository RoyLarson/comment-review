# code_concerns is a bare list of strings, so a code problem reaches no gate

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-23 (2026-08-23, splitting a-role-with-no-code-out-damages-the-prose:
          Roy, 'there is giving the machinery to surface them properly, that is the
          backend lane')
```

## Objective

A reviewer that finds a CODE problem has one channel for it, and it carries almost nothing.
`code_concerns` is published in the brief as *"a list of strings, one line each, no verdict"*;
`record.py:883` seeds it empty and `held.py:190` reads it back as `[str(c) for c in ...]`, so
anything structured a role emitted is flattened to its repr.

!! **IT IS THE ONE REVIEWER OUTPUT NO GATE CHECKS.** `verdicts.py` is stage 5 -- it joins every
prose finding against the census, resolves every citation, and refuses what does not hold. It
never reads `code_concerns`. So the channel a role is supposed to use for the findings it
cannot fix is also the only channel nothing verifies, which is the shape
[`docs/gates.md`](../docs/gates.md) is about: not *does the check pass*, but *could it fail*.

! **A CODE CONCERN HAS NO ADDRESS**, so it cannot be re-run against a later tree, deduplicated
when two roles raise it, or checked for staleness -- the three things an address buys every
other finding.

! **THIS IS THE `backend` HALF -- what the Python can carry.** What a role is TOLD it may do is
`agents` and is filed as
[`a-role-with-no-code-out-damages-the-prose`](a-role-with-no-code-out-damages-the-prose.md).
Neither half is worth landing alone: a shape nobody is told to fill stays empty, and an
instruction to propose a change the record cannot hold produces a proposal nothing can read.

## Tasks

- [ ] Give a code concern a SHAPE that can carry a located proposal -- where, what
      and why -- instead of one string. Today the brief publishes it as 'a list of
      strings, one line each, no verdict'.
- [ ] held.py:190 coerces every entry with `str(c)`, so a structured entry is
      flattened to its repr. That line is what makes a richer shape impossible
      today and is the first thing any change here has to move.
- [ ] !! NOTHING JOINS OR GATES IT. `verdicts.py` -- the stage-5 gate that checks
      every prose finding against the census and resolves every citation -- never
      reads `code_concerns`. It is the ONE reviewer output no gate checks, which
      is the shape `docs/gates.md` is about.
- [ ] * RULE whether a code concern gets an ADDRESS from the census the way a
      finding does. It has none today, so it cannot be re-run, deduplicated across
      roles, or checked for staleness.
- [ ] Decide what stage 8 does with one. `review.md` reads the finished page; a
      code concern is by definition not on the page.
