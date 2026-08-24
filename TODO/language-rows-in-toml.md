# The language rows are data and live in code

```
Status:   open
Progress: 6 of 8 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-22 (Roy, 2026-08-22: since tomllib is available the language
          definitions should live in a toml file not in code)
Cost:     2026-08-22 — THERE IS NO PARSER TO WRITE, AND NONE TO REPLACE. Roy,
          2026-08-22: *"I really thought you had made a temporary parser for the toml
          file since it was small and toml is pretty easy."* MEASURED: five readers
          across this tree parse TOML and ALL FIVE use stdlib `tomllib` -- the shipped
          `vocabulary.py`, `scripts/check_vocabulary.py`, `scripts/vocabulary_sweep.py`,
          `scripts/fetch_corpora.py` for `corpora.toml`, and nothing hand-rolled
          anywhere. `tomllib` is stdlib from 3.11, which IS the floor, verified on the
          floor interpreter. ! So the work is three steps and no machinery: transcribe
          the 18 rows, build `Language` from the table, and move the quotes-are-stated
          test from reading the Python AST to asking whether a key is present. No
          dependency, no parser, no floor risk.
```

## Objective

**The 18 language rows are data and live in code.** Roy, 2026-08-22: *"since tomllib is
available, the language definitions should live in a toml file not in code."* ! The pattern
already ships -- `references/vocabulary.toml` is read at runtime by `vocabulary.py` with
`tomllib`, stdlib since 3.11, which is the floor.

!! **IT MAKES THE MODULE'S OWN CLAIM TRUE.** `language.py` says *adding a language is a row,
not code* -- and today a row is a Python call in a Python file, so adding one means editing
shipped source that ruff, the floor gate and the shipped-syntax check all have to police. A
data file has no syntax anyone else's formatter can rewrite.

!! **AND IT TAKES THE PYTHON SPECIAL CASE WITH IT.** Roy, 2026-08-23: *"once the
languages.toml goes in the Python special case falls."* MEASURED 2026-08-22: `language.py:394`
is literally `return "tokenized" if lang.name == "python" else "lexical"`, and `page.py:694`
dispatches the READER on the same test while `page.py:815/825` stamps the tier from `tier_for`
-- so a file can be READ at one tier and LABELLED at the other, and half a fix does exactly
that. Three more sites decide *is this Python* three more ways: `census.py:160` gates its name
harvester on `lang.name != "python"`, and `prove_unchanged.py:176` and `referrers.py:53` each
re-spell the suffix tuple `language.py:99` already owns.

! **THE TIER BECOMES A FIELD ON THE ROW**, so the dispatch reads the row like every other
per-language rule.

! **WHAT MUST SURVIVE THE MOVE.** ORDER IS SIGNIFICANT within a field -- openers match
longest-first, so `///` precedes `//` and `--[==[` precedes `--[[`; TOML arrays are ordered, so
this holds, but a test should say so. `block_comment` is a list of PAIRS. An EMPTY list means
the language has no `a` series at all, which is not the same as a missing key.

! **VALIDATION GETS STRONGER, NOT WEAKER.** `test_every_row_STATES_its_own_quotes` parses the
Python AST today to tell a DECISION from an inherited default, because both look identical at
runtime. Against a TOML table it is just *is the key present*.

! **THEN CHECK WHAT ELSE IS DATA WEARING CODE.** The verdict table in `record.py` makes the
same claim in its own docstring and is a Python dataclass table for the same reasons this one
was -- not necessarily the same answer, since a verdict row carries behaviour a language row
does not.

! **SUPERSEDES [`tier-dispatched-on-name`](completed/tier-dispatched-on-name-SUPERSEDED.md)**,
whose measurements are folded in above.

## Tasks

- [x] MOVE THE 18 ROWS TO `references/languages.toml` and build `Language` from
      it. Roy, 2026-08-22: *"since tomllib is available, the language definitions
      should live in a toml file not in code."* ! THE PATTERN ALREADY SHIPS:
      `references/vocabulary.toml` is read at runtime by `vocabulary.py` with
      `tomllib` -- stdlib since 3.11, which is the floor -- resolving the path
      from `Path(__file__).parent.parent`. This is that pattern applied to the
      table that most loudly claims to be data.
- [x] IT MAKES THE MODULE'S OWN CLAIM TRUE. `language.py` says *adding a language
      is a row, not code* -- and today a row is a Python call in a Python file, so
      adding one means editing shipped source that ruff, the floor gate and the
      shipped-syntax check all have to police. A data file has no syntax anyone
      else's formatter can rewrite, which is the whole reason `except` clauses in
      this tree may not hold tuple literals.
- [x] WHAT MUST SURVIVE THE MOVE, and each is a real distinction the rows carry
      today: ORDER IS SIGNIFICANT within a field -- openers are matched longest-
      first, so `///` must precede `//` and `--[==[` must precede `--[[` (TOML
      arrays are ordered, so this holds, but a test should say so).
      `block_comment` is a list of PAIRS. And an EMPTY list is not a missing key:
      `declares = []` means the language has NO `a` series at all -- C, C++, yaml,
      toml, ini and sql -- while a missing key would mean nobody decided.
- [x] THE VALIDATION GETS STRONGER, NOT WEAKER.
      `test_every_row_STATES_its_own_quotes` currently parses the Python AST to
      tell a DECISION from an inherited default, because both look identical at
      runtime. Against a TOML table that is just *is the key present*, which is
      easier to check and harder to get wrong. ! Every per-language rule Roy has
      stated -- no row inherits from another, every language carries all of its
      own definitions -- becomes a schema check over the table rather than a
      reading of source.
- [x] IT DOES NOT FIX THE TIER, and should not pretend to. `tier_for` decides by
      the language NAME -- `return "tokenized" if lang.name == "python" else
      "lexical"` -- and `page.py` dispatches the READER on the same test while
      stamping the tier from `tier_for`. Moving the rows to data leaves that
      exactly where it is; see `tier-dispatched-on-name`.
- [x] AND CHECK WHAT ELSE IS DATA WEARING CODE once this lands. The verdict table
      in `record.py` makes the same claim in its own docstring -- *adding or
      changing a verdict is a row, not new code* -- and is a Python dataclass
      table for the same reasons this one was. It is not necessarily the same
      answer, because a verdict row carries behaviour the language rows do not,
      but the question is the same one and should be asked deliberately.
- [ ] MAKE PYTHON HAVE ITS DEFINITION IN `references/languages.toml`, alongside
      the other 17, with `tier` as a field on the row. Verify: `language.py`
      builds every `Language` from the TOML at runtime, no row is a Python call,
      and a test asserts the order-significant fields survive the move (`///`
      before `//`, `--[==[` before `--[[`) and that an EMPTY list still differs
      from a missing key.
- [ ] REMOVE THE SPECIAL-CASE HANDLING FOR PYTHON. Verify, and both are greppable
      so a stranger can close it: no module outside `language.py` tests
      `lang.name`, and no module re-spells a suffix tuple. That covers
      `language.py:394`, `page.py:694`, `census.py:160`, `prove_unchanged.py:176`
      and `referrers.py:53`.
