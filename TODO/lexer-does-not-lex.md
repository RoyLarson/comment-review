# The lexer does not lex -- it reads a parse

```
Status:   open
Progress: 0 of 4 tasks done
Owner:    comment-review
Requires-Roy: true
Raised:   2026-08-22 (Roy, 2026-08-22, on adding a token-type enum: the lexer is not
          doing lexing, it is parsing a tokenized parser and that is different)
Known:    2026-08-22 — IT MOSTLY WORKS, AND THE EXCEPTION IS NAMED. Roy, 2026-08-22:
          *"the parser-lexer will get settled later, it mostly works now except for
          comments after docstrings which the ast separates."* ! That is the shape to
          test against when the rename or the rework is taken up: a comment sitting
          BELOW a docstring is on the far side of a boundary the AST draws and a
          character reader would not -- the docstring is a node with an end, and the
          comment is not in the tree at all, so the two arrive from different sources
          and their adjacency has to be reconstructed. ! A lexical reader has the
          opposite problem and not this one: it sees both as runs of characters in
          order.
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
