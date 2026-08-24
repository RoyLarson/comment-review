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
Triaged:  2026-08-23 — !! THE FIRST BOX WAS TICKED AND THE WORK IS NOT DONE. MEASURED:
          `find . -name languages.toml -not -path "./corpora/*"` returns NOTHING, `ls
          plugins/comment-review/skills/comment-review/references/` holds `vocabulary.toml`
          and no `languages.toml`, and `language.py:96` still opens
          `LANGUAGES: tuple[Language, ...] = (` over 18 `Language(` calls. The box is
          restored to `[ ]` and now names all 18 rows, so the old task 7 -- which said
          "alongside the other 17" on the assumption the move had happened -- is
          superseded by it. ! Line numbers RE-MEASURED: `tier_for` is `language.py:546`
          (this file said :394) and the name-harvester gate is `census.py:172` (said
          :160); `page.py:694`, `prove_unchanged.py:176` and `referrers.py:53` are exact.
```

## Objective

**The 18 language rows are data and live in code.** Roy, 2026-08-22: *"since tomllib is
available, the language definitions should live in a toml file not in code."* ! The pattern
already ships -- `references/vocabulary.toml` is read at runtime by `vocabulary.py` with
`tomllib`, stdlib since 3.11, which is the floor.

!! **NONE OF IT HAS MOVED YET.** MEASURED 2026-08-23: there is no `languages.toml` anywhere
outside `corpora/`, and `language.py:96` declares `LANGUAGES: tuple[Language, ...]` built from 18
`Language(...)` calls in Python source. This file recorded the move as done; it is not.

!! **IT MAKES THE MODULE'S OWN CLAIM TRUE.** `language.py` says *adding a language is a row,
not code* -- and today a row is a Python call in a Python file, so adding one means editing
shipped source that ruff, the floor gate and the shipped-syntax check all have to police. A
data file has no syntax anyone else's formatter can rewrite, which is the whole reason `except`
clauses in this tree may not hold tuple literals.

!! **AND IT TAKES THE PYTHON SPECIAL CASE WITH IT.** Roy, 2026-08-23: *"once the
languages.toml goes in the Python special case falls."* MEASURED 2026-08-23: `language.py:546`
is literally `return "tokenized" if lang.name == "python" else "lexical"`, and `page.py:694`
dispatches the READER on the same test while `page.py:847` and `page.py:857` stamp the tier from `tier_for`
-- so a file can be READ at one tier and LABELLED at the other, and half a fix does exactly
that. Three more sites decide *is this Python* three more ways: `census.py:172` gates its name
harvester on `lang.name != "python"`, and `prove_unchanged.py:176` and `referrers.py:53` each
re-spell the suffix tuple `(".py", ".pyi")` that `language.py:99` already owns.

! **THE TIER BECOMES A FIELD ON THE ROW**, so the dispatch reads the row like every other
per-language rule.

! **WHAT MUST SURVIVE THE MOVE.** ORDER IS SIGNIFICANT within a field -- openers match
longest-first, so `///` precedes `//` and `--[==[` precedes `--[[`; TOML arrays are ordered, so
this holds, but a test should say so. `block_comment` is a list of PAIRS. An EMPTY list means
the language has no `a` series at all -- C, C++, `yaml`, `toml`, `ini` and `sql` -- which is not
the same as a missing key, and a missing key would mean nobody decided.

! **VALIDATION GETS STRONGER, NOT WEAKER.** `test_every_row_STATES_its_own_quotes` parses the
Python AST today to tell a DECISION from an inherited default, because both look identical at
runtime. Against a TOML table it is just *is the key present*. ! Every per-language rule Roy has
stated -- no row inherits from another, every language carries all of its own definitions --
becomes a schema check over the table rather than a reading of source.

! **THEN CHECK WHAT ELSE IS DATA WEARING CODE.** The verdict table in `record.py` makes the
same claim in its own docstring and is a Python dataclass table for the same reasons this one
was -- not necessarily the same answer, since a verdict row carries behaviour a language row
does not, but the question is the same one and should be asked deliberately.

! **SUPERSEDES [`tier-dispatched-on-name`](completed/tier-dispatched-on-name-SUPERSEDED.md)**,
whose measurements are folded in above.

## Tasks

- [ ] T1 -- MOVE ALL 18 ROWS TO `references/languages.toml`, PYTHON INCLUDED, with
      `tier` as a field on the row, and build `Language` from the table. Roy,
      2026-08-22: *"since tomllib is available, the language definitions should
      live in a toml file not in code."* ! THE PATTERN ALREADY SHIPS:
      `references/vocabulary.toml` is read at runtime by `vocabulary.py` with
      `tomllib` -- stdlib since 3.11, which is the floor -- resolving the path from
      `Path(__file__).parent.parent`. !! THIS BOX WAS TICKED IN ERROR: MEASURED
      2026-08-23, no `languages.toml` exists outside `corpora/` and `language.py:96`
      still holds `LANGUAGES: tuple[Language, ...]` over 18 `Language(` calls.
      Verify: `references/languages.toml` exists with 18 tables, `grep -c
      "Language(" language.py` returns 1 (the dataclass), every `Language` is built
      from the TOML at runtime, and a test asserts the order-significant fields
      survive (`///` before `//`, `--[==[` before `--[[`) and that an EMPTY list
      still differs from a missing key.
- [x] T2 -- NOT A TASK, restated in the Objective. IT MAKES THE MODULE'S OWN CLAIM
      TRUE. `language.py` says *adding a language is a row, not code* -- and today a
      row is a Python call in a Python file, so adding one means editing shipped
      source that ruff, the floor gate and the shipped-syntax check all have to
      police. A data file has no syntax anyone else's formatter can rewrite, which
      is the whole reason `except` clauses in this tree may not hold tuple literals.
- [x] T3 -- NOT A TASK, restated in the Objective. WHAT MUST SURVIVE THE MOVE, and
      each is a real distinction the rows carry today: ORDER IS SIGNIFICANT within a
      field -- openers are matched longest-first, so `///` must precede `//` and
      `--[==[` must precede `--[[` (TOML arrays are ordered, so this holds, but a
      test should say so). `block_comment` is a list of PAIRS. And an EMPTY list is
      not a missing key: `declares = []` means the language has NO `a` series at
      all -- C, C++, yaml, toml, ini and sql -- while a missing key would mean
      nobody decided. ! The checkable half is T1's verify clause.
- [x] T4 -- NOT A TASK, restated in the Objective. THE VALIDATION GETS STRONGER, NOT
      WEAKER. `test_every_row_STATES_its_own_quotes` currently parses the Python AST
      to tell a DECISION from an inherited default, because both look identical at
      runtime. Against a TOML table that is just *is the key present*, which is
      easier to check and harder to get wrong. ! Every per-language rule Roy has
      stated -- no row inherits from another, every language carries all of its own
      definitions -- becomes a schema check over the table rather than a reading of
      source.
- [x] T5 -- SUPERSEDED. It said the move DOES NOT FIX THE TIER and should not
      pretend to. Roy ruled otherwise on 2026-08-23 -- *"once the languages.toml
      goes in the Python special case falls"* -- so `tier` is a FIELD ON THE ROW in
      T1 and the dispatch is T8. The measurement it carried is exact and is in the
      Objective, at the re-measured line: `language.py:546` reads `return
      "tokenized" if lang.name == "python" else "lexical"`.
- [x] T6 -- NOT A TASK, restated in the Objective. AND CHECK WHAT ELSE IS DATA
      WEARING CODE once this lands. The verdict table in `record.py` makes the same
      claim in its own docstring -- *adding or changing a verdict is a row, not new
      code* -- and is a Python dataclass table for the same reasons this one was. It
      is not necessarily the same answer, because a verdict row carries behaviour
      the language rows do not, but the question is the same one and should be asked
      deliberately. ! Where it becomes work, it is its own TODO, not a box here.
- [x] T7 -- SUPERSEDED BY T1. It said MAKE PYTHON HAVE ITS DEFINITION IN
      `references/languages.toml`, *alongside the other 17*, with `tier` as a field
      on the row. That phrasing rests on the other 17 having moved, and MEASURED
      2026-08-23 none of them has. T1 now names all 18 and carries the same verify.
- [ ] T8 -- REMOVE THE SPECIAL-CASE HANDLING FOR PYTHON. Verify, and both halves are
      greppable so a stranger can close it: no module outside `language.py` compares
      `lang.name` to `"python"`, and no module re-spells the `(".py", ".pyi")` suffix
      tuple `language.py:99` owns. That covers `language.py:546`, `page.py:694`,
      `census.py:172`, `prove_unchanged.py:176` and `referrers.py:53`. ! Reading
      `lang.name` is not the defect -- `census.py:302` and `:446` print it and
      `lexer.py:1491` names it in a message -- so the grep is for the COMPARISON.
