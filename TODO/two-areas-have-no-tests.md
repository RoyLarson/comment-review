# Two areas have no tests, and the layout now says so

```
Status:   open
Progress: 1 of 5 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-24 (P7 of refactor/the-boundaries-are-not-real, 2026-08-24)
Updated:  2026-08-25 — machine/ now has tests/test_machine.py -- repo.read_source,
          sha_of and the two-reader disagreement. commands/ still has none.
```

## Objective

Two areas have no tests, and the layout now says so.

## Tasks

- [-] T1 | SUPERSEDED by T5: test_source_io.py:127 now covers a failing git; git absent, non-UTF-8 output remain | 22c3a0abcbc86509c74296319ce5b719a43338ca | tests/machine/test_repo.py:
      git absent, git failing, output not valid UTF-8
- [ ] T2 | tests/machine/test_constants.py: text_lines, and the console guard on
      a non- reconfigurable stream
- [ ] T3 | tests/commands/: the dispatcher refuses an unknown name and a bare
      invocation
- [ ] T4 | tests/commands/: each command's exit code on a usage error
- [ ] T5 | Cover machine.repo's git() when git is absent, plus output that is
      not UTF-8
        > 2026-11-22 Check: cases hit GIT_ERRORS -> None, a non-UTF-8 git() output
