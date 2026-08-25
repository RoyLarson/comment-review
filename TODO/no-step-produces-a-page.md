# Five sites rebuild a page from a path and none of them is a step

```
Status:   open
Progress: 0 of 4 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-25 (Roy, 2026-08-25, during the write-chain branch)
```

## Objective

Five sites rebuild a page from a path and none of them is a step.

## Tasks

- [ ] Repoint commands/census.py at page_of. Verify: it calls no page_for
- [ ] Repoint commands/galley.py at page_of. Verify: it calls no page_for
- [ ] Repoint compositor.lossless and compositor.identity at page_of, which also
      removes the prologue those two share
- [ ] A check that page_for has no caller outside flows/page.py and the tests.
      Verify: adding one back turns it red
