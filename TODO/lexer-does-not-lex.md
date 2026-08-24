# The lexer does not lex -- it reads a parse

```
Status:   decision-needed
Progress: 7 of 9 tasks done
Owner:    backend
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
Updated:  2026-08-23 — CLAUDE.md states the dependency: the tier name test has nothing
          to answer once Python is read lexically, so the module lexes and the two-jobs
          split disappears rather than being worked
TRIAGED:  2026-08-23 — seven of nine boxes are the ARGUMENT, correctly ticked already:
          the measurement, why the other tier does lex, why it costs more than a word,
          that the register is asked first, the TYPECODER candidate, that the candidate
          dissolves the naming half, and that it is not the addresser. ! TWO REAL
          TASKS remain and both are verifiable. ! The dependency is still unlanded:
          `python-cannot-read-python` is 31 of 33 as of 2026-08-23.
```

## Objective

**`lexer.py` does not lex at the tier that matters.** Roy, 2026-08-22: *"the lexer is not
doing lexing, it is parsing a tokenized parser and that is different."* `paragraphs_stdlib`
consumes `tokenize.generate_tokens` and `ast.parse` -- CPython has already lexed AND parsed,
and this module reads the result. `paragraphs_lexical` really does lex, reading characters
against a language row, so **one module holds two jobs and the name fits the smaller half**.

! **IT COSTS MORE THAN A WORD.** `scan` was ruled 2026-08-22 to mean the lexer's character
work and `iterate` to mean stepping a sequence. That split only means something if `lexer`
names the thing that scans -- and today the module owning `scan` is mostly reading a parse.

!! **`TYPECODER` IS THE CANDIDATE, AND IT NAMES THE PRODUCT RATHER THAN THE METHOD.**
Typecoding is the copy-editing pass that marks every element with a code -- A-head, extract,
caption -- so the compositor knows which spec to set. That is what `Kind` IS: nine codes, and
`compact.md` ROUTES ON THE CODE. ! Naming the module for its product dissolves the naming half
of this file's title: both tiers read differently -- characters, or CPython's parse -- and BOTH
produce one thing, a `Kind` per paragraph.

! **NOT `addresser`, which was the first guess.** `cue()` never sees prose, and
`test_the_addresser_knows_nothing_about_prose` enforces it. A typecoder reads each element and
says WHAT IT IS; the addresser says WHERE it sits.

! **AND THE PYTHON RULING MAY SETTLE IT WITHOUT A RENAME.** If Python moves to the lexical tier
-- [`python-cannot-read-python`](python-cannot-read-python.md) -- the AST half goes and the
module lexes for real, so `lexer` becomes true. **Which is why the name is determined before it
is changed, and not the other way round.**

## Tasks

- [x] T1 -- `lexer.py` DOES NOT LEX, at the tier that matters. Roy, 2026-08-22:
      *"this is making me feel icky again. The lexer is not doing lexing, it is
      parsing a tokenized parser and that is different."* MEASURED:
      `paragraphs_stdlib` consumes `tokenize.generate_tokens` and `ast.parse` --
      CPython has already lexed AND parsed, and this module reads the RESULT. The
      `Layout` enum added the same day is the tell: a module that lexes has no
      opinion about `INDENT` and `DEDENT`, because it emits them.
- [x] T2 -- ! THE OTHER TIER REALLY DOES LEX. `paragraphs_lexical` reads characters
      against a language row -- comment openers, quotes, spanning delimiters --
      and that IS lexical analysis. So one module holds two different jobs under
      one name, and the name is right for the smaller half.
- [x] T3 -- ! WHY IT MATTERS BEYOND THE WORD: `scan` was ruled 2026-08-22 to mean
      the lexer's character work, and `iterate` to mean stepping a sequence. That
      split is only meaningful if `lexer` names the thing that scans. As it
      stands, the module that owns the word `scan` is mostly reading a parse.
- [x] T4 -- ! WHAT IT MIGHT BE INSTEAD is not decided here, and the register should
      be asked before the computing word is: publishing has readers, compositors and
      copy. ! It also interacts with `python-cannot-read-python` -- if Python
      moves to the lexical tier, the AST half goes and the name becomes true
      without anyone renaming anything. * Roy's call whether to rename now or let
      that TODO settle it.
- [x] T5 -- `TYPECODER` IS THE CANDIDATE, AND IT NAMES THE PRODUCT RATHER THAN THE
      METHOD. Typecoding is the copy-editing pass that marks every element with a
      code -- A-head, extract, caption -- so the compositor knows which spec to
      set. ! That is what `Kind` IS: nine codes, and `compact.md` ROUTES ON THE
      CODE -- a `comment` is governed by LENGTH and may be cut to the cap, a
      `docstring` by FORMAT and stands. A typecode exists to decide the treatment,
      which is exactly what kind does here.
- [x] T6 -- ! IT DISSOLVES THE NAMING HALF OF THIS FILE'S OWN TITLE. Two tiers read
      differently -- characters, or CPython's parse -- but BOTH produce one thing:
      a Kind per paragraph. Name the module for its product and "one module, two
      jobs" stops being a naming problem and stays a structural one. ! And
      `flag_structural_docs` is the tell: it marks a run whose KIND IS STILL AN
      OPEN QUESTION, which is a typecoder declining to assign a code rather than
      guessing -- what a copy editor does with an ambiguous element.
- [x] T7 -- ! NOT THE ADDRESSER, WHICH WAS THE FIRST GUESS. `cue(code, documentable,
      module_insert)` never sees prose -- *"a place is emitted because `foliate`
      reached its trigger, not because prose was found sitting there"* -- and
      `test_the_addresser_knows_nothing_about_prose` enforces it. A typecoder reads
      each element and says WHAT IT IS; the addresser says WHERE things sit, blind
      to content.
- [ ] T8 -- * DETERMINE THE NAME. TYPECODER is the standing candidate; the register
      is asked before the computing word. ! Settle it AFTER the Python ruling lands,
      because if the AST half goes the module lexes for real and `lexer` becomes
      true. Verify: the name is written down with the reason, in
      docs/vocabulary.md.
- [ ] T9 -- RENAME. The module, its imports, the vocabulary entry and every prose
      use. Verify: `uv run python scripts/check_vocabulary.py` passes with the old
      word RETIRED and the new one defined, and the suite is green.
