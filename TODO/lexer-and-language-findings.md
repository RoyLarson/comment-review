# Fifteen findings in lexer.py and language.py, from three review rounds

```
Status:   decision-needed
Progress: 2 of 15 tasks done
Owner:    backend
Requires-Roy: true
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
2026-08-22 and re-measured 2026-08-23. Two are fixed. Two need a RULING from Roy before
any code can be written -- Lua's `---` (task 15) and a same-line docstring (task 14).

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
- [ ] T14 -- * NEEDS A RULING, then a fix: what happens to a declaration whose
      docstring shares its LINE. MEASURED 2026-08-23 on legal Python -- `def g():
      """Same line doc."""` yields a paragraph at `5-5 kind=docstring anchor=g` with
      an EMPTY address, and `census.py` exits 1 on the WHOLE FILE with *"1 paragraph
      carry NO ADDRESS"* and the advice *"Re-run census.py"*, which never helps. !
      The ruling: does a same-line docstring get an `a`, is it intermediate and
      ignored (the 2026-08-19 intermediate-comment ruling), or is it refused with a
      message naming the cause? The advice cannot be written before the answer.
- [ ] T15 -- * NEEDS A RULING or a new field: Lua's `---`. The row at
      language.py:455-470 records the measurement and does not fix it, so every
      documented Lua declaration reads as `undocumented`. MEASURED 2026-08-22 on
      `corpora/neovim`, the first real Lua ever censused here: 2,505 of 2,741
      declarations carry a `---` run above them (91%) and ALL came back undocumented;
      43,563 of 92,578 lines open with `---`, of which 11,987 are LuaLS annotations.
      ! THE ONE-LINE FIX IS WRONG AND WAS TRIED: adding `---` to `line_comment` and
      `doc_line` turned 4,230 comments into docstrings and 0 differing files into 8.
      LuaLS writes `--- @class` and `--- @field` runs that document NO declaration --
      whole type-stub files are nothing else -- and a docstring tied to a declaration
      that is not there cannot be set back where it was read. ! The ruling: is a doc
      run above no declaration a comment, a docstring anchored to the module, or its
      own thing?
