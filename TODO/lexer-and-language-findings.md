# Fifteen findings in lexer.py and language.py, from three review rounds

```
Status:   in-progress
Progress: 22 of 53 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-22 (/simplify rounds 1 and 2 and /code-review high round 3,
          2026-08-22 -- the ones touching the two reader modules, filed because
          those modules are settled and will not shift under front-half-undetermined)
RE-MEASURED: 2026-08-23 — every box re-checked against the tree. TWO ARE NOW FIXED and
             are ticked: Kotlin's soft keywords (`data class`, `sealed class`,
             `open class` at language.py:342-376) and Ruby's heredoc
             (`spanning_quotes=("<<~", "<<-")` at language.py:427). ! EVERY LINE
             NUMBER IN THE ORIGINAL BOXES WAS STALE -- lexer.py has grown to 1,904
             lines and every cited offset moved by 150-350 lines. The numbers below
             were re-read today. ! The title said "Ten findings" over fifteen boxes.
SPLIT:    2026-08-23 -- the boxes were cut to two lines each. Old T1-T13 became
          T1-T18; the ten already-correct boxes kept their prose byte-identical and
          only their labels moved, T14-T23 -> T19-T28, because the tool addresses
          tasks positionally and a label out of file order is a defect.
```

## Objective

Fifteen findings in `lexer.py` and `language.py`, raised by three review rounds on
2026-08-22 and re-measured 2026-08-23. Two are fixed, and **both rulings this file was
waiting on are made** -- T19 and T20, 2026-08-23. Neither produced a single fix.

!! **T20 IS RULED: PLACEMENT DECIDES.** A doc run is a DOCSTRING when a documentable
declaration follows it and a COMMENT when nothing does. Roy: *"That seems reasonable and
likely that it will be generic."*

MEASURED on `corpora/neovim`, the first real Lua censused here: **2,505 of 2,741
declarations (91%) carry a `---` run above them and ALL came back undocumented**; 43,563 of
92,578 lines open with `---`, 11,987 of them LuaLS annotations. ! **THE ONE-LINE FIX WAS
TRIED AND IS WRONG**: adding `---` to `line_comment` and `doc_line` turned 4,230 comments
into docstrings and 0 differing files into 8, because a docstring tied to a declaration
that is not there cannot be set back where it was read.

The three shapes the rule has to separate, `language.py:455-470` recording the first
measurement:

| where | shape | is |
| --- | --- | --- |
| `vim/glob.lua:89-93` | prose + `@param`/`@return` above `local function end_seg(t)` | docstring |
| `vim/glob.lua:67-69` | `@param`/`@return` ALONE above `local function start_seg(p)` | docstring |
| `vim/lsp/_meta/protocol.lua:24-28` | `@class`/`@field` above NOTHING, in a file whose line 12 reads `error('Cannot require a meta file')` | comment |

! **AN EXCLUDE-LIST OF `@`-TAGS GETS THE MIDDLE ROW WRONG** -- the only thing in it is
annotations and it is still that function's documentation. That was the alternative.

! **AND IT COSTS AN INTERNALS CHANGE, WHICH IS T25.** Roy: *"it changes some of the
internals for the lexer. The lexer looks at the strings and maybe some closing strings
currently. It could/should look at placement but we have assumed placement currently."*
`_is_doc` at lexer.py:945-955 reads the opener characters and the character after them,
and nothing else.

!! **T26-T27 ARE THE TRAP THE RULING WALKS INTO.** `language.py:122` declares Rust
`doc_line=("///", "//!")` with the two undifferentiated, and they point OPPOSITE ways:
`///` documents what FOLLOWS, `//!` documents the ENCLOSING item and correctly has nothing
under it. *Does a declaration follow* is the right question for an outer opener and the
wrong one for an inner one, and no row says which it has. ! Roy raised the Rust connection
himself -- *"This is also rusts Docstring fix a little even though rust has /// for
docstrings instead of comments."* ! **The field is shared and each row's answer is its
own** -- T26 adds it, T27 is RUST'S decision, T28 is LUA'S.

!! **T19 IS RULED, AND IT PRODUCED TWO TASKS RATHER THAN ONE FIX.** A same-line docstring
-- `def g(): """d."""` -- gets an `a`. Roy, 2026-08-23: *"gets an a but when the lexer
type thing gets it in python it will end up as a c"* and *"also on rewrite it will end up
below the function def and that as fine."*

! **The ruling reaches past the census in both directions**, which is why T21-T24
exist. Backwards: when Python goes lexical the same construct becomes a `c`, because a
lexer sees a string beside code and has no AST saying it is documentation -- so the
address MOVES and someone will read that as a regression. Forwards: setting it back
places the docstring on its own line below the `def`, which rewrites a declaring line --
the one thing `prove_unchanged` exists to refuse. **Ruled ALLOWED, which is not the same
as invisible.**

! **The two modules were chosen because they are settled.** They do not shift under
`front-half-undetermined`, so a finding filed against them stays addressable.

### What the boxes carried -- the evidence, moved out of the tasks

! **T1.** `exceptions.TOKENIZE_ERRORS` names both `tokenize.TokenError` and
`IndentationError`, and lexer.py:1783-1789 states the measurement that produced it.

! **T2.** MEASURED 2026-08-23: the EOF back-matter split runs at lexer.py:1432-1438 and
the `in_block` stamp at lexer.py:1440-1449 reaches only `out[-1]`, so the split can leave
an earlier paragraph holding code with no annotation -- contradicting the note the stamp
writes. The shape to check is a file whose block comment opens above an interior blank
and never closes.

! **T3.** MEASURED 2026-08-23 at lexer.py:1580-1584: the `ends` filter tests
`b.kind != Kind.LEADING` and nothing else, so front matter ALSO claims declaration 1. The
worked shape is a Ruby file opening `# frozen_string_literal: true` above a `def`.

! **T4.** MEASURED 2026-08-23: the shell row is language.py:435-442 and carries no field
for an inert `#`, so `n=${#arr}  # count` censuses the `#` inside the expansion, at column
5. Since the compositor keeps `line[:column-1]`, a `patch` or `drop` there writes back a
broken expansion.

! **T5.** `data`, `sealed` and `open` are soft keywords and `_declares_here` matches the
FIRST word, so `data = load()` minted a spurious `a`. Verified 2026-08-23:
language.py:342-376 carries `data class`, `sealed class`, `sealed interface` and
`open class` as two-word entries, with the reason recorded at :348-361 -- Kotlin's
grammar, not a neighbour's.

! **T6 and T7 were ONE box and both halves fail.** MEASURED 2026-08-23. (a) language.py:9
cites `scripts/check_language_leaf.py` as holding the two-importer rule; that file does
not exist -- `ls scripts/` returns 10 tools and it is not among them, and the only two
mentions of the name in the tree are that line and this TODO. (b) lexer.py:45-61 imports
and re-exports six language symbols (`BY_EXT`, `LANGUAGES`, `TIER_ANSWERS`, `Language`,
`language_for`, `tier_for`), and FIVE modules read language fields through that door:
`census` (:58), `page` (:75), `prove_unchanged` (:47), `desk` (:37) and `galley` (:89).
The first four are exactly the modules language.py:16 names as the problem the split was
made to end; `galley` is a fifth the prose does not mention. ! Only `compositor.py:68`
imports from `language` directly.

! **T8 and T9 were ONE box, and they are two different duplications.** MEASURED
2026-08-23: `tuple(sorted(lang.line_comment, key=len, reverse=True))` is byte-identical at
lexer.py:999 and desk.py:379; and the `continues-a-trailing-comment` stamp -- annotation,
note and a 3-sentence USER-VISIBLE string -- is copy-pasted across both tiers at
lexer.py:1168-1176 and lexer.py:1772-1780. The sentence to grep for the second is
*"opens on the line after a trailing comment"*, which must appear once.

! **T10.** MEASURED 2026-08-23 at lexer.py:1614:
`previous = [n for n in above_code if n < held.original_start]` scans a list
`above_code = sorted(code)` built one line earlier.

! **T11.** MEASURED 2026-08-23: `trailing_end = [_NO_TRAILING]` at lexer.py:1014 and again
at :1713, `partial_first = [0]` at :1023, `seen_code = [False]` at :1035 -- costing
subscripts at :1087, :1164, :1176, :1346, :1349, :1373, :1406, :1413, :1780 and four
comments justifying a workaround the 3.11 floor does not need.

! **T12.** `Paragraph.lines` is filled by THREE incompatible rules and read by exactly ONE
display column, census.py:588 (`{b.lines}L`). ! Related to
`census-row-carries-empty-fields`, where a margin row shows `lines=0` with `raw_lines`
holding one empty string.

!! **T13, T14 and T15 were ONE box covering three languages, which this repo's own rule
forbids.** MEASURED 2026-08-22 and still live 2026-08-23: `record` is in Java's `declares`
at language.py:248 and C#'s at :283, and `convenience` and `required` are in Swift's at
:326-327 -- all soft keywords, so `record = lookup()` is a legal assignment that mints a
spurious `a` place. ! KOTLIN'S FIX DOES NOT TRANSFER AND WAS TRIED: `data class` works
because both words are FIXED; Java's second word is the record's NAME and varies, so
`record ` + space BROKE the real declaration. Roy, 2026-08-22: *"every language gets all
of the definitions necessary to parse it specifically, because anything else is failing
the SRP rules."*

!! **T16 and T17 were ONE box covering two languages.** MEASURED 2026-08-23 by reading
every `spanning_quotes=` in language.py: rust (row at :117-146) and c (row at :185-193)
carry none. ! RUBY IS NOW DONE -- language.py:427 declares `("<<~", "<<-")`, the two
DISTINCTIVE heredoc openers, alongside the four that landed 2026-08-22 (go backtick :172,
cpp `R"` :207, csharp `@"` :292, shell `<<` :440). ! Rust's and C's are the EXPENSIVE
ones: a Rust multi-line string opens with a plain `"`, so declaring it refuses nearly
every Rust file. They want the STATEFUL reader from `python-cannot-read-python`, which
fixes them by transitivity.

! **T18.** language.py:473 stops at two `=` (`--[==[`) and language.py:483-486 states the
bound rather than leaving it silent, but `--[===[` is still read as code. ! MEASURED
2026-08-22: the compositor identity CANNOT catch this -- prose read as code sets back
byte-identical -- so the sentence test in `test_fixture_identity.py` is the only gate that
would.

## Tasks

- [x] T1 | FINISHED | unknown | T1 -- FINISHED. lexer.py's unparsed fallback
      catches `tokenize.TokenError` and `IndentationError`, not `SyntaxError`
      alone. Verified at lexer.py:1783-1789.
- [ ] T2 | T2 -- Stamp every paragraph an unterminated block comment swallowed,
      not only the last. Verify: all of them carry
      `unterminated-paragraph-comment`.
- [ ] T3 | T3 -- Exclude `Kind.MATTER` from the walk-up candidates. Verify: Ruby
      front matter above a `def` leaves `f0.declares` unset, and only `a1`
      declares 1.
- [-] T4 | Moved to language-reader-shell.md | 42f3d3e5 | T4 -- Let the shell
      row say `#` is inert after a dollar-brace. Verify: `n=${#arr} # count`
      censuses as ONE trailing comment at `# count`, not at column 5.
        > 2026-10-10 Parameter expansion value=${value#prefix} becomes a comment
- [x] T5 | FINISHED | unknown | T5 -- FIXED FOR KOTLIN 2026-08-22: the soft
      keywords are two-word entries at language.py:342-376, with the reason at
      :348-361. Java, C# and Swift are T13-T15.
- [ ] T6 | T6 -- Make language.py:9 name a file that exists, or drop the
      citation -- `scripts/check_language_leaf.py` does not. Verify: the path it
      names resolves.
- [ ] T7 | T7 -- Gate the two-importer rule: fail when a third module reads a
      language symbol. Verify: the gate exists and fails on a planted third
      importer of `language`.
- [ ] T8 | T8 -- De-duplicate the sorted `line_comment` opener tuple,
      byte-identical at lexer.py:999 and desk.py:379. Verify: the expression
      appears once.
- [ ] T9 | T9 -- De-duplicate the `continues-a-trailing-comment` stamp,
      copy-pasted at lexer.py:1168-1176 and :1772-1780. Verify: `grep -c` of its
      sentence returns 1.
- [ ] T10 | T10 -- Use `bisect` at lexer.py:1614, where a list comprehension
      scans the sorted `above_code` built one line earlier. Verify: the scan is
      gone and the suite green.
- [ ] T11 | T11 -- Replace the four one-element lists standing in for `nonlocal`
      in lexer.py. Verify: no `[0]` subscript on a one-element accumulator
      remains in lexer.py.
- [x] T12 | One rule: Paragraph.lines derives from counted_lines | b30cc510 | T12
      -- Settle what `Paragraph.lines` counts: three rules fill it, one column
      reads it. Verify: one rule fills it, or the field is gone and the column
      computes it.
        > 2026-10-25 Rule settled: counted_lines; decision-log.md Process: #223
- [-] T13 | Moved to language-reader-java.md | 42f3d3e5 | T13 -- Give Java its
      own expression of a soft keyword: `record` at language.py:248. Verify:
      `record = lookup()` in a `.java` mints no `a`, and a real one still does.
- [ ] T14 | T14 -- Give C# its own expression of a soft keyword: `record` at
      language.py:283. Verify: `record = lookup()` in a `.cs` mints no `a`, and
      a real one still does.
- [-] T15 | Moved to language-reader-swift.md | 42f3d3e5 | T15 -- Give Swift its
      own expression of soft keywords: `convenience` and `required`. Verify:
      `required = f()` in a `.swift` mints no `a`, and a real init still does.
- [x] T16 | FINISHED: the Rust scanner reads a multi-line string as one literal token, neither a read failure nor comments (tests/reading/test_rust.py) | b239c6ca | T16
      -- Declare Rust's spanning quotes; language.py:117-146 carries none.
      Verify: a Rust multi-line string is neither refused wholesale nor read as
      comments.
        > 2026-10-10 Multiline Rust literal edits compare equal as stripped code
- [ ] T17 | T17 -- Declare C's spanning quotes; language.py:185-193 carries
      none. Verify: a C multi-line string is neither refused wholesale nor read
      as comments.
- [-] T18 | Moved to language-reader-lua.md | 42f3d3e5 | T18 -- Bound Lua's
      long-bracket level, or read it; language.py:473 stops at two `=` so
      `--[===[` reads as code. Verify: a fixture with `--[===[` fails before the
      fix.
- [ ] T19 | T19 -- Make `def g(): """d."""` census instead of failing the file.
      Verify: it types `a1 kind=docstring anchor=g` and `census.py` exits 0.
- [x] T20 | FINISHED | unknown | T20 -- RULED 2026-08-23: placement decides -- a
      doc run is a docstring when a declaration follows it, a comment when
      nothing does. Evidence in the Objective.
- [ ] T21 | T21 -- Record the `a1` -> `c` move in `docs/history.md` with the
      ruling that predicted it. Verify: the entry names both tiers and the
      ruling's date.
- [ ] T22 | T22 -- Pin the address the CURRENT tier produces, so the move
      arrives as a failing test. Verify: a test asserts `a1` for a same-line
      docstring today.
- [ ] T23 | T23 -- Set a same-line docstring on its own line below the
      declaration. Verify: `def g(): """d."""` round-trips to the two-line form.
        > 2026-09-03 MEASURED 2026-09-03: the one-line form round-trips byte-exact today
        > 2026-09-03 lossless returns None; this would make it return a message
        > 2026-09-03 and it moves a CODE line, which is why T24 exists beside it
        > 2026-09-03 RULED IN by Roy 2026-09-03 -- Addressing 20. It moves to the a spot
        > 2026-09-03 tokenized tier only; lexical is python-cannot-read-python
        > 2026-09-03 the walk emits NO a place for a same-line decl
        > 2026-09-03 so this must create one first -- nothing to move into
        > 2026-09-03 MEASURED: the ast reader is right; the page assembly loses it
        > 2026-09-03 MEASURED: the ast reader is right, the page loses it
- [ ] T24 | T24 -- Make `prove_unchanged` admit that one move. Verify: PROVEN on
      the two-line form, and still FAILS when any other token on that line
      moves.
        > 2026-09-03 needed with T23: admit that one move, fail on any other token
        > 2026-09-03 ast.dump has no lineno, so it already admits every move
        > 2026-09-03 second clause already false under ast; Process 82 rules the rebuild
- [-] T25 | Moved to language-reader-lua.md | 42f3d3e5 | T25 -- Make `_is_doc`
      consult placement, not only the opener string. Verify: a Lua `---` run
      above `local function f()` types `docstring`, above nothing `comment`.
- [-] T26 | A field on the in-code row; reissued against Rust's definition | 9e376f5f | T26
      -- Give the `Language` row an `inner_doc` field, defaulting empty so every
      existing opener stays outer. Verify: the field exists and no row's typing
      changes.
- [x] T27 | Rust //! above nothing is the a0 docstring and /// above nothing is a comment: test_rust_page_inner_doc_above_nothing_is_the_module_docstring, test_rust_page_outer_doc_above_nothing_is_a_comment | b9c5ed1e | T27
      -- Declare Rust's `//!` inner; `///` stays outer. Verify: a `.rs` opening
      `//!` above nothing types `docstring`, and `///` above nothing types
      `comment`.
- [-] T28 | Moved to language-reader-lua.md | 42f3d3e5 | T28 -- Add `---` to
      Lua's `doc_line`, which T20's ruling authorises. Verify: `--- x` above
      `local function f()` types `docstring` anchored to it.
- [ ] T29 | Correct `doc_is_structural`'s docstring so it matches what Python
      yields on the lexical tier. Verify: the prose names the empty result
- [x] T30 | All literals read; removals retain quotes and executable suffixes | b96af9f5bcbfa8f77d449dcc4b7ca9aa2e005ee9 | Read
      all concatenated docstring literals in lexer.py:313; test moving second.
      from adjacent Python literals succeeds
        > 2026-10-02 Repro: .tmp/review_docstring_literals.py; second literal omitted
- [x] T31 | Contract corrected; raw removal and refusal tests passed | 6eb1fb15651b0dd1bd072a135c5040e40a26dfa4 | Clarify
      docstring.py without_raw contract; test empty-expression removal and
      invalid-edit refusal
        > 2026-10-03 Review: full removal deletes literals; invalid edits return None
- [x] T32 | FINISHED: the Rust scanner reads raw strings to their exact guard count, so a comment marker inside stays literal data (tests/reading/test_rust.py) | b239c6ca | Recognize
      raw string delimiters in lexer.py:510; verify a quoted marker inside a
      Rust raw string stays literal data
- [-] T33 | Moved to language-reader-javascript.md | 42f3d3e5 | Recognize
      JavaScript regex literals in lexer.py:1071; verify /[//]/ yields no
      comment paragraph
- [ ] T34 | Resume code scanning after block comments in lexer.py:1071; verify a
      quote in a block cannot hide a following line comment
- [-] T35 | Moved to language-reader-lua.md | 42f3d3e5 | Select the earliest
      block opener in lexer.py:1072; verify mixed Lua delimiters inside a long
      comment preserve its full body
- [ ] T36 | Replace `doc_inside` with a documentation position every language
      row states
        > 2026-10-16 Reason: 17 of 18 rows inherit above from a default; 11 declare
        > 2026-10-16 Reason: a bool states inside; above is only its absence
        > 2026-10-16 Check: Language has no default position; every row names one
        > 2026-10-16 Check: `doc_inside` is gone from src; page and compositor pass
- [ ] T37 | Rename the side `documentable` returns for a doc set above its
      declaration
        > 2026-10-16 Reason: it is `ON`, the c letter, used for between gap and code
        > 2026-10-16 Check: documentable returns no series letter for a doc side
- [ ] T38 | Rewrite the CLAUDE.md doc-position sentence to the stated field
        > 2026-10-16 Reason: Roy, 2026-10-16: on Rust it goes above, not on the line
        > 2026-10-16 Check: the sentence names the field T36 adds; Roy approves it
- [-] T39 | Widened to removing the Python row; reissued as a new task | 9e376f5f | Remove
      the Python `Language` row's grammar fields
        > 2026-10-17 Reason: `python.toml` states it; no Python read uses the row
        > 2026-10-17 Check: the Python row carries no grammar; reading suites pass
- [ ] T40 | Remove `BY_EXT`, which nothing reads
        > 2026-10-17 Reason: `language_for` rebuilds a Language on every call instead
        > 2026-10-17 Check: grep -rn BY_EXT src tests scripts finds nothing
- [ ] T41 | Remove the grammar no reader reads from the toml, ini, yaml rows
        > 2026-10-17 Reason: none is in READER_METADATA; language_for skips them
        > 2026-10-17 Check: those rows carry only name and extensions
- [ ] T42 | Move `NAMED_DEFS` into `concordance`
        > 2026-10-17 Reason: only concordance reads it; it is lexer.py's last ast use
        > 2026-10-17 Check: grep finds no `import ast` in reading/lexer.py
- [ ] T43 | Remove the Annotations banner from `lexer.py`
        > 2026-10-17 Reason: nothing under it is an annotation
        > 2026-10-17 Check: grep finds no Annotations banner in reading/lexer.py
- [ ] T44 | Move the comment-form readers out of `lexer.py` to the desk
        > 2026-10-17 Reason: only desk/marks/rules.py reads comment_form; Process #212
        > 2026-10-17 Check: lexer.py defines no comment_form or _comment_fragment
- [ ] T45 | Inline `ESCAPE_WIDTH` into `_closes_a_character`
        > 2026-10-17 Reason: it is a module constant one function reads
        > 2026-10-17 Check: grep finds ESCAPE_WIDTH nowhere in src
- [ ] T46 | Move the galley-defect account out of the lexer's loop
        > 2026-10-17 Reason: it documents results/galley.py, not this loop
        > 2026-10-17 Check: the loop comment states only what the loop does
- [x] T47 | FINISHED: doc-kind-unresolved and flag_structural_docs retired (#231) | 79cf418f | Remove
      the `doc-kind-unresolved` annotation, which nothing reads
        > 2026-10-17 Reason: grep over src and tests finds it only where it is stamped
        > 2026-10-17 Check: grep -rn doc-kind-unresolved src finds nothing
- [x] T48 | Python row removed; python.toml is its only definition | 064bd62d | Remove
      the Python `Language` row from `LANGUAGES`
- [x] T49 | rust.toml states //! and /*! as inner doc openers | 3f1a4817 | State
      Rust's inner doc openers in Rust's own definition file
- [ ] T50 | Read a line-1 comment run above a declaration as f0 matter, not an a
      docstring (#232)
        > 2026-10-26 js: // Licence, blank, function f() {} -> a1; over const x -> f0
        > 2026-10-26 At ef037f20 too; document_declarations claims before the matter cut
- [ ] T51 | Make Python decorators and Rust attributes one unit with their item
        > 2026-10-26 decision-log #238; CodeLine.joins from P18; b falls inside today
- [ ] T52 | Match a C# attribute section apart from a collection expression
- [ ] T53 | Make every comment above a module docstring front matter, per #240
        > 2026-10-26 py: lic, blank, # note, blank, doc sets back reordered; at ef037f20
        > 2026-10-26 js twin hides it: // note + /** Doc. */ read as one b0 comment
        > 2026-10-26 pymc _version.py, distributions/continuous.py, setupegg.py
        > 2026-10-26 Foot mirrors it (#240): comments under a closing doc are matter
