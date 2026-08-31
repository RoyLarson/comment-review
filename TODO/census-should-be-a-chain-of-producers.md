# The census is one step that should be a chain of producers

```
Status:   open
Progress: 0 of 4 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-25 (Roy, 2026-08-25, ruling on flows during the write-chain branch)
```

## Objective

The census is one step that should be a chain of producers.

## Tasks

- [ ] T1 | flows/annotations_for.py -- annotate a page, as a step. Verify: it
      takes a page and returns annotations, and nothing else calls annotate.py
      directly
- [ ] T2 | flows/gather.py -- chain page_for and annotations_for into the
      binder. Verify: the chain is DATA, so adding references_for later is a
      list element
- [ ] T3 | commands/census.py exposes gather and holds no orchestration. Verify:
      it calls page_for nowhere
- [ ] T4 | Decide whether the command keeps the name census once the flow is
      gather. Requires-Roy
