# The language rows are data and live in code

```
Status:   open
Progress: 6 of 16 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-22 (Roy, 2026-08-22: since tomllib is available the language
          definitions should live in a toml file not in code)
Cost:     2026-08-22 -- THERE IS NO PARSER TO WRITE, AND NONE TO REPLACE. Roy,
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
Triaged:  2026-08-23 -- !! THE FIRST BOX WAS TICKED AND THE WORK IS NOT DONE. MEASURED:
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
`tomllib`, stdlib since 3.11, which is the floor, resolving the path from
`Path(__file__).parent.parent`.

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

! **READING `lang.name` IS NOT THE DEFECT** -- `census.py:302` and `:446` print it and
`lexer.py:1491` names it in a message. What must go is the COMPARISON, which is why both halves
of the removal are greppable and a stranger can close them.

! **WHAT MUST SURVIVE THE MOVE.** ORDER IS SIGNIFICANT within a field -- openers match
longest-first, so `///` precedes `//` and `--[==[` precedes `--[[`; TOML arrays are ordered, so
this holds, but a test should say so. `block_comment` is a list of PAIRS. An EMPTY list means
the language has no `a` series at all -- C, C++, `yaml`, `toml`, `ini` and `sql` -- which is not
the same as a missing key, and a missing key would mean nobody decided.

! **VALIDATION GETS STRONGER, NOT WEAKER.** `test_every_row_STATES_its_own_quotes` parses the
Python AST today to tell a DECISION from an inherited default, because both look identical at
runtime. Against a TOML table it is just *is the key present*, which is easier to check and
harder to get wrong. ! Every per-language rule Roy has stated -- no row inherits from another,
every language carries all of its own definitions -- becomes a schema check over the table
rather than a reading of source.

! **THEN CHECK WHAT ELSE IS DATA WEARING CODE.** The verdict table in `record.py` makes the
same claim in its own docstring -- *adding or changing a verdict is a row, not new code* -- and
is a Python dataclass table for the same reasons this one was. Not necessarily the same answer,
since a verdict row carries behaviour a language row does not, but the question is the same one
and should be asked deliberately. ! Where it becomes work, it is its own TODO, not a box here.

! **SUPERSEDES [`tier-dispatched-on-name`](completed/tier-dispatched-on-name-SUPERSEDED.md)**,
whose measurements are folded in above.

## Tasks

- [ ] T1 | T1 -- Transcribe all 18 language rows into
      `references/languages.toml`, Python included, with `tier` as a field.
      Verify: the file holds 18 tables, one per row.
- [ ] T2 | T2 -- Build `Language` from that table at runtime, the way
      `vocabulary.py` reads `vocabulary.toml`. Verify: `grep -c "Language("
      language.py` returns 1.
- [ ] T3 | T3 -- Pin the order-significant fields, since openers match
      longest-first. Verify: a test fails if `///` follows `//`, or `--[==[`
      follows `--[[`.
- [ ] T4 | T4 -- Pin that an EMPTY list is not a missing key. Verify: `declares
      = []` loads as *no `a` series at all*, and a row with no `declares` key is
      refused as undecided.
- [ ] T5 | T5 -- Move `test_every_row_STATES_its_own_quotes` from parsing the
      Python AST to asking whether the key is present. Verify: the test reads
      the table, not the AST.
- [x] T6 | FINISHED | unknown | T6 -- NOT A TASK, restated in the Objective: the
      move makes `language.py`'s own claim -- *adding a language is a row, not
      code* -- true.
- [x] T7 | FINISHED | unknown | T7 -- NOT A TASK, restated in the Objective:
      WHAT MUST SURVIVE THE MOVE. The checkable halves are T3 and T4.
- [x] T8 | FINISHED | unknown | T8 -- NOT A TASK, restated in the Objective: the
      validation gets STRONGER, because a stated decision becomes *is the key
      present* rather than a reading of source.
- [x] T9 | FINISHED | unknown | T9 -- SUPERSEDED. It said the move does not fix
      the tier; Roy ruled otherwise 2026-08-23, so `tier` is a field on the row
      in T1 and the dispatch is T12.
- [x] T10 | FINISHED | unknown | T10 -- NOT A TASK, restated in the Objective:
      ask the same question of the verdict table in `record.py`. Where it
      becomes work, it is its own TODO.
- [x] T11 | FINISHED | unknown | T11 -- SUPERSEDED BY T1. It said give Python
      its definition *alongside the other 17*, which assumed they had moved.
      MEASURED 2026-08-23: none of them has.
- [ ] T12 | T12 -- Make `tier_for` (`language.py:546`) read the row's `tier`
      field instead of `lang.name == "python"`. Verify: `language.py` holds no
      comparison of `lang.name`.
- [ ] T13 | T13 -- Dispatch the READER at `page.py:694` on the row, not on
      `lang.name`. Verify: a file cannot be read at one tier and stamped at the
      other.
- [ ] T14 | T14 -- Gate the name harvester at `census.py:172` on a row field,
      not on `lang.name != "python"`. Verify: `census.py` holds no comparison of
      `lang.name`.
- [ ] T15 | T15 -- Make `prove_unchanged.py:176` take the `(".py", ".pyi")`
      suffix tuple from `language.py:99`. Verify: the tuple is not re-spelled in
      `prove_unchanged.py`.
- [ ] T16 | T16 -- Make `referrers.py:53` take the same suffix tuple from
      `language.py:99`. Verify: the tuple is not re-spelled in `referrers.py`.
