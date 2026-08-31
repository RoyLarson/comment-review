# The vendored todo tool writes em-dashes into a tree that forbids them

```
Status:   open
Progress: 0 of 3 tasks done
Owner:    systems
Requires-Roy: false
Raised:   2026-08-25 (backend, 2026-08-25, from a Task 9 review finding on the write-
          chain branch)
```

## Objective

The vendored todo tool writes em-dashes into a tree that forbids them.

## Tasks

- [ ] T1 | State whether the ASCII rule reaches TODO/ at all, given the files
      are tool- written. Requires-Roy
- [ ] T2 | If it does: patch ROY_NO and the note separator, and say so at the
      patch as the existing encoding guard does
- [ ] T3 | If it does not: say so in CLAUDE.md where the ASCII rule is stated,
      so the next reviewer does not file this again
