# prove_unchanged refuses a documentation file for having no code

```
Status:   open
Progress: 1 of 5 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-27 (2026-08-27 (the pulled/references ruling -- Roy: docs do not need
          the step))
```

## Objective

prove_unchanged refuses a documentation file for having no code.

## Tasks

- [-] T1 | SUPERSEDED by Process: #104 and split into T4 and T5 -- there is no unprovable class left | 3534c4d0 | Split
      `unprovable` into NOT-CODE and CANNOT-BE-PROVEN. Verify: code_fingerprint
      answers them differently for docs/gates.md and for a .py file that fails
      to parse
- [ ] T2 | Make _prove skip the step for a not-code page instead of refusing it.
      Verify: a docket altering a documentation file drafts at exit 0, and a .py
      file whose code changed still refuses at prove
- [ ] T3 | Pin that the skip cannot swallow a real code file. Verify: a test
      where a genuinely unparseable .py file still returns a Refusal at prove
- [ ] T4 | Update the gate so a NOT-CODE file is reported out of scope, naming
      the chain it waits on rather than a language record
        > 2026-09-07 Verify: a docs file drafts at exit 0, out of scope not proven
- [ ] T5 | Update the gate so a CODE file whose language has no record yet is
      reported out of scope, named apart from a not-code file
        > 2026-09-07 Verify: a .rs file with no row reads differently from a .md file
        > 2026-09-07 Verify: a .rs file with no row reads unlike a .md file
