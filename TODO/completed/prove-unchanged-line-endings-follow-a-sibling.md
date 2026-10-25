# prove_unchanged fails a file whose line endings the write kept

```
Status:   closed
Progress: 2 of 2 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-09-12 (2026-09-12 (a comment-review WRITE on a Windows checkout with
          core.autocrlf=true))
```

## Objective

prove_unchanged fails a file whose line endings the write kept.

## Tasks

- [-] T1 | SUPERSEDED by one-line-ending-per-file T4 | 74a033c2 | Check a
      written file's line endings against its own pre-edit bytes, not against
      one untouched sibling
- [-] T2 | SUPERSEDED by one-line-ending-per-file T4, its check | 74a033c2 | Test
      it with a CRLF file beside an LF sibling: an edit keeping CRLF proves, one
      converting to LF fails
