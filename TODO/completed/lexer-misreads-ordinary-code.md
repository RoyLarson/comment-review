# The lexer misreads three shapes of ordinary code

```
Status:   open
Progress: 6 of 6 tasks done
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
Ruled:    2026-08-20 — 2026-08-20 -- the closing-line residue is ACCEPTED, not fixed.
          The prose half of task 3 is done (the run is cut at the closer, so the
          statement is no longer censused as prose); the line still leaves code_lines.
          Both fixes cost more than the shape is worth: dropping the run leaves the
          opening line -- nothing but comment -- belonging to nothing, and keeping both
          needs a field for where the text ENDS or a kind for comment-then-code.
          MEASURED over the fetched corpora: 180,821 lines of C and JS/TS, the spanning
          shape occurs 0 times (3 apparent hits were '*/' inside a glob string) while
          the one-line twin is ordinary at 1,551 and already correct. Roy: 'it is stupid
          to break context like that' -- and ESLint's no-inline-comments plus the
          kernel, Google C++ and Java guides agree. A test pins the residue so it is
          checked rather than merely accepted.
```

## Objective

The lexer misreads three shapes of ordinary code.

## Tasks

- [x] T1 | FINISHED | unknown | !! A RUST LIFETIME BLANKS THE REST OF THE LINE.
      `lexer.py:699` `_strip_strings` treats `'` as a paired quote, but in Rust
      it is a lifetime sigil. VERIFIED: `pub fn name(&self) -> &'static str { 1
      } // the display name` censuses ZERO prose paragraphs -- the comment
      vanishes entirely -- while the identical line with `&str` yields one. A
      `/*` is hidden the same way, so a whole block comment is lost with no
      `unterminated-paragraph- comment` either. `'static` is ordinary Rust.
- [x] T2 | FINISHED | unknown | A LINE WHOSE PREFIX IS A STRING LITERAL READS AS
      A WHOLE-LINE COMMENT. `lexer.py:979` runs
      `code.strip().startswith(openers)` on the string-BLANKED line. In JS, `
      "b" // the last one` censuses as `kind=comment` and line 3 drops out of
      `code_lines`, shifting every `b` and `c` address below it. A galley splice
      over that address deletes the array element. Same shape in C.
- [x] T3 | FINISHED | unknown | CODE AFTER A BLOCK COMMENT'S CLOSER IS SWALLOWED
      INTO THE PROSE. `lexer.py:894`: `/* note\n more */ int x = 5;` yields one
      paragraph whose text is `/* note more */ int x = 5;`, so `int x = 5;` is
      handed to four reviewers as prose and leaves the code set, moving every
      interval boundary in the file. ! The file records this as fixed for the
      OPENING line; the closing line was never covered.
- [x] T4 | FINISHED | unknown | All three are silent: no refusal, no annotation,
      exit 0. Each shifts addresses, so a galley write lands somewhere other
      than where the reviewer cited.
- [x] T5 | FINISHED | unknown | * RULING WANTED: does a line whose comment
      CLOSES mid-line stay in the code set? The prose half of task 3 is fixed --
      the run is cut at the closer, so `int x = 5;` is no longer censused as
      prose. But the line still leaves `code_lines` (measured: {1, 4} on the
      four-line C file), so every interval boundary below it still moves. !
      `code_lines` rescues the FIRST line of a paragraph via `original_column`
      -- code before the text. There is no symmetric field for code AFTER the
      text on the last line, and adding one cuts against Roy's 2026-08-20 ruling
      that dropped `edit_column` because the address system resolved what it was
      for. ! The other route is a kind for comment-then-code, symmetric to
      `trailing-comment`.
- [x] T6 | FINISHED | unknown | [DONE 2026-08-20] A NESTED paragraph comment
      closes only when every layer does. `/* a /* b */ c */` censused ZERO prose
      on Rust -- the scan closed at the first `*/`, saw more comment after it,
      and applied the intermediate- comment rule. `run_ends` carries the depth
      across lines and `nests_comments` is a data row on rust, swift, kotlin.
