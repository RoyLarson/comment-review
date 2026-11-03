# Ruby lexical reader

```
Status:   closed
Progress: 7 of 7 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-25 (decision-log.md Process: #222)
```

## Objective

Read Ruby source lexically from Ruby's own language definition, as Python and
Rust are read: its own dated spec, its own definition, its own reader, and no
rule taken from another language.

Worked when it is asked for -- decision-log.md Process: #222.

## Tasks

- [-] T1 | Superseded by #259: its language or reader left the system | e2b34a22ad36b0919b9d01cfd05bb74e80e76db9 | Specify
      the Ruby lexical reader in its own dated spec
        > 2026-10-25 Check: spec states modes, directive bounds, doc owners, fixtures
- [-] T2 | Superseded by #259: its language or reader left the system | e2b34a22ad36b0919b9d01cfd05bb74e80e76db9 | Implement
      the Ruby reader from its definition
        > 2026-10-25 Check: uv run pytest -q tests/reading/test_ruby.py
- [-] T3 | Superseded by #259: its language or reader left the system | e2b34a22ad36b0919b9d01cfd05bb74e80e76db9 | Implement
      Ruby attachment
        > 2026-10-25 Moved from doc-does-not-fill-its-a T12
        > 2026-10-25 Check: blank-separated prose uses a; sections stay whole
        > 2026-10-25 Check: an intervening code block blocks attachment
- [-] T4 | Superseded by #259: its language or reader left the system | e2b34a22ad36b0919b9d01cfd05bb74e80e76db9 | Decide
      whether a Ruby `=begin`/`=end` block has its markers stripped
        > 2026-10-25 Moved from block-comment-markers-survive-into-the-prose T9
        > 2026-10-25 Check: the answer and its measurement are written into this file
- [-] T5 | Superseded by #259: its language or reader left the system | e2b34a22ad36b0919b9d01cfd05bb74e80e76db9 | Read
      Ruby's `$#` and `/#/` as code
- [-] T6 | Superseded by #259: its language or reader left the system | e2b34a22ad36b0919b9d01cfd05bb74e80e76db9 | List
      the plain `<<ID` heredoc in Ruby's spanning quotes
- [-] T7 | Superseded by #259: its language or reader left the system | e2b34a22ad36b0919b9d01cfd05bb74e80e76db9 | Match
      Ruby's `=begin` at column 0 only
