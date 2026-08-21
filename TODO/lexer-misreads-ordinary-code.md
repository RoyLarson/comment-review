# The lexer misreads three shapes of ordinary code

```
Status:   open
Progress: 1 of 4 tasks done
Owner:    session
Requires-Roy: false
Raised:   2026-08-20 (the /code-review high of 2026-08-20; the Rust case verified in-
          session)
Fixed:    2026-08-20 — 2026-08-20 task 1 -- the Language row gains char_quotes: the
          delimiters that hold exactly ONE character. A quote in that set is believed
          only where it CLOSES within a character's width, so Rust's 'static and 'a are
          ordinary text and 'x' and an escaped literal are still blanked. Set on rust,
          go, c, cpp, java, csharp, kotlin; Python, JS, Ruby, Lua, shell and SQL keep '
          as a string and are untouched. Six tests, and the original repro now censuses
          one trailing-comment.
```

## Objective

The lexer misreads three shapes of ordinary code.

## Tasks

- [x] !! A RUST LIFETIME BLANKS THE REST OF THE LINE. `lexer.py:699`
      `_strip_strings` treats `'` as a paired quote, but in Rust it is a lifetime
      sigil. VERIFIED: `pub fn name(&self) -> &'static str { 1 } // the display
      name` censuses ZERO prose paragraphs -- the comment vanishes entirely --
      while the identical line with `&str` yields one. A `/*` is hidden the same
      way, so a whole block comment is lost with no `unterminated-paragraph-
      comment` either. `'static` is ordinary Rust.
- [ ] A LINE WHOSE PREFIX IS A STRING LITERAL READS AS A WHOLE-LINE COMMENT.
      `lexer.py:979` runs `code.strip().startswith(openers)` on the string-BLANKED
      line. In JS, `  "b" // the last one` censuses as `kind=comment` and line 3
      drops out of `code_lines`, shifting every `b` and `c` address below it. A
      galley splice over that address deletes the array element. Same shape in C.
- [ ] CODE AFTER A BLOCK COMMENT'S CLOSER IS SWALLOWED INTO THE PROSE.
      `lexer.py:894`: `/* note\n   more */ int x = 5;` yields one paragraph whose
      text is `/* note more */ int x = 5;`, so `int x = 5;` is handed to four
      reviewers as prose and leaves the code set, moving every interval boundary
      in the file. ! The file records this as fixed for the OPENING line; the
      closing line was never covered.
- [ ] All three are silent: no refusal, no annotation, exit 0. Each shifts
      addresses, so a galley write lands somewhere other than where the reviewer
      cited.
