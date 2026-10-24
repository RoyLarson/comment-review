# The drop path splits Rust comments with a second Rust comment grammar

```
Status:   open
Progress: 0 of 1 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-10-23 (review)
```

## Objective

The desk's drop path splits a Rust comment paragraph with the generic lexer, a
second Rust comment grammar beside the Rust reader's scanner.

Two sites read Rust comments, and they spell the grammar differently:

- `src/comment_review/reading/rust/scanner.py` -- the Rust reader. Four or more
  slashes (`////`), `/***` and `/**/` are ordinary comments; delimited comments nest.
- `src/comment_review/reading/language.py` `comment_language_for` rebuilds a generic
  `Language` from `rust.toml` so `lexer.comment_form` and `_comment_fragment` in
  `src/comment_review/reading/lexer.py` can split a paragraph for
  `desk/marks/rules.py` (`derived_change` for a `drop` with an address) and
  `desk/marks/table.py` (`comment_at`). That splitter reads `/**` as the opener of
  `/***` and `///` as the marker of `////`.

Drops probed on `//// x` with `// y`, a decorated `/** */` comment and a nested
comment came out right, so no wrong output is known; the cost is two
implementations of one grammar that can disagree on `/***` and `////`. Found by
the final review of the feat/lexer-rust branch
(`.superpowers/sdd/2026-10-22-lexer-rust/final-review.md`, finding 7).

## Tasks

- [ ] T1 | Make the drop path split Rust comments with the Rust reader's comment
      grammar
        > 2026-10-23 Check: a drop on `//// x` above `// y` reads both as ordinary
        > 2026-10-23 Reason: scanner.py and lexer.py differ on `/***` and `////`
