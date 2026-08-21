# The AST reader gets older every release while the files get newer

```
Status:   open
Progress: 0 of 21 tasks done
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
