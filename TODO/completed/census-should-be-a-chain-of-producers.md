# The census is one step that should be a chain of producers

```
Status:   open
Progress: 4 of 4 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-25 (Roy, 2026-08-25, ruling on flows during the write-chain branch)
```

## Objective

The census is one step that should be a chain of producers.

## Tasks

- [x] T1 | FINISHED -- flows/annotations_for.py annotates the carried paragraphs in place, as annotate does, and tests/test_gather.py reads the tree: it is the one caller | 68bfc548 | flows/annotations_for.py
      -- annotate a page, as a step. Verify: it takes a page and returns
      annotations, and nothing else calls annotate.py directly
- [x] T2 | FINISHED -- flows/gather.py: STEPS is a tuple of steps over one Gathering; test_gather appends a references_for and sees it run | 68bfc548 | flows/gather.py
      -- chain page_for and annotations_for into the binder. Verify: the chain
      is DATA, so adding references_for later is a list element
- [x] T3 | FINISHED -- commands/gather.py exposes gather and names neither page_for nor annotate; test_gather_command reads its source to say so | 68bfc548 | commands/census.py
      exposes gather and holds no orchestration. Verify: it calls page_for
      nowhere
- [x] T4 | RULED Vocabulary 34: the command and the act are gather, no alias; census retired | 0001a855 | Decide
      whether the command keeps the name census once the flow is gather.
      Requires-Roy
