# The vendored todo tool writes em-dashes into a tree that forbids them

```
Status:   closed
Progress: 3 of 3 tasks closed
Owner:    systems
Requires-Roy: false
Raised:   2026-08-25 (backend, 2026-08-25, from a Task 9 review finding on the write-
          chain branch)
```

## Objective

The vendored todo tool writes em-dashes into a tree that forbids them.

## Tasks

- [-] T1 | Not this project's to track; Process #316 | fde63689f5a5b91eeefd4b1fa846038fbaa7cfc1 | State
      whether the ASCII rule reaches TODO/ at all, given the files are tool-
      written. Requires-Roy
        > 2026-11-22 Outcome: not this project's to track (Process #316)
- [-] T2 | Not this project's to track; Process #316 | fde63689f5a5b91eeefd4b1fa846038fbaa7cfc1 | If
      it does: patch ROY_NO and the note separator, and say so at the patch as
      the existing encoding guard does
- [-] T3 | Not this project's to track; Process #316 | fde63689f5a5b91eeefd4b1fa846038fbaa7cfc1 | If
      it does not: say so in CLAUDE.md where the ASCII rule is stated, so the
      next reviewer does not file this again
