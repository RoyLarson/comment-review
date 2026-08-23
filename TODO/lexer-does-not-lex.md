# The lexer does not lex -- it reads a parse

```
Status:   open
Progress: 0 of 4 tasks done
Owner:    comment-review
Requires-Roy: true
Raised:   2026-08-22 (Roy, 2026-08-22, on adding a token-type enum: the lexer is not
          doing lexing, it is parsing a tokenized parser and that is different)
```

## Objective

The lexer does not lex -- it reads a parse.

## Tasks

- [ ] `lexer.py` DOES NOT LEX, at the tier that matters. Roy, 2026-08-22: *"this
      is making me feel icky again. The lexer is not doing lexing, it is parsing a
      tokenized parser and that is different."* MEASURED: `paragraphs_stdlib`
      consumes `tokenize.generate_tokens` and `ast.parse` -- CPython has already
      lexed AND parsed, and this module reads the RESULT. The `Layout` enum added
      the same day is the tell: a module that lexes has no opinion about `INDENT`
      and `DEDENT`, because it emits them.
- [ ] ! THE OTHER TIER REALLY DOES LEX. `paragraphs_lexical` reads characters
      against a language row -- comment openers, quotes, spanning delimiters --
      and that IS lexical analysis. So one module holds two different jobs under
      one name, and the name is right for the smaller half.
- [ ] ! WHY IT MATTERS BEYOND THE WORD: `scan` was ruled 2026-08-22 to mean the
      lexer's character work, and `iterate` to mean stepping a sequence. That
      split is only meaningful if `lexer` names the thing that scans. As it
      stands, the module that owns the word `scan` is mostly reading a parse.
- [ ] ! WHAT IT MIGHT BE INSTEAD is not decided here, and the register should be
      asked before the computing word is: publishing has readers, compositors and
      copy. ! It also interacts with `python-cannot-read-python` -- if Python
      moves to the lexical tier, the AST half goes and the name becomes true
      without anyone renaming anything. * Roy's call whether to rename now or let
      that TODO settle it.
