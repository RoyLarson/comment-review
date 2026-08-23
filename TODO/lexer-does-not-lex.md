# The lexer does not lex -- it reads a parse

```
Status:   open
Progress: 0 of 7 tasks done
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
- [ ] `TYPECODER` IS THE CANDIDATE, AND IT NAMES THE PRODUCT RATHER THAN THE
      METHOD. Typecoding is the copy-editing pass that marks every element with a
      code -- A-head, extract, caption -- so the compositor knows which spec to
      set. ! That is what `Kind` IS: nine codes, and `compact.md` ROUTES ON THE
      CODE -- a `comment` is governed by LENGTH and may be cut to the cap, a
      `docstring` by FORMAT and stands. A typecode exists to decide the treatment,
      which is exactly what kind does here.
- [ ] ! IT DISSOLVES THE NAMING HALF OF THIS FILE'S OWN TITLE. Two tiers read
      differently -- characters, or CPython's parse -- but BOTH produce one thing:
      a Kind per paragraph. Name the module for its product and "one module, two
      jobs" stops being a naming problem and stays a structural one. ! And
      `flag_structural_docs` is the tell: it marks a run whose KIND IS STILL AN
      OPEN QUESTION, which is a typecoder declining to assign a code rather than
      guessing -- what a copy editor does with an ambiguous element.
- [ ] ! NOT THE ADDRESSER, WHICH WAS THE FIRST GUESS. `cue(code, documentable,
      module_insert)` never sees prose -- *"a place is emitted because `cue`
      reached its trigger, not because prose was found sitting there"* -- and
      `test_the_addresser_knows_nothing_about_prose` enforces it. A typecoder reads
      each element and says WHAT IT IS; the addresser says WHERE things sit, blind
      to content.
