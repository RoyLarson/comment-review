# An empty place is not citable, and the row cut's safety argument says it is

```
Status:   open
Progress: 0 of 4 tasks done
Owner:    backend
Requires-Roy: true
Raised:   2026-08-25 (backend, 2026-08-25, while cleaning up after the write-chain
          branch)
```

## Objective

An empty place is not citable, and the row cut's safety argument says it is.

## Tasks

- [ ] Decide how an absent place is resolved now that anchor_line is gone -- from
      neighbouring rows original_start and original_end, or by re-reading the
      page. Requires-Roy: it decides whether the addresser needs the repo as well
      as the census
- [ ] Implement it. Verify: asking for the empty b place above a line of code
      answers its address
- [ ] Make bind's docstring true -- either the mechanism works, or the sentence
      stops promising it
- [ ] A test over a real binder for a place the binder does NOT carry. Verify: it
      fails against the current code
