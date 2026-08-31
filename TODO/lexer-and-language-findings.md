# Fifteen findings in lexer.py and language.py, from three review rounds

```
Status:   in-progress
Progress: 3 of 28 tasks done
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
- [ ] T4 | T4 -- Let the shell row say `#` is inert after a dollar-brace.
      Verify: `n=${#arr} # count` censuses as ONE trailing comment at `# count`,
      not at column 5.
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
- [ ] T12 | T12 -- Settle what `Paragraph.lines` counts: three rules fill it,
      one column reads it. Verify: one rule fills it, or the field is gone and
      the column computes it.
- [ ] T13 | T13 -- Give Java its own expression of a soft keyword: `record` at
      language.py:248. Verify: `record = lookup()` in a `.java` mints no `a`,
      and a real one still does.
- [ ] T14 | T14 -- Give C# its own expression of a soft keyword: `record` at
      language.py:283. Verify: `record = lookup()` in a `.cs` mints no `a`, and
      a real one still does.
- [ ] T15 | T15 -- Give Swift its own expression of soft keywords: `convenience`
      and `required`. Verify: `required = f()` in a `.swift` mints no `a`, and a
      real init still does.
- [ ] T16 | T16 -- Declare Rust's spanning quotes; language.py:117-146 carries
      none. Verify: a Rust multi-line string is neither refused wholesale nor
      read as comments.
- [ ] T17 | T17 -- Declare C's spanning quotes; language.py:185-193 carries
      none. Verify: a C multi-line string is neither refused wholesale nor read
      as comments.
- [ ] T18 | T18 -- Bound Lua's long-bracket level, or read it; language.py:473
      stops at two `=` so `--[===[` reads as code. Verify: a fixture with
      `--[===[` fails before the fix.
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
- [ ] T24 | T24 -- Make `prove_unchanged` admit that one move. Verify: PROVEN on
      the two-line form, and still FAILS when any other token on that line
      moves.
- [ ] T25 | T25 -- Make `_is_doc` consult placement, not only the opener string.
      Verify: a Lua `---` run above `local function f()` types `docstring`,
      above nothing `comment`.
- [ ] T26 | T26 -- Give the `Language` row an `inner_doc` field, defaulting
      empty so every existing opener stays outer. Verify: the field exists and
      no row's typing changes.
- [ ] T27 | T27 -- Declare Rust's `//!` inner; `///` stays outer. Verify: a
      `.rs` opening `//!` above nothing types `docstring`, and `///` above
      nothing types `comment`.
- [ ] T28 | T28 -- Add `---` to Lua's `doc_line`, which T20's ruling authorises.
      Verify: `--- x` above `local function f()` types `docstring` anchored to
      it.
