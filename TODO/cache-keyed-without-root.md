# The source cache is keyed on the cited path and not the root

```
Status:   open
Progress: 0 of 2 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-30 (2026-08-30, from the blind rewrite of collator.py)
```

## Objective

The source cache is keyed on the cited path and not the root.

## Tasks

- [ ] Reproduce it: one cache, two roots holding the same path with different
      text. Verify: the second read returns the first root's lines, and the test
      fails against today's code.
- [ ] Key the cache on the root as well, or refuse a cache handed a second root.
      Verify: whichever is chosen, the staged design cannot answer from the wrong
      tree -- a run reads an original at one stage and a revise at the next.
