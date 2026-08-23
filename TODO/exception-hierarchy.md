# The exception tuples are a surface, not a hierarchy

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    comment-review
Requires-Roy: false
Raised:   2026-08-22 (Roy, 2026-08-22, on the exceptions.py layer: a human would have
          created the hierarchy rather than moving the tuples)
Criterion: 2026-08-22 — THE TEST IS NOT WHETHER IT CAN BE REFACTORED. Roy, 2026-08-22:
           *"I know technically all code can eventually be refactored, but sometimes
           that is a serious mess that becomes not worth it."* Everything is possible in
           principle; what decays is whether anyone will pay for it. Nine definitions of
           one name across nine files, two of them subtly different, is the state where
           the cost keeps rising until the answer is permanently no -- not because it is
           impossible, but because no version of the work is ever worth its price. The
           named surface holds that cost flat, which is what makes waiting a decision
           rather than a drift.
Deferral: 2026-08-22 — AND THE DEFERRAL ALWAYS LOOKS CHEAP, WHICH IS HOW IT GETS
          DEFERRED. Roy, 2026-08-22: *"the amortization of the now cost versus the over
          always seems small."* Spread the fix across every future encounter and the
          per-encounter share is below the threshold that would make anyone act -- so
          the comparison comes out in favour of waiting EVERY time it is made, and the
          decision is never actually taken. ! That is exactly how nine definitions of
          `READ_ERRORS` arrived: adding the TENTH costs nothing visible, and the bill
          only lands when two of them disagree. ! So a filed TODO is not free, and this
          one is filed on a specific ground rather than by default -- the named surface
          holds the future cost flat. Where there is no seam, the same reasoning argues
          for paying NOW, because the per-encounter share will never rise enough to
          force it later.
```

## Objective

The exception tuples are a surface, not a hierarchy.

## Tasks

- [ ] DESIGN THE HIERARCHY. Roy, 2026-08-22: *"a human would not have just moved
      the tuples, they would have properly created the exception hierarchy and
      used that to catch the expected exceptions."* The shape: a
      `CommentReviewError(Exception)` root over `Refused` (we declined this page),
      `Unreadable` (the bytes could not be got), `Undecodable` (the bytes came,
      the TOML would not decode), `Unparsable` (the source came, it would not
      parse) and `GitSilent` (git could not answer). ! Then `except
      exceptions.Unreadable` replaces `except exceptions.READ_ERRORS`, and a
      caller catches OUR concept rather than a list of stdlib classes that happen
      to co-occur.
- [ ] THE COST IS THE BOUNDARY, and it is why this is a TODO rather than a patch.
      Python raises `OSError`, not `Unreadable`, so every read, parse and git site
      has to catch the stdlib tuple and re-raise as ours with `from e` -- roughly
      30 sites across 14 modules. It changes what escapes `page_for`, `identity`,
      `code_names` and the census, and it makes the tuples INTERNAL to the
      wrappers rather than the public surface they are today.
- [ ] WHY DEFERRING IS SAFE, which is the whole reason this can wait: the named
      tuples in `exceptions.py` are the SEAM. Roy: *"we have the surface, we
      understand the problem. The constants in that file will allow us to get past
      this without too much risk of this being unrefactorable later."* Every call
      site now names a QUESTION -- read, decode, tokenize, parse, git -- instead
      of spelling a tuple, so swapping what that name resolves to is contained.
      The version of this that WOULD have been unrefactorable is the one from
      before 2026-08-22, with nine definitions of `READ_ERRORS` in nine files and
      two of them a different tuple.
- [ ] AND CHECK THE `raise` SIDE WHEN IT LANDS. MEASURED 2026-08-22: 25 bare
      `raise ValueError` across the tree, while `ValueError` is a member of
      `PARSE_ERRORS` -- `ast.parse` raises it on a NUL byte. Three of those were
      DELIBERATE refusals and are `exceptions.Refused` now, but the other 22 were
      not audited. Each one either means something the hierarchy should name, or
      is genuinely a bad argument and should stay a `ValueError`.
- [ ] THE DEVELOPMENT SCRIPTS ARE STILL SEPARATE. Five files under `scripts/`
      define their own `READ_ERRORS`, two of them the TOML variant. They cannot
      import the shipped leaf without coupling the dev tree to `plugins/`, which
      ships alone -- so either they take it through the path shim two of them
      already use, or the duplication is stated as deliberate. It is currently
      neither.
