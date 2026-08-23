# The language rows are data and live in code

```
Status:   open
Progress: 0 of 6 tasks done
Owner:    comment-review
Requires-Roy: false
Raised:   2026-08-22 (Roy, 2026-08-22: since tomllib is available the language
          definitions should live in a toml file not in code)
```

## Objective

The language rows are data and live in code.

## Tasks

- [ ] MOVE THE 18 ROWS TO `references/languages.toml` and build `Language` from
      it. Roy, 2026-08-22: *"since tomllib is available, the language definitions
      should live in a toml file not in code."* ! THE PATTERN ALREADY SHIPS:
      `references/vocabulary.toml` is read at runtime by `vocabulary.py` with
      `tomllib` -- stdlib since 3.11, which is the floor -- resolving the path
      from `Path(__file__).parent.parent`. This is that pattern applied to the
      table that most loudly claims to be data.
- [ ] IT MAKES THE MODULE'S OWN CLAIM TRUE. `language.py` says *adding a language
      is a row, not code* -- and today a row is a Python call in a Python file, so
      adding one means editing shipped source that ruff, the floor gate and the
      shipped-syntax check all have to police. A data file has no syntax anyone
      else's formatter can rewrite, which is the whole reason `except` clauses in
      this tree may not hold tuple literals.
- [ ] WHAT MUST SURVIVE THE MOVE, and each is a real distinction the rows carry
      today: ORDER IS SIGNIFICANT within a field -- openers are matched longest-
      first, so `///` must precede `//` and `--[==[` must precede `--[[` (TOML
      arrays are ordered, so this holds, but a test should say so).
      `block_comment` is a list of PAIRS. And an EMPTY list is not a missing key:
      `declares = []` means the language has NO `a` series at all -- C, C++, yaml,
      toml, ini and sql -- while a missing key would mean nobody decided.
- [ ] THE VALIDATION GETS STRONGER, NOT WEAKER.
      `test_every_row_STATES_its_own_quotes` currently parses the Python AST to
      tell a DECISION from an inherited default, because both look identical at
      runtime. Against a TOML table that is just *is the key present*, which is
      easier to check and harder to get wrong. ! Every per-language rule Roy has
      stated -- no row inherits from another, every language carries all of its
      own definitions -- becomes a schema check over the table rather than a
      reading of source.
- [ ] IT DOES NOT FIX THE TIER, and should not pretend to. `tier_for` decides by
      the language NAME -- `return "tokenized" if lang.name == "python" else
      "lexical"` -- and `page.py` dispatches the READER on the same test while
      stamping the tier from `tier_for`. Moving the rows to data leaves that
      exactly where it is; see `tier-dispatched-on-name`.
- [ ] AND CHECK WHAT ELSE IS DATA WEARING CODE once this lands. The verdict table
      in `record.py` makes the same claim in its own docstring -- *adding or
      changing a verdict is a row, not new code* -- and is a Python dataclass
      table for the same reasons this one was. It is not necessarily the same
      answer, because a verdict row carries behaviour the language rows do not,
      but the question is the same one and should be asked deliberately.
