# Fifteen findings in lexer.py and language.py, from three review rounds

```
Status:   in-progress
Progress: 3 of 23 tasks done
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
```

## Objective

Fifteen findings in `lexer.py` and `language.py`, raised by three review rounds on
2026-08-22 and re-measured 2026-08-23. Two are fixed, and **both rulings this file was
waiting on are made** -- T14 and T15, 2026-08-23. Neither produced a single fix.

!! **T15 IS RULED: PLACEMENT DECIDES.** A doc run is a DOCSTRING when a documentable
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

! **AND IT COSTS AN INTERNALS CHANGE, WHICH IS T20.** Roy: *"it changes some of the
internals for the lexer. The lexer looks at the strings and maybe some closing strings
currently. It could/should look at placement but we have assumed placement currently."*
`_is_doc` at lexer.py:945-955 reads the opener characters and the character after them,
and nothing else.

!! **T21-T22 ARE THE TRAP THE RULING WALKS INTO.** `language.py:122` declares Rust
`doc_line=("///", "//!")` with the two undifferentiated, and they point OPPOSITE ways:
`///` documents what FOLLOWS, `//!` documents the ENCLOSING item and correctly has nothing
under it. *Does a declaration follow* is the right question for an outer opener and the
wrong one for an inner one, and no row says which it has. ! Roy raised the Rust connection
himself -- *"This is also rusts Docstring fix a little even though rust has /// for
docstrings instead of comments."* ! **The field is shared and each row's answer is its
own** -- T21 adds it, T22 is RUST'S decision, T23 is LUA'S.

!! **T14 IS RULED, AND IT PRODUCED TWO TASKS RATHER THAN ONE FIX.** A same-line docstring
-- `def g(): """d."""` -- gets an `a`. Roy, 2026-08-23: *"gets an a but when the lexer
type thing gets it in python it will end up as a c"* and *"also on rewrite it will end up
below the function def and that as fine."*

! **The ruling reaches past the census in both directions**, which is why T16-T19
exist. Backwards: when Python goes lexical the same construct becomes a `c`, because a
lexer sees a string beside code and has no AST saying it is documentation -- so the
address MOVES and someone will read that as a regression. Forwards: setting it back
places the docstring on its own line below the `def`, which rewrites a declaring line --
the one thing `prove_unchanged` exists to refuse. **Ruled ALLOWED, which is not the same
as invisible.**

! **The two modules were chosen because they are settled.** They do not shift under
`front-half-undetermined`, so a finding filed against them stays addressable.

## Tasks

- [x] T1 -- FINISHED. lexer.py's unparsed fallback now catches `tokenize.TokenError`
      and `IndentationError`, not `SyntaxError` alone. Verified 2026-08-23:
      `exceptions.TOKENIZE_ERRORS` names both, and lexer.py:1783-1789 states the
      measurement that produced it.
- [ ] T2 -- Annotate EVERY paragraph an unterminated block comment swallowed, not
      just the last. MEASURED 2026-08-23: the EOF back-matter split runs at
      lexer.py:1432-1438 and the `in_block` stamp at lexer.py:1440-1449 reaches only
      `out[-1]`, so the split can leave an earlier paragraph holding code with no
      annotation -- contradicting the note the stamp writes. Verify: a file whose
      block comment opens above an interior blank and never closes carries
      `unterminated-paragraph-comment` on every paragraph below the opener.
- [ ] T3 -- Exclude `Kind.MATTER` from the walk-up candidates, as `Kind.LEADING`
      already is. MEASURED 2026-08-23 at lexer.py:1580-1584: the `ends` filter tests
      `b.kind != Kind.LEADING` and nothing else, so front matter ALSO claims
      declaration 1. Verify: a Ruby file opening `# frozen_string_literal: true`
      above a `def` yields `f0` with `declares` unset, and only `a1` declares 1.
- [ ] T4 -- Let the shell row say `#` is inert after a dollar-brace. MEASURED
      2026-08-23: the shell row is language.py:435-442 and carries no such field, so
      `n=${#arr}  # count` censuses the `#` inside the expansion. Since the
      compositor keeps `line[:column-1]`, a `patch` or `drop` there writes back a
      broken expansion. Verify: that line censuses as ONE trailing comment at the
      `#` of `# count`, not at column 5.
- [x] T5 -- FIXED FOR KOTLIN, 2026-08-22. `data`, `sealed` and `open` are soft
      keywords and `_declares_here` matches the FIRST word, so `data = load()` minted
      a spurious `a`. Verified 2026-08-23: language.py:342-376 carries `data class`,
      `sealed class`, `sealed interface` and `open class` as two-word entries, with
      the reason recorded at :348-361 -- Kotlin's grammar, not a neighbour's. ! The
      Java, C# and Swift half of the same class is T11, which tracks the remainder.
- [ ] T6 -- Make the two-importer rule TRUE or stop asserting it. MEASURED
      2026-08-23, and both halves fail. (a) language.py:9 cites
      `scripts/check_language_leaf.py` as holding the rule; that file does not exist
      -- `ls scripts/` returns 10 tools and it is not among them, and the only two
      mentions of the name in the tree are that line and this TODO. (b) lexer.py:45-61
      imports and re-exports six language symbols (`BY_EXT`, `LANGUAGES`,
      `TIER_ANSWERS`, `Language`, `language_for`, `tier_for`), and FIVE modules read
      language fields through that door: `census` (:58), `page` (:75),
      `prove_unchanged` (:47), `desk` (:37) and `galley` (:89). The first four are
      exactly the modules language.py:16 names as the problem the split was made to
      end; `galley` is a fifth the prose does not mention. ! Only `compositor.py:68`
      imports from `language` directly. Verify: a gate exists and fails when a third
      module imports a language symbol, and language.py:9 names a file that exists.
- [ ] T7 -- Remove the two duplications. MEASURED 2026-08-23:
      `tuple(sorted(lang.line_comment, key=len, reverse=True))` is byte-identical at
      lexer.py:999 and desk.py:379; and the `continues-a-trailing-comment` stamp --
      annotation, note and a 3-sentence USER-VISIBLE string -- is copy-pasted across
      both tiers at lexer.py:1168-1176 and lexer.py:1772-1780. Verify: each appears
      once, and `grep -c "opens on the line after a trailing comment"` returns 1.
- [ ] T8 -- Use `bisect` where a sorted list is filtered. MEASURED 2026-08-23 at
      lexer.py:1614: `previous = [n for n in above_code if n < held.original_start]`
      scans a list `above_code = sorted(code)` built one line earlier. Verify: the
      scan is gone and the suite is green.
- [ ] T9 -- Replace the four one-element lists standing in for `nonlocal`.
      MEASURED 2026-08-23: `trailing_end = [_NO_TRAILING]` at lexer.py:1014 and again
      at :1713, `partial_first = [0]` at :1023, `seen_code = [False]` at :1035 --
      costing subscripts at :1087, :1164, :1176, :1346, :1349, :1373, :1406, :1413,
      :1780 and four comments justifying a workaround the 3.11 floor does not need.
      Verify: no `[0]` subscript on a one-element accumulator remains in lexer.py.
- [ ] T10 -- Settle what `Paragraph.lines` counts. It is filled by THREE incompatible
      rules and read by exactly ONE display column, census.py:588 (`{b.lines}L`).
      Verify: one rule fills it, or the field is gone and the column computes what it
      prints. ! Related to `census-row-carries-empty-fields`, where a margin row shows
      `lines=0` with `raw_lines` holding one empty string.
- [ ] T11 -- Give Java, C# and Swift their OWN expression of a soft keyword.
      MEASURED 2026-08-22 and still live 2026-08-23: `record` is in Java's `declares`
      at language.py:248 and C#'s at :283, and `convenience` and `required` are in
      Swift's at :326-327 -- all soft keywords, so `record = lookup()` is a legal
      assignment that mints a spurious `a` place. ! KOTLIN'S FIX DOES NOT TRANSFER
      AND WAS TRIED: `data class` works because both words are FIXED; Java's second
      word is the record's NAME and varies, so `record ` + space BROKE the real
      declaration. Roy, 2026-08-22: *"every language gets all of the definitions
      necessary to parse it specifically, because anything else is failing the SRP
      rules."* Verify: `record = lookup()` in a `.java` mints no `a`, and a real
      `record Point(int x)` still does.
- [ ] T12 -- Declare Rust's and C's spanning quotes. MEASURED 2026-08-23 by reading
      every `spanning_quotes=` in language.py: rust (row at :117-146) and c (row at
      :185-193) carry none. ! RUBY IS NOW DONE -- language.py:427 declares
      `("<<~", "<<-")`, the two DISTINCTIVE heredoc openers, alongside the four that
      landed 2026-08-22 (go backtick :172, cpp `R"` :207, csharp `@"` :292, shell
      `<<` :440). ! Rust's and C's are the EXPENSIVE ones: a Rust multi-line string
      opens with a plain `"`, so declaring it refuses nearly every Rust file. They
      want the STATEFUL reader from `python-cannot-read-python`, which fixes them by
      transitivity. Verify: a Rust file holding a multi-line string is neither
      refused wholesale nor has a line inside the literal stripped as a comment.
- [ ] T13 -- Bound Lua's long-bracket level, or read it. language.py:473 stops at two
      `=` (`--[==[`) and language.py:483-486 states the bound rather than leaving it
      silent, but `--[===[` is still read as code. ! MEASURED 2026-08-22: the
      compositor identity CANNOT catch this -- prose read as code sets back
      byte-identical -- so the sentence test in `test_fixture_identity.py` is the only
      gate that would. Verify: a fixture with `--[===[` fails before the fix.
- [ ] T14 -- Make `def g(): """d."""` census instead of failing the file. Verify: it
      types `a1 kind=docstring anchor=g` and `census.py` exits 0.
- [x] T15 -- RULED 2026-08-23: placement decides -- a doc run is a docstring when a
      declaration follows it, a comment when nothing does. Evidence in the Objective.
- [ ] T16 -- Record the `a1` -> `c` move in `docs/history.md` with the ruling that
      predicted it. Verify: the entry names both tiers and the ruling's date.
- [ ] T17 -- Pin the address the CURRENT tier produces, so the move arrives as a failing
      test. Verify: a test asserts `a1` for a same-line docstring today.
- [ ] T18 -- Set a same-line docstring on its own line below the declaration. Verify:
      `def g(): """d."""` round-trips to the two-line form.
- [ ] T19 -- Make `prove_unchanged` admit that one move. Verify: PROVEN on the two-line
      form, and still FAILS when any other token on that line moves.
- [ ] T20 -- Make `_is_doc` consult placement, not only the opener string. Verify: a Lua
      `---` run above `local function f()` types `docstring`, above nothing `comment`.
- [ ] T21 -- Give the `Language` row an `inner_doc` field, defaulting empty so every
      existing opener stays outer. Verify: the field exists and no row's typing changes.
- [ ] T22 -- Declare Rust's `//!` inner; `///` stays outer. Verify: a `.rs` opening `//!`
      above nothing types `docstring`, and `///` above nothing types `comment`.
- [ ] T23 -- Add `---` to Lua's `doc_line`, which T15's ruling authorises. Verify: `--- x`
      above `local function f()` types `docstring` anchored to it.
