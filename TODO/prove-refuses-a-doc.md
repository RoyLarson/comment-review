# prove_unchanged refuses a documentation file for having no code

```
Status:   open
Progress: 0 of 3 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-27 (2026-08-27 (the pulled/references ruling -- Roy: docs do not need
          the step))
```

## Objective

prove_unchanged refuses a documentation file for having no code.

## Tasks

- [ ] T1 | Split `unprovable` into NOT-CODE and CANNOT-BE-PROVEN. Verify:
      code_fingerprint answers them differently for docs/gates.md and for a .py
      file that fails to parse
- [ ] T2 | Make _prove skip the step for a not-code page instead of refusing it.
      Verify: a docket altering a documentation file drafts at exit 0, and a .py
      file whose code changed still refuses at prove
- [ ] T3 | Pin that the skip cannot swallow a real code file. Verify: a test
      where a genuinely unparseable .py file still returns a Refusal at prove
