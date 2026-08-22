# The AST reader gets older every release while the files get newer

```
Status:   open
Progress: 0 of 27 tasks done
Owner:    session
Requires-Roy: true
Raised:   2026-08-21 (Roy, 2026-08-21, on four sentry files the floor interpreter cannot
          parse: 'we can't use python to parse python files ... that means using the ast
          to bootstrap the pieces fails on new python syntax. This puts python right
          next to the other languages in the lexer')
```

## Objective

The AST reader gets older every release while the files get newer.

## Tasks

- [ ] !! THE FLOOR IS A HARD CONSTRAINT AND THE LANGUAGE KEEPS MOVING. `.python-
      version` pins 3.11 because that is what `plugins/` ships against -- Roy:
      *"the floor will not fail if we are using the floor to evaluate the code."*
      So `ast.parse` reads the syntax of 2023 forever, while the files under
      review are written this year. MEASURED 2026-08-21: 4 of 2,310 `.py` files in
      `corpora/` do not parse on 3.11, every one of them PEP 695 -- `class
      SequencePaginator[T]:`, `type QueryOp = Literal[...]`, `def sudo_required[T,
      **P](...)`. ! 0.17% today and one-directional.
- [ ] !! AN UNPARSED PAGE SETS AS AN EMPTY FILE, which is the sharp edge of it.
      `page_for` skips the walk when any paragraph is `unparsed`, so
      `foliation.reading` is empty and `compositor.set_page` returns `""`.
      MEASURED on `sentry/src/sentry/api/paginator.py`: 884 lines in, 0 characters
      out. ! `draft()` would write that empty file. Roy's *"no editing on the real
      file until approved"* is what stands between it and the tree. * THE GUARD IS
      SMALL AND SHOULD LAND FIRST: the compositor must REFUSE a page with no
      places, never set one.
- [ ] !! TWO READERS MEANS EVERY RULE IS WRITTEN TWICE, AND ONE WRITTEN ONCE IS
      SILENTLY WRONG ON THE OTHER TIER. Roy: *"which is certainly hiding a lot of
      bugs."* THREE instances in a single day, 2026-08-21:
- [ ]   ! THE MATTER TYPE was written in `paragraphs_lexical` alone, so every
      `.py` file reported NO front matter at all while `.c` reported it correctly.
      Caught only because a test fixture happened to be Python.
- [ ]   !! THE DELIMITER FLUSH is the one that matters: `paragraphs_lexical` ended
      a paragraph at a comment's opener AND its closer, so `/* one */`, a blank
      and `/* two */` shared one address. MEASURED: 157 shared addresses in the
      lexical languages and ZERO in Python, whose reader merged runs correctly all
      along. **PYTHON'S CORRECTNESS HID THE LEXICAL DEFECT FOR AS LONG AS THE TREE
      EXISTED** -- every Python test passed over it.
- [ ]   ! `_is_doc` was computed INLINE in `flush` and re-derived differently in
      `carry`, so a `/** */` at the head of a file was documentation to one and an
      ordinary comment to the other.
- [ ] MEASURED, the surface: FOUR structural branch points -- `census.py:160`,
      `language.tier_for`, `lexer.declarations` on `doc_inside`, and `page_for`
      choosing a reader -- plus `paragraphs_stdlib` at 159 lines doing what
      `paragraphs_lexical` does in 375. ! `prove_unchanged` carries the SAME
      dependency: `ast.dump(_blank_docstrings(ast.parse(text)))` for Python and
      stripped text for everything else.
- [ ] ! WHAT THE AST ACTUALLY BUYS, stated so the trade is not one-sided. (1) A
      triple-quoted string at the head of a body IS a docstring and one elsewhere
      is a bare expression -- position alone cannot tell them apart. (2) WHERE THE
      BODY STARTS, which a wrapped signature moves several lines down. (3)
      `prove_unchanged`'s statement-order fingerprint, which ignores docstring
      CONTENT while keeping its PRESENCE. Each has to be answered lexically or
      knowingly given up.
- [ ] * RULING WANTED ON THE TRADE. Dropping the AST puts Python on the lexical
      tier beside the other sixteen -- one reader, every rule written once, and
      the `tokenized` tier either empties or disappears. It also gives up the
      three answers above, and `a` placement for Python becomes a keyword-and-
      position question like every other language's.
- [ ] ! A THIRD MEASURE OF CORRECTNESS ARRIVED WITH THIS, ruled by Roy the same
      day: *"out ~= in if out.replace('\\n', '') == in.replace('\\n', '')"* -- a
      run of the project's own formatter settles the rest. MEASURED over 3,082
      files: 3,049 byte-identical, 3,075 identical ignoring newlines, and 7
      differing in more than newlines. It is what separates a spacing question
      from a defect.
- [ ] !! `prove_unchanged` CARRIES THE SAME DEPENDENCY AND IS NOT IN THE LEXER. It
      fingerprints Python as `ast.dump(_blank_docstrings(ast.parse(text)))` and
      everything else as stripped text. That is the CODE CHECK -- what
      `foliator.py` calls the thing that *"MAKES it constant across this tool's
      own work"* -- so the whole addressing scheme rests on it. Dropping the AST
      from the reader leaves it standing there unanswered. ! A candidate answer
      arrived the same day: the compositor sets code from the `c` places' anchors,
      so "the code is unchanged" could become "every `c` anchor is unchanged" --
      stronger than an `ast.dump`, and language-independent.
- [ ] !! THE TEST SUITE IS 4:1 PYTHON, so it barely covers the path Python would
      move ONTO. MEASURED 2026-08-21: 456 references to a `.py` path against 115
      to a lexical language, and one fixture each for `.go`, `.rb` and `.rs`.
      ! THAT IS BOTH THE RISK AND THE PAYOFF -- the suite today exercises the
      reader that works and not the one where 157 collisions lived, and the moment
      Python moves, all 456 assertions become coverage of the path that has the
      bugs.
- [ ] ! NO HOLE IN THE LEXER CONTRACT, checked 2026-08-21 when Roy asked. Its
      output shape is pinned and the ORACLE now exists: `compositor.identity` over
      2,399 Python files, plus `lossless` and the newline-insensitive measure. A
      replacement reader has to reproduce 2,368 byte-identical round trips.
      ! Before this day there was no way to check that a reader change preserved
      anything at all.
- [ ] * SCOPE, ruled by Roy 2026-08-21: *"the python thing ends up with its own
      branch once we merge this branch back to the 0.2.4 branch. It doesn't depend
      on the folio system being correct or the lexer or page or census."* It may
      touch the lexer only to document edge cases.
- [ ] !! FOUR AST DEPENDENCIES, AND THREE ARE OUTSIDE THE LEXER. MEASURED
      2026-08-21: `lexer` (paragraphs and declarations), `prove_unchanged` (the
      CODE CHECK fingerprint), `census` (the name corpus, `ast.parse` at line
      165), and `referrers` (which files name a symbol). Every one of them fails
      on syntax newer than the floor, so the same four files break all four.
- [ ] ! ONLY THE LEXER AND THE COMPOSITOR MAY INTERPRET A FILE, and three of these
      do it anyway. Roy, 2026-08-21: *"lexer and compositor are the things that
      are reading files."* ! THE TEST IS NOT `read_text` -- the LEXER READS ZERO
      FILES, it takes `text` as a parameter, and `census` is what hands it one.
      The line is who INTERPRETS the content, and `ast.parse` outside the lexer is
      interpretation.
- [ ] ! `census.py` NAMES ITS OWN GAP ALREADY: *"Liveness in these languages needs
      its own harvester; the gap until there is one."* Its harvest is Python-only,
      so the name corpus a reviewer checks a cited symbol against exists for one
      language of seventeen -- and vanishes for a Python file the floor cannot
      parse.
- [ ] !! THE FOLIATOR DESCRIBES A MECHANISM IT NEVER TOUCHES. It has NO `import
      ast` and no call; two paragraphs of its module docstring explain `ast.dump`
      and `_blank_docstrings`, which live in `prove_unchanged`. ! Roy, 2026-08-21,
      on why: *"when it was addresser a long time ago that kind of made sense."*
      Addressing was the subject then, and the code check is what makes an address
      constant. The rename to `foliator` left prose two modules from the code it
      describes, with nothing able to check it -- which is the obituary class
      `block-context` is chartered to catch, shipping inside the tool that catches
      it.
- [ ] * RULED 2026-08-21 -- THE CODE CHECK BELONGS TO THE COMPOSITOR. Roy: *"that
      check if it was actually possible should live in compositor since before and
      after are in some ways its job to verify."* The compositor PRODUCES the
      after, and every question it already answers is a before/after one --
      `identity` asks whether an unchanged page sets back byte for byte,
      `lossless` whether any line was lost. *Did the code survive* is the same
      question at the same seam.
- [ ] ! IT ALSO ANSWERS THE AST PROBLEM RATHER THAN MOVING IT. `prove_unchanged`
      fingerprints Python with `ast.dump(_blank_docstrings(ast.parse(text)))`,
      which fails on syntax newer than the floor. In the compositor the check has
      the PAGE, whose `c` places hold every line of code verbatim -- so *the code
      is unchanged* becomes *every `c` anchor is unchanged*. No parser, one rule
      for seventeen languages, and stronger than an `ast.dump`, which compares
      statements and their order rather than the characters.
- [ ] ! AND IT PUTS THE PROSE BACK BESIDE THE CODE IT DESCRIBES. `foliator.py`
      carries two paragraphs explaining `ast.dump` and `_blank_docstrings` and
      imports neither -- Roy: *"when it was addresser a long time ago that kind of
      made sense."* Addressing was the subject then and the code check is what
      makes an address constant. Moving the check to the compositor leaves the
      foliator free to say what it does, and the explanation lands where a reader
      can check it.
- [ ] ! IT CARRIES `a-closing-quote-with-a-comment` WITH IT, FOR FREE. CHECKED
      2026-08-21: read through `paragraphs_lexical` with `"""` as a delimiter, the
      numpy shape yields ONE paragraph and line 5 is owned ONCE -- the `# NOQA`
      rides along on the closing line as part of the run. A reader that cuts at
      the delimiter has no second half to reconcile, so that defect is gone by
      construction rather than fixed.
- [ ] !! WHAT THIS BRANCH ACTUALLY OWES IS THE POSITION RULE, and it is the third
      of the three things listed above. `"""` is BOTH Python's string quote and
      its doc delimiter: the row lists it under `spanning_quotes`, and
      `_strip_strings` blanks a spanning quote BEFORE the comment-opener test --
      by design, so a `//` inside a string cannot open a comment. So a docstring
      is a STRING IN A PARTICULAR POSITION, and stating that position is what
      replaces the parser.
- [ ] * PROPOSED 2026-08-22 (Roy): THE ANCHORS MAY NEED THEIR DEPTH. The position
      rule this branch owes -- a docstring is a STRING IN A PARTICULAR POSITION --
      is a rule about DEPTH once there is no parser. MEASURED 2026-08-22: an
      anchor already holds its line VERBATIM WITH ITS INDENTATION (a2 is "    def
      m(self):" at 4, c2 is "        x = 1" at 8), so depth is DERIVABLE from
      every place today and STATED by none. ! It answers TWO of the three things
      the AST buys: WHERE THE BODY STARTS is the first anchor deeper than the
      declaration, which a wrapped signature no longer moves, and INSIDE THIS BODY
      is depth greater than the declaration. ! NECESSARY, NOT SUFFICIENT: on the
      same fixture y = """not a docstring""" sits at depth 8 like every other line
      of that body, so depth says WHICH BODY and the walk order says FIRST -- the
      pair replaces ast.get_docstring, not depth alone.
- [ ] * DEFERRED HERE BY TRANSITIVITY, Roy 2026-08-22: *"to make python capable of
      being read correctly we are going to have to do this ... the fix to one will
      fix the other."* MAKE _strip_strings STATEFUL -- carry open-quote state
      across lines instead of reading each line alone. It is the same reader:
      triple-quote is Pythons doc delimiter AND a spanning quote, so whatever
      computes parity for one computes it for the other
- [ ] THE COST OF NOT HAVING IT, MEASURED 2026-08-22 by a code review and
      reproduced here: prove_unchanged refuses a file on the PRESENCE of a
      spanning delimiter, because parity is what a per-line reader cannot compute
      -- its own words, *a proof that refuses costs a report; a proof that lies
      costs the claim*. TEN languages declared none, so the refusal never fired
      and the gate LIED instead: an edit made INSIDE a Rust string literal
      reported PROVEN at exit 0, fingerprints identical. That is the stage 7b gate
      failing open
- [ ] ! FOUR ROWS WERE FIXED THE SAME DAY AND FOUR WERE NOT, and the split is why
      this task exists. Go raw-string backtick, Ruby heredoc, Lua long-bracket and
      TOML triple-quote are DISTINCTIVE delimiters, so declaring them costs almost
      nothing. rust, shell, sql and the C++ raw string use the ordinary double and
      single quote, which appear in nearly every file -- declaring those is
      CORRECT by the rule and makes Rust effectively unprovable. A stateful reader
      is what removes the choice between refusing everything and lying sometimes
