# The AST reader gets older every release while the files get newer

```
Status:   open
Progress: 0 of 10 tasks done
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
