# addresser.triggers() has no production caller and takes a shape the walk no longer uses

```
Status:   open
Progress: 0 of 3 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-20 (found while collapsing three code-line functions into one ordered
          mapping, 2026-08-20)
```

## Objective

addresser.triggers() has no production caller and takes a shape the walk no longer uses.

## Tasks

- [ ] T1 | `triggers(code: list[int])` is called by `tests/test_cues.py:963` and
      by NOTHING in the shipped tree. `cue` walks `code` directly and calls
      `c.skip()` for the module rather than prepending it.
- [ ] T2 | Its parameter is `list[int]`, which is not what the walk is given any
      more -- that is now `dict[int, str]`. So the one thing that exercises it
      exercises a shape no caller produces.
- [ ] T3 | DECIDE: is the MODULE-then-code list still a fact worth stating in
      one place, in which case `cue` should call it -- or is it residue of the
      pre-mapping walk, in which case it and its test go?
