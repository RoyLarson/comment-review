# Java lexical reader

```
Status:   open
Progress: 0 of 5 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-25 (decision-log.md Process: #222)
```

## Objective

Read Java source lexically from Java's own language definition, as Python and
Rust are read: its own dated spec, its own definition, its own reader, and no
rule taken from another language.

Worked when it is asked for -- decision-log.md Process: #222.

## Tasks

- [ ] T1 | Specify the Java lexical reader in its own dated spec
        > 2026-10-25 Check: spec states modes, directive bounds, doc owners, fixtures
- [ ] T2 | Implement the Java reader from its definition
        > 2026-10-25 Check: uv run pytest -q tests/reading/test_java.py
- [ ] T3 | Give Java its own soft-keyword rule for `record`
        > 2026-10-25 Moved from lexer-and-language-findings T13
        > 2026-10-25 Check: `record = lookup()` in a .java mints no a; a real one does
- [ ] T4 | Strip the block-comment opener and closer from Java prose
        > 2026-10-25 Moved from block-comment-markers-survive-into-the-prose T1
        > 2026-10-25 Check: a .java docstring's text holds no `/**` and no `*/`
- [ ] T5 | Add a multi-line Javadoc to `tests/fixtures/sample.java`
        > 2026-10-25 Moved from block-comment-markers-survive-into-the-prose T8
        > 2026-10-25 Check: the fixture carries a continuation `*` on 3 or more lines
