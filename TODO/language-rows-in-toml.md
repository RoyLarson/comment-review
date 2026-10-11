# The language rows are data and live in code

```
Status:   open
Progress: 6 of 18 tasks closed
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

Each supported programming language has its own specification and definition
file. The definition owns its lexical forms, declaration and documentation
rules, supported dialects, and the configuration that makes its parser correct.
Declarative settings remain TOML, in a separate file for each language.
Procedural recognition can use language-owned code selected by that definition.

Parsing engines and mechanical helpers may be reused. Language families must not
supply definitions, default rules or inherited configuration. Each language's
rules are established independently from its own authoritative references and
tested with fixtures for that language.

Roy's instruction:

> A strong rule of mine is that each langauage gets its own spec. Any ideas, thoughts or other combining the languages into families is a strong failure of the Single Responsibility Principle and must not happen. How the code runs, the engines that parse the code correctly can be reused but the configuration pieces and how the engine is built to parse correctly needs to be configurable by language and each language must have its own definition file

T17 and T18 state the separate-specification and separate-definition goals. The
lexical-reader design maps the older combined-table and two-tier tasks to their
proposed replacements. Those old tasks require board supersession when the
implementation plan reconciles ownership; they are not completion evidence. Keep
delimiter precedence, explicit capabilities and registry dispatch checks. The
full name-harvester capability work remains separately scoped.

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
- [ ] T17 | Specify each supported language independently; verify each has its
      own dated spec, references and fixtures
        > 2026-10-11 Roy requires an independent specification for each language.
- [ ] T18 | Implement one definition file per language; verify each configures
      its parser without family defaults or language inheritance
        > 2026-10-11 Roy requires per-language definitions; engines may be reused.
