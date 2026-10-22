# Lexical readers implementation

```
Status:   decision-needed
Progress: 34 of 162 TODO tasks closed
Plan-tasks: 11 of 53 plan tasks closed
Owner:    backend
Requires-Roy: true
Raised:   2026-10-11 (founded by move-t from 0.2.4-the-middle-rebuilt)
```

## Objective

Implement the approved lexical-reader design in
docs/superpowers/specs/2026-10-11-lexical-readers-design.md. Read maintained
source with project-owned standard-library-only Python. Each language owns its
dated specification, TOML definition, recognition rules and implementation
subplan. Shared source regions, ownership, diagnostics and saved reading context
support existing addresses, setting and both preservation checks. Develop the
shared contract and registry before the Python end-to-end implementation; use
its verified integration contract for the remaining independent language
subplans. Complete the mechanism before updating operational instructions.
Generated output is excluded during target selection. The design mapping defines
the closure boundaries and superseded prescriptions for the linked TODOs;
preserve their behavioral goals in replacement tasks before retiring obsolete
checks. The branch is feat/lexical-readers; language branches use
feat/lexer-<language> and merge back with no-ff. Existing addressing, whole
sections and the agreed Go rule remain fixed. No full name harvesting, new C or
C++ declaration places, mark composition, markup addressing or release
publication is included. Executors receive task-only briefs with required
interfaces, inputs and checks, without internal development files or history.

## TODO tasks this plan closes

### A - [lexical-code-identity](../../TODO/lexical-code-identity.md)

- [x] T1 | MOVED to 2026-10-11-lexer-python | Replace Python AST identity checks
      with lexical comparison; verify docstring add and removal agree at both
      gates
- [ ] T2 | Preserve literal whitespace in prove_unchanged.py:191-207; verify
      blank-line and trailing-space edits change the fingerprint

### B - [smoke-fixture-defects](../../TODO/smoke-fixture-defects.md)

- [ ] T1 | Update wrapped-drop expected text for paragraph rewrapping and verify
      the full command smoke passes

### C - [the-flow-lives-in-the-command](../../TODO/the-flow-lives-in-the-command.md)

- [-] T8 | Update page_of to return (None, reason) for an unparsed page so
      _pages drops its bare except and kind scan. Verify: one call in _pages

### D - [language-rows-in-toml](../../TODO/language-rows-in-toml.md)

- [ ] T17 | Specify each supported language independently; verify each has its
      own dated spec, references and fixtures
- [ ] T18 | Implement one definition file per language; verify each configures
      its parser without family defaults or language inheritance
- [-] T1 | T1 -- Transcribe all 18 language rows into
      `references/languages.toml`, Python included, with `tier` as a field.
      Verify: the file holds 18 tables, one per row.
- [-] T2 | T2 -- Build `Language` from that table at runtime, the way
      `vocabulary.py` reads `vocabulary.toml`. Verify: `grep -c "Language("
      language.py` returns 1.
- [-] T3 | T3 -- Pin the order-significant fields, since openers match
      longest-first. Verify: a test fails if `///` follows `//`, or `--[==[`
      follows `--[[`.
- [-] T4 | T4 -- Pin that an EMPTY list is not a missing key. Verify: `declares
      = []` loads as *no `a` series at all*, and a row with no `declares` key is
      refused as undecided.
- [-] T5 | T5 -- Move `test_every_row_STATES_its_own_quotes` from parsing the
      Python AST to asking whether the key is present. Verify: the test reads
      the table, not the AST.
- [ ] T12 | T12 -- Make `tier_for` (`language.py:546`) read the row's `tier`
      field instead of `lang.name == "python"`. Verify: `language.py` holds no
      comparison of `lang.name`.
- [ ] T13 | T13 -- Dispatch the READER at `page.py:694` on the row, not on
      `lang.name`. Verify: a file cannot be read at one tier and stamped at the
      other.
- [ ] T15 | T15 -- Make `prove_unchanged.py:176` take the `(".py", ".pyi")`
      suffix tuple from `language.py:99`. Verify: the tuple is not re-spelled in
      `prove_unchanged.py`.
- [ ] T16 | T16 -- Make `referrers.py:53` take the same suffix tuple from
      `language.py:99`. Verify: the tuple is not re-spelled in `referrers.py`.

### E - [doc-does-not-fill-its-a](../../TODO/doc-does-not-fill-its-a.md)

- [ ] T10 | Implement Go documentation adjacency; verify touching comments use
      a, separated comments use b, and reader prose agrees
- [ ] T6 | T6 -- Name in `compact.md:113` whatever remains genuinely unresolved
      after T5. Verify: the stamp's explanation at :113 names the case that
      still fires.
- [-] T8 | T8 -- * RULE ruby's adjacency, from ruby's own grammar and not from
      go's. Verify: one of the two comments is corrected to cite the other, for
      ruby.
- [x] T11 | Record Ruby attachment from authoritative RDoc sources; verify the
      spec permits blank lines and preserves whole sections
- [ ] T12 | Implement Ruby attachment; verify blank-separated prose uses a,
      intervening code blocks attachment, and sections stay whole

### F - [python-cannot-read-python](../../TODO/completed/python-cannot-read-python.md)

- [-] T32 | T32 -- Read Python on the lexical tier -- no `import ast` in the
      lexer. Verify: `grep -rn 'import ast' plugins/` misses lexer.py:28 and a
      `.py` file still censuses.
- [-] T33 | T33 -- Hold the round-trip identity over the Python corpora with the
      new reader. Verify: `compositor.identity` reproduces R13's 2,368
      byte-identical round trips.
- [-] T34 | T34 -- A file with syntax NEWER than the floor censuses instead of
      setting empty. Verify: sentry's `api/paginator.py` yields places and sets
      back its 884 lines.
- [-] T36 | T36 -- Keep the Python fixtures passing under the `stripped` proof.
      Verify: `uv run python -m unittest discover -s tests -k prove_unchanged`
      is green.
- [-] T37 | T37 -- Say in `prove_unchanged`'s docstring what `stripped` does NOT
      cover. Verify: the docstring claims same lines in the same order, never
      semantic equivalence.
- [x] T38 | MOVED to 2026-10-11-lexer-python | Rebuild `prove_unchanged` to
      prove code unchanged with no `ast` branch. Verify: an edited docstring
      proves, a moved token does not
- [-] T39 | Emit a paragraph for a Python docstring on the lexical tier. Verify:
      `paragraphs_lexical` over a documented def returns one

### G - [lexer-and-language-findings](../../TODO/lexer-and-language-findings.md)

- [ ] T3 | T3 -- Exclude `Kind.MATTER` from the walk-up candidates. Verify: Ruby
      front matter above a `def` leaves `f0.declares` unset, and only `a1`
      declares 1.
- [ ] T4 | T4 -- Let the shell row say `#` is inert after a dollar-brace.
      Verify: `n=${#arr} # count` censuses as ONE trailing comment at `# count`,
      not at column 5.
- [ ] T13 | T13 -- Give Java its own expression of a soft keyword: `record` at
      language.py:248. Verify: `record = lookup()` in a `.java` mints no `a`,
      and a real one still does.
- [ ] T14 | T14 -- Give C# its own expression of a soft keyword: `record` at
      language.py:283. Verify: `record = lookup()` in a `.cs` mints no `a`, and
      a real one still does.
- [ ] T15 | T15 -- Give Swift its own expression of soft keywords: `convenience`
      and `required`. Verify: `required = f()` in a `.swift` mints no `a`, and a
      real init still does.
- [ ] T16 | MOVED to 2026-10-22-lexer-rust | T16 -- Declare Rust's spanning
      quotes; language.py:117-146 carries none. Verify: a Rust multi-line string
      is neither refused wholesale nor read as comments.
- [ ] T17 | T17 -- Declare C's spanning quotes; language.py:185-193 carries
      none. Verify: a C multi-line string is neither refused wholesale nor read
      as comments.
- [ ] T18 | T18 -- Bound Lua's long-bracket level, or read it; language.py:473
      stops at two `=` so `--[===[` reads as code. Verify: a fixture with
      `--[===[` fails before the fix.
- [ ] T19 | T19 -- Make `def g(): """d."""` census instead of failing the file.
      Verify: it types `a1 kind=docstring anchor=g` and `census.py` exits 0.
- [ ] T22 | T22 -- Pin the address the CURRENT tier produces, so the move
      arrives as a failing test. Verify: a test asserts `a1` for a same-line
      docstring today.
- [ ] T23 | T23 -- Set a same-line docstring on its own line below the
      declaration. Verify: `def g(): """d."""` round-trips to the two-line form.
- [ ] T24 | T24 -- Make `prove_unchanged` admit that one move. Verify: PROVEN on
      the two-line form, and still FAILS when any other token on that line
      moves.
- [ ] T25 | T25 -- Make `_is_doc` consult placement, not only the opener string.
      Verify: a Lua `---` run above `local function f()` types `docstring`,
      above nothing `comment`.
- [ ] T27 | MOVED to 2026-10-22-lexer-rust | T27 -- Declare Rust's `//!` inner;
      `///` stays outer. Verify: a `.rs` opening `//!` above nothing types
      `docstring`, and `///` above nothing types `comment`.
- [ ] T28 | T28 -- Add `---` to Lua's `doc_line`, which T20's ruling authorises.
      Verify: `--- x` above `local function f()` types `docstring` anchored to
      it.
- [ ] T32 | MOVED to 2026-10-22-lexer-rust | Recognize raw string delimiters in
      lexer.py:510; verify a quoted marker inside a Rust raw string stays
      literal data
- [ ] T33 | Recognize JavaScript regex literals in lexer.py:1071; verify /[//]/
      yields no comment paragraph
- [ ] T34 | Resume code scanning after block comments in lexer.py:1071; verify a
      quote in a block cannot hide a following line comment
- [ ] T35 | Select the earliest block opener in lexer.py:1072; verify mixed Lua
      delimiters inside a long comment preserve its full body
- [ ] T6 | T6 -- Make language.py:9 name a file that exists, or drop the
      citation -- `scripts/check_language_leaf.py` does not. Verify: the path it
      names resolves.
- [ ] T8 | T8 -- De-duplicate the sorted `line_comment` opener tuple,
      byte-identical at lexer.py:999 and desk.py:379. Verify: the expression
      appears once.
- [ ] T9 | T9 -- De-duplicate the `continues-a-trailing-comment` stamp,
      copy-pasted at lexer.py:1168-1176 and :1772-1780. Verify: `grep -c` of its
      sentence returns 1.
- [ ] T2 | T2 -- Stamp every paragraph an unterminated block comment swallowed,
      not only the last. Verify: all of them carry
      `unterminated-paragraph-comment`.
- [ ] T7 | T7 -- Gate the two-importer rule: fail when a third module reads a
      language symbol. Verify: the gate exists and fails on a planted third
      importer of `language`.
- [ ] T10 | T10 -- Use `bisect` at lexer.py:1614, where a list comprehension
      scans the sorted `above_code` built one line earlier. Verify: the scan is
      gone and the suite green.
- [ ] T11 | T11 -- Replace the four one-element lists standing in for `nonlocal`
      in lexer.py. Verify: no `[0]` subscript on a one-element accumulator
      remains in lexer.py.
- [ ] T21 | T21 -- Record the `a1` -> `c` move in `docs/history.md` with the
      ruling that predicted it. Verify: the entry names both tiers and the
      ruling's date.
- [-] T26 | T26 -- Give the `Language` row an `inner_doc` field, defaulting
      empty so every existing opener stays outer. Verify: the field exists and
      no row's typing changes.
- [ ] T29 | Correct `doc_is_structural`'s docstring so it matches what Python
      yields on the lexical tier. Verify: the prose names the empty result
- [ ] T12 | T12 -- Settle what `Paragraph.lines` counts: three rules fill it,
      one column reads it. Verify: one rule fills it, or the field is gone and
      the column computes it.
- [ ] T49 | MOVED to 2026-10-22-lexer-rust | State Rust's inner doc openers in
      Rust's own definition file

### H - [a-doc-comment-is-cued-a-and-typed-b](../../TODO/a-doc-comment-is-cued-a-and-typed-b.md)

- [ ] T1 | Decide whether the lexer types by MARKER or by the place the walk
      gave it
- [ ] T2 | Make the kind agree with the cue for go, ruby and lua
- [ ] T3 | Remove the three strict xfails in tests/test_reading.py once they
      pass
- [ ] T4 | Update the retype comment at page.py:1074-1081, which states that
      kind and series must agree while its branch tests one kind of four

### I - [matter-misses-two-languages](../../TODO/matter-misses-two-languages.md)

- [ ] T2 | MOVED to 2026-10-22-lexer-rust | T2 -- Stop a Rust file's opening
      `//` run being claimed as a declaration's doc. Verify: a `.rs` opening `//
      Copyright` types `f0 matter` and an empty `a1`.

### J - [block-comment-markers-survive-into-the-prose](../../TODO/block-comment-markers-survive-into-the-prose.md)

- [ ] T1 | T1 -- Strip the `block_comment` and `doc_block` opener and closer in
      `_join`. Verify: a `.java` docstring's census `text` holds no `/**` and no
      `*/`.
- [ ] T2 | T2 -- Strip the interior continuation marker as well. Verify: a
      multi-line Javadoc's census `text` carries no leading `*` on any line
      after the first.
- [ ] T7 | T7 -- Write the unit fixtures for the fix from INVENTED text, not
      from the corpus. Verify: no assertion under `tests/` quotes a line from
      any file in the table above.
- [ ] T8 | T8 -- Add a multi-line Javadoc to `tests/fixtures/sample.java`.
      Verify: the fixture carries a continuation `*` on three or more lines.
- [ ] T9 | T9 -- Decide whether a Ruby `=begin`/`=end` block gets the same
      stripping. Verify: the answer and its measurement are written into this
      file.
- [ ] T10 | T10 -- Decide the same for a Lua `--[[ ]]` block, from Lua's own
      grammar and not Ruby's. Verify: the answer and its measurement are written
      into this file.
- [ ] T3 | T3 -- Change `block_text` (`lexer.py:609`) in the SAME commit as each
      `_join` change. Verify: the round trip is green on that commit.

### K - [doc-on-the-declaring-line](../../TODO/doc-on-the-declaring-line.md)

- [ ] T3 | Add the shape to tests/test_reading.SOURCES and
      tests/test_compositor.FORMS. Verify: both go red before the two boxes
      above and green after.
- [ ] T4 | Update the lexer so a docstring attaches to the line of code it
      shares, and the walk emits that line's places

### L - [closing-line-deletes-code](../../TODO/closing-line-deletes-code.md)

- [ ] T4 | T4 -- * RE-RULE the 2026-08-20 acceptance with the DELETED CODE on
      the table, and say which of the two contradicting notes stands. Verify:
      the answer is in this file.
- [ ] T7 | T7 -- When the galley's composition step lands, take whichever option
      T4 leaves standing. Verify: the Objective's C input refuses, or keeps `int
      x = 5;`.
- [ ] T8 | T8 -- Pin T7 with a test on that same four-line C input. Verify: the
      test fails on the pre-change tree and passes after it.

### M - [a-comment-inside-a-line-makes-the-file-unprovable](../../TODO/a-comment-inside-a-line-makes-the-file-unprovable.md)

- [ ] T2 | T2 -- Print a DIFFERENT named cause at each of the eight refusal
      sites listed in the Objective. Verify: the eight causes are distinct, and
      none is the empty string.
- [ ] T3 | T3 -- Assert the causes the CLI can reach. Verify: a test asserts the
      four reachable causes named in the Objective, and fails if any two are the
      same.
- [ ] T5 | T5 -- DEFERRED, only if the model moves: give a paragraph a COLUMN
      SPAN. Verify: a paragraph names a span WITHIN a line, and both pinned test
      classes pass unweakened.
- [ ] T6 | T6 -- DEFERRED, and in T5's commit: make `code_lines` and
      `_without_comments` read the span. Verify: `int x = /* why */ 5;` changed
      to `7` reports NOT PROVEN.
- [ ] T4 | T4 -- DEFERRED. Count the shape across the corpora before building
      anything. Verify: a per-language rate of a closed `/* */` with code after
      it, over the corpus.

### N - [bom-is-read-as-source](../../TODO/bom-is-read-as-source.md)

- [ ] T1 | T1 -- Read with `utf-8-sig` at `repo.py:52` and `census.py:336`, the
      lexical route. Verify: the BOM'd `.c` shows all three results named just
      above the task list.
- [ ] T2 | T2 -- Read with `utf-8-sig` at `census.py:177`, which feeds
      `ast.parse`. Verify: a BOM'd `.py` censuses its module docstring, not one
      `unparsed` paragraph.

### O - [census-degrades-silently](../../TODO/census-degrades-silently.md)

- [ ] T7 | T7 -- Open the three readers with `utf-8-sig` -- `repo.py:52`,
      `census.py:336`, `census.py:177`. Verify: a BOM'd `.py` censuses its
      module docstring.
- [ ] T5 | T5 -- Correct `references/compact.md:100` -- it says an `unparsed`
      file was not censused, and it was. Verify: the row says the paragraphs
      carry no address.
- [ ] T6 | T6 -- Refuse an `add` at the `a` place of a one-line declaration
      instead of writing above the `def`. Verify: `galley.reset` returns a
      problem for that edit, not `[]`.

### P - [prove-unchanged-line-endings-follow-a-sibling](../../TODO/prove-unchanged-line-endings-follow-a-sibling.md)

- [ ] T1 | Check a written file's line endings against its own pre-edit bytes,
      not against one untouched sibling
- [ ] T2 | Test it with a CRLF file beside an LF sibling: an edit keeping CRLF
      proves, one converting to LF fails

### Q - [the-cue-legend-and-its-round-trip](../../TODO/the-cue-legend-and-its-round-trip.md)

- [ ] T2 | T2 -- Re-lex a written page and compare its cues against the
      census's. Verify: an unedited page round-trips with every cue holding the
      same content.
- [ ] T3 | T3 -- Refuse a page whose cues came back different. Verify: moving
      one paragraph's text under a neighbouring cue is caught and named.
- [ ] T4 | T4 -- Report the `f` series separately rather than as a disagreement.
      Verify: a file with front matter round-trips without a false finding.
- [ ] T5 | T5 -- Prove the check can FAIL. Verify: with T3's refusal removed,
      T3's own case passes and the test goes red.

### R - [the-code-check-refuses-add-and-drop-on-a-docstring](../../TODO/the-code-check-refuses-add-and-drop-on-a-docstring.md)

- [ ] T4 | T4 -- Measure the LEXICAL side: a `///` or `/**` doc comment ADDED
      and REMOVED, against the `stripped` comparison. Verify: this file records
      which way each goes.
- [ ] T2 | T2 -- Report docstring-presence deltas SEPARATELY from executable
      ones. Verify: `prove_unchanged.py` prints them under their own heading
      with each declaration.
- [ ] T3 | T3 -- Say in `write.md` what a docstring `add` does today, until T1
      is settled. Verify: `write.md` states that it fails the CODE CHECK and
      that the rail restores.

### S - [prove-refuses-a-doc](../../TODO/prove-refuses-a-doc.md)

- [ ] T4 | Update the gate so a NOT-CODE file is reported out of scope, naming
      the chain it waits on rather than a language record
- [ ] T5 | Update the gate so a CODE file whose language has no record yet is
      reported out of scope, named apart from a not-code file

### T - [computed-and-never-read](../../TODO/computed-and-never-read.md)

- [ ] T6 | T6 -- Compute `code_lines` and `declarations` once per page, not at
      :419-420 and again at :725-726. Verify: each is computed once and the four
      test callers pass.

### U - [page-and-addresser-scans](../../TODO/page-and-addresser-scans.md)

- [ ] T5 | T5 -- Stop `page.declarations()` running TWICE per file
      (`page.py:420`, `:726`). Verify: `grep -n 'declarations(' page.py` returns
      ONE call site, census unchanged.

### V - [name-corpus-sees-one-language](../../TODO/name-corpus-sees-one-language.md)

- [ ] T1 | declarations() gains the identifier on the declaring line, per
      language row
- [ ] T5 | referrers.tokens_for stops parsing Python for top-level defs, or says
      why it still must

### W - [galley-and-compositor-write-path](../../TODO/galley-and-compositor-write-path.md)

- [-] T5 | T5 -- **Test the newline axis the gates never saw.** Verify: a CRLF
      fixture makes `line_endings()` answer CRLF, and the test fails on HEAD.
- [-] T6 | T6 -- **Extract the prologue the two gates share** -- read, resolve
      the language, build the page, set it. Verify: one function does all four.
- [-] T7 | T7 -- **Make `lossless` and `identity` call that one function.**
      Verify: neither repeats the four steps.
- [-] T8 | T8 -- **Make `main` read each file once** rather than running the
      pair twice per file. Verify: a run over one file performs one read of it.
- [-] T9 | T9 -- **Make `page_for` RECORD whether the source was read**, rather
      than throwing the fact away. Verify: a page built from an unread source
      carries that fact.
- [-] T10 | T10 -- **Make `compositor.py:231` refuse on that fact, not on an
      empty list.** Verify: an empty file with no text still sets back as empty.
- [x] T51 | MOVED to 2026-10-11-lexical-read-results | Consolidate round-trip
      checks in a flow; verify one acquisition and setting per file and
      independent comparison outcomes
- [x] T52 | MOVED to 2026-10-11-lexical-read-results | Verify source-byte
      preservation using invented BOM, newline and empty fixtures; detect
      normalization at the actual I/O boundary

### X - [no-step-produces-a-page](../../TODO/no-step-produces-a-page.md)

- [-] T3 | Repoint compositor.lossless and compositor.identity at page_of, which
      also removes the prologue those two share

### Y - [only-a-flow-reaches-the-machine](../../TODO/only-a-flow-reaches-the-machine.md)

- [ ] T3 | Move read_source out of results.compositor lossless and the identity
      check
- [ ] T4 | Move read_raw out of results.prove_unchanged
- [ ] T10 | Move the git call out of results.prove_unchanged into the flow; grep
      finds no results import of machine.repo

### Z - [fixtures-do-not-test-the-shape](../../TODO/fixtures-do-not-test-the-shape.md)

- [ ] T2 | MOVED to 2026-10-22-lexer-rust | T2 -- Make
      `tests/fixtures/sample.rs` open the way a licence header does, or add a
      `.rs` fixture that does. Verify: it reproduces
      `matter-misses-two-languages`.
- [ ] T3 | T3 -- Audit the other sixteen fixtures -- for each language row, name
      the shape its open TODOs are about. Verify: a list of language -> shape ->
      does it exercise it.
- [ ] T5 | T5 -- Say in `tests/fixtures/` what each file is a fixture OF, so a
      reader can tell coverage from resemblance. Verify: every `sample.*` names
      what it exercises.

### AA - [assertions-that-gate-a-substring](../../TODO/assertions-that-gate-a-substring.md)

- [ ] T3 | T3 -- Assert the EXTENT at `test_census_blocks.py:937` -- `(start,
      end)` and `raw_lines`, not `b.start`. Verify: ending `matter` at its first
      line goes red.
- [ ] T8 | T8 -- Run the keyword scan over real lines in
      `test_declarations.py:313-319`, not `""`. Verify: `_declares_here`
      returning False always turns the class red.

### AB - [b-addresser-uninitialised](../../TODO/b-addresser-uninitialised.md)

- [ ] T16 | T16 -- Make `test_every_b_the_marks_name_exists`
      (`tests/test_edge_cases.py:81`) assert each mark's ANCHOR. Verify: shift
      every `b` mark by one and it goes red.
- [ ] T17 | T17 -- Make `test_every_a_and_c_the_marks_name_exists`
      (`tests/test_edge_cases.py:106`) assert the ANCHOR. Verify: shift a `c`
      mark, red.
- [ ] T18 | T18 -- Make `test_b1_is_the_gap_above_the_first_line_of_code` assert
      the ANCHOR of the cue it names. Verify: it goes red today -- `b1` anchors
      the SECOND line of code.

### AC - [the-anchor-claims-are-inverted](../../TODO/the-anchor-claims-are-inverted.md)

- [ ] T1 | T1 -- Take *"a comment's anchor"* out of the `tokenized` CANNOT
      ANSWER column at `SKILL.md:430`. Verify: no row of that table says a
      comment has no anchor.
- [ ] T2 | T2 -- Drop the false premise at `SKILL.md:433-435`, keeping the
      CANDIDATE conclusion. Verify: no sentence in `SKILL.md` says a comment
      carries no anchor.
- [ ] T3 | T3 -- Correct `reviewer-brief.md:126-127` to say a LINE OF CODE, not
      a declaration. Verify: `grep -rn "names the declaration" plugins/` comes
      back empty.
- [ ] T4 | T4 -- Drop *"and is empty where none was"* from the same sentence --
      a reviewer's slot never is. Verify: `grep -rn "empty where none was"
      plugins/` comes back empty.

### AD - [docstrings-need-their-own-address-series](../../TODO/docstrings-need-their-own-address-series.md)

- [ ] T8 | T8 -- Tell a role when its `a` series is empty, and why. Verify: a
      run over a `.sh` file hands the role that sentence.
- [ ] T9 | T9 -- Correct the two "The three series" sentences at `SKILL.md:378`
      and `reviewer-brief.md:69`. Verify: neither states three series
      unconditionally.

### AE - [the-cue-legend-was-never-written](../../TODO/the-cue-legend-was-never-written.md)

- [ ] T1 | Write the legend: every series letter, what it names, and where its
      prose sits
- [ ] T2 | Say where it lives -- the brief, a reference of its own, or each role
      file

### AF - [doc-is-structural-means-two-things](../../TODO/doc-is-structural-means-two-things.md)

- [ ] T1 | T1 -- Split or rename `doc_is_structural` so each reader names the
      property it uses. Verify: `grep -n doc_is_structural scripts/*.py` shows
      each reader's property.
- [ ] T2 | T2 -- Correct `lexer.block_text`'s docstring at `:634-635` and
      `:643-644`, which call it a string in a body. Verify: no comment says only
      Python sets the flag.
- [ ] T3 | T3 -- Refuse or route the latent case -- a record with both
      `doc_line` and `doc_is_structural=True`. Verify: a `///` run through
      `block_text` keeps no marker.

### AG - [a-series-never-fills-outside-python](../../TODO/a-series-never-fills-outside-python.md)

- [ ] T18 | T18 -- Match a `declares` keyword ANYWHERE in the line, per the
      Objective's body. Verify: the ten cases in the Objective answer correctly,
      and `_FIRST_WORD` is gone.

### AH - [one-stem-four-jobs](../../TODO/one-stem-four-jobs.md)

- [ ] T2 | T2 -- Rename `Language.declares` to `introduces`, on the field and on
      every row. Verify: `grep -n declares` over `language.py` returns nothing.
- [ ] T3 | T3 -- Rename `lexer._declares_here` to match `introduces`. Verify:
      `grep -n declares` over `lexer.py` returns no use of the language keyword
      tuple.

### AI - [lexer-does-not-lex](../../TODO/lexer-does-not-lex.md)

- [?] T8 | T8 -- * DETERMINE THE NAME, after the Python ruling lands. Verify:
      the name and its reason are written in `docs/vocabulary.md`.
- [ ] T9 | T9 -- Rename the module and every import of it. Verify: `uv run
      pytest -q` is green and no file under `plugins/` imports the old module
      name.
- [ ] T10 | T10 -- Retire the old word in the vocabulary entry and in every
      prose use. Verify: `check_vocabulary.py` passes with the old word RETIRED
      and the new one defined.

### AJ - [the-lexer-reads-no-files](../../TODO/the-lexer-reads-no-files.md)

- [ ] T9 | T9 -- **Create `io.py` and move `read_raw` into it from `repo.py`.**
      Verify: `io.read_raw` resolves, and `repo.py` defines no reader.
- [ ] T10 | T10 -- **Move `text_lines` out of `constants.py` into `io.py`.**
      Verify: it resolves from `io.py`, and `constants.py` no longer defines it.
- [ ] T11 | T11 -- **Move `utf8_console` out of `constants.py` into `io.py`.**
      Verify: it resolves from `io.py`, and `constants.py` exports `LINE_BREAK`
      and nothing else.
- [ ] T12 | T12 -- **Move the `newline=""` write out of `compositor.py` into
      `io.py`.** Verify: `grep -n 'newline=' compositor.py` returns nothing.
- [ ] T13 | T13 -- **Write the read/write gate**: a shipped
      `read_text\|write_text\|open(` outside `io.py` fails. Verify: it exits
      nonzero on the tree as it stands, naming each site.
- [ ] T14 | T14 -- **Give `page_for` a PATH instead of text.** Verify: no caller
      of `page_for` passes text, and the signature takes a path.
- [ ] T15 | T15 -- **Let the lexer open the file, with `io.read_raw` and
      `utf-8-sig`.** Verify: a CRLF file carrying a BOM reads back with both
      preserved.
- [ ] T16 | T16 -- **Route the nine bypassing source reads through `io.py`.**
      Verify: T13's gate exits 0 on the tree, and every source read in the
      shipped scripts is the lexer's.
- [-] T17 | T17 -- **Fix `compositor.identity` so the round trip is compared in
      BYTES.** Verify: it reads through `io.read_raw` and not `read_text`.
- [-] T18 | T18 -- **Test `identity` on a CRLF file, FAILING FIRST.** Verify: a
      file written `b'# a note\r\nx = 1\r\n'` reports a difference before the
      fix and `None` after.
- [ ] T19 | T19 -- **Assert the READ chain as data**: it IS `[language,
      read_text, lexer, addresser, page]`. Verify: the test fails when a step is
      removed from the list.
- [ ] T20 | T20 -- **Assert the WRITE chain as data**, the seven steps named in
      the Objective. Verify: the test fails when a step is removed from the
      list.
- [x] T23 | MOVED to 2026-10-11-lexical-read-results | Acquire exact UTF-8
      source from files and Git; verify BOM, line endings, Unicode, identity and
      named failures
- [x] T24 | MOVED to 2026-10-11-lexical-read-results | Write exact UTF-8 bytes;
      verify unchanged round trips and encoding failure before target truncation

### AK - [7a-can-prove-the-change-by-applying-it-to-a-copy](../../TODO/7a-can-prove-the-change-by-applying-it-to-a-copy.md)

- [ ] T5 | T5 -- Derive the galley census from the splice's line deltas instead
      of re-running `census.py`. Verify: derived and re-run agree on every
      range-replacement paragraph.
- [ ] T6 | T6 -- Carry the `add` insertion out of the splice so an empty
      interval derives too. Verify: a derived census gives `(9, 9)` not `(9,
      11)`, with kind `comment`.
- [ ] T7 | T7 -- Cut the cycle to ONE census on disk. Verify: `SKILL.md` names
      one census artifact, not both `census.json` and `galley-census.json`.

### AL - [two-live-runs-proposed-fifteen-changes](../../TODO/two-live-runs-proposed-fifteen-changes.md)

- [ ] T15 | T15 -- P1 (redacted-corpus) -- parse after every write, for the
      NON-PYTHON cases. Verify: name what stands in for a parse at the `lexical`
      tier, or close this.

### AM - [exception-hierarchy](../../TODO/exception-hierarchy.md)

- [ ] T4 | T4 -- Retire `TOKENIZE_ERRORS` -- each site re-raises `Unparsable`
      with `from e`. Verify: `grep -rn exceptions.TOKENIZE_ERRORS plugins/` is
      empty and pytest is green.

### AN - [a-comment-run-merges-across-blanks](../../TODO/a-comment-run-merges-across-blanks.md)

- [?] T6 | Decide whether Paragraph.lines still has a place, given the mark
      changes and the address system carrying the text properly?

### AO - [2026-10-11-source-reading-contract](../../TODO/completed/2026-10-11-source-reading-contract.md)

- [x] T1 | MOVED to 2026-10-11-lexical-source-contract | Represent source as
      ordered regions and ownership facts; verify exact reconstruction and
      independently expected classifications
- [x] T2 | MOVED to 2026-10-11-lexical-reading-context | Carry reader
      compatibility and language settings through saved runs; verify
      incompatible contexts refuse before address use
- [x] T5 | MOVED to 2026-10-11-lexical-read-results | Define immutable read
      diagnostics and failures; verify location units, field validation and
      successful empty input
- [x] T6 | MOVED to 2026-10-11-lexical-read-results | Reject failed readings at
      page and proof admission; verify either-side failures, empty success and
      cleanup

### AP - [2026-10-11-maintained-source-selection](../../TODO/2026-10-11-maintained-source-selection.md)

- [ ] T1 | Exclude generated and preprocessed output from review targets; verify
      the task instructions select maintained source

## Plan Tasks

- [x] P1 | Source contract subplan implemented, tested and reviewed; 196 focused tests pass | 1c455282 | Define
      ordered regions and ownership in reading/source.py; verify reconstruction
      and independently expected classifications
        > 2026-10-11 Check: uv run pytest -q tests/test_reading_source.py
        > 2026-10-11 Implemented by subplan 2026-10-11-lexical-source-contract
- [x] P2 | Explicit failed-read admission implemented and verified in child | fd1e56a1 | Define
      lexical and placement diagnostics; verify incomplete reads cannot supply
      successful pages or preservation proofs
        > 2026-10-11 Check: uv run pytest -q tests/test_reading_diagnostics.py
        > 2026-10-11 Subplan 2026-10-11-lexical-read-results owns this work
- [-] P3 | Replaced by P51; approved spec uses source I/O tests rather than saved proof JSON tests | b03adaa8 | Integrate
      exact source acquisition; verify BOM, CRLF, mixed endings, Unicode and
      empty input survive the read and write path
        > 2026-10-11 Check: uv run pytest -q tests/test_proof_io.py
- [-] P4 | Approved split: P52 owns shared registry machinery; P53 owns per-language definitions | d2d29ccf | Load
      independent TOML language definitions; verify registry dispatch, explicit
      capabilities and excluded file categories
        > 2026-10-11 Check: uv run pytest -q tests/test_language_definitions.py
- [x] P5 | Required reading settings and identities persist through saved containers; full gates pass | afef752e | Carry
      reading compatibility and dialect settings through pages and binders;
      verify serialization preserves their identity
        > 2026-10-11 Check: uv run pytest -q tests/test_reading_context.py
        > 2026-10-11 Subplan 2026-10-11-lexical-reading-context owns this work
- [x] P6 | Saved context admission precedes distribution folding drafting and resume; full gates pass | afef752e | Reject
      incompatible saved reading contexts before address admission; verify
      distribution, folding, drafting and resume
        > 2026-10-11 Check: uv run pytest -q tests/test_reading_context.py
        > 2026-10-11 Subplan 2026-10-11-lexical-reading-context owns this work
- [x] P7 | Approved Python spec and subplan define modes, directives, ownership and fixtures | 9546ebe1 | Specify
      Python independently; verify supported modes, directive boundaries,
      declaration ownership and expected fixtures
        > 2026-10-11 Own dated spec and subplan; branch feat/lexer-python
        > 2026-10-11 Python child: docs/plans/2026-10-11-lexer-python.md
- [x] P8 | Child lexer-python closed; test_python.py 1275 pass | 2bf15f2b | Implement
      the Python reader from its definition; verify expected comments, protected
      code, addresses and set/proof behavior
        > 2026-10-11 Check: uv run pytest -q tests/reading/test_python.py
        > 2026-10-11 Python child: docs/plans/2026-10-11-lexer-python.md
- [ ] P9 | Specify Rust independently; verify supported modes, directive
      boundaries, declaration ownership and expected fixtures
        > 2026-10-11 Own dated spec and subplan; branch feat/lexer-rust
- [ ] P10 | Implement the Rust reader from its definition; verify expected
      comments, protected code, addresses and set/proof behavior
        > 2026-10-11 Check: uv run pytest -q tests/reading/test_rust.py
- [ ] P11 | Specify Go independently; verify supported modes, directive
      boundaries, declaration ownership and expected fixtures
        > 2026-10-11 Own dated spec and subplan; branch feat/lexer-go
- [ ] P12 | Implement the Go reader from its definition; verify expected
      comments, protected code, addresses and set/proof behavior
        > 2026-10-11 Check: uv run pytest -q tests/reading/test_go.py
- [ ] P13 | Specify C independently; verify supported modes, directive
      boundaries, declaration ownership and expected fixtures
        > 2026-10-11 Own dated spec and subplan; branch feat/lexer-c
- [ ] P14 | Implement the C reader from its definition; verify expected
      comments, protected code, addresses and set/proof behavior
        > 2026-10-11 Check: uv run pytest -q tests/reading/test_c.py
- [ ] P15 | Specify C++ independently; verify supported modes, directive
      boundaries, declaration ownership and expected fixtures
        > 2026-10-11 Own dated spec and subplan; branch feat/lexer-cpp
- [ ] P16 | Implement the C++ reader from its definition; verify expected
      comments, protected code, addresses and set/proof behavior
        > 2026-10-11 Check: uv run pytest -q tests/reading/test_cpp.py
- [ ] P17 | Specify Java independently; verify supported modes, directive
      boundaries, declaration ownership and expected fixtures
        > 2026-10-11 Own dated spec and subplan; branch feat/lexer-java
- [ ] P18 | Implement the Java reader from its definition; verify expected
      comments, protected code, addresses and set/proof behavior
        > 2026-10-11 Check: uv run pytest -q tests/reading/test_java.py
- [ ] P19 | Specify C# independently; verify supported modes, directive
      boundaries, declaration ownership and expected fixtures
        > 2026-10-11 Own dated spec and subplan; branch feat/lexer-csharp
- [ ] P20 | Implement the C# reader from its definition; verify expected
      comments, protected code, addresses and set/proof behavior
        > 2026-10-11 Check: uv run pytest -q tests/reading/test_csharp.py
- [ ] P21 | Specify Swift independently; verify supported modes, directive
      boundaries, declaration ownership and expected fixtures
        > 2026-10-11 Own dated spec and subplan; branch feat/lexer-swift
- [ ] P22 | Implement the Swift reader from its definition; verify expected
      comments, protected code, addresses and set/proof behavior
        > 2026-10-11 Check: uv run pytest -q tests/reading/test_swift.py
- [ ] P23 | Specify Kotlin independently; verify supported modes, directive
      boundaries, declaration ownership and expected fixtures
        > 2026-10-11 Own dated spec and subplan; branch feat/lexer-kotlin
- [ ] P24 | Implement the Kotlin reader from its definition; verify expected
      comments, protected code, addresses and set/proof behavior
        > 2026-10-11 Check: uv run pytest -q tests/reading/test_kotlin.py
- [ ] P25 | Specify JavaScript independently; verify supported modes, directive
      boundaries, declaration ownership and expected fixtures
        > 2026-10-11 Own dated spec and subplan; branch feat/lexer-javascript
- [ ] P26 | Implement the JavaScript reader from its definition; verify expected
      comments, protected code, addresses and set/proof behavior
        > 2026-10-11 Check: uv run pytest -q tests/reading/test_javascript.py
- [ ] P27 | Specify TypeScript independently; verify supported modes, directive
      boundaries, declaration ownership and expected fixtures
        > 2026-10-11 Own dated spec and subplan; branch feat/lexer-typescript
- [ ] P28 | Implement the TypeScript reader from its definition; verify expected
      comments, protected code, addresses and set/proof behavior
        > 2026-10-11 Check: uv run pytest -q tests/reading/test_typescript.py
- [ ] P29 | Specify Ruby independently; verify supported modes, directive
      boundaries, declaration ownership and expected fixtures
        > 2026-10-11 Own dated spec and subplan; branch feat/lexer-ruby
- [ ] P30 | Implement the Ruby reader from its definition; verify expected
      comments, protected code, addresses and set/proof behavior
        > 2026-10-11 Check: uv run pytest -q tests/reading/test_ruby.py
- [ ] P31 | Specify Shell independently; verify supported modes, directive
      boundaries, declaration ownership and expected fixtures
        > 2026-10-11 Own dated spec and subplan; branch feat/lexer-shell
- [ ] P32 | Implement the Shell reader from its definition; verify expected
      comments, protected code, addresses and set/proof behavior
        > 2026-10-11 Check: uv run pytest -q tests/reading/test_shell.py
- [ ] P33 | Specify SQL independently; verify supported modes, directive
      boundaries, declaration ownership and expected fixtures
        > 2026-10-11 Own dated spec and subplan; branch feat/lexer-sql
- [ ] P34 | Implement the SQL reader from its definition; verify expected
      comments, protected code, addresses and set/proof behavior
        > 2026-10-11 Check: uv run pytest -q tests/reading/test_sql.py
- [ ] P35 | Specify Lua independently; verify supported modes, directive
      boundaries, declaration ownership and expected fixtures
        > 2026-10-11 Own dated spec and subplan; branch feat/lexer-lua
- [ ] P36 | Implement the Lua reader from its definition; verify expected
      comments, protected code, addresses and set/proof behavior
        > 2026-10-11 Check: uv run pytest -q tests/reading/test_lua.py
- [x] P37 | Child lexer-python closed: gather, setting, both proofs, 3.11 | 2bf15f2b | Integrate
      Python reading through gather, setting and both proof commands; verify
      newer syntax works on Python 3.11
        > 2026-10-11 Complete the Python workflow before other language integration
        > 2026-10-11 Python child: docs/plans/2026-10-11-lexer-python.md
- [ ] P38 | Share reader results with paragraphs, forms and declarations; verify
      whole sections retain the existing a, b, c and f anchors
        > 2026-10-11 Check: uv run pytest -q tests/test_reading.py
- [ ] P39 | Map decoded prose to raw payloads; verify escapes, adjacent
      literals, marker recovery and binder raw_text reconstruction
        > 2026-10-11 Check: uv run pytest -q tests/test_comment_wrapping.py
- [ ] P40 | Reread every set result; verify add, rewrite, drop and move reach
      intended places without consuming neighboring code
        > 2026-10-11 Check: uv run pytest -q tests/test_proof_setter.py
- [ ] P41 | Unify both executable comparisons; verify token, literal, order,
      structure, directive and significant-separator mutations refuse
        > 2026-10-11 Check: uv run pytest -q tests/test_lexical_preservation.py
- [ ] P42 | Apply documentation ownership rules in both comparisons; verify
      additions, removals and replacement owners preserve ordinary literals
        > 2026-10-11 Check: uv run pytest -q tests/test_proof_command.py
- [ ] P43 | Supply declaration facts to referrer discovery; verify path terms
      remain and unavailable wider harvesting is reported explicitly
        > 2026-10-11 Check: uv run pytest -q tests/test_referrers.py
- [ ] P44 | Replace retired reader paths and duplicated language facts; verify
      consumers use the shared result and diagnostics
        > 2026-10-11 Check: uv run pytest -q tests/test_reading.py
- [ ] P45 | Update source-selection instructions; verify generated output is
      excluded and maintained input reaches gathering
        > 2026-10-11 Mechanism first; TODO 2026-10-11-maintained-source-selection
- [ ] P46 | Update agent references for current addresses and reader coverage;
      verify operational text contains only task-facing instructions
        > 2026-10-11 Check: uv run python scripts/check_vocabulary.py
- [ ] P47 | Update write instructions; verify proof precedes formatting and
      available local validation follows prove_unchanged
        > 2026-10-11 Preserve the exact approved local-validation instruction
- [ ] P48 | Replace obsolete fixture prescriptions with invented boundary cases;
      verify each expected classification can detect a wrong read
        > 2026-10-11 Use the design TODO mapping; retain independent behavioral goals
- [ ] P49 | Verify the command smoke and full regression suite with all
      supported reader definitions and unchanged dependency gates
        > 2026-10-11 Check: uv run pytest -q
- [ ] P50 | Verify lint, formatting, types, shipped syntax and vocabulary for
      the completed implementation
        > 2026-10-11 Run the existing CLAUDE.md completion commands
- [x] P51 | Exact source acquisition writing and integrations verified | fd1e56a1 | Integrate
      exact source acquisition and writing; verify UTF-8 byte fixtures in
      test_source_io and source-path integration tests
        > 2026-10-11 Subplan 2026-10-11-lexical-read-results owns this work
- [x] P52 | Immutable definitions and unique registry routes are implemented; full gates and review pass | afef752e | Build
      shared definition loading and registry selection; verify unique routes,
      explicit capabilities and excluded categories
        > 2026-10-11 Subplan 2026-10-11-lexical-reading-context owns this work
- [ ] P53 | Implement each language definition with its own spec and reader;
      verify independent rules without inherited configuration
        > 2026-10-11 Each language subplan supplies its own spec, definition and reader
